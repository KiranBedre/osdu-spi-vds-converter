#!/usr/bin/env sh
#
#  Purpose: Create Dags
#  Usage:
#    prepare_dags.sh


###############################
## ARGUMENT INPUT            ##
###############################

usage() { echo "Usage: prepare_dags.sh"; }

printf "\n"
echo "------------------------------------";
echo "Creating Dags -- START ";
echo "------------------------------------";

if [ -z $NAMESPACE ]; then
  NAMESPACE=airflow
fi
export NAMESPACE

if [ -z $BUILD_VERSION ]; then
  BUILD_VERSION=$(echo ${CI_COMMIT_SHA} | cut -c -5)
fi
export BUILD_VERSION

echo "NAMESPACE: $NAMESPACE"
echo "BUILD_VERSION: $BUILD_VERSION"

printf "\n"
echo "Execute Python Script output_dag_folder.py";
echo "------------------------------------";

python $AZURE_DEPLOYMENTS_SUBDIR/scripts/output_dag_folder.py -f $DAG_DIRECTORY/segy_to_vds_ssdms_conversion_dag.py
