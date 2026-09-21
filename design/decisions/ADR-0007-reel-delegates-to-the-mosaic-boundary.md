# ADR-0007: Reel plans; Mosaic's MCP boundary validates and executes — Reel is an untrusted planner behind Mosaic's validating relay

- **Status:** Accepted
- **Date:** 2026-09-11
- **Deciders:** labadorf, design session (recommended resolution — records the Reel side of Mosaic ADR-0009 (Accepted) and ADR-0010 (Proposed))
- **Related:** ADR-0005 (headless core — the "agent surface" and seam-1 bullets), ADR-0006 (v1 State is the QuerySpec), ADR-0008 (Exon seeds Reel — the prototype already sits in this position); **Mosaic ADR-0009** (Mosaic hosts an MCP boundary over a server-derived capability manifest and the QuerySpec artifact; rejects hosting the validator/executor in a planner), **Mosaic ADR-0010** (the boundary may delegate outbound to a planning service, as an untrusted planner behind a validating relay — "any future outbound delegate on this surface (a Reel engine, another planner) inherits items 1–7"), Mosaic `sec8` (inbound auth); **Aperture ADR-0032** (rejects a dedicated control-plane service — why the browser reaches a planner only through Mosaic), Aperture ADR-0009 (headless dry-run validation), Aperture ADR-0021 (agent-first surface); DataHelix platform ADR-0006 (authenticating proxy), `sec6_security_model.md` (Bridge as sole PEP/PDP)

## Context

Reel's model requires that every instruction be **dry-run-validated before it applies**
(ADR-0001, citing Aperture ADR-0009), and `prefab/data-stories.md` calls that validation "the
keystone guardrail." The open question was *who hosts the validator and the executor*. Three
places were possible: inside Reel (the planner validates its own output), inside the shell, or
inside the data runtime.

The platform has since answered this for the prototype, twice:

- **Mosaic ADR-0009** (Accepted 2026-09-01) rejected the original design of hosting the
  validator/executor inside the planner (Exon) because it "requires every future consumer (a Reel
  engine, a generic coding agent) to either route through Exon specifically or reimplement the
  same validator/executor independently." Mosaic hosts the boundary: `mosaic://schema` and
  `mosaic://capabilities` resources; `validate_query_spec`, `execute_query_spec`,
  `count_query_spec`, `facet_query_spec`, `field_range_query_spec`, `search_query_spec` tools; a
  `construct-query-spec` prompt; read-only, no mutation tool.
- **Mosaic ADR-0010** (Proposed 2026-09-08; implemented as `converse_query_spec`) let that
  boundary **delegate outbound** to a configured planning service on seven terms: configured-or-
  absent; the planner is untrusted and Mosaic re-validates *every* QuerySpec in the response
  in-process; strict response-shape validation; every failure is a structured `error` turn;
  client-visible failures name the role not the address; it never executes; the wire contract is
  owned by the planner's repo, not Mosaic. It states that a Reel engine inherits these terms.

Aperture, meanwhile, has no backend of its own (Aperture ADR-0032), so a browser shell can reach
a planner only *through* Mosaic. The topology that exists today is therefore
**Aperture → Mosaic (MCP) → planner (HTTP) → Mosaic (validate)**, with the planner being Exon.

The question for Reel: does it accept this position — planner only, behind Mosaic's relay — or
does it own validation/execution as the "headless core" (ADR-0005) might suggest?

## Decision

**Reel will be a planner and composer only. It never validates or executes a query on its own
authority; Mosaic's MCP boundary does both, and Reel sits behind Mosaic's validating relay on
Mosaic ADR-0010's terms.** Concretely:

1. **Reel never carries its own query validator or executor.** Every candidate `QuerySpec` a Reel
   instruction elaborates is checked via Mosaic's `validate_query_spec` (as an MCP client, inside
   Reel's own retry loop — the actionable per-criterion errors are the model's self-correction
   signal), and Reel treats Mosaic's in-process re-validation of its response as authoritative.
   "Dry-run-validatable" (ADR-0001) is satisfied by the *platform's* validator, not a Reel copy.
2. **Reel never decides to execute.** A validated `proposal` is handed back; fetching results is
   the caller's explicit `execute_query_spec` (or the shell's existing data path). Reel's output
   is instructions, States, and — later — View Contract instances bound to results the caller
   fetched or that Reel fetched *through the same boundary* on the caller's explicit request.
