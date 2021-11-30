#  Copyright 2021 Google LLC
#  Copyright 2021 EPAM Systems
#
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

"""DAG for transformation SEGY file stored Seismic Store to VDS files in Seismic Store."""

from datetime import timedelta

import airflow
from airflow import DAG

from osdu_airflow.backward_compatibility.default_args import \
    update_default_args
from osdu_airflow.operators.process_manifest_r3 import \
    ProcessManifestOperatorR3
from osdu_airflow.operators.segy_open_vds_conversion import \
    KubernetesPodSegyToOpenVDSOperator
from osdu_airflow.operators.update_status import UpdateStatusOperator

default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": "none_failed",
}

default_args = update_default_args(default_args)

dag_name = "{| DAG_NAME |}"
docker_image = "{| DOCKER_IMAGE |}"
k8s_namespace = "{| K8S_NAMESPACE |}"
K8S_POD_KWARGS = {| K8S_POD_KWARGS |}
if not K8S_POD_KWARGS:
    K8S_POD_KWARGS = {}
seismic_store_url = "{| SEISMIC_STORE_URL |}"

dag = DAG(
    dag_name,
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
        task_id='segy_to_vds_ssdms_conversion',
        name='segy_vds_conversion',
        env_vars={
            "SD_SVC_URL": seismic_store_url,
            "SD_SVC_API_KEY": "test"
        },
        cmds=['SEGYImport'],
        namespace=k8s_namespace,
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
