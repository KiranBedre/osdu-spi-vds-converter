import json
import requests
import os
import argparse


class RegisterDag:

    def __init__(self, file_path):
        self.token = os.environ.get('BEARER_TOKEN')
        self.data_partition_id = os.environ.get('SHARED_TENANT')
        self.workflow_service_url = os.environ.get('WORKFLOW_URL')
        self.docker_image = os.environ.get('DAG_TASK_IMAGE')
        self.dns_host_name = os.environ.get('AZURE_DNS_NAME')
        self.namespace = os.environ.get('NAMESPACE')
        self.file_path = file_path
        self.service_name = self.docker_image[self.docker_image.index("/") + 1: self.docker_image.index(":")]
        self.build_version = self.docker_image[self.docker_image.index(":") + 1:]
        self.dag_name = f"{self.service_name}-{self.build_version}"
        self.dag_name = f"segy-to-zgy-conversion-{self.build_version}"
        self.env_vars = {
            "storage_service_endpoint": f"https://{self.dns_host_name}/api/storage/v2",
            "schema_service_endpoint": f"https://{self.dns_host_name}/api/schema-service/v1",
            "search_service_endpoint": f"https://{self.dns_host_name}/api/search/v2",
            "partition_service_endpoint": f"https://{self.dns_host_name}/api/partition/v1",
            "unit_service_endpoint": f"https://{self.dns_host_name}/api/unit/v2/unit/symbol",
            "file_service_endpoint": f"https://{self.dns_host_name}/api/file/v2",
            "AZURE_TENANT_ID": "{{ var.value.azure_tenant_id }}",
            "AZURE_CLIENT_ID": "{{ var.value.azure_client_id }}",
            "AZURE_CLIENT_SECRET": "{{ var.value.azure_client_secret }}",
            "aad_client_id": "{{ var.value.aad_client_id }}",
            "KEYVAULT_URI": "{{ var.value.keyvault_uri }}",
            "appinsights_key": "{{ var.value.appinsights_key }}"
        }

        print(f"data_partition_id: {self.data_partition_id}")
        print(f"workflow_service_url: {self.workflow_service_url}")
        print(f"docker_image: {self.docker_image}")
        print(f"file_path: {self.file_path}")
        print(f"service_name: {self.service_name}")
        print(f"build_version: {self.build_version}")
        print(f"dag_name: {self.dag_name}")

    def register(self):
        dag = self.read_dag_and_replace_placeholders()
        self.register_dag(dag)

    def read_dag_and_replace_placeholders(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            data = data.replace("DAG_NAME_PLACEHOLDER", self.dag_name)
            data = data.replace("DOCKER_IMAGE_PLACEHOLDER", self.docker_image)
            data = data.replace("DNS_HOST_PLACEHOLDER", self.dns_host_name)
            data = data.replace("NAMESPACE_PLACEHOLDER", self.namespace)
            data = data.replace("ENV_VARS_PLACEHOLDER", json.dumps(self.env_vars, indent=4))
            return data

    def register_dag(self, dag):
        data = json.dumps({
              "description": self.service_name,
              "registrationInstructions": {
                "dagName": self.dag_name,
                "dagContent": dag
              },
              "workflowName": self.dag_name
            })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'data-partition-id': self.data_partition_id,
            'correlation-id': self.service_name
        }

        response = requests.post(self.workflow_service_url, headers=headers, data=data)
        if response.status_code == 200 or response.status_code == 409: #needs to be registered only once as per discussion with team
            workflow_id = response.json().get('workflowId')
            print("DAG registered with workflowId: {0}".format(workflow_id))
        else:
            print("Error while registering DAG {0}".format(response.text))
            exit(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Register python dag file to the workflow service.")

    parser.add_argument('-f', type=str,
                        help='The path to the load python dag file.',
                        default=None)

    arguments = parser.parse_args()

    if arguments.f is not None:
        file_path = arguments.f

    RegisterDag(file_path).register()
