#!/usr/bin/env bash

set -ex

###############################
## ARGUMENT INPUT            ##
###############################

usage() { echo "Usage: bootstrap_segy_to_vds.sh"; }

printf "\n"
echo "------------------------------------";
echo "BOOTSTRAP -- START";
echo "------------------------------------";


if [ -z $K8S_NAMESPACE ]; then
  echo 'ERROR: K8S_NAMESPASE not provided'
  usage;
else
  export NAMESPACE=$K8S_NAMESPACE
fi

if [ -z $K8S_NODE_POOLS ]; then
  echo 'WARNING: K8S_NODE_POOLS not provided. Will be used default node pool'
  export K8S_NODE_POOLS=default
else
  export K8S_NODE_POOLS=$K8S_NODE_POOLS
fi

if [ -z $SD_SVC_URL ]; then
  echo 'ERROR: SD_SVC_URL not provided'
  usage;
else
  export SD_SVC_URL=$SD_SVC_URL
fi

if [ -z $SEGY_VDS_DOCKER_IMAGE ]; then
  echo 'ERROR: SEGY_VDS_DOCKER_IMAGE not provided'
  usage;
else
  SEGY_VDS_DOCKER_IMAGE=${SEGY_VDS_DOCKER_IMAGE}
fi
export SEGY_VDS_DOCKER_IMAGE


printf "\n"
echo "SETTING POPULATION TO THE DAG FILE";
echo "------------------------------------";

if [ -z $OUTPUT_FILE ]; then
  echo "THE ORIGINAL DAG FILE WILL BE OVERWRITTEN"
  python3 $OSDU_GCP_DEPLOYMENTS_SUBDIR/render_dag_file.py -f $OSDU_GCP_DAG_DIRECTORY/segy_to_vds_ssdms_conversion_dag.py
else
  echo "RENDERED OUTPUT WILL BE SAVED INTO ${OUTPUT_FILE}"
  python3 $OSDU_GCP_DEPLOYMENTS_SUBDIR/render_dag_file.py -f $OSDU_GCP_DAG_DIRECTORY/segy_to_vds_ssdms_conversion_dag.py -o ${OUTPUT_FILE}
fi

# get airflow bucket variable
BUCKET=$(gcloud composer environments describe $COMP_NAME --location $LOCATION --format json | jq .config.dagGcsPrefix | tr -d '"' | sed -e 's|/dags||')

gsutil -m rsync -R -x '(?!^segy_to_vds_ssdms_conversion_dag.py$)' /opt/dags  $BUCKET/dags/segy_to_vds
