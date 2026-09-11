# Migrating Exon into Reel — readiness runbook

**Status:** 🟡 Preparation (2026-09-11). **Not executing yet.** This runbook prepares Reel as the
landing site for the **Exon** prototype (`BU-Neuromics/mosaic-demo-small`, `exon/`) and states
the preconditions under which the migration starts. It is authorized by
[ADR-0008](../design/decisions/ADR-0008-exon-seeds-reel.md) (`Proposed`) and follows the pattern
of the DataHelix `proposals/hippo-split.md` / `proposals/aperture-split.md` runbooks. Nothing in
`mosaic-demo-small` is modified by this preparation.

> **What Exon is, in one paragraph.** A schema-grounded natural-language → `QuerySpec` planner
> for a Mosaic instance, plus a reliability harness that measures it. An LLM emits a typed
> `QuerySpec` grounded in Mosaic's server-derived capability manifest; Mosaic's MCP boundary
> validates it (`validate_query_spec`) before anything executes; a harness runs each benchmark
> question *k* times, grades **faithfulness** as well as validity, and tunes the model's context
> in a measure → refine → re-measure loop. A conversational **turn contract** (one stateless
> function: `(query_spec | null, prior turns, utterance, edit_turn_id?) → turn`) was specified in
> Reel's vocabulary so that Mosaic's `converse_query_spec` relay (Mosaic ADR-0010) can drive it
> and Aperture's chat UI can consume it. It is Reel rung 1, running under another name.

## 0. Current state (verified 2026-09-11 against the five repos)

| Where | State |
|---|---|
| **Reel** (this repo) | Design only. ADR-0001–0005 migrated from Aperture; ADR-0006–0008 added today. No `src/`, no `pyproject.toml`, no CI. |
| **Exon** — `mosaic-demo-small/exon/` | `planner.py` (legacy `QueryPlan` emitter) **and** `spec_planner.py` (`QuerySpec` emitter, added 2026-09-07 as Phase 2 step 1 of `add-mosaic-mcp-boundary`, grounded in `mosaic://capabilities`); `validator.py`/`executor.py`/`ops.py` (QueryPlan path — scheduled for retirement, Phase 2.4); `harness/` (probe, runner, grading, refine, loop, report/compare; 77 tests, no model calls); `context/` (seed context + template). **No HTTP turn endpoint yet** — `add-exon-conversational-contract` tasks 2.2–2.9 are unchecked. |
| **Exon Phase 2** (`add-mosaic-mcp-boundary/tasks.md`) | 2.1 ✅ boundary verified live; 2.2 ✅ QuerySpec emitter alongside; 2.3–2.7 ☐ (switch to MCP client calls; retire local validator/executor; re-baseline harness on **result equivalence**; docs; spec sync). Task 2.5b was blocked on mosaic#195 (aggregation tools) — those tools (`count_query_spec`, `facet_query_spec`, `field_range_query_spec`, `search_query_spec`) **are now registered** in `mosaic/mcp/server.py`. |
| **Mosaic** (`v0.13.0` + unreleased) | ADR-0009 Accepted; MCP boundary live with schema/capabilities resources, validate/execute/count/facet/range/search tools, `construct-query-spec` prompt; ADR-0010 Proposed and implemented (`converse_query_spec`, registered only when `MOSAIC_EXON_URL` is set; re-validates every turn; strict envelope; `error` turns). Graph-level `asOf` (ADR-0001, Accepted) partly built — not combinable with relationship predicates. |
| **Aperture** | ADR-0035 QuerySpec Accepted (client-side `validateQuerySpec()` in `web/src/query/querySpec.ts`; URL-carried `qs` state); no chat UI yet (Phase 3 of the Exon contract, informational). |
| **DataHelix** | Platform ADR-0003 executed; Reel **not mounted** as a submodule; no `reel` entry in `mkdocs.yml`; `decision-tracker` skill lists Reel as "(not mounted)". `roadmap-1.0.md` places data stories post-1.0 with the MCP surface + keystone probe (P3.5) as the 1.0 beachhead. |

## 1. Decisions (locked by ADRs; confirm at execution)

1. **Migrate, don't rewrite** — ADR-0008.
2. **v1 `State` = `QuerySpec`; Reel owns no query noun** — ADR-0006.
3. **Reel plans; Mosaic validates and executes; Reel is behind Mosaic's validating relay** — ADR-0007.
4. **The turn contract's wire shape does not change at migration**; ownership of the contract
   moves from `mosaic-demo-small` to Reel (Mosaic ADR-0010 term 7 transfers) — ADR-0008 §3.
