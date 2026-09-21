"""Measuring whether discovery actually works.

Separate from the reliability harness that arrives at Phase B-harness: that one
grades the retired plan emitter and is gated on being re-based. This grades the
capability Reel exists for, and can therefore be built now.

What it asserts is fixed by the goal statement, not chosen:

    "...ask questions about the classes and slots available FOR THE PURPOSE OF
    identifying the specific data elements they wish to include in a query. The
    response is only useful for constructing a query spec that pulls back
    specific fields."

So the unit of success is **which slots the turn named** — not prose quality,
not row counts, not a table of field metadata. A discovery answer that reads
beautifully and names the wrong field has failed; one that is terse and names
the right field has not.
"""
from .discovery import (  # noqa: F401
    DiscoveryCase,
    DiscoveryOutcome,
    grade_turn,
    load_cases,
    slots_in_schema,
)
