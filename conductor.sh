#!/usr/bin/env bash
# Legacy compatibility entry point. Use the dev helper for the primary interface.
set -Eeuo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
CONDUCTOR="$SCRIPT_DIR/.venv/bin/conductor"

if [[ ! -x "$CONDUCTOR" ]]; then
  printf 'conductor: installed CLI is unavailable; run ./dev setup first\n' >&2
  exit 1
fi

exec "$CONDUCTOR" "$@"
