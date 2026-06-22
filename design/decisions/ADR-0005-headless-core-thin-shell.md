# ADR-0005: Reel is a headless interaction core + a thin, replaceable shell

- **Status:** Proposed
- **Date:** 2026-06-22
- **Deciders:** labadorf, design session
- **Related:** reframes Aperture ADR-0014 (application architecture); depends on Aperture ADR-0008 (injected capability-scoped client), Aperture ADR-0009 (view-descriptions, not DOM), Aperture ADR-0017 (data plane / control-plane port), ADR-0001 (instruction-path model); informs Aperture ADR-0011 (component runtime), Aperture ADR-0015 (composability); `vision.md`; Aperture `architecture.md`; `drylims:platform/design/view-contract.md`

> **Migrated from Aperture ADR-0026 (2026-06-22)** on the data-story-engine split
> (`drylims:proposals/reel-split.md`; boundary `drylims:platform/design/decisions/ADR-0001`).
> Renumbered 0026 → Reel 0005. **Post-split reframing:** this ADR was authored while the engine
> still lived inside Aperture; it now describes **Reel** as the headless core. The core↔shell
> seam it argues for is realized across the split as **Reel (headless producer) → the View
> Contract → a renderer** (the Aperture portal, a notebook, or a third-party shell). The
> renderer/shell injection seam (#3 below) is the **View Contract**
> (`drylims:platform/design/view-contract.md`); platform ADR-0001 is the more-decoupled,
> cross-component form of this decision. References to the *portal's* decisions are qualified
> **"Aperture ADR-NNNN"**; bare `ADR-NNNN` refers to Reel's own ADRs.

## Context

The 2026-06-17 reframe (`vision.md`) replaced the product framing: the AI-native surface over the
BASS domain graph is an **interaction layer**, not a rendered config-driven portal (the portal is
its substrate/MVP). But the application-architecture decision (Aperture ADR-0014) still asks the
*portal* question — "server-rendered vs. client-side **app shell**" — as though a rendered UI is
the product. It is not: the near-term agent surface is an **external MCP coding agent** with no
portal UI at all (Aperture ADR-0021), and the UI, when it exists, is a *renderer over the
instruction-path model* (ADR-0001), one of five admitted modes.

Two further forces converge on the same point:

1. **The design already separates "what to show" from "how to paint it."** Components and views
   emit serializable **view-descriptions**, never DOM (Aperture ADR-0009); the data reach is an
   **injected** capability-scoped client (Aperture ADR-0008); the config/state store is a **port**
   with a reference impl, not a hard dependency (Aperture ADR-0017). These are exactly the seams a
   framework- and shell-agnostic core needs.
2. **Embeddability is a requirement (2026-06-22).** The engine should be embeddable in a larger
   host app, with **no specific host named** — i.e. embeddability must be a *property of the
   architecture*, not a one-off integration. The granularity chosen is **headless core + thin
   shell** (a host mounts the core and supplies/overrides the shell), the SDK-first principle
   (root `CLAUDE.md`) extended up to the UI layer.

The question this ADR settles is therefore **not** "SSR vs SPA" — it is **what is the product
unit, and where is the boundary between reusable core and replaceable shell.** Get this wrong and
the framework choice (Aperture ADR-0011/0014) becomes a load-bearing, hard-to-reverse bet; get it
right and that choice collapses to "which default shell," low-stakes and swappable.

## Decision

**Reel is a framework-agnostic, headless *interaction core* that produces View Contract instances;
a thin, replaceable *shell* (a renderer) realizes them. The product is the core; any shipped
application is one ordinary consumer of it.**

**The headless core** (no DOM, no framework, pure logic) owns all interaction logic:

- the **instruction-path engine** — `state[n] = apply(instruction[n], state[n-1])` over the typed
  op catalog (ADR-0001/0003), deterministic and as-of-pinned (ADR-0002);
- the **view-description / View Contract types + headless validators** (Aperture ADR-0009/0010;
  `drylims:platform/design/view-contract.md`) — the engine's output is serializable
  descriptions + attached data, never pixels;
- the **component runtime** (Aperture ADR-0011) — Web Worker, view-spec-emitting;
- the **data-plane source adapter** behind the **injected capability-scoped client**
  (Aperture ADR-0008/0017);
- the **control-plane store port** (Aperture ADR-0017) — config, user state, and `DataStory`
  persistence;
- the **agent surface** (MCP/API, Aperture ADR-0021).

**The shell** is the only part that touches a UI framework: it realizes view-descriptions / View
Contract instances into pixels and owns layout, routing, navigation, and theming. The Aperture
portal is *a* shell (the reference renderer), not *the* product.

**Embeddability is then a property, delivered by three injection seams the host fills** — none
new, each already a decision:

1. **The capability-scoped client (Aperture ADR-0008)** — the host injects auth/data access; Reel
   stays auth-unaware.
2. **The control-plane store port (Aperture ADR-0017)** — the host may supply config/state
   persistence, or accept the LinkML-on-Hippo reference impl.
3. **The renderer/shell, via the View Contract** — the host either mounts a default shell as a
   component or consumes View Contract instances and renders them in its own shell (down to a
   single `DataStory` or view artifact).

A host embeds Reel by filling these seams; a default app fills them with defaults. There is
**one** core, exercised identically whether driven by a shipped shell, an embedding host, the
MCP agent, or the headless validators.

## Consequences

- **Aperture ADR-0014 is reframed, not answered as posed.** "SSR vs SPA vs hybrid" is no longer
  the product architecture — it is a **delivery option for a shell**. SSR, SPA, embedded widget,
  and "headless, host renders" all become *consumers of the same core via the View Contract*.
  Aperture ADR-0014 should be superseded/rewritten to record this, and the framework-selection
  question it defers (now lower-stakes) gets its own ADR (in whichever component ships the
  reference shell).
- **The framework choice is demoted from keystone to shell detail.** Because the core is
  framework-agnostic, picking React/Svelte/web-components for a default shell does not bind the
  product; a host on a different stack still consumes the core. Strongly favors shipping the
  renderer as framework-neutral (e.g. web components) so embedding doesn't require the host adopt
  a particular framework — to be settled in the framework ADR.
- **New invariant: no interaction logic in the shell.** Anything that decides *what* to show
  (instruction ops, state reduction, binding, validation) lives in the core; the shell only
  decides *how to paint* a view-description. Logic leaking into the shell is the signal the core
  boundary has drifted — the UI-layer analogue of Aperture ADR-0002's domain-noun grep.
- **Headlessness is enforced, not aspirational.** The same view-description→validation path that
  Aperture ADR-0009 already requires (Node/Web Worker, no browser) *is* the core's public surface,
  so "the core runs with no shell" is checked by the existing headless tests, not a separate
  effort.
- **Theming/design-tokens become an explicit seam** so an embedded Reel can inherit a host's
  look — a follow-on for the shell/framework ADR.
- **SDK-first stays consistent across the stack** (root `CLAUDE.md`): business logic in a typed
  core, transport/render as thin wrappers — now true on the frontend, not just Python/REST.

## Alternatives considered

- **Answer Aperture ADR-0014 as posed (pick SSR or SPA for "the app").** Treats a rendered shell
  as the product — the portal-era framing `vision.md` retired. It also makes the framework choice
  load-bearing and forecloses embedding. Rejected: it answers a question we no longer ask.
- **Embed by shipping a self-contained app the host iframes.** Strong isolation, but weak
  integration (styling, deep state/selection sharing, auth handoff) and it doesn't make the
  *engine* reusable — the host gets a black box, not a core. Kept as one *shell delivery option*
  (for cross-stack third-party hosts), not the architecture.
- **Micro-frontend (module federation) as the embedding model.** Heaviest infra, couples host and
  build tooling, and still needs the core/shell split underneath to be worth it. Rejected as the
  baseline; admissible later as a shell delivery option if a host demands it.
- **Headless SDK only, no shipped shell.** Maximally flexible but ships nothing usable and starves
  the keystone probe (which needs a running surface). Rejected: ship a default shell *as a
  consumer* (the Aperture portal), don't omit it.

## Notes / open sub-questions

- **Does not depend on the Aperture ADR-0010 vocabulary probe.** The core/shell boundary holds
  whatever the primitive catalog turns out to be; the probe only sizes the *renderer's* primitive
  set, inside the shell. So this ADR can ratify ahead of the keystone — and it *removes* the
  framework choice from the keystone's critical path.
- The exact **core public API** (how a host obtains and drives an instruction-path session, mounts
  a renderer, and injects the three seams) is a follow-on design once this boundary is accepted.
- Boundary of "thin": is the framework-neutral **View Contract renderer** part of the core
  (framework-agnostic, e.g. web components) or part of the shell? Leaning: the renderer is a
  framework-neutral artifact; the *shell* is only routing/nav/layout/theming. Settle in the
  framework ADR.
- Relationship to the **default control-plane**: embedding hosts that decline LinkML-on-Hippo need
  the store port surface specified (Aperture ADR-0017 says "port, not dependency" — this makes a
  host the first non-Hippo consumer to pressure-test it).
