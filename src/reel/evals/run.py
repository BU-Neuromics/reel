"""`python -m reel.evals.run` — score a discovery case set against a live schema.

Deliberately NOT part of `pytest tests/`. Every case spends a model
invocation, so folding it into the unit suite would make CI slow, costly and
dependent on provider credentials. The unit suite proves the grader; this
proves the planner.

    MOSAIC_MCP_URL=http://localhost:8099/mcp \\
    REEL_EVAL_CASES=../mosaic-demo-small/evals/discovery.yaml \\
        python -m reel.evals.run

Each case runs `--samples` times (default 3) because model behaviour is a
distribution: a single run cannot tell a broken prompt from an unlucky one. A
case counts as passing only when EVERY run passes -- 2 of 3 is a coin flip the
next prompt edit may tip, and calling it green hides that.

Exit status is the number of unreliable cases, capped at 125, so this is usable
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
    ap.add_argument(
        "-n", "--samples", type=int, default=3,
        help="runs per case (default 3). Model behaviour is a DISTRIBUTION -- a single "
             "run cannot tell a broken prompt from an unlucky one, and will report both "
             "kinds of noise as a regression.",
    )
    ap.add_argument("--model", default=None, help=f"override the planner model (default {MODEL})")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every turn's message")
    args = ap.parse_args(argv)

    from ..planner.boundary import fetch_capabilities, mcp_url
    from ..story.turn import request_turn

    cases = load_cases(args.cases)
    print(f"grounding from {mcp_url()} ...", file=sys.stderr)
    capabilities = fetch_capabilities()
    print(f"{len(cases)} case(s), {len(capabilities)} entity type(s), model {args.model or MODEL}\n")

    n = max(1, args.samples)
    unreliable = []
    for case in cases:
        passes, details, errors = 0, [], 0
        for _ in range(n):
            attempt = request_turn(case.utterance, capabilities, model=args.model)
            if attempt.error or attempt.turn is None:
                # A transport or parse failure is an environment problem, not a
                # discovery failure. Counted separately so a flaky provider never
                # reads as the planner getting worse.
                errors += 1
                continue
            outcome = grade_turn(case, attempt.turn, capabilities)
            if outcome.passed:
                passes += 1
            else:
                details.append((outcome.detail, attempt.turn.get("message") or ""))

        scored = n - errors
        # Anything short of every run is worth seeing. A case that passes 2 of 3
        # is not "passing" -- it is a coin flip the next prompt edit may tip.
        mark = "pass" if scored and passes == scored else "FAIL"
        rate = f"{passes}/{scored}" if scored else "0/0"
        print(f"  {mark} {case.id}  [{rate}]  {case.utterance}")
        if errors:
            print(f"        {errors} run(s) errored — environment, not scored")
        for detail, message in details[:2]:
            print(f"        {detail}")
            if args.verbose:
                print(f"        > {' '.join(message.split())[:300]}")
        if mark == "FAIL":
            unreliable.append(f"{case.id} ({rate})")

    print(f"\n{len(cases) - len(unreliable)}/{len(cases)} cases passed every run (n={n})")
    if unreliable:
        print(f"not reliable: {', '.join(unreliable)}")
    return min(len(unreliable), 125)


if __name__ == "__main__":
    raise SystemExit(main())
