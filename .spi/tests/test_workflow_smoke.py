import io
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

import pytest

from spi_vds.workflow_smoke import WorkflowCheck, get_workflow, main


class Response:
    status = 200

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"workflowName":"segy-to-vds-conversion"}'


def test_get_workflow_sends_required_headers() -> None:
    config = WorkflowCheck(
        workflow_url="https://example.test/api/workflow/v1",
        partition="opendes",
        token="token",
        workflow_name="segy-to-vds-conversion",
    )

    with patch("spi_vds.workflow_smoke.urlopen", return_value=Response()) as request:
        payload = get_workflow(config)

    assert payload["workflowName"] == "segy-to-vds-conversion"
    sent_request = request.call_args.args[0]
    assert sent_request.full_url.endswith("/workflow/segy-to-vds-conversion")
    assert sent_request.get_header("Authorization") == "Bearer token"
    assert sent_request.get_header("Data-partition-id") == "opendes"


def test_main_writes_failure_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = tmp_path / "workflow.xml"
    monkeypatch.setattr(
        "sys.argv",
        [
            "workflow-smoke",
            "--workflow-url",
            "https://example.test/api/workflow/v1",
            "--partition",
            "opendes",
            "--token",
            "token",
            "--workflow-name",
            "segy-to-vds-conversion",
            "--report",
            str(report),
        ],
    )
    error = HTTPError("https://example.test", 404, "Not Found", {}, io.BytesIO())

    with patch("spi_vds.workflow_smoke.urlopen", side_effect=error):
        result = main()

    assert result == 1
    suite = ET.parse(report).getroot()
    assert suite.attrib["failures"] == "1"


def test_main_writes_success_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = tmp_path / "workflow.xml"
    monkeypatch.setattr(
        "sys.argv",
        [
            "workflow-smoke",
            "--workflow-url",
            "https://example.test/api/workflow/v1",
            "--partition",
            "opendes",
            "--token",
            "token",
            "--workflow-name",
            "segy-to-vds-conversion",
            "--report",
            str(report),
        ],
    )

    with patch("spi_vds.workflow_smoke.urlopen", return_value=Response()):
        result = main()

    assert result == 0
    suite = ET.parse(report).getroot()
    assert suite.attrib["failures"] == "0"
