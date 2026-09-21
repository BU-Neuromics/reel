# ADR-0008: Exon seeds Reel's implementation — migrate the prototype, do not rewrite; its turn contract is the v1 wire form of `Instruction`

- **Status:** Accepted
- **Date:** 2026-09-11
- **Deciders:** labadorf, design session
- **Related:** ADR-0001–0004 (the model the prototype was deliberately written against), ADR-0006 (v1 State = QuerySpec), ADR-0007 (planner behind Mosaic's relay); `../../proposals/exon-migration.md` (the runbook this ADR authorizes); **`BU-Neuromics/mosaic-demo-small`** — `exon/`, `APERTURE_EXON_CONTRACT.md`, `openspec/changes/add-mosaic-mcp-boundary/` (Phase 2: migrate Exon onto the boundary), `openspec/changes/add-exon-conversational-contract/` (design.md Decision 1 "Exon hosts it now, shaped for Reel to inherit later"; Decision 8, the wire contract); **Mosaic ADR-0009/0010**; Aperture ADR-0035 ("Reel composes instances of it"); DataHelix platform ADR-0002 (`datahelix-<component>` dists, bare imports), platform ADR-0003 (the split), `proposals/hippo-split.md` / `proposals/aperture-split.md` (the migration pattern)

## Context

Reel has had no code since the split (platform ADR-0003, 2026-06-22). Meanwhile the platform
needed a conversational NL → `QuerySpec` capability for Aperture's chat MVP *before* Reel
existed, and built it as **Exon** in `BU-Neuromics/mosaic-demo-small`: a schema-grounded planner
(`spec_planner.py`) emitting `QuerySpec`s grounded in Mosaic's capability manifest; a
reliability **harness** (`exon/harness/`) that measures per-case pass rates over repeated
samples, grades *faithfulness* (not just validity), and runs a measure → refine → re-measure loop
over the model's context; and a **conversational turn contract** (design.md Decision 8) that
Mosaic's `converse_query_spec` relay already implements against.

That contract was written **in Reel's vocabulary on purpose**. Its design records: "Aperture's
accepted ADR-0035 states Reel's role almost verbatim … This MVP is a genuine subset of Reel's
stated job, requested before Reel has any code. **Resolution: Exon hosts this now, deliberately
shaped so Reel can inherit it later — not a permanent home, not built inside Reel** … so a future
migration is a translation, not a rewrite." Its turn maps 1:1 onto ADR-0001's `Instruction`
(`utterance` = `raw`; `status: proposal|clarification|suspended` ⊂ `valid|invalid|suspended`;
`query_spec` = the resulting `State`), its edit semantics are ADR-0004's recompute-with-suspend
(`edit_turn_id`, `suspended_turn_ids`), and its scoping is ADR-0003's v1 (linear, `filter` +
`exists-related-filter` only).

Exon is also the **keystone probe** Reel's INDEX said to "run first": it has been running since
2026-08 with measured results (ADR-0001 status update). It is, in every respect but its
repository, Reel rung 1.

The question: when Reel gets code, does it start fresh from the design (as Aperture did on its
split) or by migrating Exon?

## Decision

**Reel's implementation will be seeded by migrating Exon's planner, harness, and turn contract
into this repository — a translation onto Reel's persisted model, not a rewrite — when the
preconditions in `proposals/exon-migration.md` are met. Until then Exon stays where it is,
`mosaic-demo-small` is not modified from Reel, and Reel prepares the landing site.**

1. **What migrates (the carry-set):** the `QuerySpec` emitter and its grounding-context builder;
   the conversational turn function and its HTTP endpoint (once built there); the harness
   (probe, runner, grading, refine loop, report/compare) as Reel's reliability suite; the
   `add-exon-conversational-contract` spec deltas as Reel's first OpenSpec specs. The
   demo-specific eval cases, expected results, fingerprints and the demo schema **do not**
   migrate into Reel source — they are domain-bearing fixtures (Aperture ADR-0002's generic rule,
   inherited); Reel's harness must load cases from a deployment-supplied fixture set.
2. **What is retired rather than migrated:** `ops.py`/`validator.py`/`executor.py` (the
   `QueryPlan` path — already scheduled for retirement in Exon's Phase 2.4 per Mosaic ADR-0009;
   ADR-0007 forbids a Reel-hosted validator/executor).
