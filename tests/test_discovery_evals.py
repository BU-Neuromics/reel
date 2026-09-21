"""The grader, proved without calling a model.

What is asserted here is fixed by the goal statement: a discovery turn succeeds
when it names the slots a user would need in their query. So these tests are
about *which slots were named*, and deliberately say nothing about wording.
"""
import pytest

from reel.evals import DiscoveryCase, grade_turn, load_cases, slots_in_schema

CAPS = {
    "Donor": {"fields": [
        {"name": "history_of_rhi"}, {"name": "cause_of_death"},
        {"name": "notes"}, {"name": "cohort"},
    ]},
    "Sample": {"fields": [{"name": "storage_condition"}, {"name": "donor"}]},
}


def proposal(spec, message="ok"):
    return {"status": "proposal", "message": message, "query_spec": spec}


def answered(message):
    return {"status": "clarification", "message": message, "query_spec": None}


class TestWhatCountsAsNaming:
    def test_a_filtered_slot_counts(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"history_of_rhi"}))
        turn = proposal({"criteria": [{"kind": "field", "slot": "history_of_rhi"}]})
        assert grade_turn(case, turn, CAPS).passed

    def test_a_slot_named_in_prose_counts(self):
        # An answered clarification communicates the field just as well as a
        # filter does; the goal is that the user learns what to include.
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"storage_condition"}))
        assert grade_turn(case, answered("storage_condition records how it was kept."), CAPS).passed

    def test_a_traversed_edge_and_its_related_slot_both_count(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"donor", "cohort"}))
        turn = proposal({"criteria": [
            {"kind": "related", "edge": "donor", "quantifier": "some",
             "criteria": [{"slot": "cohort", "op": "eq", "value": "case"}]},
        ]})
        assert grade_turn(case, turn, CAPS).passed

    def test_only_real_slots_are_credited(self):
        # Prose mentioning a field the schema has no such slot for must not
        # count -- otherwise an invented field would score as a hit.
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"history_of_rhi"}))
        out = grade_turn(case, answered("try tox_screen_result"), CAPS)
        assert not out.passed
        assert out.named == frozenset()


class TestSubsetNotEquality:
    def test_naming_extra_relevant_slots_still_passes(self):
        # Offering cause_of_death alongside history_of_rhi is a better answer.
        # Equality here would train the prompt to be stingy.
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"history_of_rhi"}))
        turn = answered("history_of_rhi is the flag; cause_of_death and notes may mention it too.")
        assert grade_turn(case, turn, CAPS).passed

    def test_missing_one_expected_slot_fails_and_says_which(self):
        case = DiscoveryCase(id="c", utterance="u",
                             expect_slots=frozenset({"access_level", "history_of_rhi"}))
        out = grade_turn(case, answered("history_of_rhi is the flag."), CAPS)
        assert not out.passed
        assert "access_level" in out.detail

    def test_a_forbidden_slot_fails_even_when_the_expected_one_is_named(self):
        case = DiscoveryCase(id="c", utterance="u",
                             expect_slots=frozenset({"cause_of_death"}),
                             forbid_slots=frozenset({"cohort"}))
        # `cohort` written as a field reference — a bare mention is prose and is
        # deliberately not credited (see TestSlotNamesThatAreAlsoEnglishWords).
        out = grade_turn(case, answered("cause_of_death, and `cohort` groups them."), CAPS)
        assert not out.passed
        assert "cohort" in out.detail


class TestTheNegativeCase:
    """The case that catches a planner which always finds *something*.

    A planner that reaches for the nearest plausible field reads as confident
    and is occasionally wrong. Only a topic the schema does not model catches
    it, and nothing else in a suite of positive cases will.
    """

    def test_naming_nothing_passes(self):
        case = DiscoveryCase(id="c", utterance="toxicology?", expect_none=True)
        assert grade_turn(case, answered("Nothing here records toxicology."), CAPS).passed

    def test_reaching_for_a_plausible_field_fails(self):
        case = DiscoveryCase(id="c", utterance="toxicology?", expect_none=True)
        out = grade_turn(case, proposal({"criteria": [{"kind": "field", "slot": "notes"}]}), CAPS)
        assert not out.passed
        assert "notes" in out.detail

    def test_an_error_turn_does_not_pass_by_naming_nothing(self):
        # An error names no slot either. Without this it would score as a pass
        # for the wrong reason -- exactly what this case exists to prevent.
        case = DiscoveryCase(id="c", utterance="toxicology?", expect_none=True)
        out = grade_turn(case, {"status": "error", "message": "unreachable", "query_spec": None}, CAPS)
        assert not out.passed
        assert "error" in out.detail


