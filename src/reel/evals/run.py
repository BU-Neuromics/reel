"""`python -m reel.evals.run` — score a discovery case set against a live schema.

Deliberately NOT part of `pytest tests/`. Every case spends a model
invocation, so folding it into the unit suite would make CI slow, costly and
dependent on provider credentials. The unit suite proves the grader; this
proves the planner.

    MOSAIC_MCP_URL=http://localhost:8099/mcp \\
    REEL_EVAL_CASES=../mosaic-demo-small/evals/discovery.yaml \\
        python -m reel.evals.run

Exit status is the number of failing cases, capped at 125, so this is usable
as a gate without parsing the output.
"""
from __future__ import annotations

import argparse
import sys

from ..config import MODEL
from .discovery import grade_turn, load_cases


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="reel.evals.run", description=__doc__)
    ap.add_argument("--cases", default=None, help="path to a case set (else REEL_EVAL_CASES)")
    ap.add_argument("--model", default=None, help=f"override the planner model (default {MODEL})")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every turn's message")
    args = ap.parse_args(argv)

    from ..planner.boundary import fetch_capabilities, mcp_url
    from ..story.turn import request_turn

    cases = load_cases(args.cases)
    print(f"grounding from {mcp_url()} ...", file=sys.stderr)
    capabilities = fetch_capabilities()
    print(f"{len(cases)} case(s), {len(capabilities)} entity type(s), model {args.model or MODEL}\n")

    failures = []
    for case in cases:
        attempt = request_turn(case.utterance, capabilities, model=args.model)
        if attempt.error or attempt.turn is None:
            # A transport or parse failure is an environment problem, not a
            # discovery failure. Reported as such rather than scored, so a flaky
            # provider never reads as the planner getting worse.
            print(f"  ERROR {case.id}: {attempt.error or 'no turn produced'}")
            failures.append(case.id)
            continue

        outcome = grade_turn(case, attempt.turn, capabilities)
        mark = "pass" if outcome.passed else "FAIL"
        print(f"  {mark} {case.id}  [{outcome.status}]  {case.utterance}")
        if outcome.named:
            print(f"        named: {', '.join(sorted(outcome.named))}")
        if not outcome.passed:
            print(f"        {outcome.detail}")
            failures.append(case.id)
        if args.verbose:
            print(f"        > {' '.join((attempt.turn.get('message') or '').split())[:300]}")

    print(f"\n{len(cases) - len(failures)}/{len(cases)} passed")
    if failures:
        print(f"failing: {', '.join(failures)}")
    return min(len(failures), 125)


if __name__ == "__main__":
    raise SystemExit(main())
