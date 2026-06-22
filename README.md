# Reel — AI-Native Data-Story Engine (BASS platform)

**Reel** is the BASS platform's **headless data-story / instruction-path engine** over the
domain graph. It turns natural-language and UI-driven exploration into **typed, replayable,
reproducible data stories**, and emits **View Contract** instances (a declarative spec + the data
to show) for *any* renderer to visualize. Reel does **no rendering** itself.

> **Provisional codename.** "Reel" is a working name (candidates: Strand, Loom, Lumen, Cadence).
> Lock it before code lands — see [`design/vision.md`](design/vision.md).

## Status

**Design seed (2026-06-22).** No code yet — this repo currently carries design only. Reel was
split out of the **Aperture** component so the config-driven **portal** (Aperture) can ship as the
rendering MVP while the AI-native engine matures on its own cadence. The boundary decision and the
joining interface live in the `drylims` platform repo:

- Boundary: `platform/design/decisions/ADR-0001` — *Separate the data-story engine (Reel) from the rendering portal (Aperture)*
- Interface: `platform/design/view-contract.md` — the renderer-agnostic spec-with-data-attached
- Runbook: `proposals/reel-split.md`

## Where to start

- [`design/vision.md`](design/vision.md) — what Reel is and why.
- [`design/INDEX.md`](design/INDEX.md) — the design index + **Decision Log** (the source of truth).
- [`design/instruction-path-model.md`](design/instruction-path-model.md) — the formal data-story model.
- [`design/prefab/data-stories.md`](design/prefab/data-stories.md) — the keystone MVP / first probe.
- [`design/decisions/`](design/decisions/) — the ADRs (0001–0005), migrated/renumbered from Aperture 0022–0026.

## Relationship to the BASS platform

Reel is one component of the BASS platform, attached to the `drylims` integration repo as a
submodule (alongside Hippo and Aperture). It is **headless** and **generic** (no domain nouns):
the domain schema is the deployment's LinkML, hosted in **Hippo**; the **Aperture** portal (and
other shells) render Reel's View Contract output.

## License

MIT — see [`LICENSE`](LICENSE).
