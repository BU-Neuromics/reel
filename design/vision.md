# Reel — North-star vision (the AI-native data-story engine)

**Status:** 🔵 Vision / charter (2026-06-22). Reel's charter, seeded on the data-story-engine
split from Aperture. The boundary decision is `drylims:platform/design/decisions/ADR-0001`
("Separate the data-story engine (Reel) from the rendering portal (Aperture)"); the joining
interface is `drylims:platform/design/view-contract.md`.

> **Codename.** "Reel" is the working codename for this component (a reel of frames ≈ a sequence
> of data-story states; stays in Aperture's optical family). Candidates if it changes: Strand,
> Loom, Lumen, Cadence. Lock before code lands.

## What Reel is

Reel is the BASS platform's **AI-native data-story engine** over the
[domain graph](../../platform/design/domain-graph.md). It is the ambitious half of what was
originally "Aperture": the part that turns natural-language and UI-driven exploration into a
**typed, replayable, reproducible data story**, while the config-driven **portal** (Aperture)
ships independently as the rendering substrate.

Reel is **headless** ([ADR-0005](./decisions/ADR-0005-headless-core-thin-shell.md)): it produces
**View Contract instances** (a declarative spec + the data to show) and does **no rendering**. A
renderer — the Aperture portal, a notebook, or any third-party shell — consumes the contract and
paints it, knowing nothing about how it was produced (the Vega-Lite pattern). This is what lets
the portal ship now and Reel mature on its own cadence.

## The core idea: a data story is an instruction path

A "data story" is modeled as an **instruction path**
([`instruction-path-model.md`](./instruction-path-model.md);
[ADR-0001](./decisions/ADR-0001-data-story-is-an-instruction-path.md)): an ordered/linked set of
source-tagged, typed `Instruction`s that deterministically reduce to a sequence of subgraph
`State`s and the `Artifact`s rendered from them — `state[n] = apply(instruction[n], state[n-1])`.
Chat turns and UI events are both `Instruction`s; the path *is* the provenance log; a saved story
is a serializable, validatable LinkML artifact.

The load-bearing properties:

- **Intensional state + reproducibility.** State is stored as a *specification* re-evaluated
  against Hippo, pinned to **one as-of watermark** per story-version, so a story reproduces
  identically on replay; "pull new data" is an explicit, recorded watermark-advance
  ([ADR-0002](./decisions/ADR-0002-data-story-reproducibility-as-of-watermark.md)).
- **General model, narrow validator.** `parents` is a list from day one (linear/tree/DAG with no
  migration), but v1 validates linear-only
  ([ADR-0003](./decisions/ADR-0003-instruction-path-linear-first-general-schema.md)).
- **Non-lossy editing.** Mid-path edits recompute downstream against the fixed watermark and
  suspend-on-invalid rather than discard
  ([ADR-0004](./decisions/ADR-0004-mid-path-edit-recompute-with-suspend.md)).

## The keystone probe

Reel carries the platform's least-proven, highest-value bet and its keystone test:
**"can an LLM reliably drive a typed declarative artifact through a validator to a correct
change?"** The cheapest decisive version is the linear, Hippo-only conversational data story in
[`prefab/data-stories.md`](./prefab/data-stories.md). If it works, the AI-native vision is real;
if NL→validated-query proves unreliable even here, we learn it cheaply — without holding the
portal MVP hostage.

## What stays out of Reel

- **Rendering / the portal** — Aperture (the config-driven portal) renders View Contract
  instances; Reel never paints pixels.
- **The View Contract spec** — platform-owned (`drylims:platform/design/view-contract.md`), since
  it has two producers (Reel and the portal config path) and many consumers.
- **Domain nouns** — Reel is generic; the domain schema is the deployment's LinkML
  (inheriting Aperture ADR-0002's principle).

## Relationship to the rest of the platform

| Concern | Owner |
|---|---|
| Data-story / instruction-path engine (headless) | **Reel** (this repo) |
| Rendering portal (the deployable MVP, a View Contract consumer) | Aperture |
| The View Contract (renderer-agnostic spec + data) | `drylims/platform/` |
| Metadata / domain graph + provenance + as-of | Hippo |
| Workflow execution / bulk-data slicing | Cappella / Canon |
