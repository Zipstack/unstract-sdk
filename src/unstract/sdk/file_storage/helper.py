import logging
from typing import Any

import fsspec
from fsspec import AbstractFileSystem
from google.oauth2 import service_account

from unstract.sdk.exceptions import FileStorageError
from unstract.sdk.file_storage.constants import GCS, Minio
from unstract.sdk.file_storage.fs_provider import FileStorageProvider

logger = logging.getLogger(__name__)


class FileStorageHelper:
    @staticmethod
    def file_storage_init(provider: FileStorageProvider, credentials: dict[str, Any]):
        """Initialises file storage based on provider.

        Args:
            provider (FileStorageProvider): Provider
            credentials (dict): Credentials based on provider

        Returns:
            NA
        """
        if provider == FileStorageProvider.GCS:
            return FileStorageHelper.gcs_init(credentials)
        elif provider == FileStorageProvider.Minio:
            return FileStorageHelper.minio_init(credentials)
        elif provider == FileStorageProvider.Local:
            return FileStorageHelper.local_file_system_init()

    @staticmethod
    def gcs_init(credentials: dict[str, Any]) -> AbstractFileSystem:
        """Initialises FileStorage backed up by GCS.

        Args:
            credentials (dict): credentials

        Returns:
            NA
        """
        try:
            gcs_creds = service_account.Credentials.from_service_account_file(
                credentials[GCS.CREDS],
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

            fs = fsspec.filesystem(
                protocol=FileStorageProvider.GCS.value,
                project=credentials[GCS.PROJECT_ID],
                token=gcs_creds,
            )
            logger.debug(f"Connected to {FileStorageProvider.GCS.value} file system")
        except Exception as e:
            logger.error(
                f"Error in initialising {FileStorageProvider.GCS.value} "
                f"file system {e}",
                stack_info=True,
                exc_info=True,
            )
            raise FileStorageError(str(e))
        return fs

    @staticmethod
    def azure_init(extra_config):
        raise NotImplementedError

    @staticmethod
    def local_file_system_init() -> AbstractFileSystem:
        """Initialises FileStorage backed up by Local file system.

        Returns:
            NA
        """
        try:
            fs = fsspec.filesystem(protocol=FileStorageProvider.Local.value)
            logger.debug(f"Connected to {FileStorageProvider.Local.value} file system")
            return fs
        except Exception as e:
            logger.error(
                f"Error in initialising {FileStorageProvider.GCS.value}"
                f" file system {e}",
                stack_info=True,
                exc_info=True,
            )
            raise FileStorageError(str(e))

    @staticmethod
    def minio_init(config: dict[str, Any]) -> AbstractFileSystem:
        """Initialises FileStorage backed up by Minio.

        Args:
            credentials (dict): credentials

        Returns:
            NA
        """
        try:
            endpoint = config[Minio.ENDPOINT]
            access_key = config[Minio.ACCESS_KEY]
            secret_key = config[Minio.SECRET_KEY]
            fs = fsspec.filesystem(
                "s3",
                endpoint_url=endpoint,
                key=secret_key,
                secret=access_key,
            )
            logger.debug(f"Connected to {FileStorageProvider.Minio.value} file system")
            return fs
        except Exception as e:
            logger.error(
                f"Error in initialising {FileStorageProvider.Minio.value}"
                f" file system {e}",
                stack_info=True,
                exc_info=True,
            )
            raise FileStorageError(str(e))