5. **Packaging:** `datahelix-reel` distribution, `import reel`, `src/reel/` (platform ADR-0002
   Layout A). Env vars `REEL_*` (from `EXON_*`); provider via `litellm`, chosen by config.
6. **Generic source, domain-bearing fixtures stay out** (Aperture ADR-0002 rule, inherited): the
   demo schema, generated data, eval cases and expected results remain in `mosaic-demo-small`
   (or a successor fixture repo) and are *pointed at*, not copied into `src/reel/`.

### 1.1 Open sub-decisions (low stakes; settle at execution)

- Code-history preservation: `git subtree` merge vs. copy-with-attribution (hippo/aperture used
  copy + pointer).
- Whether the harness's *refine loop* ships in `datahelix-reel` or as a dev-only extra
  (`reel[harness]`).
- Whether to add `source` and `ops` to the wire `Turn` before or after migration (additive either
  way — ADR-0008 deltas D4/D5).

## 2. Preconditions (all must hold before Phase B starts)

- [ ] **P1 — Exon Phase 2 complete** in `mosaic-demo-small` (`add-mosaic-mcp-boundary` tasks
      2.3–2.7): the `QueryPlan` path retired, the harness grading on result equivalence with the
      three stale `expect_rejection` cases re-baselined (q32/q33/q34), and the silent-degradation
      class (2.5c) and empty-related-criteria class (2.5d) graded. *Rationale:* migrating an
      in-flight refactor across repos mid-stream loses the before/after the harness exists to
      provide.
- [ ] **P2 — The conversational turn endpoint exists and is exercised by Mosaic's relay**
      (`add-exon-conversational-contract` tasks 2.2–2.7 + at least one live
      Aperture-or-MCP-client → `converse_query_spec` → Exon round trip). *Rationale:* the wire
      contract must be proven in place before its ownership transfers.
- [ ] **P3 — ADR-0006/0007/0008 ratified** (status flips in `design/INDEX.md`), and Mosaic
      ADR-0010 ratified (ADR-0007 should not lead it).
- [ ] **P4 — ADR-0001–0004 ratified** on the strength of the probe (they were gated on it), or an
      explicit decision to migrate with them still `Proposed`.
- [ ] **P5 — Landing site ready** (Phase A below complete).

## 3. Migration phases

### Phase A — Prepare the landing site (in Reel; **this is the current phase**)

- [x] A1. Bring the design set up to date with the platform (this pass, 2026-09-11): names
      (DataHelix, Mosaic), cross-references (platform ADR-0003; Mosaic ADR-0001), dated status
      notes on ADR-0001–0005, `design/platform-alignment.md`.
- [x] A2. Record the Reel-side decisions the migration rests on: ADR-0006, ADR-0007, ADR-0008.
- [x] A3. This runbook; `.gitignore`; README/CLAUDE.md describing the intended code layout.
- [ ] A4. `pyproject.toml` skeleton for `datahelix-reel` (name, `src/` layout, `litellm` +
      `mcp` client deps, `reel[harness]` extra) — **only when the migration is scheduled**, so an
      empty package is never published.
- [ ] A5. `.github/workflows/tests.yml` mirroring Exon's test invocation (`pytest tests/`, no
      model calls) — with A4.
- [ ] A6. Register the intended fixture seam: how `reel.harness` locates a case set
      (`REEL_EVAL_CASES=<path>`), so the demo repo's `evals/` can be pointed at without copying.

### Phase B — Build the Reel seed from Exon's carry-set

```
# In a scratch checkout of mosaic-demo-small at the Phase-2-complete commit:
# 1. Carry the planner + grounding.
exon/spec_planner.py            -> src/reel/planner/spec_planner.py
exon/schema.py                  -> src/reel/planner/capabilities.py   # manifest loader (MCP resource)
exon/context/{seed,template}.py -> src/reel/planner/context/
# 2. Carry the turn function + HTTP endpoint (built under P2).
exon/<turn module>              -> src/reel/story/turn.py             # (existing QuerySpec|null, turns, utterance, edit_turn_id) -> turn
exon/<http module>              -> src/reel/serve/http.py             # the relay-facing endpoint
# 3. Carry the harness as Reel's reliability suite.
exon/harness/*                  -> src/reel/harness/*
tests/test_grading.py, test_harness_invariants.py, test_independence.py,
tests/test_runner_fake.py, test_spec_planner.py -> tests/
# 4. Do NOT carry: exon/ops.py, validator.py, executor.py, planner.py (QueryPlan path — retired);
#    schemas/, generate.py, hints.yaml, evals/ (domain-bearing fixtures — stay in the demo repo).
# 5. Carry the spec deltas as Reel's first OpenSpec specs (renamed exon-* -> reel-*):
openspec/changes/add-exon-conversational-contract/specs/exon-conversational-planner/spec.md
                                -> openspec/specs/reel-conversational-planner/spec.md
# 6. Rename EXON_* -> REEL_*; update docstrings that name Exon; keep the wire shape byte-for-byte.
```

