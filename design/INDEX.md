# Reel — AI-Native Data-Story Engine
## Design Index

**Component:** Headless data-story / instruction-path engine over the DataHelix domain graph.
Composes typed query states (**QuerySpec** instances) into replayable, reproducible stories and
produces **View Contract** instances; does no rendering (the Aperture portal renders) and no
query validation/execution of its own (Mosaic's MCP boundary does).
**Name:** Reel — ratified (platform ADR-0003); no longer a provisional codename.
**Version:** 0.2 — design brought up to date with the platform (2026-09-11); still no code.
**Prototype:** **Exon** in [`BU-Neuromics/mosaic-demo-small`](https://github.com/BU-Neuromics/mosaic-demo-small)
(`exon/`) — Reel rung 1 running under another name; migrates here per ADR-0008 /
[`proposals/exon-migration.md`](../proposals/exon-migration.md).

---

Reel was extracted from the `aperture` component when the data-story engine was split from the
rendering portal (DataHelix platform
[ADR-0003](https://github.com/BU-Neuromics/datahelix/blob/main/platform/design/decisions/ADR-0003-reel-data-story-engine-separate-from-portal.md),
2026-06-22; its **Outcome** section records the execution). ADR-0001–0005 were authored as
Aperture ADR-0022–0026 and **renumbered** on extraction; the originals are `Superseded by` these
in Aperture with forward pointers. The design set was written when the platform was **BASS**
and the graph runtime **Hippo**; it now reads **DataHelix** and **Mosaic** (Mosaic ADR-0004),
with data-contract identifiers (`hippoSchema`, `hippo_core`) unchanged.

## Document Map

| File | Section | Status | Notes |
|---|---|---|---|
| `decisions/` | **Design decisions (ADRs)** | 🟢 Canonical | The source of truth for *what was decided and why*. See `decisions/README.md`; the Decision Log below is the index. |
| `vision.md` | North-star vision / charter | 🔵 Vision | Reel as the headless AI-native data-story engine; the instruction-path core; the keystone probe (now run, as Exon); what stays out (rendering, the View Contract, query validation/execution, domain nouns). |
| `platform-alignment.md` | **Reel ↔ platform crosswalk** | 🟢 Reference | Every claim/dependency in the older docs mapped to the current platform state: names, ADR statuses, the interfaces `prefab/` asked for (all now exist), the keystone-probe results, roadmap position, stale references in sibling repos. **Read this first if you last read Reel before 2026-09.** |
| `instruction-path-model.md` | Instruction-path model (working) | 🟠 Working | The formal data structure under `prefab/data-stories.md`: a data story as a path of source-tagged typed instructions producing intensional subgraph **states** + materialized **artifacts**. Topology as a data property; one as-of watermark; UI modes as topology slices. §9's "new platform requirement" is now Mosaic ADR-0001 (Accepted). v1 `State` = `QuerySpec` (ADR-0006). |
| `prefab/data-stories.md` | Keystone MVP (working) | 🟠 Working | The simplest concrete realization: a conversational exploration of the Mosaic domain graph. DS-2/DS-3 resolved; the probe has run (Exon). |
| `../proposals/exon-migration.md` | **Exon → Reel migration runbook** | 🟡 Preparation | Current state of Exon, preconditions, phases (A: prepare landing site — *current*; B: build seed; C: relay cutover; D: mount in DataHelix), the translation deltas D1–D5, inherited backlog. Authorized by ADR-0008. |

## How decisions are recorded

Every load-bearing choice is an **ADR** in [`decisions/`](./decisions/), indexed by the Decision
Log below, following the **platform-wide convention**
([`datahelix:platform/design/decisions/README.md`](https://github.com/BU-Neuromics/datahelix/blob/main/platform/design/decisions/README.md)).
Open questions are `Proposed` ADRs (the decision queue); ratifying one is a status flip to
`Accepted`, not a new document. Decisions are never deleted — reversals `Supersede` with a forward
pointer. Cross-component references are always qualified (**Aperture ADR-NNNN**, **Mosaic
ADR-NNNN**, **platform ADR-NNNN**); see `decisions/README.md` for the numbering caveats.

## Decision Log

| ADR | Decision | Status | Notes |
|---|---|---|---|
| [0001](./decisions/ADR-0001-data-story-is-an-instruction-path.md) | A data story is an instruction path → typed subgraph states + artifacts | 🟡 Proposed | migrated from Aperture ADR-0022; was gated on the keystone probe — **the probe has run** (Exon); status update appended 2026-09-11 recommends ratifying with 0003/0004 |
| [0002](./decisions/ADR-0002-data-story-reproducibility-as-of-watermark.md) | Reproducibility: one as-of watermark per story-version; "pull new data" = recorded watermark-advance | 🟡 Proposed | migrated from Aperture ADR-0023; blocker cleared — **Mosaic ADR-0001 Accepted** (graph-level as-of), implementation in progress; `asOf` ⟂ `RelatedCondition` until Mosaic's temporal join |
| [0003](./decisions/ADR-0003-instruction-path-linear-first-general-schema.md) | Topology: general `parents`-list schema now, linear-only validator in v1 | 🟡 Proposed | migrated from Aperture ADR-0024; cited reciprocally by Aperture ADR-0035 (rejects arbitrary joins); prototype is linear-only |
| [0004](./decisions/ADR-0004-mid-path-edit-recompute-with-suspend.md) | Mid-path edits recompute downstream + suspend-on-invalid (not discard) | 🟡 Proposed | migrated from Aperture ADR-0025; **exercised end to end** by the prototype's `edit_turn_id` / `suspended_turn_ids` and Mosaic ADR-0010 term 2 |
| [0005](./decisions/ADR-0005-headless-core-thin-shell.md) | Headless interaction core + thin replaceable shell; renderer seam = the View Contract | 🟡 Proposed | migrated from Aperture ADR-0026 (Aperture later reused 0026 — cite this one); Aperture ADR-0014/0030/0031 settled the shell; the MCP surface is Mosaic's (see 0007) |
| [0006](./decisions/ADR-0006-v1-state-is-the-queryspec.md) | Reel's v1 `State` **is** the platform **QuerySpec**; Reel composes the query noun, never defines one; op catalog → QuerySpec fields / Mosaic boundary tools | 🟢 Accepted | 2026-09-11; Reel side of **Aperture ADR-0035** (Accepted) + **Mosaic ADR-0009** (Accepted). **Corrected 2026-09-22** ([#2](https://github.com/BU-Neuromics/reel/issues/2)): `pivot-grain` is no longer blocked on mosaic#204 — the mechanism merged and Mosaic ADR-0011 is ratified; what remains is a Mosaic release + a deployment declaring the `inverse:` slot. Its `explode` half gets an artifact in **Aperture ADR-0041**. |
| [0007](./decisions/ADR-0007-reel-delegates-to-the-mosaic-boundary.md) | Reel plans; **Mosaic's MCP boundary validates and executes**; Reel is an untrusted planner behind Mosaic's validating relay, configured-or-absent, auth-unaware | 🟢 Accepted | 2026-09-11; Reel side of **Mosaic ADR-0009** (Accepted) / **ADR-0010** (Proposed — do not lead it) |
| [0008](./decisions/ADR-0008-exon-seeds-reel.md) | **Exon seeds Reel** — migrate the prototype (planner, harness, turn contract), don't rewrite; the turn contract is the v1 wire form of `Instruction`; `datahelix-reel` / `import reel` | 🟢 Accepted | 2026-09-11; runbook `../proposals/exon-migration.md`; `mosaic-demo-small` untouched until Phase C |

## Decision Queue (open — resolve in dependency order)

1. **Ratify ADR-0001, 0003, 0004** on the strength of the probe (`platform-alignment.md`
   "Keystone probe"): the instruction-path model, linear-first topology, and recompute-with-suspend
   all held in the prototype. The one open sub-question (multi-type ops) was already deferred.
2. **Ratify ADR-0006** (v1 State = QuerySpec) — it records the Reel side of two Accepted
   decisions; the only Reel-local choice is *not* keeping a translation shim, argued in the ADR.
3. **Ratify ADR-0002** now that Mosaic ADR-0001 is Accepted — with the v1 caveat that a story
   containing an `exists-related-filter` cannot pin a watermark until Mosaic's temporal join
   (M5a) lands. Decide whether v1 *refuses* to pin such stories (recommended: yes, coded error)
   or pins and marks the related step unpinned.
4. **ADR-0007 follows Mosaic ADR-0010** (Proposed 2026-09-08). Flip together.
5. **ADR-0008** (migrate Exon) — ratify once 1–4 are settled; execution waits on the
   preconditions in `../proposals/exon-migration.md` §2 (Exon Phase 2 complete; turn endpoint
   live behind Mosaic's relay).
6. **ADR-0005** can ratify independently (it never depended on the probe), noting the narrowed
   "core" (ADR-0007): the query validator and the MCP surface are Mosaic's.
7. **View Contract grammar** — a platform-level design pass
   (`datahelix:platform/design/view-contract.md`, still a stub). Reel's op→primitive mapping
   (`render-as-primitive`) and the `provenance` block (watermark, producing instruction, State
   reference) feed that spec. Not blocking v1 of the story engine.

## Platform decisions that bind Reel (reciprocal references)

| Decision | Status | What it fixes for Reel |
|---|---|---|
| platform ADR-0002 (metapackage + extras) | Accepted | `datahelix-reel` dist, `import reel` |
| platform ADR-0003 (Reel ⟂ Aperture, View Contract) | Accepted, executed | Reel's boundary; the renderer seam |
| Aperture ADR-0035 (QuerySpec) | Accepted 2026-08-19 | the v1 `State` (ADR-0006); "Reel composes instances of it" |
| Mosaic ADR-0001 (graph-level as-of) | Accepted; in progress | ADR-0002's watermark substrate |
| Mosaic ADR-0006 / 0007 (typed filters; aggregation & ordering) | Accepted; shipped v0.13 | `exists-related-filter`, `distinct-values`, `group-by+count` have server semantics |
| Mosaic ADR-0009 (MCP boundary, capability manifest, QuerySpec tools) | Accepted 2026-09-01 | where validation/execution live (ADR-0007); the LLM's grounding (`mosaic://capabilities`) |
| Mosaic ADR-0010 (outbound delegation to a planner behind a validating relay) | Proposed 2026-09-08; implemented | Reel's topology and response obligations (ADR-0007); "a Reel engine inherits items 1–7" |
