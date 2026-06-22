# Reel Design Decisions (ADRs)

Reel records design decisions as **ADRs** following the **platform-wide convention** — the
canonical process, lifecycle/statuses, and template live in the `drylims` parent repo at
`platform/design/decisions/README.md` (see also the root `CLAUDE.md`). [`_template.md`](./_template.md)
is the local copy of the canonical template.

> If a decision isn't recorded here, it isn't decided. Prose in `vision.md` is *context*; an ADR
> is the *decision*.

The [`../INDEX.md`](../INDEX.md) **Decision Log** table is Reel's index of record — one row per
ADR, status-tracked. Open questions are `Proposed` ADRs (the *decision queue*); ratifying one is
a status flip from `Proposed` → `Accepted`, not a new document. Decisions are never deleted —
reversals `Supersede` with a forward pointer.

## Provenance: migrated from Aperture

ADR-0001–0005 were authored inside the `aperture` component as **Aperture ADR-0022–0026** and
**renumbered** when the data-story engine was split into Reel (2026-06-22; boundary decision
`drylims:platform/design/decisions/ADR-0001`, runbook `drylims:proposals/reel-split.md`). The
originals are `Superseded by` these in Aperture with forward pointers. The renumbering map:

| Reel ADR | was Aperture ADR | Topic |
|---|---|---|
| [0001](./ADR-0001-data-story-is-an-instruction-path.md) | 0022 | data story = instruction path |
| [0002](./ADR-0002-data-story-reproducibility-as-of-watermark.md) | 0023 | as-of watermark reproducibility |
| [0003](./ADR-0003-instruction-path-linear-first-general-schema.md) | 0024 | topology: general schema, linear validator |
| [0004](./ADR-0004-mid-path-edit-recompute-with-suspend.md) | 0025 | mid-path edit: recompute + suspend |
| [0005](./ADR-0005-headless-core-thin-shell.md) | 0026 | headless core + thin shell |

**Cross-reference convention.** Inside these ADRs, bare `ADR-NNNN` refers to **Reel's own** ADRs;
references to the *portal's* decisions (which stay in Aperture) are qualified **"Aperture
ADR-NNNN"**. This disambiguates the overlapping low numbers (e.g. Reel ADR-0003 *topology* vs.
Aperture ADR-0003 *config-as-LinkML-in-Hippo*).
