#  Copyright 2021 Amazon Web Services
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import airflow
from json import dumps
from datetime import timedelta
import os
from airflow import DAG
from osdu_airflow.operators.segy_open_vds_conversion import KubernetesPodSegyToOpenVDSOperator
from osdu_airflow.operators.process_manifest_r3 import ProcessManifestOperatorR3
from airflow import configuration as conf
from osdu_airflow.operators.update_status import UpdateStatusOperator
from osdu_airflow.backward_compatibility.default_args import update_default_args

# default args for airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(seconds=30),
    "trigger_rule": "none_failed",
    'schedule_interval': None
}
default_args = update_default_args(default_args)

# Constants
DAG_INIT = "dag-init"
DAG_NAME = "openvds_import"
NAMESPACE = conf.get('kubernetes', 'NAMESPACE')
IN_CLUSTER = True

# Get environment variables
# AWS implementation so far assumed the API base url is in coming from OS level. It can be updated to use Airflow Variables
#{{ var.value.api_base_url}} and specify the variable in Airflow UI
env_vars = {
    "storage_service_endpoint": f"{os.environ['API_BASE_URL']}/api/storage/v2",
    "schema_service_endpoint": f"{os.environ['API_BASE_URL']}/api/schema-service/v1",
    "search_service_endpoint": f"{os.environ['API_BASE_URL']}/api/search/v2",
    "partition_service_endpoint": f"{os.environ['API_BASE_URL']}/api/partition/v1",
    "unit_service_endpoint": f"{os.environ['API_BASE_URL']}/api/unit/v2/unit/symbol",
    "dataset_service_endpoint": f"{os.environ['API_BASE_URL']}/api/dataset/v1",
    "AWS_REGION": os.environ['AWS_DEFAULT_REGION'],
    "SD_SVC_URL":  f"{os.environ['API_BASE_URL']}/api/seismic-store/v3",
    "SD_SVC_API_KEY": "xx",
}

dag = DAG(DAG_NAME, default_args=default_args, schedule_interval=None, dagrun_timeout=timedelta(minutes=60))

docker_image = f"{os.environ['VDS_OPERATOR_IMAGE']}"
#the docker image can be hard coded or using a airflow variable to specify
# please make sure you have onboarded the Docker image from OSDU Forum Registry to the deployment environment
# or configure docker session login to OSDU Forum registry

K8S_KWARGS = {
            "resources": {
                "request_memory": airflow.models.Variable.get("1Gi", default_var="1Gi"),
                "request_cpu": airflow.models.Variable.get("200m", default_var="200m"),
                "limit_memory": airflow.models.Variable.get("1Gi", default_var="1Gi"),
                "limit_cpu": airflow.models.Variable.get("1000m", default_var="1000m"),
            },
            "startup_timeout_seconds": 300, 
            "annotations": {
                "sidecar.istio.io/inject": "false"
            }
        }

if not K8S_KWARGS:
    K8S_KWARGS = {}

with dag:
    update_status_running = UpdateStatusOperator(
        task_id="update_status_running",
    )
    openvds_converter = KubernetesPodSegyToOpenVDSOperator(
        namespace=NAMESPACE,
        task_id="OPENVDS",
        name="OPENVDS",
        env_vars=env_vars,
        cmds=['SEGYImport'],
        is_delete_operator_pod=True,
        image=docker_image,
        trigger_rule="none_failed_or_skipped",
        **K8S_KWARGS
    )
    process_single_manifest_file = ProcessManifestOperatorR3(
        task_id="process_single_manifest_file_task",
        previous_task_id=openvds_converter.task_id,
        trigger_rule="none_failed_or_skipped"
    )

    update_status_finished = UpdateStatusOperator(
        task_id="update_status_finished",
        trigger_rule="all_done"
    )

update_status_running >> openvds_converter >> update_status_finished # pylint: disable=pointless-statement