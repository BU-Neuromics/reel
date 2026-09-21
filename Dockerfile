# Reel — the planning service Mosaic's relay delegates to.
#
# Runs the turn endpoint only. Reel plans; it never validates and never executes
# (ADR-0007) — Mosaic's boundary does both, and re-validates everything this
# service returns before any caller sees it.
#
# Build:
#   docker build -t ghcr.io/bu-neuromics/reel:dev .
#
# Run (needs a reachable Mosaic serving --mcp, and model credentials):
#   docker run --rm -p 9100:9100 \
#     -e MOSAIC_MCP_URL=http://mosaic:8001/mcp \
#     -e AWS_REGION -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
#     ghcr.io/bu-neuromics/reel:dev
#
# Then point Mosaic back at it: MOSAIC_EXON_URL=http://reel:9100/turn
# (renamed MOSAIC_REEL_URL at migration Phase C2, old name kept as an alias).

FROM python:3.12-slim

# Capability grounding is fetched from Mosaic at startup and the service exits 3
# if it cannot reach it — so this image is useless without a Mosaic to point at,
# by design. A planner with no grounding would accept turns and fail every one,
# which is strictly worse than not starting.

WORKDIR /app

# Dependency layer first: the source changes far more often than the deps do,
# so this keeps rebuilds cheap during the migration.
COPY pyproject.toml README.md ./
COPY src/reel/__init__.py ./src/reel/__init__.py
RUN pip install --no-cache-dir . && pip uninstall -y datahelix-reel

COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps .

# Not root. The image carries no state and writes nothing, so there is no
# volume-ownership problem to trade against this.
RUN useradd --create-home --uid 10001 reel
USER reel

# Carries NO schema, NO generated data and NO evaluation cases. Those belong to
# the deployment being described, not to the planner planning against it; a
# planner that vendored them could only ever plan for one project. The schema it
# plans against arrives at runtime, from Mosaic's capability manifest.

EXPOSE 9100
ENV REEL_TURN_HOST=0.0.0.0 \
    REEL_TURN_PORT=9100

ENTRYPOINT ["python", "-m", "reel.serve.http"]
