import argparse
import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List


class DAGFileRenderer:

    def __init__(self, file_path):
        self.file_path = file_path
        self.docker_image = "{{ var.value.anthos__image__segy_to_vds_converter }}"
        # As for 25 FEB 2022, there is no namespace parameter in template_fields (https://github.com/apache/airflow/blob/2.2.0/airflow/providers/cncf/kubernetes/operators/kubernetes_pod.py#L165), 
        # so we have to hardcode this value for now.
        self.namespace = "{{ var.value.anthos__parsers_k8s_namespace }}"
        self.sd_svc_url = "{{ var.value.core__service__seismic__url }}"
        self.dag_name = "Segy_to_vds_conversion_sdms"

    def _get_resources(self):
        return """{
                "request_memory": airflow.models.Variable.get("anthos__vds_ingestion_request_memory", default_var="2Gi"),
                "request_cpu": airflow.models.Variable.get("anthos__vds_ingestion_request_cpu", default_var="200m"),
                "limit_memory": airflow.models.Variable.get("anthos__vds_ingestion_limit_memory", default_var="8Gi"),
                "limit_cpu": airflow.models.Variable.get("anthos__vds_ingestion_limit_cpu", default_var="1000m")
            }"""

    def _prepare_operator_kwargs(self) -> Dict:
        return f"""{{
            "resources": {self._get_resources()},
            "startup_timeout_seconds": 300, 
            "annotations": {{
                "sidecar.istio.io/inject": "false"
            }}
        }}"""

    def _prepare_extra_env_vars(self) -> Dict:
        return """{
            "S3_ENDPOINT_OVERRIDE": "{{ var.value.core__service__minio__url }}"
        }"""

    def _render_template(self, file) -> str:
        env = Environment(
            loader=FileSystemLoader(searchpath=os.getenv("OSDU_GCP_DAG_DIRECTORY", default="src/dags")),
            variable_start_string='{|', variable_end_string='|}',
        )
        template = env.get_template(os.path.basename(file.name))

        params = {
            "DAG_NAME": self.dag_name,
            "DOCKER_IMAGE": self.docker_image,
            "K8S_NAMESPACE": self.namespace,
            "K8S_POD_KWARGS": self._prepare_operator_kwargs(),
            "EXTRA_ENV_VARS": self._prepare_extra_env_vars(),
            "SEISMIC_STORE_URL": self.sd_svc_url,
        }

        return template.render(**params)

    def render(self, output_path=None):
        print(f"Start {self.file_path} file rendering")

        output_path = output_path or self.file_path
        with open(self.file_path, "r") as f:
            rendered_file_data = self._render_template(f)

        with open(output_path, "w") as f:
            f.write(rendered_file_data)

        print(f"Finish {self.file_path} file rendering")
        print(f"Rendered output file: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Render python dag file. Populate required environment settins and parameters.")

    parser.add_argument("-f", type=str,
                        help="The path to the load python dag file.",
                        default=None)

    parser.add_argument("-o", type=str,
                        help="The path to the rendered dag file.",
                        default=None)

    arguments = parser.parse_args()

    file_path = arguments.f
    output_path = arguments.o

    DAGFileRenderer(file_path).render(output_path=output_path)
