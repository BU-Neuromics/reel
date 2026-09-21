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

## 0. Current state (verified 2026-09-11; Reel/Exon rows refreshed 2026-09-21)

| Where | State |
|---|---|
| **Reel** (this repo) | Design only. ADR-0001–0005 migrated from Aperture; ADR-0006–0008 added 2026-09-11. No `src/`, no `pyproject.toml`, no CI. Phase B now split into B-runtime / B-harness (see Phase B). |
| **Exon** — `mosaic-demo-small/exon/` | `planner.py` (legacy `QueryPlan` emitter) **and** `spec_planner.py` (`QuerySpec` emitter, added 2026-09-07 as Phase 2 step 1 of `add-mosaic-mcp-boundary`, grounded in `mosaic://capabilities`); `validator.py`/`executor.py`/`ops.py` (QueryPlan path — scheduled for retirement, Phase 2.4); `harness/` (probe, runner, grading, refine, loop, report/compare; 77 tests, no model calls); `context/` (seed context + template). **HTTP turn endpoint EXISTS** (`conversational_server.py`) and was exercised end to end through Mosaic's relay on 2026-09-21 — Aperture chat panel → `converseQuerySpec` → Exon → proposal → executed, in a real browser. Supersedes the 2026-09-11 note that said otherwise. Also added since: `add-schema-discovery-for-query-building` — slot descriptions in the grounding, discovery answered as a clarification carrying `resolution: "answered"`, and the edit-cascade scoped to blocking clarifications. All three are in the B-runtime carry-set. |
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

> **AMENDED 2026-09-21.** Phase B is now two phases (see Phase B). These
> preconditions gate them differently:
>
> | | B-runtime | B-harness |
> |---|---|---|
> | **P1** (Exon Phase 2 / task 2.5) | not required — the runtime imports nothing from the retired path | **required** — `grading.py` resolves slots through `validator.py` |
> | **P2** (turn endpoint proven) | required — **met** | required — met |
> | **P3** (ADR-0006/7/8 + Mosaic ADR-0010 ratified) | **MET 2026-09-21** | met |
> | **P4** (ADR-0001–0004 ratified, or explicit decision) | explicit decision available | same |
> | **P5** (landing site / Phase A) | required — A4/A5/A6 outstanding | required |
>
> **P3 was the one live blocker for B-runtime; it is met as of 2026-09-21.**
> Mosaic ADR-0010 was ratified first (its own precondition — ADR-0007 must not
> lead it), then 0006/0007/0008 here. B-runtime is unblocked. P4's escape clause
> is not needed: 0001–0004 remain Proposed, and B-runtime proceeds on that basis
> as P4 expressly allows.

- [ ] **P1 — Exon Phase 2 complete** in `mosaic-demo-small` (`add-mosaic-mcp-boundary` tasks
      2.3–2.7): the `QueryPlan` path retired, the harness grading on result equivalence with the
      three stale `expect_rejection` cases re-baselined (q32/q33/q34), and the silent-degradation
      class (2.5c) and empty-related-criteria class (2.5d) graded. *Rationale:* migrating an
      in-flight refactor across repos mid-stream loses the before/after the harness exists to
      provide.
      **Scope narrowed 2026-09-21:** this gates **B-harness only**. The turn-path runtime
      imports nothing from the retired QueryPlan modules, so nothing about carrying it is
      "mid-stream" — see the Phase B amendment for the import graph.
- [x] **P2 — The conversational turn endpoint exists and is exercised by Mosaic's relay**
      (`add-exon-conversational-contract` tasks 2.2–2.7 + at least one live
      Aperture-or-MCP-client → `converse_query_spec` → Exon round trip). *Rationale:* the wire
      contract must be proven in place before its ownership transfers.
      **MET 2026-09-21.** Aperture's chat panel, in a browser, against a live
      `mosaic serve --graphql --mcp` with `MOSAIC_EXON_URL` set: a discovery turn named
      `history_of_rhi`, the follow-up proposed `history_of_rhi eq true`, Mosaic re-validated it
      (`{"valid": true, "errors": []}`) and executing it returned 50 donors — the number
      `evals/expected-results.json` has carried for q05 since August. Driven additionally through
      Aperture's own client functions (`deriveConversationModel` → `buildConverseMutation` →
      `normalizeConverseResult`), so the introspection-gated path is proven, not just the transport.
