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
DAG_NAME = "openvds_import"
NAMESPACE = conf.get('kubernetes', 'NAMESPACE')
IN_CLUSTER = False
CLUSTER_CONTEXT = conf.get('kubernetes', 'cluster_context')



# Get environment variables
# AWS implementation so far assumed the API base url is in coming from OS level. It can be updated to use Airflow Variables
#{{ var.value.api_base_url}} and specify the variable in Airflow UI
env_vars = {
    "storage_service_endpoint": f"{os.environ['API_BASE_URL']}/api/storage/v2",
    "schema_service_endpoint": f"{os.environ['API_BASE_URL']}/api/schema-service/v1",
    "search_service_endpoint": f"{os.environ['API_BASE_URL']}/api/search/v2",
    "partition_service_endpoint": f"{os.environ['API_BASE_URL']}/api/partition/v1",
    "unit_service_endpoint": f"{os.environ['API_BASE_URL']}/api/unit/v2/unit/symbol",
    "dataset_service_endpoint": f"{os.environ['API_BASE_URL']}/api/dataset/v1"
}

dag = DAG(DAG_NAME, default_args=default_args)
kube_config_path = os.path.join(os.environ['AIRFLOW_HOME'], 'kube_config.yaml')

docker_image = "888733619319.dkr.ecr.us-east-1.amazonaws.com/openvds:2.0-AWS"
#the docker image can be hard coded or using a airflow variable to specify
# please make sure you have onboarded the Docker image from OSDU Forum Registry to the deployment environment
# or configure docker session login to OSDU Forum registry

#This will be part of <execution_context>
#{
#"url_connection":"Region=us-east-1;AccessKeyId=XXX;SecretKey=XX;SessionToken=XXX",
#"input_connection":"Region=us-east-1;AccessKeyId=XXX;SecretKey=XXX;SessionToken=XXX"
#"segy_file":"s3://aws-osdu-sample-data/sample-data/seismic/st0202/stacks/ST0202R08_PS_PSDM_RAW_PP_TIME.MIG_RAW.POST_STACK.3D.JS-017534.segy",
#"url":"s3://aws-osdu-sample-data/"
#}




input_connection = "{{ dag_run.conf['execution_context']['input_connection'] }}"
url_connection = "{{ dag_run.conf['execution_context']['url_connection'] }}"
url = "{{dag_run.conf['execution_context']['url']}}"
segy_file="{{dag_run.conf['execution_context']['segy_file']}}"

openvds_converter = KubernetesPodOperator(
    namespace=NAMESPACE,
    task_id="OPENVDS",
    name="OPENVDS",
    env_vars=env_vars,
    in_cluster=IN_CLUSTER,
    cluster_context=CLUSTER_CONTEXT,
    arguments=["import", "--input-connection="+input_connection,"--url="+url, "--url-connection="+url_connection,segy_file],
    is_delete_operator_pod=True,
    image=docker_image,
    config_file=kube_config_path,
    dag=dag)
