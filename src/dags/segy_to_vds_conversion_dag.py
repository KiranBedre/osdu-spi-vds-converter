#  Copyright 2020 Google LLC
#  Copyright 2020 EPAM Systems
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

import airflow
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from datetime import timedelta

default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": "none_failed",
}

dag = DAG (
    "segy_to_vds_conversion",
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60)
)


auth_token = "{{ dag_run.conf['authToken'] }}"
data_partition_id = "{{ dag_run.conf['runConfiguration']['dataPartitionId'] }}"
run_id = "{{ dag_run.conf['runId'] }}"
segy_url = ""
vds_url = ""
dag_name = "${DAG_NAME}" # Should be replace from CICD 
docker_image = "${DOCKER_IMAGE}" # Should be replace from CICD
k8s_namespace = "${K8S_NAMESPACE}" # Should be replace from CICD
env_vars = {}
args = ["--segy", segy_url, "--vds", vds_url]


converter = KubernetesPodOperator(
    # dag=dag,
    task_id="segy_to_vds_conversion",
    name="segy_to_vds_conversion",
    image=docker_image, 
    namespace=k8s_namespace,
    env_vars=env_vars,
    arguments=args,
    is_delete_operator_pod=True,
)

test = KubernetesPodOperator(
    namespace='default',
    image="python",
    cmds=["python", "-c"],
    arguments=["print('HELLO')"],
    labels={"foo": "bar"},
    image_pull_policy="Always",
    name="test_task",
    task_id="test_task",
    is_delete_operator_pod=False,
    get_logs=True,
    dag=dag
)