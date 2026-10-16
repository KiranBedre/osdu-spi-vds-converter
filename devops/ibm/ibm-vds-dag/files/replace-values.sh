#!/bin/bash
echo "Changing Source Dags"
sed -i '/from datetime import timedelta/ifrom json import dumps, loads' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/from datetime import timedelta/ifrom airflow.models import Variable' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i 's/"{| DAG_NAME |}"/"openvds_import"/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i 's/"{| DOCKER_IMAGE |}"/Variable.get("SGY_TO_VDS_DOCKER_IMAGE")/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i 's/"{| K8S_NAMESPACE |}"/Variable.get("SGY_TO_VDS_NAMESPACE")/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i 's/{| K8S_POD_KWARGS |}/{}/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/seismic_store_url/d' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py  
sed -i 's/^env_vars = {/env_vars = loads(env_dict)/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/env_vars = loads(env_dict)/ienv_dict = Variable.get("sgy_to_vds_env_var")' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/^    "SD_SVC_API_KEY": "test",/,+1d' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/env_vars.update/d' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py  
sed  -i 's/^        trigger_rule="none_failed_or_skipped",/        trigger_rule="none_failed_or_skipped"/g' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py
sed -i '/**K8S_POD_KWARGS/d' /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py  
echo "VDS DAGS Changed"
ls -ltr /opt/airflow/dags
