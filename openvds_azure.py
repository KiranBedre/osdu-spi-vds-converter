#  Copyright © Microsoft Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import airflow
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from json import dumps
from datetime import timedelta
import os
from airflow import configuration as conf



# default args for airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': None
}

# Get values from dag run configuration
record_id = "{{ dag_run.conf['execution_context']['id'] }}"
authorization = "{{ dag_run.conf['authToken'] }}".replace("Bearer ", "")
dataPartitionId = "{{ dag_run.conf['workflowRequestHeaders']['data-partition-id']}}"
run_id = "{{ dag_run.conf['run_id'] }}"
steps = ["LOAD_FROM_CSV", "TYPE_COERCION", "ID", "ACL", "LEGAL", "KIND", "META", "TAGS", "UNIT", "CRS", "RELATIONSHIP", "STORE_TO_OSDU"]

# Constants
DAG_INIT = "dag-init"
DAG_NAME = "vds_dag-0.10.0"
NAMESPACE = "NAMESPACE_PLACEHOLDER"



# Get environment variables
# AWS implementation so far assumed the API base url is in coming from OS level. It can be updated to use Airflow Variables
#{{ var.value.api_base_url}} and specify the variable in Airflow UI
env_vars = {
    "storage_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/storage/v2",
    "schema_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/schema-service/v1",
    "search_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/search/v2",
    "partition_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/partition/v1",
    "unit_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/unit/v3/unit/symbol",
    "dataset_service_endpoint": "https://DNS_HOST_PLACEHOLDER/api/dataset/v1",
}

dag = DAG(DAG_NAME, default_args=default_args)
kube_config_path = os.path.join(os.environ['AIRFLOW_HOME'], 'kube_config.yaml')

docker_image = "DOCKER_IMAGE_PLACEHOLDER"

input_connection = "{{ dag_run.conf['execution_context']['input_connection'] }}"
url_connection = "{{ dag_run.conf['execution_context']['url_connection'] }}"
url = "{{dag_run.conf['execution_context']['url']}}"
segy_file="{{dag_run.conf['execution_context']['segy_file']}}"
persistent_id="{{dag_run.conf['execution_context']['persistent_id']}}"

openvds_converter = KubernetesPodOperator(
    namespace=NAMESPACE,
    task_id="OPENVDS",
    name="OPENVDS",
    env_vars=env_vars,
    arguments=["import","--input="+segy_file,"--input-connection="+input_connection,"--url="+url,"--url-connection="+url_connection,"--persistentID="+persistent_id],
    is_delete_operator_pod=True,
    image=docker_image,
    config_file=kube_config_path,
    dag=dag)
