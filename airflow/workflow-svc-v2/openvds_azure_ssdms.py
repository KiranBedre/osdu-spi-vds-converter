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

import airflow
from airflow import DAG
from airflow import configuration as conf

from osdu_airflow.backward_compatibility.default_args import \
    update_default_args
from osdu_airflow.operators.process_manifest_r3 import \
    ProcessManifestOperatorR3
from osdu_airflow.operators.segy_open_vds_conversion import \
    KubernetesPodSegyToOpenVDSOperator
from osdu_airflow.operators.update_status import UpdateStatusOperator

# default args for airflow
default_args = {
    'start_date': airflow.utils.dates.days_ago(0),
    'retries': 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": "none_failed",
}

default_args = update_default_args(default_args)

# Get values from dag run configuration
record_id = "{{ dag_run.conf['execution_context']['id'] }}"
authorization = "{{ dag_run.conf['authToken'] }}".replace("Bearer ", "")
svc_token = "{{ dag_run.conf['execution_context']['id_token'] or dag_run.conf['authToken'] }}"

# Constants
DAG_NAME = "{| DAG_NAME |}"
docker_image =  "{| DOCKER_IMAGE |}"
NAMESPACE = "{| NAMESPACE |}"
SEGY_CONVERTER = "segy-to-vds"
K8S_POD_KWARGS =  {| K8S_POD_OPERATOR_KWARGS |}
if not K8S_POD_KWARGS:
    K8S_POD_KWARGS = {}
seismic_store_url = "{| SEISMIC_STORE_URL |}"

env_vars = {
    "SD_SVC_URL": seismic_store_url,
    "SD_SVC_API_KEY": "NA",
}

dag = DAG(
    DAG_NAME,
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60)
)

with dag:
    update_status_running = UpdateStatusOperator(
        task_id="update_status_running",
    )

    segy_to_vds = KubernetesPodSegyToOpenVDSOperator(
        task_id=SEGY_CONVERTER,
        dag=dag,
        name=DAG_NAME,
        env_vars=env_vars,
        cmds=['SEGYImport'],
        namespace=NAMESPACE,
        image=docker_image,
        is_delete_operator_pod=True,
        trigger_rule="none_failed_or_skipped",
        **K8S_POD_KWARGS
    )

    process_single_manifest_file = ProcessManifestOperatorR3(
        task_id="process_single_manifest_file_task",
        previous_task_id=segy_to_vds.task_id,
        trigger_rule="none_failed_or_skipped"
    )

    update_status_finished = UpdateStatusOperator(
        task_id="update_status_finished",
        trigger_rule="all_done"
    )

update_status_running >> segy_to_vds >> process_single_manifest_file >> update_status_finished # pylint: disable=pointless-statement
