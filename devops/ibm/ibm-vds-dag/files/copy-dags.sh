#!/bin/bash
VDS_DAG="/opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py"
chown -R 50000:root /opt/airflow/dags
chmod 775 /opt/airflow/dags
df -h
pwd
ls -ltr
echo "Printing Source Dags"
ls -ltr /tmp/scripts
cp /tmp/scripts/segy_to_vds_ssdms_conversion_dag.py /opt/airflow/dags/.
chown -R 50000:root /opt/airflow/dags
chmod 775 /opt/airflow/dags
echo "printing target dags"
ls -ltr /opt/airflow/dags
