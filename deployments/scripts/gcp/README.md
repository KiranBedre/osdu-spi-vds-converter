## GCP: DAG FILE RENDERING

```bash
# Install requirements
pip install Jinja2==2.10.1

# Setup Variables
export K8S_NAMESPACE="<your_k8s_namespace>"  # ie: default
export SEGY_VDS_DOCKER_IMAGE="<image_tag>"
export K8S_NODE_POOLS=<node_pools>  # i.e. pool-1,pool-2  the value will be split by comma
export SD_SVC_URL=<ssdms_host>  # i.e https://<ssdms_host>/seistore-svc/api/v3

OSDU_GCP_DEPLOYMENTS_SUBDIR="<path_to_folder>" # ie: path to GCP deployment scripts folder
OSDU_GCP_DAG_DIRECTORY="<path_to_folder>" # ie: segy-to-vds-conversion/airflow/workflow-svc-v2

OUTPUT_FILE="<path_to_output_file>" # ie. to avoid original file overwriting

chmod +x bootstrap.sh
./bootstrap.sh
```

Workflow Payload Example:

{
    "executionContext": {
        "Payload": {
            "AppKey": "<some-app-key>",
            "data-partition-id": "<data-partition-id>"
        },
        "vds_url": "sd://<tenant>/<subproject>/<path>",
        "segy_url": "sd://<tenant>/<subproject>/<path>/<filename>",
        "persistent_id": "<string>",
        "id_token": "<id_token>"
    }
}
