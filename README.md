# OSDU SEG-Y to OpenVDS Conversion DAG for Azure

[![Validate](https://github.com/KiranBedre/osdu-spi-vds-converter/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/KiranBedre/osdu-spi-vds-converter/actions/workflows/validate.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

This repository packages the community
[SEG-Y to OpenVDS conversion DAG](https://community.opengroup.org/osdu/platform/data-flow/ingestion/segy-to-vds-conversion)
for the Azure-native OSDU SPI Stack. The DAG reads SEG-Y metadata from OSDU,
launches `SEGYImport` in a Workload Identity-enabled Kubernetes pod, and writes
the OpenVDS metadata back through OSDU services.

## At a glance

| | |
|---|---|
| Airflow DAG ID | `segy-to-vds-conversion` |
| Airflow runtime | Airflow 3.2.2 on Python 3.12 |
| Conversion runtime | OpenVDS `SEGYImport`, pinned separately by SPI Stack |
| Depends on | Airflow, Workflow, Seismic Store, Storage, Search, Schema, Dataset, Partition |
| Azure authentication | AKS Workload Identity through `platform:workload-identity-sa` |
| Deployed by | [OSDU SPI Stack](https://github.com/Azure/osdu-spi-stack) |

## Repository layout

[CONTRIBUTING.md](CONTRIBUTING.md) explains the fork ownership model.

| Path | Owner | Contents |
|---|---|---|
| `src/`, `openvds.py`, `requirements.txt` | OSDU upstream | Community DAG source and runtime dependencies |
| `.spi/` | This repository | Azure rendering, DAG artifact, tests, and service descriptor |
| `.github/` and `build/` | SPI template | Shared repository automation |

The upstream DAG remains unchanged. `.spi/ci/spi_vds/render_dag.py` resolves its
deployment placeholders for SPI so future upstream syncs remain reviewable.

## Build and test

CI installs the exact Airflow release under the official Python 3.12
constraints, renders the DAG, runs the fork-owned unit tests with at least 90%
coverage, parses the result with Airflow's `DagBag`, and builds the independently
versioned DAG artifact.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python \
  "apache-airflow==3.2.2" \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.2.2/constraints-3.12.txt
uv pip install --python .venv/bin/python \
  --requirement .spi/runtime/requirements.txt \
  --requirement .spi/runtime/requirements-tests.in \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.2.2/constraints-3.12.txt
PATH="$PWD/.venv/bin:$PATH" \
SPI_TEST_REPORT=.spi/results/test-results.xml \
SPI_COVERAGE_FILE=.spi/results/coverage.xml \
  .spi/ci/build.sh
```

The build image uses
`apache/airflow:3.2.2-python3.12@sha256:bbe58e3204d550ab98dbf738a42c0e6663c455357ecd0e2d1440ef9cb6a75f00`
to verify the rendered DAG against the exact dependencies in
`.spi/runtime/requirements.txt`. `osdu-airflow` is pinned to 0.30.7 because
0.30.8 raises its Airflow 3 minimum to 3.3.0.

The Stack does not run that repository image. The shared Airflow runtime is
released separately. This repository publishes
`ghcr.io/kiranbedre/osdu-spi-vds-converter-dag` with:

- `dag.zip`, the rendered `segy-to-vds-conversion` DAG.
- `dag.zip.sha256`, the checksum verified before delivery.
- `workflow.json`, the matching Workflow registration request body.

The OpenVDS conversion image is also released separately and pinned through an
Airflow Variable, so the DAG, task image, and Airflow control plane retain
independent release boundaries.

## Runtime contract

SPI Stack supplies these Airflow Variables:

| Variable | Purpose |
|---|---|
| `openvds_ingestion_image` | Immutable OpenVDS companion image reference |
| `core__service__seismic__url` | In-cluster Seismic Store V3 endpoint |

The conversion pod runs in the `platform` namespace with service account
`workload-identity-sa` and label `azure.workload.identity/use=true`. The Azure
Workload Identity webhook injects its client ID and federated token. No client
secret is stored in the DAG or passed through Airflow Variables.

The pod selects the `osdu` node pool and tolerates its workload and spot
taints. It requests 500m CPU and 1 GiB memory, with limits of 2 CPU and 4 GiB.
The pod runs as non-root with RuntimeDefault seccomp; its container cannot
escalate privileges and drops every Linux capability.

## Acceptance

The source acceptance suite verifies that Workflow service can resolve the
`segy-to-vds-conversion` registration through the gateway. SPI Stack owns the
deployment-level conversion proof because it must pin the DAG and OpenVDS
images together, load the approved SEG-Y sample, and clean up the resulting
records and objects.

## License

Copyright Microsoft Corporation

Licensed under the [Apache License 2.0](LICENSE).