class TestCaseFileHygiene:
    def test_a_case_that_asserts_nothing_is_refused(self):
        with pytest.raises(ValueError, match="asserts nothing"):
            DiscoveryCase(id="c", utterance="u")

    def test_contradictory_expectations_are_refused(self):
        with pytest.raises(ValueError, match="contradict"):
            DiscoveryCase(id="c", utterance="u",
                          expect_slots=frozenset({"notes"}), expect_none=True)

    def test_loading_without_a_path_says_where_cases_live(self, monkeypatch):
        monkeypatch.delenv("REEL_EVAL_CASES", raising=False)
        with pytest.raises(FileNotFoundError, match="REEL_EVAL_CASES"):
            load_cases()

    def test_duplicate_ids_are_refused(self, tmp_path, monkeypatch):
        f = tmp_path / "cases.yaml"
        f.write_text(
            "- id: a\n  utterance: u\n  expect_slots: [notes]\n"
            "- id: a\n  utterance: v\n  expect_slots: [cohort]\n"
        )
        with pytest.raises(ValueError, match="duplicate case ids"):
            load_cases(f)

    def test_a_case_set_round_trips(self, tmp_path):
        f = tmp_path / "cases.yaml"
        f.write_text(
            "- id: d1\n  utterance: head injuries?\n  expect_slots: [history_of_rhi]\n"
            "- id: d2\n  utterance: toxicology?\n  expect_none: true\n  note: not modelled yet\n"
        )
        cases = load_cases(f)
        assert [c.id for c in cases] == ["d1", "d2"]
        assert cases[1].expect_none and cases[1].note


def test_slots_in_schema_spans_every_entity_type():
    assert slots_in_schema(CAPS) >= {"history_of_rhi", "storage_condition"}


class TestSlotNamesThatAreAlsoEnglishWords:
    """`donor`, `name`, `notes` are slot names AND ordinary words.

    Crediting the bare word turned the toxicology negative case into a false
    failure on the first live run: the answer said "the donor's free-text
    notes" — prose, not field references — and scored as naming two slots.
    """

    def test_a_bare_common_word_is_not_credited(self):
        case = DiscoveryCase(id="c", utterance="toxicology?", expect_none=True)
        turn = answered("Nothing models toxicology; the donor has free-text notes.")
        assert grade_turn(case, turn, CAPS).passed

    def test_the_same_word_as_a_field_reference_is_credited(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"notes"}))
        assert grade_turn(case, answered("Search `notes` for it."), CAPS).passed
        assert grade_turn(case, answered("Search **notes** for it."), CAPS).passed

    def test_a_compound_name_is_credited_bare(self):
        # `history_of_rhi` in prose can only mean the field, so requiring
        # backticks there would lose real hits.
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"history_of_rhi"}))
        assert grade_turn(case, answered("history_of_rhi records it."), CAPS).passed

    def test_a_common_word_still_counts_when_the_spec_filters_on_it(self):
        # The spec is unambiguous regardless of how the prose reads.
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"notes"}))
        turn = proposal({"criteria": [{"kind": "field", "slot": "notes"}]}, "searching the notes")
        assert grade_turn(case, turn, CAPS).passed


class TestTheSpokenFormOfAFieldName:
    """"storage condition" communicates the data element as well as
    `storage_condition` does, and the goal is that the user learns which element
    to include — not that the answer quotes an identifier. Scoring only the
    underscored spelling marked a correct, readable answer wrong on the first
    live run."""

    def test_the_spoken_form_is_credited(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"history_of_rhi"}))
        assert grade_turn(case, answered("We record history of rhi for each donor."), CAPS).passed

    def test_case_is_ignored(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"cause_of_death"}))
        assert grade_turn(case, answered("Cause Of Death is free text."), CAPS).passed

    def test_a_plural_still_contains_the_singular(self):
        case = DiscoveryCase(id="c", utterance="u", expect_slots=frozenset({"cause_of_death"}))
        assert grade_turn(case, answered("the cause_of_death values vary"), CAPS).passed

    def test_common_word_slots_are_unaffected_by_the_spoken_form(self):
        # `notes` has no underscore, so it stays in the strict bucket: a bare
        # mention is prose, not a field reference.
        case = DiscoveryCase(id="c", utterance="toxicology?", expect_none=True)
        assert grade_turn(case, answered("check the donor notes"), CAPS).passed
