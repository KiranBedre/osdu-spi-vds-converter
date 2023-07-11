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
# Adding below source urls to see where the code is coming from in airflow dag's code page
# Please change these lines if any dependencies are changed in future or if the code is moved
# This code is coming from repo: https://community.opengroup.org/osdu/platform/data-flow/ingestion/segy-to-vds-conversion
# File: https://community.opengroup.org/osdu/platform/data-flow/ingestion/segy-to-vds-conversion/-/blob/master/openvds.py
# Dependencies: 
# osdu-api==0.21.3
# osdu-airflow==0.21.2
# osdu-ingestion==0.21.0

"""DAG for transformation SEGY file to VDS files."""

from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators.gc.kubernetes_pod_with_auth import \
    KubernetesPodOperatorWithAuth

default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": "none_failed",
}

dag_name = "segy_to_vds_conversion"
docker_image = "{{ var.value.get('seismic__config__vds_docker_image') }}"
k8s_namespace = "default"
persistent_id = "{{ dag_run.conf['execution_context']['persistent_id'] }}"
vds_url = "{{ dag_run.conf['execution_context']['vds_url'] }}"
segy_url = "{{ dag_run.conf['execution_context']['segy_url'] }}"

dag = DAG(
    dag_name,
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60)
)

with dag:
    start = DummyOperator(
        dag=dag,
        task_id="start"
    )

    segy_to_vds = KubernetesPodOperatorWithAuth(
        dag=dag,
        task_id='pod-ex',
        name='pod-ex',
        cmds=['SEGYImport'],
        arguments=[
            f"--url={vds_url}",
            f"--persistentID={persistent_id}",
            f"{segy_url}"],
        namespace=k8s_namespace,
        image=docker_image,
        is_delete_operator_pod=True
    )

start >> segy_to_vds  # pylint: disable=pointless-statement
