#!/usr/bin/env sh
#
#  Purpose: Initialize the VDS Parser DAGS.
#  Usage:
#    bootstrap.sh


###############################
## ARGUMENT INPUT            ##
###############################

usage() { echo "Usage: bootstrap.sh"; }

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
  python3 $GCP_DEPLOYMENTS_SUBDIR/render_dag_file.py -f $GCP_DAG_DIRECTORY/segy_to_vds_ssdms_conversion_dag.py
else
  echo "RENDERED OUTPUT WILL BE SAVED INTO ${OUTPUT_FILE}"
  python3 $GCP_DEPLOYMENTS_SUBDIR/render_dag_file.py -f $GCP_DAG_DIRECTORY/segy_to_vds_ssdms_conversion_dag.py -o ${OUTPUT_FILE}
fi

if test $? = '1'; then
printf "\n"
  echo "------------------------------------";
  echo "BOOTSTRAP -- ERROR";
  echo "------------------------------------";
  exit 1
else
  printf "\n"
  echo "------------------------------------";
  echo "BOOTSTRAP -- FINISH";
  echo "------------------------------------";
  exit 0
fi

