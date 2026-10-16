#!/usr/bin/env sh

set -eu

spi_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
export PYTHONPATH="$spi_root/ci${PYTHONPATH:+:$PYTHONPATH}"

exec python3 -m spi_vds.workflow_smoke "$@"
