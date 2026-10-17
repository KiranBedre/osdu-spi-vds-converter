from argparse import ArgumentParser
from pathlib import Path
import re


REPLACEMENTS = {
    "{| DAG_NAME |}": "segy-to-vds-conversion",
    "{| DOCKER_IMAGE |}": "{{ var.value.openvds_ingestion_image }}",
    "{| K8S_NAMESPACE |}": "platform",
    "{| K8S_POD_KWARGS |}": """{
    "annotations": {"sidecar.istio.io/inject": "false"},
    "labels": {"azure.workload.identity/use": "true"},
    "service_account_name": "workload-identity-sa",
    "startup_timeout_seconds": 300,
}""",
    "{| SEISMIC_STORE_URL |}": "{{ var.value.core__service__seismic__url }}",
    "{| EXTRA_ENV_VARS|default('{}') |}": "{}",
}
UNRESOLVED_TOKEN = re.compile(r"\{\|.*?\|\}")


def render_dag(source: str) -> str:
    rendered = source
    for token, value in REPLACEMENTS.items():
        occurrences = rendered.count(token)
        if occurrences != 1:
            raise ValueError(f"Expected one occurrence of {token!r}, found {occurrences}")
        rendered = rendered.replace(token, value)

    unresolved = sorted(set(UNRESOLVED_TOKEN.findall(rendered)))
    if unresolved:
        raise ValueError(f"Unresolved DAG template tokens: {', '.join(unresolved)}")
    return rendered


def render_file(source: Path, output: Path) -> None:
    rendered = render_dag(source.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = ArgumentParser(description="Render the upstream VDS DAG for Azure SPI")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render_file(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
