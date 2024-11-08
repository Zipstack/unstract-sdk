import logging

import fsspec
from fsspec import AbstractFileSystem

from unstract.sdk.exceptions import FileStorageError
from unstract.sdk.file_storage.fs_provider import FileStorageProvider

logger = logging.getLogger(__name__)


class FileStorageHelper:
    @staticmethod
    def file_storage_init(provider: FileStorageProvider, **storage_config):
        """Initialises file storage based on provider.

        Args:
            provider (FileStorageProvider): Provider
            storage_config : Storage config params based on the provider.
            Sent as-is to the provider implementation.

        Returns:
            NA
        """

        try:
            protocol = provider.value
            if provider == FileStorageProvider.Local:
                storage_config.update({"auto_mkdir": True})
            elif provider in [FileStorageProvider.Minio]:
                # Initialise using s3 for Minio
                protocol = FileStorageProvider.S3.value

            fs = fsspec.filesystem(
                protocol=protocol,
                **storage_config,
            )
            logger.debug(f"Connected to {provider.value} file system")
        except KeyError as e:
            logger.error(
                f"Error in initialising {provider.value} "
                f"file system because of missing config {e}",
                stack_info=True,
                exc_info=True,
            )
            raise FileStorageError(str(e))
        except Exception as e:
            logger.error(
                f"Error in initialising {provider.value} " f"file system {e}",
                stack_info=True,
                exc_info=True,
            )
            raise FileStorageError(str(e))
        return fs

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
