# Reel — North-star vision (the AI-native data-story engine)

**Status:** 🔵 Vision / charter (2026-06-22; names and platform state refreshed 2026-09-11).
Reel's charter, seeded on the data-story-engine split from Aperture. The boundary decision is
DataHelix platform
[ADR-0003](https://github.com/BU-Neuromics/datahelix/blob/main/platform/design/decisions/ADR-0003-reel-data-story-engine-separate-from-portal.md)
("Separate the data-story engine (Reel) from the rendering portal (Aperture)"); the joining
interface is
[`platform/design/view-contract.md`](https://github.com/BU-Neuromics/datahelix/blob/main/platform/design/view-contract.md).

> **Name.** "Reel" — a reel of frames ≈ a sequence of data-story states; in Aperture's optical
> family. It began as a working codename (alternatives: Strand, Loom, Lumen, Cadence) and was
> ratified with the split (platform ADR-0003).

## What Reel is

Reel is the DataHelix platform's **AI-native data-story engine** over the
[domain graph](https://github.com/BU-Neuromics/datahelix/blob/main/platform/design/domain-graph.md)
— one typed knowledge graph whose type system is the deployment's LinkML schema and whose runtime
is **Mosaic** (formerly Hippo, Mosaic ADR-0004). Reel is the ambitious half of what was
originally "Aperture": the part that turns natural-language and UI-driven exploration into a
**typed, replayable, reproducible data story**, while the config-driven **portal** (Aperture)
ships independently as the rendering substrate.

Reel is **headless** ([ADR-0005](./decisions/ADR-0005-headless-core-thin-shell.md)): it produces
**View Contract instances** (a declarative spec + the data to show) and does **no rendering**. A
renderer — the Aperture portal, a notebook, or any third-party shell — consumes the contract and
paints it, knowing nothing about how it was produced (the Vega-Lite pattern).

Reel is also **a planner, not a validator or executor**
([ADR-0007](./decisions/ADR-0007-reel-delegates-to-the-mosaic-boundary.md)): every query it
composes is a platform **QuerySpec** ([ADR-0006](./decisions/ADR-0006-v1-state-is-the-queryspec.md);
Aperture ADR-0035) that **Mosaic's MCP boundary** validates and executes (Mosaic ADR-0009). Reel
sits behind Mosaic's validating relay (Mosaic ADR-0010): a shell reaches it only through Mosaic,
its proposals are re-validated before anyone sees them, and it never decides to execute.

## The core idea: a data story is an instruction path

A "data story" is modeled as an **instruction path**
([`instruction-path-model.md`](./instruction-path-model.md);
[ADR-0001](./decisions/ADR-0001-data-story-is-an-instruction-path.md)): an ordered/linked set of
source-tagged, typed `Instruction`s that deterministically reduce to a sequence of subgraph
`State`s and the `Artifact`s rendered from them — `state[n] = apply(instruction[n], state[n-1])`.
Chat turns and UI events are both `Instruction`s; the path *is* the provenance log; a saved story
is a serializable, validatable LinkML artifact. In v1 each `State` is a `QuerySpec` — one
anchored, criteria-bound subgraph selection — so **a story is a sequence of QuerySpecs plus the
instructions that produced them**.

The load-bearing properties:

- **Intensional state + reproducibility.** State is stored as a *specification* re-evaluated
  against Mosaic, pinned to **one as-of watermark** per story-version, so a story reproduces
  identically on replay; "pull new data" is an explicit, recorded watermark-advance
  ([ADR-0002](./decisions/ADR-0002-data-story-reproducibility-as-of-watermark.md); substrate:
  Mosaic ADR-0001, Accepted).
- **General model, narrow validator.** `parents` is a list from day one (linear/tree/DAG with no
  migration), but v1 validates linear-only
  ([ADR-0003](./decisions/ADR-0003-instruction-path-linear-first-general-schema.md)).
- **Non-lossy editing.** Mid-path edits recompute downstream against the fixed watermark and
  suspend-on-invalid rather than discard
  ([ADR-0004](./decisions/ADR-0004-mid-path-edit-recompute-with-suspend.md)).

## The keystone probe — run

Reel carries the platform's least-proven, highest-value bet and its keystone test:
**"can an LLM reliably drive a typed declarative artifact through a validator to a correct
change?"** The cheapest decisive version was the linear, Mosaic-only conversational data story in
[`prefab/data-stories.md`](./prefab/data-stories.md).

That probe **has been running since 2026-08 as Exon**
([`BU-Neuromics/mosaic-demo-small`](https://github.com/BU-Neuromics/mosaic-demo-small), `exon/`) —
a schema-grounded NL → QuerySpec planner with a harness that measures pass rates over repeated
samples and grades *faithfulness*, not just validity. The answer so far
([`platform-alignment.md`](./platform-alignment.md) "Keystone probe"): the typed-artifact →
validator loop **works structurally** with hosted models; the reliability gap is
**faithfulness** — a valid artifact that paraphrases an enum value or answers a counting question
with a row listing — which no validator can catch. That is Reel's real problem, and it is
measurable. Exon was written in Reel's vocabulary so it can migrate here
([ADR-0008](./decisions/ADR-0008-exon-seeds-reel.md); [`../proposals/exon-migration.md`](../proposals/exon-migration.md)).

## What stays out of Reel

- **Rendering / the portal** — Aperture (the config-driven portal) renders View Contract
  instances; Reel never paints pixels.
- **The View Contract spec** — platform-owned (`datahelix:platform/design/view-contract.md`),
  since it has two producers (Reel and the portal config path) and many consumers.
- **The query noun** — the QuerySpec is Aperture's (ADR-0035) and Mosaic's to validate
  (ADR-0009); Reel composes instances and proposes amendments, never a dialect (ADR-0006).
- **Query validation and execution** — Mosaic's MCP boundary; Reel holds no validator or executor
  of its own and never decides to execute (ADR-0007).
- **Domain nouns** — Reel is generic; the domain schema is the deployment's LinkML (inheriting
  Aperture ADR-0002's principle). Domain-bearing eval fixtures live beside Reel, not in it.

## Relationship to the rest of the platform

| Concern | Owner |
|---|---|
| Data-story / instruction-path engine (headless planner + composer) | **Reel** (this repo) |
| Reel's running prototype (rung 1) and its reliability harness | **Exon** in `mosaic-demo-small` — migrating here (ADR-0008) |
| Rendering portal (the deployable MVP, a View Contract consumer) | Aperture |
| The typed query artifact (QuerySpec) | Aperture (ADR-0035) defines; Mosaic (ADR-0009) validates/executes |
| The View Contract (renderer-agnostic spec + data) | `datahelix/platform/` |
| Domain graph + provenance + as-of; the MCP boundary and its validating relay | Mosaic |
| Workflow execution / bulk-data slicing | Cappella / Canon |
| Authentication / authorization (the sole PEP/PDP) | Bridge (Reel stays auth-unaware) |
