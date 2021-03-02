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
from airflow.contrib.operators import kubernetes_pod_operator
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


k8s_test = kubernetes_pod_operator.KubernetesPodOperator(
    dag=dag,
    # The ID specified for the task.
    task_id='pod-ex-minimum',
    # Name of task you want to run, used to generate Pod ID.
    name='pod-ex-minimum',
    # Entrypoint of the container, if not specified the Docker container's
    # entrypoint is used. The cmds parameter is templated.
    cmds=['echo'],
    # The namespace to run within Kubernetes, default namespace is
    # `default`. There is the potential for the resource starvation of
    # Airflow workers and scheduler within the Cloud Composer environment,
    # the recommended solution is to increase the amount of nodes in order
    # to satisfy the computing requirements. Alternatively, launching pods
    # into a custom namespace will stop fighting over resources.
    namespace='default',
    # Docker image specified. Defaults to hub.docker.com, but any fully
    # qualified URLs will point to a custom repository. Supports private
    # gcr.io images if the Composer Environment is under the same
    # project-id as the gcr.io images and the service account that Composer
    # uses has permission to access the Google Container Registry
    # (the default service account has permission)
    image='gcr.io/gcp-runtimes/ubuntu_18_0_4'
)