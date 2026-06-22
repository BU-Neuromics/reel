# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Component Overview

**Reel** is the BASS platform's **AI-native data-story engine** — the headless instruction-path
core that produces **View Contract** instances over the domain graph. It does **no rendering**;
the Aperture portal (and other shells) consume its output. See the `drylims` root `../CLAUDE.md`
for repo-wide conventions, and `design/vision.md` for Reel's charter. Reel was split out of
Aperture on 2026-06-22 (boundary: `drylims:platform/design/decisions/ADR-0001`; runbook:
`drylims:proposals/reel-split.md`).

> **Codename.** "Reel" is provisional (candidates: Strand, Loom, Lumen, Cadence). Lock before code.

## Spec Structure

Design docs live in `design/`. Reel is designed **ADR-first**: load-bearing decisions are recorded
as ADRs in `design/decisions/`, indexed by the **Decision Log** in `design/INDEX.md` (the source
of truth — always check it before drafting or modifying design content). `vision.md` and the
working-design docs (`instruction-path-model.md`, `prefab/`) provide narrative context; **cite
ADRs for decisions**.

## Design Decisions (ADRs)

- Decisions are recorded as **ADRs** per the **platform-wide convention** — canonical process and
  template in `drylims:platform/design/decisions/README.md`; local process notes in
  `design/decisions/README.md`.
- ADR-0001–0005 were **migrated and renumbered from Aperture ADR-0022–0026** on the split. Inside
  these ADRs, bare `ADR-NNNN` is a **Reel** ADR; portal decisions are qualified **"Aperture
  ADR-NNNN"** (the low numbers overlap — e.g. Reel ADR-0003 *topology* vs. Aperture ADR-0003
  *config-as-LinkML*).
- New/non-trivial decisions get an ADR; open questions are `Proposed` ADRs ratified by a status
  flip. Decisions are never deleted — reversals `Supersede` with a forward pointer.
- When a Reel ADR imposes a requirement on another component, cross-reference that component's ADR
  / spec so the dependency is legible from both sides (e.g. ADR-0002 ↔ Hippo graph-level as-of).

## Writing Guidelines

- Keep the platform's **SDK-first** principle and the **typed/declarative substrate** invariants
  (config-as-LinkML-in-Hippo, no middle scripting layer, view-descriptions/View-Contract-not-DOM,
  dry-run-validatable) consistent across design docs.
- Reel is **headless** — it produces View Contract instances, never pixels. Rendering belongs to a
  consumer (the Aperture portal, a notebook, a third-party shell).
- Reel source is **generic** — no domain (e.g. brain-bank) nouns; the domain schema is the
  deployment's LinkML (inheriting Aperture ADR-0002's principle).