3. **Reel is reachable server-to-server, configured-or-absent.** Reel exposes an HTTP turn
   endpoint; Mosaic's relay is configured with its URL and calls out. A deployment without Reel
   configured advertises no Reel capability. Reel holds the LLM provider credentials; Mosaic
   and the browser never do.
4. **Reel inherits Mosaic ADR-0010 items 1–7 as obligations on its response contract:** strict,
   discriminated turn envelopes; absent-vs-empty state kept distinguishable; failures as
   structured turns; no endpoint addresses in client-visible text.
5. **Reel stays auth-unaware (ADR-0005 seam 1)** — but the follow-ups Mosaic ADR-0010 assigns
   to "the planner's repo" (E1 authenticate the turn endpoint with a shared secret or
   Bridge-issued token; E2/E3 per-turn cost/usage logged against the propagated actor) are
   Reel's to implement once it hosts the planner. Until Bridge verifies identity, any actor Reel
   receives is unverified provenance, never authentication.

## Consequences

- **The "headless core" is narrower than ADR-0005 sketched.** ADR-0005 listed "view-description
  / View Contract types + headless validators" and "the agent surface (MCP/API)" as core-owned.
  Post-split: the *query* validator is Mosaic's; the View Contract validator is the platform
  spec's; the MCP surface is Mosaic's. Reel's core is the instruction-path engine (reduction,
  topology, watermark, recompute-with-suspend, content addressing) and the elaboration loop
  (NL → ops → QuerySpec, with validation feedback). Nothing is lost: "headless" and "no
  interaction logic in the shell" still hold.
- **One validator, three consumers.** Aperture's builder, a generic MCP client, and Reel all
  converge on correct queries through the same `validate → read error → fix → retry` loop, so
  a validator fix reaches Reel without a Reel release.
- **Reel's reliability problem is faithfulness, not validity** — the boundary guarantees shape
  and legality; nothing guarantees the artifact means what the user said. That is Reel's
  problem to measure (the prototype's harness) and to mitigate (value-vocabulary grounding,
  routing counting questions to counting tools, treating an empty `RelatedCondition.criteria`
  as a dropped constraint). See `../../proposals/exon-migration.md`.
- **A future Reel-native MCP surface is not precluded** (e.g. story-level tools: replay, rewind,
  fork) — but query validation/execution would still be Mosaic's; Reel would call it, not clone
  it.
- **Reciprocal references:** Mosaic ADR-0009 and ADR-0010 already name "a Reel engine"; this
  ADR is the Reel-side record. Aperture ADR-0032/0035 need no change.

## Alternatives considered

- **Reel hosts its own validator/executor (the original Exon design, `add-exon-mcp-boundary`).**
  Rejected by Mosaic ADR-0009 for exactly the reason that matters to Reel: it makes Reel *the*
  path every agent must route through and duplicates Mosaic's capability logic in a second repo
  that must track it. Superseded before Reel had code.
- **Aperture calls Reel directly from the browser.** Rejected: Aperture has no backend (Aperture
  ADR-0032), so this would put LLM credentials and orchestration in the browser and give the
  shell a second, non-uniform call surface.
- **Mosaic imports Reel in-process.** Rejected by Mosaic ADR-0010: it drags `litellm` and
  provider credentials into `datahelix-mosaic`, a generic runtime.
- **Reel validates and Mosaic trusts it (no re-validation).** Rejected: makes Mosaic's central
  guarantee ("Mosaic validates before anything executes") a property of Reel's release cycle;
  Mosaic ADR-0010 term 2 exists to prevent it.

## Notes / open sub-questions

- Mosaic ADR-0010 is itself `Proposed`; this ADR should not flip to `Accepted` before it does.
- Actor propagation across the hop (Mosaic ADR-0010 Consequences; Mosaic sec8 §8.6) needs a wire
  field the planner's contract does not yet carry — an amendment to the contract Reel will own
  after migration (ADR-0008).
- Transport for the relay → Reel hop is plain HTTP/JSON today; whether Reel should *also* be an
  MCP server (so a coding agent can drive stories without the relay) is open.

## Ratification

Ratified 2026-09-21, after Mosaic ADR-0010 (its precondition: this ADR must not lead the Mosaic-side terms it records). The arrangement runs: the prototype proposes, Mosaic re-validates in-process, and nothing executes without an explicit user action -- verified end to end through a browser on 2026-09-21.
