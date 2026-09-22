# ADR-0006: Reel's v1 `State` is the platform QuerySpec; Reel composes the query noun, it does not define one

- **Status:** Accepted
- **Date:** 2026-09-11
- **Deciders:** labadorf, design session (recommended resolution — records the Reel side of two Accepted cross-component decisions)
- **Related:** ADR-0001 (instruction-path model — `State` is an intensional subgraph spec), ADR-0003 (grain discipline; set-ops deferred), ADR-0007 (validation/execution delegated to Mosaic's boundary), ADR-0008 (Exon seeds Reel); **Aperture ADR-0041** (Proposed 2026-09-22 — builds `QuerySpec.columns`, the `explode` half of `pivot-grain`; see Notes), **Aperture ADR-0035** (Accepted 2026-08-19 — cross-class queries are a typed `QuerySpec` artifact; "Aperture owns the noun and its execution; Reel composes instances of it"), Aperture ADR-0004 (no middle scripting layer), Aperture ADR-0005 (one typed artifact for humans and LLMs); **Mosaic ADR-0006** (typed GraphQL filter contract), **Mosaic ADR-0007** (aggregation & ordering surface), **Mosaic ADR-0009** (MCP boundary accepts `QuerySpec` as its canonical typed query artifact); `../instruction-path-model.md` §2, §8; `../prefab/data-stories.md` interface #1–#2

## Context

ADR-0001 defines a Reel `State` abstractly: a typed, intensional **subgraph specification** — the
predicates and selections that denote a subgraph of `Entity`/`Relationship` instances under the
deployment's LinkML schema — with a "cohort" being a State viewed through a focal lens. When
that ADR was written no such artifact existed anywhere on the platform, and
`prefab/data-stories.md` listed "a serializable selection/cohort object" and "a query capability
over Mosaic supporting relationship-existence filters and group-by+count" as interfaces Reel would
need someone to build.

Since then the platform built it, in two Accepted decisions that cite Reel by name:

- **Aperture ADR-0035** made the **`QuerySpec`** — `{v, anchor, mode, criteria, columns, sort,
  asOf}` with `FieldCondition`, quantified `RelatedCondition`, and depth-capped `CriteriaGroup`s —
  Aperture's typed, serializable, introspection-validated query artifact, and defined it *in
  ADR-0001's terms*: "an intensional subgraph state restricted to a single focal lens — the
  cohort/query-state foundation Reel's stories build on." It draws the seam explicitly: "One
  query state here, stories there."
- **Mosaic ADR-0009** made the same `QuerySpec` (not a Mosaic-invented shape, not Exon's
  `QueryPlan`) the canonical artifact Mosaic's MCP boundary validates and executes, with a
  Python parser/validator (`mosaic/core/query_spec.py`) and compiler that track ADR-0035; Mosaic
  ADR-0006/0007 supply the server capabilities it compiles to (typed per-slot operators,
  relationship predicates, counts, facet counts, min/max, ordering).

The question for Reel: does it adopt `QuerySpec` as the concrete v1 realization of `State`, or
keep its own richer `State {focal_type, predicates, grain}` shape and translate at the boundary?

## Decision

**Reel's v1 `State` *is* a `QuerySpec` instance, and Reel does not define a query noun of its
own.** Concretely:

1. **`State` (v1) = `QuerySpec`.** The `focal_type` of ADR-0001's sketch is the `anchor`; the
   `predicates` are the `criteria` tree; the `grain` is the anchor's grain (a to-many `explode`
   is a declared grain change). ADR-0001's *general* `State` remains the conceptual model; the
   `QuerySpec` is the only wire/persisted form Reel emits in v1.
2. **The op catalog binds to QuerySpec fields and Mosaic boundary tools**, not to a Reel-owned
   query language:

   | Reel op (ADR-0001) | v1 realization | Status |
   |---|---|---|
   | `filter` | `FieldCondition {slot, op, value}` (LinkML slot names, never camelCase) | built (prototype) |
   | `exists-related-filter` | `RelatedCondition {edge, quantifier: some\|none, criteria}` | built (prototype) |
   | `distinct-values` | Mosaic `facet_query_spec` over the current State (Mosaic ADR-0007; mosaic#195) | server tool live; not yet routed |
   | `group-by+count` | Mosaic `count_query_spec` / `facet_query_spec` | server tool live; not yet routed |
   | `pivot-grain` | a new `anchor` with the prior State re-derived as a `RelatedCondition` (the prototype's Decision 6), or an explicit `explode` | **mechanism shipped, not yet routed** — reverse edges via LinkML `inverse:` ([mosaic#204](https://github.com/BU-Neuromics/mosaic/issues/204), merged; [Mosaic ADR-0011](https://github.com/BU-Neuromics/mosaic/pull/219)); gated on a Mosaic release ([mosaic#218](https://github.com/BU-Neuromics/mosaic/issues/218)) and a deployment declaring the slot |
   | `set-op` | between States — Reel's own; **deferred** (ADR-0003) | unbuilt |
   | `render-as-primitive` | a View Contract instance bound to the State's result (ADR-0005) | unbuilt |

3. **Changes to the noun go to its owner first.** Reel does not add, rename, or repurpose
   `QuerySpec` fields; a need Reel discovers (e.g. multi-anchor set-ops, a `parents`-aware
   provenance block) is proposed as an amendment to Aperture ADR-0035 and mirrored by Mosaic
   ADR-0009's validator — then consumed here. `set-op` results that cannot be expressed as one
   `QuerySpec` are Reel-level composition over *several* States, not a new artifact.
4. **Ops that QuerySpec cannot express are refused, not approximated** — the same
   reject-don't-approximate discipline the boundary enforces (Aperture ADR-0029; Mosaic
   ADR-0009's actionable per-criterion errors).

## Consequences

- **The "set it up correctly" list in `prefab/data-stories.md` is satisfied by the platform**, not
  by Reel: interfaces #1 (serializable cohort object) and #2 (relationship-existence filters,
  group-by+count) exist; #3 (schema grounding) is Mosaic's server-derived capability manifest
  (`mosaic://capabilities`, with per-field legal operators and `enum_values`); #5 (dry-run
  validation) is `validate_query_spec`. Reel builds #1's *sequencing* and the story layer.