- [x] **P3 — ADR-0006/0007/0008 ratified** (status flips in `design/INDEX.md`), and Mosaic
      ADR-0010 ratified (ADR-0007 should not lead it). **MET 2026-09-21**, in that order: Mosaic
      ADR-0010 first (`ef49522`), then 0006/0007/0008 here. ADR-0010's own gate — its terms
      awaiting a design session — was released deliberately rather than satisfied; no session was
      held, and its Notes say so. Cost amplification is accepted, not mitigated (E4 still
      deferred).
- [ ] **P4 — ADR-0001–0004 ratified** on the strength of the probe (they were gated on it), or an
      explicit decision to migrate with them still `Proposed`.
- [x] **P5 — Landing site ready** (Phase A below complete). **MET 2026-09-21** — A4/A5/A6 landed.

## 3. Migration phases

### Phase A — Prepare the landing site (in Reel; **this is the current phase**)

- [x] A1. Bring the design set up to date with the platform (this pass, 2026-09-11): names
      (DataHelix, Mosaic), cross-references (platform ADR-0003; Mosaic ADR-0001), dated status
      notes on ADR-0001–0005, `design/platform-alignment.md`.
- [x] A2. Record the Reel-side decisions the migration rests on: ADR-0006, ADR-0007, ADR-0008.
- [x] A3. This runbook; `.gitignore`; README/CLAUDE.md describing the intended code layout.
- [x] A4. `pyproject.toml` skeleton for `datahelix-reel` (name, `src/` layout, `litellm` +
      `mcp` client deps, `reel[harness]` extra) — **only when the migration is scheduled**, so an
      empty package is never published.
- [x] A5. `.github/workflows/tests.yml` mirroring Exon's test invocation (`pytest tests/`, no
      model calls) — with A4.
- [x] A6. Register the intended fixture seam: how `reel.harness` locates a case set
      (`REEL_EVAL_CASES=<path>`), so the demo repo's `evals/` can be pointed at without copying.

### Phase B — Build the Reel seed from Exon's carry-set

> **AMENDED 2026-09-21: Phase B splits into B-runtime and B-harness.**
> Authority: `mosaic-demo-small` OpenSpec change `extract-exon-runtime-to-reel`.
>
> **Why.** P1's rationale is *"migrating an in-flight refactor across repos
> mid-stream loses the before/after the harness exists to provide."* That is a
> claim about the harness, and it is correct about the harness. Phase B being one
> atomic step is what extends it to the runtime as well.
>
> The two halves are already separable in the source. The turn-path runtime
> imports **nothing** from the retired QueryPlan path — its only tie to
> `planner.py` is five configuration constants:
>
> | Module | Sibling imports |
> |---|---|
> | `spec_planner.py` | `planner` (`MAX_ATTEMPTS`, `MAX_TOKENS`, `MODEL`, `REQUEST_TIMEOUT`, `decode_kwargs_for`) |
> | `conversational_planner.py` | `planner` (same constants), `spec_planner` |
> | `conversational_orchestrator.py` | `conversational_planner`, `planner` (constants) |
> | `conversational_server.py` | `conversational_orchestrator` |
> | `query_router.py` | `planner` (constants), `spec_planner` |
> | `mosaic_mcp.py`, `schema.py` | none |
>
> `harness/grading.py` is the **sole** module coupled to the retired path, via
> `validator.resolve_field` — the same dependency task 2.4 already names as
> blocking its own deletion. That dependency is what times the harness's move,
> and nothing else times the runtime's.
>
> The runtime is also fixture-free: the only `evals/` references in those modules
> are docstrings describing what the MCP capability manifest replaced.
>
> **Consequence.** B-runtime proceeds without P1. B-harness still waits for task
> 2.5, so every rationale P1 states is honoured. Between the two, Reel ships a
> runtime whose grading lives in the demo repo — accepted deliberately, and
> bounded by ADR-0008's guarantee that the wire shape does not change.

