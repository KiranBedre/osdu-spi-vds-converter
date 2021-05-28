#!/usr/bin/env sh
#
#  Purpose: Initialize the DAGS.
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

export NAMESPACE=airflow

if [ -z $AZURE_DNS_NAME ]; then
  echo 'ERROR: AZURE_DNS_NAME not provided'
  usage;
else
  export AZURE_DNS_NAME=$AZURE_DNS_NAME
  export WORKFLOW_URL=https://${AZURE_DNS_NAME}/api/workflow/v1/workflow
fi

if [ -z $DATA_PARTITION ]; then
  SHARED_TENANT="opendes"
else
  SHARED_TENANT=$DATA_PARTITION
fi
export SHARED_TENANT

if [ -z $DAG_TASK_IMAGE ]; then
  DAG_TASK_IMAGE=${AZURE_REGISTRY}.azurecr.io/${CI_PROJECT_NAME}-${CI_COMMIT_REF_SLUG}:latest
fi
export DAG_TASK_IMAGE

echo "AZURE_DNS_NAME: $AZURE_DNS_NAME"
echo "WORKFLOW_URL: $WORKFLOW_URL"
echo "SHARED_TENANT: $SHARED_TENANT"
echo "DAG_TASK_IMAGE: $DAG_TASK_IMAGE"

printf "\n"
echo "Execute Python Script Token.py";
echo "------------------------------------";

BEARER_TOKEN=$(python $AZURE_DEPLOYMENTS_SUBDIR/Token.py)
export BEARER_TOKEN

echo "$(echo $BEARER_TOKEN | cut -c -20)***********"

printf "\n"
echo "Execute Python Script register_dag.py";
echo "------------------------------------";

python $AZURE_DEPLOYMENTS_SUBDIR/register_dag.py -f $DAG_DIRECTORY/openvds.py

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
