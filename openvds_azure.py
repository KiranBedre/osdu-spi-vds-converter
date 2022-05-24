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

import os
from datetime import timedelta
from json import dumps

from osdu_airflow.backward_compatibility.default_args import \
    update_default_args

import airflow
from airflow import DAG
from airflow import configuration as conf
from airflow.contrib.operators.kubernetes_pod_operator import \
    KubernetesPodOperator

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
authorization = "{{ dag_run.conf['authToken'] }}".replace("Bearer ", "")
svc_token = "{{ dag_run.conf['execution_context']['id_token'] or dag_run.conf['authToken'] }}"


# Constants
DAG_INIT = "dag-init"
DAG_NAME = "{| DAG_NAME |}"
NAMESPACE = "{| NAMESPACE |}"
docker_image =  "{| DOCKER_IMAGE |}"
SEGY_CONVERTER = "segy-to-vds"

K8S_POD_KWARGS =  {| K8S_POD_OPERATOR_KWARGS |}

if not K8S_POD_KWARGS:
    K8S_POD_KWARGS = {}



persistent_id = "{{ dag_run.conf['execution_context']['persistent_id'] }}"
vds_url = "{{ dag_run.conf['execution_context']['vds_url'] }}"
segy_url = "{{ dag_run.conf['execution_context']['segy_url'] }}"



# Get environment variables
# AWS implementation so far assumed the API base url is in coming from OS level. It can be updated to use Airflow Variables
#{{ var.value.api_base_url}} and specify the variable in Airflow UI

dag = DAG(DAG_NAME, default_args=default_args)


kube_config_path = os.path.join(os.environ['AIRFLOW_HOME'], 'kube_config.yaml')


env_vars = {
    "SD_SVC_URL": "https://{{ var.value.azure_dns_host }}/seistore-svc/api/v3",
    "SD_SVC_TOKEN": svc_token,
    "SD_SVC_API_KEY": "NA",
}

svc_connection_string = f'sdauthorityurl={env_vars["SD_SVC_URL"]};sdapikey={env_vars["SD_SVC_API_KEY"]};sdtoken={svc_token}'

segy_to_vds = KubernetesPodOperator(
    task_id=SEGY_CONVERTER,
    dag=dag,
    name=DAG_NAME,
    env_vars=env_vars,
    cmds=['SEGYImport'],
    arguments=[
            f'--persistentID', f'{persistent_id}',
            f'--url', f'{vds_url}',
            f'--url-connection', f'{svc_connection_string}',
            f'--input-connection', f'{svc_connection_string}',
            f"{segy_url}"
    ],
    namespace=NAMESPACE,
    image=docker_image,
    is_delete_operator_pod=True,
    **K8S_POD_KWARGS
)

segy_to_vds