- **Reel inherits QuerySpec's current limits as v1 limits:** `asOf` is not combinable with a
  `RelatedCondition` until Mosaic's temporal join lands (bears on ADR-0002); `columns`
  (aggregate-vs-explode) is rejected by Mosaic's validator today; single-column `sort`.
- **Saved stories survive server upgrades for the same reason saved QuerySpecs do** (Aperture
  ADR-0035's IR-first payoff): the artifact is stable, only the planner/compiler moves.
- **A story becomes a sequence of `QuerySpec`s plus the instructions that produced them** — the
  prototype's `turns` list is already exactly this (ADR-0008).
- **Obligation on Reel:** track ADR-0035 / Mosaic ADR-0009 when the artifact's shape changes
  (the same obligation Mosaic recorded for itself). Reciprocal references are in place on both
  sides (Aperture ADR-0035 and Mosaic ADR-0009 both cite Reel ADR-0001/0003).

## Alternatives considered

- **Keep Reel's own `State {focal_type, predicates, grain}` and translate to QuerySpec at the
  boundary.** Preserves the general model in code, but re-creates the three-way artifact
  duplication (Aperture TS, Mosaic Python, Reel) that Mosaic ADR-0009 exists to eliminate, and
  every translation is a place for the dry-run guarantee to leak. Rejected: the general model
  stays conceptual; the wire form is the shared one.
- **Reel defines a superset artifact (QuerySpec + `parents` + set-ops) and asks Aperture/Mosaic
  to adopt it.** Premature — set-ops and multi-type ops are the *deferred* parts of Reel's own
  model (ADR-0003); asking two shipped components to carry unproven fields inverts the "general
  schema now, narrow validator now" rule. Rejected for now; revisit when rung 2 (cohort
  assembly) is scheduled.
- **Adopt Exon's `QueryPlan` (`FilterStep`/`RelatedLookupStep`) instead.** Already superseded by
  Mosaic ADR-0009 (QueryPlan's chained `source_step` shape existed only because Mosaic lacked
  server-side relationship predicates). Rejected.

## Notes / open sub-questions

- Whether `render-as-primitive` should carry a `QuerySpec` reference inside the View Contract's
  `provenance` block (so a rendered artifact points back at the State that produced it) is a
  View Contract design-pass question (`datahelix:platform/design/view-contract.md`).
- **`pivot-grain`: the mechanism shipped (correction, 2026-09-22).** This note read
  "**blocked** on reverse-edge traversal ([mosaic#204](https://github.com/BU-Neuromics/mosaic/issues/204))",
  which was true on 2026-09-11 and is not now. The proposed fix — LinkML `inverse:`-declared slots
  resolved through the forward slot — is **merged** (`7fc300c`) and tested across Mosaic's
  QuerySpec compiler, GraphQL, MCP and both storage adapters; Mosaic ADR-0011 is ratified in
  [mosaic#219](https://github.com/BU-Neuromics/mosaic/pull/219). A deployment declaring
  `inverse: donor` gets `Donor.samples` and `DonorFilter.samples: SampleEdgeQuantifiers
  { some, none }` with no Mosaic code change, which is exactly the "nameable and validated
  server-side" property this note asked for (ADR-0007), so Reel's requirement is met on the
  mechanism's own terms.

  **What remains is not engineering.** No tag contains the merge (Mosaic's latest is `v0.13.0`,
  which `datahelix`'s certification pins — [mosaic#218](https://github.com/BU-Neuromics/mosaic/issues/218)),
  and no deployment LinkML declares an `inverse:` slot yet. The blocker moved from *engineering*
  to *release + schema authoring*; it did not vanish, and this ADR should not be read as claiming
  `pivot-grain` is routable today. Reel still takes no position on the mechanism.

  **The other half of `pivot-grain` also has an artifact now.** This row offers "or an explicit
  `explode`", which had nowhere to live: `QuerySpec.columns` was reserved by Aperture ADR-0035 and
  never built. **Aperture ADR-0041** (Proposed 2026-09-22) builds it, split by the test *does
  changing it change the row set?* — traversal and grain (`explode`) stay in the artifact,
  visibility and ordering become view-side state that never reaches a server. An `explode`
  `ColumnSpec` is therefore the declared grain change `pivot-grain` binds to, and the view-side
  half is where `render-as-primitive` eventually lands via the View Contract's `table` encoding.
  Per §3 of this ADR, that amendment is being made by the noun's owner, for Reel to consume —
  which is the seam working as designed. No Reel change is required for it to ship.
- Polymorphic `is_a` anchors (Aperture ADR-0035 notes) will surface here as soon as a story
  pivots across a class hierarchy; no Reel position yet.

## Ratification

Ratified 2026-09-21. The QuerySpec is live on both sides of the boundary: Mosaic validates and executes it (ADR-0009, Accepted), Aperture carries it in the URL and validates it client-side (Aperture ADR-0035, Accepted), and the prototype emits it conversationally. Reel composing the noun rather than defining one is now observed, not projected.
