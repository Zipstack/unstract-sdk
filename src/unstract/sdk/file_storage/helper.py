import logging
import os

import fsspec
from google.cloud import storage

from unstract.sdk.exceptions import FileStorageError
from unstract.sdk.file_storage.constants import GCS
from unstract.sdk.file_storage.fs_type import FileStorageType

logger = logging.getLogger(__name__)


class FileStorageHelper:
    @staticmethod
    def file_storage_init(type: FileStorageType, credentials):
        if type == FileStorageType.GCS:
            return FileStorageHelper.gcs_init(credentials)
        elif type == FileStorageType.Local:
            return FileStorageHelper.local_file_system_init()

    @staticmethod
    def gcs_init(credentials):
        try:
            os.environ[GCS.CREDS] = credentials[GCS.CREDS]
            storage_client = storage.Client()

            fs = fsspec.filesystem(
                protocol=FileStorageType.GCS.value,
                project=credentials[GCS.PROJECT_ID],
                client=storage_client,
            )
            logger.info(f"Connected to {FileStorageType.GCS.value} file system")
        except Exception as e:
            logger.error(
                f"Error in initialising {FileStorageType.GCS.value} file system {e}"
            )
            raise FileStorageError(str(e))
        return fs

    @staticmethod
    def azure_init(extra_config):
        return

    @staticmethod
    def local_file_system_init():
        try:
            fs = fsspec.filesystem(protocol=FileStorageType.Local.value)
            logger.info(f"Connected to {FileStorageType.Local.value} file system")
            return fs
        except Exception as e:
            logger.error(
                f"Error in initialising {FileStorageType.GCS.value} file system {e}"
            )
            raise FileStorageError(str(e))