3. **The turn contract becomes Reel's v1 wire form of `Instruction`, and Reel becomes its
   owner.** Mosaic ADR-0010 term 7 ("the wire contract is not Mosaic's to change … an amendment
   [in the planner's repo] first, then here") transfers to Reel on migration. The **shape does
   not change at migration** — Mosaic's relay keeps working — and the mapping to the persisted
   model is a translation layer:

   | Wire (Decision 8) | Persisted model (ADR-0001–0004) | Delta on migration |
   |---|---|---|
   | `turns: [Turn]` (ordered) | `DataStory.instructions`, each with `parents: [state_id]` (≤1) | D1: persist `parents` as a list |
   | `Turn.id` (opaque) | `Instruction.id`; `node_hash = hash(op, parent-hashes, watermark)` | D2 (with watermark) |
   | `Turn.utterance` | `Instruction.raw` (`source: chat`) | — |
   | `Turn.query_spec` | the `State` produced (ADR-0006) | — |
   | `Turn.status` | `Instruction.status`; `clarification` = no state advanced | — |
   | `edit_turn_id` + `suspended_turn_ids` | ADR-0004 recompute-with-suspend | D3: append-only edit-history event |
   | *(absent)* | `DataStory.as_of_watermark` (ADR-0002) | D2: one watermark per story-version |
   | *(absent)* | `Instruction.source: ui_event \| agent \| replay` | D4: non-chat sources |
   | *(absent)* | `Instruction.ops: [Op]` (inspectable expansion) | D5: expose the derived ops |

4. **Packaging follows platform ADR-0002:** distribution `datahelix-reel`, import name `reel`,
   source under `src/reel/`; the harness under `src/reel/harness/`; provider access via `litellm`
   with the model chosen by configuration (`REEL_MODEL` and that provider's own credential —
   Exon's `EXON_*` variables renamed, never vendor-branched).
5. **Exon's name is retired at migration**; the Mosaic-side `MOSAIC_EXON_URL` /
   `MOSAIC_EXON_TIMEOUT` names are Mosaic's to rename (an amendment to Mosaic ADR-0010) and
   may stay as aliases through a deprecation window, as the `hippo.*` names did (Mosaic ADR-0004).

## Consequences

- **Reel's first code is proven code.** The planner has live results against a real Mosaic; the
  harness has caught real bugs (provider parameter rejections, context-window truncation, the
  `is_null` boolean operand) that a fresh start would rediscover.
- **Reel inherits an honest baseline and its open gaps**: holdout pass rate 0.50–0.67 depending on
  model; three named failure classes (value-vocabulary paraphrase, silent degradation of counting
  questions into row queries, empty related-criteria that validate clean). These become Reel's
  first measured backlog, not surprises.
- **Reel inherits Exon's obligations:** Mosaic ADR-0010 items 1–7 (ADR-0007) and follow-ups
  E1–E3 (endpoint authentication, per-turn cost logging); Phase 2 of `add-mosaic-mcp-boundary`
  (retire the QueryPlan path, re-baseline the eval suite on result equivalence).
- **The conceptual model gains a concrete reference implementation**, which is what ADR-0001–0004
  have been waiting on to ratify.
- **The design-first repo pattern is kept**: the ADRs, INDEX Decision Log, and the runbook stay
  the source of truth; the migration lands as an ordinary PR sequence against them.

## Alternatives considered

- **Fresh start from the design (the Aperture-split pattern).** Aperture's split deliberately
  left an obsolete CLI behind; Exon is not obsolete — it is the probe the design asked for, built
  against the design. Rewriting it would re-learn its bugs and lose the harness's baselines.
  Rejected.
- **Leave the conversational engine in Exon permanently and have Reel wrap it.** Contradicts
  Exon's own recorded resolution ("not a permanent home") and Aperture ADR-0035 ("Reel composes
  instances of it"); leaves the component boundary of platform ADR-0003 unrealized. Rejected.
- **Migrate now, before Exon's Phase 2 and the turn endpoint exist.** Would move an in-flight
  refactor across repos mid-stream and break the one live relay integration (Mosaic
  `converse_query_spec` → Exon). Rejected: preconditions first (`proposals/exon-migration.md`).
- **Migrate `mosaic-demo-small` wholesale (schema, data generator, evals) as Reel's test bed.**
  Puts domain nouns and a specific demo in Reel source (Aperture ADR-0002 rule). Rejected; the
  demo stays a sibling fixture repo Reel's harness can point at.

## Notes / open sub-questions

- Whether the harness's refine loop (context tuning) is Reel's long-term concern or a development
  tool that lives beside Reel — decide during migration.
- The turn contract carries no `source` and no `ops`; whether to add them to the wire before or
  after migration (additive fields, so either order works) is a sequencing choice for the
  runbook.
- Code-history preservation (subtree merge vs. copy with attribution) — low stakes; the
  hippo/aperture splits used copy-with-pointer.

## Ratification

Ratified 2026-09-21. The carry-set is no longer hypothetical: Phase B is split into B-runtime and B-harness on the strength of the prototype's import graph, Phase A's landing site exists (`pyproject.toml`, CI, `src/reel/`), and preconditions P2 and P5 are met. The turn contract this ADR calls the v1 wire form of `Instruction` has been exercised by a real client.
