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


DAG_DOCKER_IMAGE=${DAG_IMAGE}


export DAG_DOCKER_IMAGE
export SERVICE_NAME 
echo "AZURE_DNS_NAME: $AZURE_DNS_NAME"
echo "WORKFLOW_URL: $WORKFLOW_URL"
echo "SHARED_TENANT: $SHARED_TENANT"
echo "DAG_DOCKER_IMAGE: $DAG_DOCKER_IMAGE"
echo "SERVICE_NAME: $SERVICE_NAME"

printf "\n"
echo "Execute Python Script Token.py";
echo "------------------------------------";

BEARER_TOKEN=$(python $AZURE_DEPLOYMENTS_SUBDIR/Token.py)
export BEARER_TOKEN

echo "$(echo $BEARER_TOKEN | cut -c -20)***********"


printf "\n"
echo "Execute Python Script register_dag.py";
echo "------------------------------------";

python $AZURE_DEPLOYMENTS_SUBDIR/register_dag.py -f $DAG_DIRECTORY/segy_to_vds_conversion_dag.py



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
