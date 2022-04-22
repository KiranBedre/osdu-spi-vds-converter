#  Licensed Materials - Property of IBM
#  (c) Copyright IBM Corp. 2020. All Rights Reserved.

"""DAG for transformation SEGY file stored Seismic Store to VDS files in Seismic Store."""

from datetime import timedelta

import airflow
from airflow import DAG
from json import dumps, loads
from osdu_airflow.backward_compatibility.default_args import \
    update_default_args
from osdu_airflow.operators.process_manifest_r3 import \
    ProcessManifestOperatorR3
from osdu_airflow.operators.segy_open_vds_conversion import \
    KubernetesPodSegyToOpenVDSOperator
from osdu_airflow.operators.update_status import UpdateStatusOperator
from airflow.models import Variable

default_args = {
    "start_date": airflow.utils.dates.days_ago(0),
    "retries": 0,
    "retry_delay": timedelta(seconds=30),
    "trigger_rule": "none_failed",
}

default_args = update_default_args(default_args)

dag_name = "openvds_import"
docker_image = Variable.get("SGY_TO_VDS_DOCKER_IMAGE")
k8s_namespace = Variable.get("SGY_TO_VDS_NAMESPACE")

env_dict = Variable.get("sgy_to_vds_env_var")
env_vars = loads(env_dict)

dag = DAG(
    dag_name,
    default_args=default_args,
    description="Airflow DAG for transformation from SEGY to OpenVDS",
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=120)
)

with dag:
    update_status_running = UpdateStatusOperator(
        task_id="update_status_running",
    )

    segy_to_vds = KubernetesPodSegyToOpenVDSOperator(
        task_id='segy_to_vds_ssdms_conversion',
        name='segy_vds_conversion',
        env_vars=env_vars,
        cmds=['SEGYImport'],
        namespace=k8s_namespace,
        image=docker_image,
        is_delete_operator_pod=True,
        trigger_rule="none_failed_or_skipped"
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
