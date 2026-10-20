import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from spi_vds.build_artifact import DAG_NAME, WORKFLOW_REQUEST, build_artifact, main


def test_build_artifact_is_deterministic_and_complete(tmp_path: Path) -> None:
    dag = tmp_path / "segy_to_vds.py"
    dag.write_text("DAG_ID = 'segy-to-vds-conversion'\n", encoding="utf-8")
    output = tmp_path / "artifact"

    build_artifact(dag, output)
    first_zip = (output / "dag.zip").read_bytes()
    build_artifact(dag, output)

    assert (output / "dag.zip").read_bytes() == first_zip
    with ZipFile(output / "dag.zip") as archive:
        assert archive.namelist() == [dag.name]
        assert archive.read(dag.name) == dag.read_bytes()

    digest = hashlib.sha256(first_zip).hexdigest()
    assert (output / "dag.zip.sha256").read_text(encoding="utf-8") == (f"{digest}  dag.zip\n")
    assert json.loads((output / "workflow.json").read_text(encoding="utf-8")) == (WORKFLOW_REQUEST)
    assert WORKFLOW_REQUEST[0]["workflowName"] == DAG_NAME
    assert WORKFLOW_REQUEST[0]["registrationInstructions"]["dagName"] == DAG_NAME


def test_main_builds_the_requested_artifact(tmp_path: Path, monkeypatch) -> None:
    dag = tmp_path / "dag.py"
    dag.write_text("pass\n", encoding="utf-8")
    output = tmp_path / "artifact"
    monkeypatch.setattr(
        "sys.argv",
        ["build-artifact", "--dag", str(dag), "--output", str(output)],
    )

    assert main() == 0
    assert {path.name for path in output.iterdir()} == {
        "dag.zip",
        "dag.zip.sha256",
        "workflow.json",
    }
