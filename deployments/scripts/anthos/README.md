## ANTHOS: DAG FILE RENDERING

```bash
# Install requirements
pip install Jinja2==2.10.1

# Setup Variables
GC_DEPLOYMENTS_SUBDIR="<path_to_folder>" # ie: path to Google Cloud deployment scripts folder
GC_DAG_DIRECTORY="<path_to_folder>" # ie: segy-to-vds-conversion/airflow/workflow-svc-v2

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
