import hashlib
import json
from argparse import ArgumentParser
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

DAG_NAME = "segy-to-vds-conversion"
WORKFLOW_REQUEST = [
    {
        "workflowName": DAG_NAME,
        "description": "VDSConverter",
        "registrationInstructions": {"dagName": DAG_NAME},
    }
]


def build_artifact(dag: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    dag_zip = output / "dag.zip"
    member = ZipInfo(dag.name, date_time=(1980, 1, 1, 0, 0, 0))
    member.compress_type = ZIP_DEFLATED
    member.external_attr = 0o100644 << 16
    with ZipFile(dag_zip, "w") as archive:
        archive.writestr(member, dag.read_bytes())

    digest = hashlib.sha256(dag_zip.read_bytes()).hexdigest()
    (output / "dag.zip.sha256").write_text(
        f"{digest}  dag.zip\n",
        encoding="utf-8",
    )
    (output / "workflow.json").write_text(
        json.dumps(WORKFLOW_REQUEST, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = ArgumentParser(description="Build the VDS OCI DAG artifact payload")
    parser.add_argument("--dag", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_artifact(args.dag, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
