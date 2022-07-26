FROM google/cloud-sdk:slim

COPY ./deployments/scripts/gcp /opt
COPY ./src /opt

ARG SEGY_VDS_DOCKER_IMAGE_ARG

ENV SEGY_VDS_DOCKER_IMAGE=$SEGY_VDS_DOCKER_IMAGE_ARG
ENV OSDU_GCP_DEPLOYMENTS_SUBDIR=/opt
ENV OSDU_GCP_DAG_DIRECTORY=/opt/dags
ENV PREFIX=$(pwd)

RUN apt-get update && apt-get install -yq jq && pip3 install -r /opt/requirements.txt && chmod 775 /opt/bootstrap_segy_to_vds.sh

CMD ["/bin/bash", "-c", "/opt/bootstrap_segy_to_vds.sh"]
