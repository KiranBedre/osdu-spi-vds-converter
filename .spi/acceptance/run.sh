#!/usr/bin/env sh

set -eu

acceptance_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

exec node "$acceptance_dir/workflow-smoke.mjs" "$@"
