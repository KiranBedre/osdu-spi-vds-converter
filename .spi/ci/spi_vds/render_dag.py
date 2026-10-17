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
    "node_selector": {"spi-pool": "osdu"},
    "tolerations": [
        k8s.V1Toleration(
            key="workload", operator="Equal", value="osdu", effect="NoSchedule"
        ),
        k8s.V1Toleration(
            key="kubernetes.azure.com/scalesetpriority",
            operator="Equal",
            value="spot",
            effect="NoSchedule",
        ),
    ],
    "security_context": k8s.V1PodSecurityContext(
        run_as_non_root=True,
        seccomp_profile=k8s.V1SeccompProfile(type="RuntimeDefault"),
    ),
    "container_security_context": k8s.V1SecurityContext(
        allow_privilege_escalation=False,
        capabilities=k8s.V1Capabilities(drop=["ALL"]),
    ),
    "container_resources": k8s.V1ResourceRequirements(
        requests={"cpu": "500m", "memory": "1Gi"},
        limits={"cpu": "2", "memory": "4Gi"},
    ),
    "startup_timeout_seconds": 300,
}""",
    "{| SEISMIC_STORE_URL |}": "{{ var.value.core__service__seismic__url }}",
    "{| EXTRA_ENV_VARS|default('{}') |}": "{}",
    "from airflow.models import Variable": (
        "from airflow.models import Variable\n"
        "from kubernetes.client import models as k8s"
    ),
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
