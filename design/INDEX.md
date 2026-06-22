# Reel — AI-Native Data-Story Engine
## Design Index

**Codename:** Reel *(provisional — see [`vision.md`](vision.md); candidates: Strand, Loom, Lumen, Cadence)*
**Component:** Headless data-story / instruction-path engine over the BASS domain graph. Produces
**View Contract** instances; does no rendering. The config-driven **portal** (Aperture) is the
renderer that ships now.
**Version:** 0.1 — design seed (split from Aperture 2026-06-22)

---

This repository is a **fresh, design-first start** extracted from the `aperture` component when
the data-story engine was split out (boundary decision
`drylims:platform/design/decisions/ADR-0001`; runbook `drylims:proposals/reel-split.md`). There
is **no Reel code yet** — the carry-set is design docs only. The decisions below were authored as
Aperture ADR-0022–0026 and **renumbered** to Reel ADR-0001–0005 on extraction; the originals are
`Superseded by` these in Aperture with forward pointers.

## Document Map

| File | Section | Status | Notes |
|---|---|---|---|
| `decisions/` | **Design decisions (ADRs)** | 🟢 Canonical | The source of truth for *what was decided and why*. See `decisions/README.md`; the Decision Log below is the index. |
| `vision.md` | North-star vision / charter | 🔵 Vision | Reel as the headless AI-native data-story engine; the instruction-path core; the keystone probe; what stays out (rendering, the View Contract, domain nouns). |
| `instruction-path-model.md` | Instruction-path model (working) | 🟠 Working | The formal data structure under `prefab/data-stories.md`: a data story as a path of source-tagged typed instructions producing intensional subgraph **states** + materialized **artifacts**. Topology (linear/tree/DAG) as a data property; reproducibility via one as-of watermark; UI modes as topology slices. |
| `prefab/data-stories.md` | Keystone MVP (working) | 🟠 Working | The simplest concrete realization: a NotebookLM-style conversational exploration of Hippo metadata. Keystone probe rung 1–2. |

## How decisions are recorded

Every load-bearing choice is an **ADR** in [`decisions/`](./decisions/), indexed by the Decision
Log below, following the **platform-wide convention**
(`drylims:platform/design/decisions/README.md`). Open questions are `Proposed` ADRs (the decision
queue); ratifying one is a status flip to `Accepted`, not a new document. Decisions are never
deleted — reversals `Supersede` with a forward pointer.

## Decision Log

| ADR | Decision | Status | Notes |
|---|---|---|---|
| [0001](./decisions/ADR-0001-data-story-is-an-instruction-path.md) | A data story is an instruction path → typed subgraph states + artifacts | 🟡 Proposed | migrated from Aperture ADR-0022; behind keystone Aperture ADR-0010 |
| [0002](./decisions/ADR-0002-data-story-reproducibility-as-of-watermark.md) | Reproducibility: one as-of watermark per story-version; "pull new data" = recorded watermark-advance | 🟡 Proposed | migrated from Aperture ADR-0023; depends on Hippo graph-level as-of (Hippo ADR-0001) |
| [0003](./decisions/ADR-0003-instruction-path-linear-first-general-schema.md) | Topology: general `parents`-list schema now, linear-only validator in v1 | 🟡 Proposed | migrated from Aperture ADR-0024 |
| [0004](./decisions/ADR-0004-mid-path-edit-recompute-with-suspend.md) | Mid-path edits recompute downstream + suspend-on-invalid (not discard) | 🟡 Proposed | migrated from Aperture ADR-0025 |
| [0005](./decisions/ADR-0005-headless-core-thin-shell.md) | Headless interaction core + thin replaceable shell; renderer seam = the View Contract | 🟡 Proposed | migrated from Aperture ADR-0026; reframed by platform ADR-0001 + view-contract |

## Decision Queue (open — resolve in dependency order)

- **First action: run the keystone probe** (`prefab/data-stories.md`) — the cheapest decisive
  test of NL→typed-query→validate→render. ADR-0001–0004 ratify *after* the probe (they are
  `Proposed` pending it).
- **ADR-0002 is blocked on Hippo graph-level as-of** (Hippo ADR-0001) — confirm it is on Hippo's
  roadmap / delivered before ratifying.
- **View Contract grammar** — a platform-level design pass
  (`drylims:platform/design/view-contract.md`); Reel is a producer, so its op→primitive mapping
  feeds that spec.
