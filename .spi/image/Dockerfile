FROM apache/airflow:3.2.2-python3.12@sha256:bbe58e3204d550ab98dbf738a42c0e6663c455357ecd0e2d1440ef9cb6a75f00

ARG AIRFLOW_VERSION=3.2.2
ARG PYTHON_VERSION=3.12

COPY --chown=airflow:root .spi/runtime/requirements.txt /tmp/spi/requirements.txt
COPY --chown=airflow:root .spi/ci/spi_vds /tmp/spi/spi_vds
COPY --chown=airflow:root src/dags/segy_to_vds_ssdms_conversion_dag.py /tmp/spi/source.py

RUN python -m pip install --no-cache-dir \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
      --requirement /tmp/spi/requirements.txt \
    && PYTHONPATH=/tmp/spi python -m spi_vds.render_dag \
      --source /tmp/spi/source.py \
      --output /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py \
    && python -m compileall -q /opt/airflow/dags/segy_to_vds_ssdms_conversion_dag.py \
    && rm -rf /tmp/spi
