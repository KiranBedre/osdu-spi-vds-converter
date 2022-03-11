FROM community.opengroup.org:5555/osdu/platform/deployment-and-operations/base-containers-azure/alpine-python3:0.0.2

ARG DATA_PARTITION=opendes

ENV BUILD_PACKAGES \
  py-cryptography

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
  apk update && \
  apk add --no-cache ${BUILD_PACKAGES} &&\
  rm -rf /var/cache/apk/*

# Install Requirements
ADD deployments/scripts/azure/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add Scripts
ADD deployments/scripts/azure/*.py scripts/
ADD deployments/scripts/azure/bootstrap.sh scripts/
RUN chmod +x scripts/bootstrap.sh

# Add DAGs
ADD airflow airflow

# Execute as non root user.
USER osdu
WORKDIR /home/osdu/scripts

ENTRYPOINT ["/home/osdu/scripts/bootstrap.sh"]