#### Phase B-runtime — carry the turn path (does NOT require P1)

```
# 1. Carry the planner + grounding.
exon/spec_planner.py                  -> src/reel/planner/spec_planner.py
exon/schema.py                        -> src/reel/planner/capabilities.py   # manifest loader
exon/mosaic_mcp.py                    -> src/reel/planner/boundary.py       # MCP client to Mosaic
exon/context/{seed,template}.py       -> src/reel/planner/context/
# 2. Carry the turn function + HTTP endpoint (both exist as of P2).
exon/conversational_planner.py        -> src/reel/story/turn.py             # one stateless turn
exon/conversational_orchestrator.py   -> src/reel/story/conversation.py     # turn-list bookkeeping
exon/conversational_server.py         -> src/reel/serve/http.py             # the relay-facing endpoint
# 3. NEW, not a copy: the five constants currently imported from planner.py.
#    Carrying planner.py to satisfy them would drag the retired QueryPlan
#    emitter into Reel and undo the split.
(new)                                 -> src/reel/config.py
# 4. Carry the runtime's own unit tests.
tests/test_spec_planner.py, test_conversational_planner.py,
tests/test_conversational_orchestrator.py, test_conversational_server.py -> tests/
# 5. Undecided, mechanically clean either way: exon/query_router.py (the
#    single-shot product surface). Settle at execution.
# 6. Carry the spec deltas as Reel's first OpenSpec specs (renamed exon-* -> reel-*):
openspec/changes/add-exon-conversational-contract/specs/exon-conversational-planner/spec.md
                                      -> openspec/specs/reel-conversational-planner/spec.md
# 7. Rename EXON_* -> REEL_*; update docstrings that name Exon; keep the wire
#    shape byte-for-byte.
```

#### Phase B-harness — carry the reliability suite (REQUIRES P1 / task 2.5)

```
exon/harness/*                        -> src/reel/harness/*
tests/test_grading.py, test_harness_invariants.py,
tests/test_independence.py, test_runner_fake.py                          -> tests/
# Blocked until task 2.5 re-bases grading onto the QuerySpec shape: grading.py
# imports validator.resolve_field, so it would arrive unable to grade anything.
# A6's REEL_EVAL_CASES seam is what lets it read the demo repo's evals/ without
# copying them.
```

```
# NEVER carried, in either phase:
#   exon/ops.py, validator.py, executor.py, planner.py  (QueryPlan path — task 2.4
#     deletes them in place)
#   schemas/, generate.py, hints.yaml, evals/           (domain-bearing fixtures —
#     stay in the demo repo permanently)
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
| Anchor pivots over a reverse edge ("the donors of those samples") are inexpressible — `RelatedCondition.edge` is forward-only | [mosaic#204](https://github.com/BU-Neuromics/mosaic/issues/204) (blocks `add-aperture-chat-panel` Phase 2 in the demo repo) | Mosaic-side: `inverse:` slots as virtual fields; Reel's `pivot-grain` op waits on it (ADR-0006) |
| Endpoint unauthenticated; no per-turn cost accounting | Mosaic ADR-0010 follow-ups E1–E3 | Reel's once it hosts the planner (ADR-0007 §5) |

## 5. Explicitly out of scope for the migration

- Any change to `mosaic-demo-small` before Phase C (it is the running prototype and a sibling
  repo's property).
- Tree/DAG topology, set-ops, multi-type ops (ADR-0003; `instruction-path-model.md` §11).
- The View Contract grammar (platform-owned) and `render-as-primitive` (waits on it).
- A Reel-hosted validator or executor (forbidden by ADR-0007).
