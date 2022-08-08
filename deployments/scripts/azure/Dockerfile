FROM mcr.microsoft.com/mirror/docker/library/python:3.8-slim

ARG DATA_PARTITION=opendes

ENV BUILD_PACKAGES \
  python3-cryptography

ENV PYTHONUNBUFFERED=1 \
  PATH="/home/osdu/.local/bin:${PATH}" \
  DATA_PARTITION=${DATA_PARTITION} \
  DAG_DIRECTORY=../airflow/workflow-svc-v2 \
  DAG_TASK_IMAGE=${DAG_TASK_IMAGE} \
  AZURE_DEPLOYMENTS_SUBDIR=. \
  AZURE_DEPLOYMENTS_SCRIPTS_SUBDIR=.

USER root

RUN set -x \
  echo "**** install Python ****" && \
  apt-get update && \
  apt-get install -y -o APT::Keep-Downloaded-Packages=false ${BUILD_PACKAGES} &&\
  rm -rf /var/cache/apt/archives/*

# Install Requirements
ADD deployments/scripts/azure/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add debian repo to install busybox package
RUN \
  echo '@debian http://deb.debian.org/debian' >> /etc/apt/repositories && \
  echo '@debian http://deb.debian.org/debian-security' >> /etc/apt/repositories

RUN \
  apt-get update && \
  apt-get install busybox -y

# Add Scripts
WORKDIR /home/osdu
ADD deployments/scripts/azure/*.py scripts/
ADD deployments/scripts/azure/bootstrap.sh scripts/
RUN chmod +x scripts/bootstrap.sh

# Add DAGs
ADD airflow airflow

# Execute as non root user.
RUN addgroup --system osdu && adduser --system osdu --ingroup osdu
USER osdu
WORKDIR /home/osdu/scripts

ENTRYPOINT ["/home/osdu/scripts/bootstrap.sh"]