Then apply the **translation layer** (ADR-0008 §3) in the order that keeps the relay green:

| Delta | Change | Why it is safe |
|---|---|---|
| **D1** | Persist a `DataStory` with `instructions[].parents: [state_id]` (validator enforces ≤1); project it to the wire `turns` list. | Wire unchanged; storage general per ADR-0003. |
| **D2** | Add `as_of_watermark` per story-version; compute `node_hash = hash(op, parent-hashes, watermark)`; "pull new data" = recorded watermark-advance. Gate: refuse to pin a watermark on a path containing a `RelatedCondition` until Mosaic's temporal join lands. | Additive; opaque `id` on the wire stays. |
| **D3** | Append-only edit-history event on every `edit_turn_id` recompute. | Internal; wire `suspended_turn_ids` unchanged. |
| **D4** | `Instruction.source` (`chat` today; `ui_event`, `agent`, `replay` later). | Additive wire field if exposed. |
| **D5** | Expose the derived `ops` expansion on a turn for inspection ("why did it return that?"). | Additive wire field. |

### Phase C — Cut the relay over and retire the Exon name

- C1. Publish `datahelix-reel` (first tag), CI green.
- C2. Mosaic: rename `MOSAIC_EXON_URL`/`MOSAIC_EXON_TIMEOUT` → `MOSAIC_REEL_URL`/`_TIMEOUT` with
      the old names as deprecated aliases (an amendment to Mosaic ADR-0010, Mosaic's to make);
      update `docs/configuration.md` and `mcp/server.py` docstrings that say "Exon".
- C3. `mosaic-demo-small`: replace `exon/` with a pointer to Reel and a `requirements.txt`
      pin; keep `schemas/`, `generate.py`, `evals/` as the fixture set; its OpenSpec
      `exon-*` specs archived with forward pointers. (Owner: that repo — not done from Reel.)
- C4. Aperture: no change required (calls Mosaic only). Cross-reference ADR-0035 ↔ Reel ADR-0006
      remains valid.

### Phase D — Mount Reel in DataHelix

- D1. `git submodule add https://github.com/BU-Neuromics/reel.git reel` in `datahelix`;
      `mkdocs.yml` nav entry; `README.md` components table row; `decision-tracker` skill table
      "(not mounted)" → `reel/`. (Owner: `datahelix`; platform ADR-0003 Notes already names this
      as follow-on work.)
- D2. Add Reel to the certified-frontier ledger (platform ADR-0001) once it has a release and a
      Mosaic pair to certify against.

## 4. What Reel gains and what it inherits

**Gains:** a planner with live results; a harness with saved baselines
(`evals/baselines/2026-08-18-*`); a wire contract already implemented by Mosaic's relay; 77 tests
that need no model.

**Inherits (the measured backlog):**

| Gap | Evidence | Lever |
|---|---|---|
| Value-vocabulary paraphrase (`"brain tissue"` for `tissue`; `at-risk` for `at_risk`) | 12/29 `PLAN_UNFAITHFUL` on Haiku baseline | manifest `enum_values` are now in the grounding (`spec_planner.py`); measure again |
| Silent degradation of counting questions into row listings | q33 emitted a valid 300-row spec for "how many per cohort" | route to `count_query_spec` / `facet_query_spec` (ADR-0006 table) and grade routing explicitly |
| Empty `RelatedCondition.criteria` validates clean and matches everything | Phase 2 finding 2.5d | grade as failure; consider a planner-side guard |
| Determinism ceiling at `temperature=1` on some provider/model pairs | Sonnet 5 via Bedrock: 40 % | measured, not tunable — report it |
| No reproducibility promise | Exon Decision 6 | D2 above |
| Endpoint unauthenticated; no per-turn cost accounting | Mosaic ADR-0010 follow-ups E1–E3 | Reel's once it hosts the planner (ADR-0007 §5) |

## 5. Explicitly out of scope for the migration

- Any change to `mosaic-demo-small` before Phase C (it is the running prototype and a sibling
  repo's property).
- Tree/DAG topology, set-ops, multi-type ops (ADR-0003; `instruction-path-model.md` §11).
- The View Contract grammar (platform-owned) and `render-as-primitive` (waits on it).
- A Reel-hosted validator or executor (forbidden by ADR-0007).
