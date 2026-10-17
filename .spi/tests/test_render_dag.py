from pathlib import Path

import pytest

from spi_vds.render_dag import REPLACEMENTS, main, render_dag, render_file


REPO_ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_DAG = REPO_ROOT / "src/dags/segy_to_vds_ssdms_conversion_dag.py"


def test_render_upstream_dag(tmp_path: Path) -> None:
    output = tmp_path / "rendered.py"

    render_file(UPSTREAM_DAG, output)

    rendered = output.read_text(encoding="utf-8")
    assert 'dag_name = "segy-to-vds-conversion"' in rendered
    assert "{{ var.value.openvds_ingestion_image }}" in rendered
    assert 'k8s_namespace = "platform"' in rendered
    assert '"azure.workload.identity/use": "true"' in rendered
    assert '"service_account_name": "workload-identity-sa"' in rendered
    assert "AZURE_CLIENT_SECRET" not in rendered
    assert "{|" not in rendered


def test_render_rejects_missing_contract_token() -> None:
    token = next(iter(REPLACEMENTS))
    source = UPSTREAM_DAG.read_text(encoding="utf-8").replace(token, "")

    with pytest.raises(ValueError, match="Expected one occurrence"):
        render_dag(source)


def test_render_rejects_unknown_template_token() -> None:
    source = UPSTREAM_DAG.read_text(encoding="utf-8") + "\n{| UNKNOWN |}\n"

    with pytest.raises(ValueError, match="Unresolved DAG template tokens"):
        render_dag(source)


def test_main_renders_requested_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "rendered.py"
    monkeypatch.setattr(
        "sys.argv",
        [
            "render-dag",
            "--source",
            str(UPSTREAM_DAG),
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    assert output.is_file()
