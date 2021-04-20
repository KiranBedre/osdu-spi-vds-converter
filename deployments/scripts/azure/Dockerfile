# Base Image from https://github.com/docker-library/python/blob/master/3.8/alpine3.13/Dockerfile
FROM python:3.8

ARG DATA_PARTITION=opendes

ENV PYTHONUNBUFFERED=1 \
  PATH="/home/osdu/.local/bin:${PATH}" \
  DATA_PARTITION=${DATA_PARTITION} \
  DAG_DIRECTORY=../src/dags \
  DAG_IMAGE=${DAG_IMAGE} \
  AZURE_DEPLOYMENTS_SUBDIR=. \
  AZURE_DEPLOYMENTS_SCRIPTS_SUBDIR=. \
  SERVICE_NAME="segy-to-vds-conversion"

USER root

# Create osdu user
RUN addgroup --system osdu && adduser --system osdu --ingroup osdu
WORKDIR /home/osdu

# Install Requirements
ADD deployments/scripts/azure/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add Scripts
ADD deployments/scripts/azure/*.py scripts/
ADD deployments/scripts/azure/bootstrap.sh scripts/
RUN chmod +x scripts/bootstrap.sh

# Add DAGs
ADD src src

# Execute as non root user.
USER osdu
WORKDIR /home/osdu/scripts

ENTRYPOINT ["/home/osdu/scripts/bootstrap.sh"]
