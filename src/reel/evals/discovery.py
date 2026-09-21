"""Grading a discovery turn on the slots it named.

A case is deliberately thin. Everything it asserts is derivable from the goal
statement, and nothing else is asserted at all:

    expect_slots    every one of these must be named. A SUBSET check, not
                    equality -- offering `cause_of_death` alongside
                    `history_of_rhi` is a better answer, not a failure, and an
                    equality check would train the prompt to be stingy.

    forbid_slots    none of these may be named. For a question whose obvious
                    lexical match is the wrong field.

    expect_none     the schema holds nothing on this topic, so the turn must
                    name no slot and say so. The negative case matters more
                    than it looks: a planner that always finds *something*
                    reads as confident and is occasionally wrong, and only a
                    case like this catches it. A topic absent today becomes an
                    ordinary positive case the day it is modelled -- the case
                    file follows the schema.

Cases live with the schema they describe, not here. A case set is domain-bearing
-- it belongs to the deployment being described -- so Reel reads one by path
through ``REEL_EVAL_CASES`` rather than vendoring a copy (Phase A6).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .. import EVAL_CASES_ENV


@dataclass(frozen=True)
class DiscoveryCase:
    id: str
    utterance: str
    expect_slots: frozenset[str] = field(default_factory=frozenset)
    forbid_slots: frozenset[str] = field(default_factory=frozenset)
    expect_none: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if self.expect_none and self.expect_slots:
            raise ValueError(
                f"{self.id}: expect_none and expect_slots contradict each other — "
                f"a turn cannot both name these slots and name none"
            )
        if not self.expect_none and not self.expect_slots:
            raise ValueError(
                f"{self.id}: asserts nothing. Give it expect_slots, or expect_none "
                f"if the schema genuinely holds nothing on this topic"
            )


@dataclass(frozen=True)
class DiscoveryOutcome:
    case_id: str
    passed: bool
    named: frozenset[str]
    missing: frozenset[str]
    forbidden: frozenset[str]
    status: str
    detail: str = ""


def slots_in_schema(capabilities: dict) -> frozenset[str]:
    """Every slot name the deployment exposes, across all entity types."""
    return frozenset(
        f["name"] for caps in capabilities.values() for f in caps.get("fields", [])
    )


def _slots_in_spec(spec: object) -> set[str]:
    """Slot names a QuerySpec filters on, including inside related criteria."""
    found: set[str] = set()
    if not isinstance(spec, dict):
        return found
    for crit in spec.get("criteria") or ():
        if not isinstance(crit, dict):
            continue
        if isinstance(crit.get("slot"), str):
            found.add(crit["slot"])
        if isinstance(crit.get("edge"), str):
            found.add(crit["edge"])
        for sub in crit.get("criteria") or ():
            if isinstance(sub, dict) and isinstance(sub.get("slot"), str):
                found.add(sub["slot"])
    for s in spec.get("sort") or ():
        if isinstance(s, dict) and isinstance(s.get("slot"), str):
            found.add(s["slot"])
    return found


#: Slot names that are also ordinary English words are only credited from prose
#: when written as a field reference. Scoring the bare word would credit
#: "collected from the donor" as naming the `donor` slot, and "what is its
#: name?" as naming `name` -- which turned a negative case into a false failure
#: on the first live run.
_FIELD_REFERENCE = ("`{}`", "**{}**", "'{}'", '"{}"')


def _looks_distinctive(name: str) -> bool:
    """Whether a bare mention of this name can only mean the field.

    `history_of_rhi` in prose is unambiguous. `donor` is not. The dividing line
    is whether the schema author wrote a compound identifier: an underscore is
    a good proxy, and it costs nothing to be wrong in the safe direction --
    a distinctive name missed in prose is still credited from the spec.
    """
    return "_" in name


def _slots_in_message(message: str, known: frozenset[str]) -> set[str]:
    """Slot names the prose mentions, as field references rather than as words.

    Matched against the schema's own slot list rather than by pattern, so a
    field name is only ever credited when it exists. Longest-first so that
    mentioning `cause_of_death` does not also credit a hypothetical `cause`.
    """
    text = (message or "").lower()
    found: set[str] = set()
    for name in sorted(known, key=len, reverse=True):
        spoken = name.replace("_", " ").lower()
        if _looks_distinctive(name):
            # Either spelling. "storage condition" communicates the data element
            # exactly as well as `storage_condition` does, and the goal is that
            # the user learns which element to include -- not that the answer
            # quotes an identifier. Scoring only the underscored form would mark
            # a correct answer wrong for being readable.
            if name.lower() in text or spoken in text:
                found.add(name)
        elif any(marker.format(name) in (message or "") for marker in _FIELD_REFERENCE):
            found.add(name)
    return found


def grade_turn(case: DiscoveryCase, turn: dict, capabilities: dict) -> DiscoveryOutcome:
    """Score one turn against one case.

    A turn names a slot either by filtering on it (a proposal) or by saying its
    name (an answered clarification). Both count: the goal is that the user
    learns which data elements to include, and a proposal that filters on the
    right field has communicated that at least as well as prose naming it.
    """
    known = slots_in_schema(capabilities)
    named = frozenset(
        _slots_in_spec(turn.get("query_spec")) | _slots_in_message(turn.get("message", ""), known)
    )
    status = str(turn.get("status", "?"))

    if case.expect_none:
        # Naming nothing is the whole assertion. An `error` turn also names
        # nothing, so it is excluded explicitly -- it would otherwise pass for
        # the wrong reason, which is the failure mode this case exists to catch.
        passed = not named and status in ("proposal", "clarification")
        detail = (
            f"named {sorted(named)} for a topic the schema does not model"
            if named
            else ("" if passed else f"status {status!r} — no answer was produced at all")
        )
        return DiscoveryOutcome(case.id, passed, named, frozenset(), named, status, detail)

    missing = case.expect_slots - named
    forbidden = case.forbid_slots & named
    passed = not missing and not forbidden
    bits = []
    if missing:
        bits.append(f"did not name {sorted(missing)}")
    if forbidden:
        bits.append(f"named forbidden {sorted(forbidden)}")
    return DiscoveryOutcome(case.id, passed, named, missing, forbidden, status, "; ".join(bits))


def load_cases(path: str | Path | None = None) -> list[DiscoveryCase]:
    """Read a case set.

    Resolution order: the argument, then ``REEL_EVAL_CASES``. There is no
    bundled default on purpose — a case set that shipped with Reel would be
    describing a schema Reel does not have.
    """
    import yaml

    resolved = str(path or os.environ.get(EVAL_CASES_ENV, "")).strip()
    if not resolved:
        raise FileNotFoundError(
            f"no discovery case set given — pass a path or set {EVAL_CASES_ENV}. "
            f"Cases live with the schema they describe, not in this repository."
        )
    raw = yaml.safe_load(Path(resolved).read_text()) or []
    cases = []
    for entry in raw:
        cases.append(
            DiscoveryCase(
                id=entry["id"],
                utterance=entry["utterance"],
                expect_slots=frozenset(entry.get("expect_slots", ())),
                forbid_slots=frozenset(entry.get("forbid_slots", ())),
                expect_none=bool(entry.get("expect_none", False)),
                note=entry.get("note", ""),
            )
        )
    ids = [c.id for c in cases]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate case ids in {resolved}: {sorted(dupes)}")
    return cases
