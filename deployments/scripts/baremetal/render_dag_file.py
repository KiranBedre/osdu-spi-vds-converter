import argparse
import os
import pathlib
from dag_version_creation.dag_version_creation import DAGVersionGenerator
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List


class DAGFileRenderer:

    def __init__(self, file_path):
        self.file_path = file_path
        self.docker_image = "{{ var.value.image__segy_to_vds_converter }}"
        # As for 25 FEB 2022, there is no namespace parameter in template_fields (https://github.com/apache/airflow/blob/2.2.0/airflow/providers/cncf/kubernetes/operators/kubernetes_pod.py#L165), 
        # so we have to hardcode this value for now.
        self.namespace = "default"
        self.sd_svc_url = "{{ var.value.core__service__seismic__url }}"
        self.dag_name = "Segy_to_vds_conversion_sdms"

    def _get_resources(self):
        return """k8s_models.V1ResourceRequirements(
                limits={
                    "memory": airflow.models.Variable.get("vds_ingestion__limit__memory", default_var="8Gi"),
                    "cpu": airflow.models.Variable.get("vds_ingestion__limit__cpu", default_var="1000m")
                },
                requests={
                    "memory": airflow.models.Variable.get("vds_ingestion__request__memory", default_var="2Gi"),
                    "cpu": airflow.models.Variable.get("vds_ingestion__request__cpu", default_var="200m")
                }
            )"""

    def _prepare_operator_kwargs(self) -> Dict:
        return f"""{{
            "container_resources": {self._get_resources()},
            "startup_timeout_seconds": 300, 
            "annotations": {{
                "sidecar.istio.io/inject": "false"
            }}
        }}"""

    def _prepare_extra_env_vars(self) -> Dict:
        return """{
            "S3_ENDPOINT_OVERRIDE": "{{ var.value.core__service__minio__url }}"
        }"""

    def _add_k8s_import(self, dag_file: str) -> str:
        dag_file = "import airflow\n" + dag_file
        first_import_idx = dag_file.find("import airflow")
        import_stmt = "\nfrom kubernetes.client import models as k8s_models\n"
        dag_file = dag_file[:first_import_idx] + import_stmt + dag_file[first_import_idx:]
        return dag_file

    def _render_template(self, file) -> str:
        env = Environment(
            loader=FileSystemLoader(searchpath=os.getenv("GC_DAG_DIRECTORY", default="src/dags")),
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

        rendered_file_data = template.render(**params)
        rendered_file_data = self._add_k8s_import(rendered_file_data)

        return rendered_file_data

    def render(self, output_path=None):
        print(f"Start {self.file_path} file rendering")

        output_path = output_path or self.file_path
        with open(self.file_path, "r") as f:
            rendered_file_data = self._render_template(f)

        rendered_file_data = DAGVersionGenerator(
            rendered_file_data
        ).add_dag_version()

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
