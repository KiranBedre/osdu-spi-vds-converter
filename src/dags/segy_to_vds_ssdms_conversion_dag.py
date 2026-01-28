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
# osdu-api==0.28.0
# osdu-airflow==0.28.0
# osdu-ingestion==0.28.0


"""DAG for transformation SEGY file stored Seismic Store to VDS files in Seismic Store.

Run example from Workflow service
{
    "executionContext": {
        "Payload": {
            "AppKey": "test-app",
            "data-partition-id": "{{data-partition-id}}"
        },
        "file_record_id": "{{data-partition-id}}:dataset--FileCollection.SEGY:test",
        "persistent_id": "test.vds",
        "userId": "test",
        "work_product_id": "{{data-partition-id}}:work-product--WorkProduct:test"
    }
}
"""

from datetime import timedelta
import logging

## Not used but required for DAG rendering
import airflow

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.utils.log.secrets_masker import mask_secret
from airflow.utils.trigger_rule import TriggerRule

from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from osdu_airflow.operators.process_manifest_r3 import \
    ProcessManifestOperatorR3
from osdu_airflow.operators.update_status import UpdateStatusOperator
from osdu_api.clients.storage.record_client import RecordClient
from osdu_api.clients.search.search_client import SearchClient
from osdu_ingestion.libs.context import Context
from osdu_ingestion.libs.refresh_token import AirflowTokenRefresher
from osdu_ingestion.libs.segy_conversion_metadata.open_vds import OpenVDSMetadata
from osdu_ingestion.libs.segy_conversion_metadata.headers_byte_locations import (
    HeadersByteLocations, ovds_converter_byte_locations)

default_args = {
    "start_date": days_ago(0),
    "retries": 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": TriggerRule.NONE_FAILED_OR_SKIPPED,
}

dag_name = "{| DAG_NAME |}"
docker_image = "{| DOCKER_IMAGE |}"
k8s_namespace = "{| K8S_NAMESPACE |}"
K8S_POD_KWARGS = {| K8S_POD_KWARGS |}
if not K8S_POD_KWARGS:
    K8S_POD_KWARGS = {}
seismic_store_url = "{| SEISMIC_STORE_URL |}"
env_vars = {
    "SD_SVC_URL": seismic_store_url,
    "SD_SVC_API_KEY": "test",
}
env_vars.update({| EXTRA_ENV_VARS|default('{}') |})

logger = logging.getLogger()

@task(multiple_outputs=True)
def pre_conversion(params = None):
    execution_context: dict = params.get('execution_context')

    auth_token: str = execution_context.get("id_token") or params.get("authToken")

    payload_context = Context.populate(execution_context)
    token_refresher = AirflowTokenRefresher()
    user_id = execution_context.get("userId")

    record_client = RecordClient(
        storage_url=Variable.get("core__service__storage__url", default_var=None),
        token_refresher=token_refresher,
        data_partition_id=payload_context.data_partition_id,
        user_id=user_id
    )
    search_client = SearchClient(
        search_url=Variable.get("core__service__search__url", default_var=None),
        token_refresher=token_refresher,
        data_partition_id=payload_context.data_partition_id,
        user_id=user_id
    )
    segy_vds_metadata = OpenVDSMetadata(record_client, payload_context)
    segy_headers_extractor = HeadersByteLocations(record_client, search_client)

    segy_url = segy_vds_metadata.get_file_collection_path(execution_context['file_record_id'])
    vds_url, persistent_id = segy_vds_metadata.get_vds_name_and_url_from_segy_path(segy_url)
    segy_headers = segy_headers_extractor.get_segy_headers_byte_locations(execution_context['file_record_id'])
    ovds_segy_headers = ovds_converter_byte_locations(segy_headers)

    if 'Bearer ' in auth_token:
        auth_token = auth_token.replace('Bearer ', '')

    sdtoken= f'sdtoken={auth_token}'
    mask_secret(sdtoken)

    arguments = [
        f'--url', f'{vds_url}',
        f'--url-connection', f'{sdtoken}',
        f'--persistentID', f'{persistent_id}',
        f'--input-connection', sdtoken,
        f"{segy_url}"
    ]

    if ovds_segy_headers:
        headers_str = []
        for header in ovds_segy_headers:
            headers_str.append(f"Header name: {header.field_name}, header offset: {header.offset}, width: {header.width}")
            arguments.extend(["--header-field", f"{header.field_name}={header.offset}:{header.width}"])
        headers_override_message = ",\n".join(headers_str)
        logger.info("The following header-field locations are going to be overwritten:")
        logger.info(headers_override_message)
        
    return {
        'arguments': arguments,
        'persistent_id': persistent_id,
        'vds_url': vds_url
    }

@task(multiple_outputs=True)
def post_conversion(persistent_id, vds_url, params = None):
    logger.debug("SEGY converted to VDS.")

    execution_context = params["execution_context"]
    payload_context = Context.populate(execution_context)
    work_product_id = execution_context['work_product_id']
    file_record_id = execution_context['file_record_id']

    token_refresher = AirflowTokenRefresher()
    user_id = execution_context.get("userId")

    record_client = RecordClient(
        storage_url=Variable.get("core__service__storage__url", default_var=None),
        token_refresher=token_refresher,
        data_partition_id=payload_context.data_partition_id,
        user_id=user_id
    )

    segy_vds_metadata = OpenVDSMetadata(record_client, payload_context)
 
    open_vds_manifest = segy_vds_metadata.create_metadata(
        f"{vds_url}/{persistent_id}",
        work_product_id,
        file_record_id
    )

    wpc_tags = {}
    for wpc in open_vds_manifest['Data']['WorkProductComponents']:
        wpc_tags[wpc['id']] = wpc.get('tags', '')

    logger.debug(f"New manifest is {open_vds_manifest}")
    return {"manifest": open_vds_manifest, "wpc_tags": wpc_tags}

@dag(
    dag_name,
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(hours=24)
)

def segy_to_openvds():
    update_status_running = UpdateStatusOperator(
        task_id="update_status_running",
    )

    pre_convert = pre_conversion()

    segy_to_vds = KubernetesPodOperator(
        task_id='segy_to_vds_ssdms_conversion',
        name='segy_vds_conversion',
        env_vars=env_vars,
        cmds=['SEGYImport'],
        namespace=k8s_namespace,
        image=docker_image,
        is_delete_operator_pod=True,
        arguments=pre_convert['arguments'],
        **K8S_POD_KWARGS
    )
    
    post_convert = post_conversion(pre_convert['persistent_id'], pre_convert['vds_url'])

    process_single_manifest_file = ProcessManifestOperatorR3(
        task_id="process_single_manifest_file_task",
        previous_task_id='post_conversion'
    )

    update_status_finished = UpdateStatusOperator(
        task_id="update_status_finished",
        trigger_rule=TriggerRule.ALL_DONE
    )

    update_status_running >> pre_convert >> segy_to_vds >> post_convert >> process_single_manifest_file >> update_status_finished # pylint: disable=pointless-statement

conversion_dag = segy_to_openvds()
