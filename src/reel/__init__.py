"""Reel — the data-story engine.

Plans a typed `QuerySpec` from natural language, conversationally, behind
Mosaic's validating relay (Mosaic ADR-0009/0010). Reel never executes a query
and never decides to: it proposes, the boundary validates, and a person acts.

Seeded by migrating Exon rather than rewriting it (ADR-0008) — the turn contract
is the v1 wire form of `Instruction` (ADR-0001), and the shape does not change
at migration. See `proposals/exon-migration.md`.

Layout (platform ADR-0002: distribution `datahelix-reel`, bare import `reel`):

    reel.planner   the QuerySpec emitter, its capability grounding, the MCP
                   client to Mosaic's boundary
    reel.story     one stateless turn, and the turn-list bookkeeping over it
    reel.serve     the relay-facing HTTP endpoint
    reel.harness   the reliability suite (arrives at Phase B-harness, gated on
                   mosaic-demo-small task 2.5)
"""

__version__ = "0.0.0"

#: Where `reel.harness` looks for a case set (Phase A6). A case set is
#: domain-bearing — it belongs to the deployment being described, not to the
#: planner — so Reel reads one by path rather than vendoring a copy. Two copies
#: of a case set are two answers to the same question, and the one that is not
#: regenerated becomes wrong silently.
#:
#: Registered here now; consumed at Phase B-harness.
EVAL_CASES_ENV = "REEL_EVAL_CASES"

#: Where the ground-truth tests look for a LinkML schema to build a capability
#: manifest from. Same principle as :data:`EVAL_CASES_ENV`: a schema belongs to
#: the deployment being described, so Reel reads one by path rather than
#: vendoring a copy. Unset, those tests skip — `pytest tests/` stays green in a
#: checkout that carries no fixtures, which is every checkout of this repo.
TEST_SCHEMA_ENV = "REEL_TEST_SCHEMA"
