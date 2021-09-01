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
from airflow.contrib.operators.kubernetes_pod_operator import \
    KubernetesPodOperator
from osdu_airflow.backward_compatibility.default_args import \
    update_default_args

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

persistent_id = "{{ dag_run.conf['execution_context']['persistent_id'] }}"
vds_url = "{{ dag_run.conf['execution_context']['vds_url'] }}"
segy_url = "{{ dag_run.conf['execution_context']['segy_url'] }}"
id_token = "{{ dag_run.conf['execution_context']['id_token'] }}"

dag = DAG(
    dag_name,
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60)
)

with dag:
    segy_to_vds = KubernetesPodOperator(
        task_id='segy_to_vds_ssdms_conversion',
        name='segy_vds_conversion',
        env_vars={
            "SD_SVC_URL": seismic_store_url,
            "SD_SVC_API_KEY": "test"
        },
        cmds=['SEGYImport'],
        arguments=[
            f'--url', f'{vds_url}',
            f'--url-connection', f'sdtoken={id_token}',
            f'--persistentID', f'{persistent_id}',
            f'--input-connection', f'sdtoken={id_token}',
            f"{segy_url}"
        ],
        namespace=k8s_namespace,
        image=docker_image,
        is_delete_operator_pod=True,
        **K8S_POD_KWARGS
    )

segy_to_vds  # pylint: disable=pointless-statement
