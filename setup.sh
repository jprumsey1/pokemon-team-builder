#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# `run` on a profiled service starts its dependencies (db) and enables the profile itself.
docker compose run --rm --build api alembic upgrade head
docker compose run --rm api python -m app.lib.sync
docker compose down
