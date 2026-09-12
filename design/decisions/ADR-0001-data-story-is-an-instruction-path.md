# ADR-0001: A data story is an instruction path producing typed subgraph states + artifacts

- **Status:** Proposed
- **Date:** 2026-06-17 (migrated to Reel 2026-06-22)
- **Deciders:** labadorf, design session
- **Related:** Aperture ADR-0003 (config-as-LinkML-in-Mosaic), Aperture ADR-0009 (view-descriptions + headless validation), Aperture ADR-0010 (typed noun-catalog, keystone), Aperture ADR-0020 (conversations/actions are provenance events), Aperture ADR-0002 (generic, no domain nouns); ADR-0002 (as-of reproducibility), ADR-0005 (headless core); `instruction-path-model.md`; `prefab/data-stories.md`

> **Migrated from Aperture ADR-0022 (2026-06-22)** on the data-story-engine split
> (boundary decision `datahelix:platform/design/decisions/ADR-0003`, whose **Outcome** section
> records the execution).
> Renumbered 0022 → Reel 0001. References to the *portal's* decisions are qualified
> **"Aperture ADR-NNNN"**; bare `ADR-NNNN` refers to Reel's own ADRs.
> **Names updated 2026-09-11:** Hippo → **Mosaic** (Mosaic ADR-0004), BASS/drylims → **DataHelix**;
> data-contract identifiers (e.g. `hippoSchema`, `hippo_core`) deliberately keep their spelling.

## Context

The AI-native explorer (`vision.md`) and the keystone MVP (`prefab/data-stories.md`) both
center on a "data story." We surveyed five UI prototypes (conversational notebook, transcript +
live artifact, steerable portal, spatial exploration graph, document/briefing composer) and
found they are not five apps but **five renderers over one underlying object**. Building five
UIs against five ad-hoc state models would be wasteful and would foreclose the richer modes. We
need to name the object precisely, independent of any UI, so the model is built once and
rendered many ways — and so a simple linear UI can ship now without painting us into a corner.

`data-stories.md` already framed it as "a sequence of cohort-states + transforms, narrated," but
left the structure informal: what *is* a transform, what *is* a state, what is the unit of edit?

## Decision

**Reel models a data story as an *instruction path*: an ordered/linked set of first-class,
source-tagged `Instruction`s that deterministically produces a sequence of `State`s and the
`Artifact`s rendered from them**, per the reduction `state[n] = apply(instruction[n], state[n-1])`.

- **`Instruction`** — a first-class **source-tagged** event (`chat | ui_event | agent | replay`)
  that expands to one or more nested, sequential typed **ops** (think tool calls) drawn from the
  closed catalog (`filter · exists-related-filter · distinct-values · group-by+count ·
  pivot-grain · set-op · render-as-primitive`). A UI event is born as one op; a chat turn is raw
  intent elaborated by the LLM into ops and **dry-run-validated** (Aperture ADR-0009) before
  applying. The `Instruction` is the **unit of rewind**; its nested ops are inspectable but not
  independently addressable — to change a turn, edit the prompt and re-elaborate.
- **`State`** — a typed **subgraph specification** (intensional): the predicates/selections that
  *denote* a subgraph of `Entity`/`Relationship` instances per the LinkML schema. A "cohort" is a
  State viewed through a focal lens (focal type + selection); re-rooting/grain-pivot changes the
  lens. State is stored as the spec, **not** the materialized objects.
- **`Artifact`** — the materialization of work (an evaluated subgraph, or a rendered view
  primitive), immutable and provenance-stamped. Transform ops advance the State; render ops bind
  an Artifact to the current State without advancing it.
- **`DataStory`** — the persisted container (instructions + one as-of watermark + artifacts),
  itself a LinkML artifact stored in Mosaic (Aperture ADR-0003).

The full model lives in [`instruction-path-model.md`](../instruction-path-model.md).

## Consequences

- **One model, many renderers.** Each UI mode is a slice — `(admitted topology) × (admitted
  instruction sources) × (state projection) × (deliverable slice)`. The five prototypes become
  points in this space; we build the substrate once. The renderer is on the far side of the
  **View Contract** (`datahelix:platform/design/view-contract.md`): Reel emits contract instances,
  it does not paint pixels (ADR-0005).
