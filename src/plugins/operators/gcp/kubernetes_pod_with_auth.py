import json
import logging
import os
from urllib.parse import urlparse

from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.models import Variable
from google.cloud import storage


class KubernetesPodOperatorWithAuth(KubernetesPodOperator):
    """Custom Kubernetes Pod Operator with authorization logic"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_sa_info_from_google_storage(bucket_name: str, source_blob_name: str) -> dict:
        """Get sa_file content from Google Storage.

        :param bucket_name: The name of the bucket
        :type bucket_name: str
        :param source_blob_name: The name of the file
        :type source_blob_name: str
        :return: Service account info as dict
        :rtype: dict
        """
        bucket = storage.Client().bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        logging.info("Got SA_file.")
        sa_info = json.loads(blob.download_as_string())
        return sa_info

    @staticmethod
    def _get_sa_info_from_file(path: str) -> dict:
        """Return info from file.

        :param path: The path of the file.
        :type path: str
        :return: Loaded file as dict
        :rtype: dict
        """
        with open(path) as f:
            return json.load(f)

    def _get_sa_file_from_storage(self) -> dict:
        """Get sa_file content from Google Storage.

        :return: Service account info as dict
        :rtype: dict
        """
        sa_file_path = os.environ.get("SA_FILE_PATH", None) or Variable.get("gcp__config__sa_file")
        parsed_path = urlparse(sa_file_path)
        sa_info = None
        if parsed_path.scheme == "gs":
            bucket_name = parsed_path.netloc
            source_blob_name = parsed_path.path[1:]
            sa_info = self._get_sa_info_from_google_storage(bucket_name, source_blob_name)
        elif not parsed_path.scheme and os.path.isfile(parsed_path.path):
            sa_info = self._get_sa_info_from_file(parsed_path.path)
        return sa_info

    def pre_execute(self, context):
        """
        Pre-execute step: add connections fields to arguments

        If 'token' field is passed it is used for connections
        Otherwise json credential file is used.
        """
        conf = context["dag_run"].conf
        execution_context = conf["execution_context"]
        if execution_context.get("token", None):
            connection = f"Token={execution_context['connection']}"
            self.arguments.append(f"--url-connection={connection}")
            self.arguments.append(f"--input-connection={connection}")
        else:
            json_credential = self._get_sa_file_from_storage()
            connection = f"JsonCredentials={json.dumps(json_credential)}"
            self.arguments.append(f"--url-connection={connection}")
            self.arguments.append(f"--input-connection={connection}")

    def execute(self, context):
        super().execute(context)
