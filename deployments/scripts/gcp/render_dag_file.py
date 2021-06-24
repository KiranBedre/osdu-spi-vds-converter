import argparse
import json
import os
from typing import Dict, List


class DAGFileRenderer:

    def __init__(self, file_path):
        self.file_path = file_path
        self.docker_image = os.getenv("SEGY_VDS_DOCKER_IMAGE")
        self.namespace = os.getenv("NAMESPACE")
        self.sd_svc_url = os.getenv("SD_SVC_URL")
        self.dag_name = "Segy_to_vds_conversion_sdms"

    def _get_node_pools(self) -> List:
        pools = os.getenv("K8S_NODE_POOLS")
        return [p.strip() for p in pools.split(",")]

    def _get_resources(self):
        return {
            "request_memory": os.getenv("GCP_VDS_INGESTION_REQUEST_MEMORY", default="4Gi"),
            "request_cpu": os.getenv("GCP_VDS_INGESTION_REQUEST_CPU", default="200m"),
            "limit_memory": os.getenv("GCP_VDS_INGESTION_LIMIT_MEMORY", default="8Gi"),
            "limit_cpu": os.getenv("GCP_VDS_INGESTION_LIMIT_CPU", default="1000m")
        }

    def _prepare_operator_kwargs(self) -> Dict:
        return {
            "affinity": {
                "nodeAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": {
                        "nodeSelectorTerms": [{
                            "matchExpressions": [{
                                "key": "cloud.google.com/gke-nodepool",
                                "operator": "In",
                                "values": self._get_node_pools()
                            }]
                        }]
                    }
                }
            },
            "resources": self._get_resources(),
            "startup_timeout_seconds": os.getenv("GCP_VDS_INGESTION_STARTUP_TIMEOUT", default=300)
        }

    def _populate_settings(self, file_data: str) -> str:
        file_data = file_data.replace("DAG_NAME_PLACEHOLDER", self.dag_name)
        file_data = file_data.replace(
            "DOCKER_IMAGE_PLACEHOLDER", self.docker_image)
        file_data = file_data.replace("K8S_NAMESPACE_PLACEHOLDER", f"{self.namespace}")
        file_data = file_data.replace(f"K8S_POD_KWARGS_PLACEHOLDER",
                                      json.dumps(self._prepare_operator_kwargs(), indent=4))
        file_data = file_data.replace(
            "SEISMIC_STORE_URL_PLACEHOLDER",
            self.sd_svc_url
        )
        return file_data

    def render(self, output_path=None):
        print(f"Start {self.file_path} file rendering")

        output_path = output_path or self.file_path
        with open(self.file_path, "r") as f:
            rendered_file_data = self._populate_settings(f.read())

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
