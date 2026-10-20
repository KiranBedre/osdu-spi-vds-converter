#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

export PYTHONPATH="$repo_root/.spi/ci${PYTHONPATH:+:$PYTHONPATH}"

python -m spi_vds.render_dag \
  --source src/dags/segy_to_vds_ssdms_conversion_dag.py \
  --output .spi/generated/segy_to_vds_ssdms_conversion_dag.py

python -m spi_vds.build_artifact \
  --dag .spi/generated/segy_to_vds_ssdms_conversion_dag.py \
  --output .spi/artifacts

python -m ruff check --line-length 100 .spi/ci/spi_vds .spi/tests
node --test .spi/tests/*.test.mjs
python -m pytest .spi/tests \
  --junitxml "$SPI_TEST_REPORT" \
  --cov spi_vds \
  --cov-report "xml:$SPI_COVERAGE_FILE" \
  --cov-fail-under 90