- **The instruction path *is* the provenance log** (Aperture ADR-0020): chat turns, agent
  actions, and config revisions are already first-class provenance events; the path is that log
  made navigable. A saved story is a serializable, validatable, shareable LinkML artifact for
  free (Aperture ADR-0003) — and the "re-runnable declarative artifact" `vision.md` promises is
  literally "replay the path."
- **Obligations:** the op catalog must be closed and typed (couples to Aperture ADR-0010); every
  instruction must be dry-run-validatable before apply (Aperture ADR-0009); State must stay
  intensional (forces the reproducibility model — ADR-0002).
- **Deferred:** ops over *heterogeneous* entity types within one subgraph (multi-type op
  semantics) are hard and out of scope for v1; the v1 op catalog stays single-focal-type.

## Alternatives considered

- **A bespoke state model per UI prototype.** Five renderers, five models — wasteful, and each
  forecloses the others. Rejected: the prototypes share one object.
- **State = materialized subgraph (extensional).** Simpler to render, but stories balloon and
  lose replayability/reproducibility. Rejected in favor of intensional State + materialized
  Artifacts (ADR-0002).
- **Leave "transform"/"cohort-state" informal** (as in `data-stories.md`). Insufficient to build
  rewind, edit, validation, or topology on. Rejected: this ADR formalizes them.

## Notes / open sub-questions

- This whole chain sits behind the keystone **Aperture ADR-0010** probe ("can an LLM reliably
  drive a typed declarative artifact through a validator to a correct change?"). If rung 1 fails,
  this model is moot. Ratify after the probe.
- Multi-type op semantics (§2 of the model doc) remain an open design problem.

### Status update (2026-09-11) — the probe has run

- **The keystone probe is no longer hypothetical.** It has been running since 2026-08 as **Exon**
  (`BU-Neuromics/mosaic-demo-small`, `exon/`): an LLM emits a typed query artifact, a validator
  checks it against the live schema and capability manifest before anything executes, and a
  harness measures pass rates over repeated samples. Result: the NL → typed artifact → validator
  → execute loop **works structurally** with hosted models (forced tool calls comply; plans are
  well-shaped; holdout pass rate rose from 0.50 to 0.67 after one context-tuning iteration on
  Sonnet 5). The open reliability gap is **faithfulness** — a structurally valid artifact that
  paraphrases an enum value (`"brain tissue"` for `tissue`) or silently degrades a counting
  question into a row listing — which a validator **cannot** catch by design. Grounding the
  model in each field's actual value vocabulary (Mosaic's server-derived capability manifest now
  carries `enum_values`) is the identified lever. See `../../proposals/exon-migration.md`.
- **The keystone moved to Reel with the split** (Aperture `design/INDEX.md` records it as
  "relocated to Reel"; DataHelix `roadmap-1.0.md` P3.5). Aperture ADR-0010 (the view
  noun-catalog) is still `Proposed` but is no longer on this ADR's critical path: view primitives
  sit on the far side of the View Contract, and the probe exercised the *query* half of the loop
  without them.
- **`State` has a concrete v1 form.** Aperture ADR-0035 (Accepted 2026-08-19) defines the
  **QuerySpec** as "an intensional subgraph state restricted to a single focal lens — the
  cohort/query-state foundation Reel's stories build on," and Mosaic ADR-0009 (Accepted
  2026-09-01) makes it the artifact Mosaic's MCP boundary validates and executes. Reel
  [ADR-0006](./ADR-0006-v1-state-is-the-queryspec.md) records the Reel side.
- **Op catalog coverage in the prototype:** `filter` and `exists-related-filter` (as QuerySpec
  `FieldCondition` / `RelatedCondition`). `distinct-values`, `group-by+count` now have server
  tools to bind to (Mosaic `facet_query_spec` / `count_query_spec`, mosaic#195); `pivot-grain`
  and `set-op` remain unbuilt. Multi-type ops (the named open problem) are untouched.
- **Ratification recommendation:** the model held up under the probe; the remaining sub-question
  is multi-type op semantics, which was already deferred. Ratify alongside ADR-0003/0004.
