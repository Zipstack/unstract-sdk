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
            if provider in [FileStorageProvider.GCS, FileStorageProvider.Minio]:
                fs = fsspec.filesystem(
                    protocol=provider.value,
                    **storage_config,
                )
            elif provider == FileStorageProvider.Local:
                return FileStorageHelper.local_file_system_init()
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
        # if provider == FileStorageProvider.GCS:
        #     return FileStorageHelper.gcs_init(**storage_config)
        # elif provider == FileStorageProvider.Minio:
        #     return FileStorageHelper.minio_init(**storage_config)
        # elif provider == FileStorageProvider.Local:
        #     return FileStorageHelper.local_file_system_init()

    # @staticmethod
    # def gcs_init(**storage_config) -> AbstractFileSystem:
    #     """Initialises FileStorage backed up by GCS.
    #
    #     Args:
    #         storage_config: Storage config params based on the provider.
    #         Sent as-is to the provider implementation.
    #
    #     Returns:
    #         NA
    #     """
    #     try:
    #         fs = fsspec.filesystem(
    #             protocol=FileStorageProvider.GCS.value,
    #             **storage_config,
    #         )
    #         logger.debug(
    #             f"Connected to {FileStorageProvider.GCS.value} file system"
    #         )
    #     except KeyError as e:
    #         logger.error(
    #             f"Error in initialising {FileStorageProvider.GCS.value} "
    #             f"file system because of missing config {e}",
    #             stack_info=True,
    #             exc_info=True,
    #         )
    #         raise FileStorageError(str(e))
    #     except Exception as e:
    #         logger.error(
    #             f"Error in initialising {FileStorageProvider.GCS.value} "
    #             f"file system {e}",
    #             stack_info=True,
    #             exc_info=True,
    #         )
    #         raise FileStorageError(str(e))
    #     return fs
    #
    # @staticmethod
    # def azure_init(extra_config):
    #     raise NotImplementedError

    @staticmethod
    def local_file_system_init() -> AbstractFileSystem:
        """Initialises FileStorage backed up by Local file system.

        Returns:
            NA
        """
        try:
            fs = fsspec.filesystem(
                protocol=FileStorageProvider.Local.value, auto_mkdir=True
            )
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

    # @staticmethod
    # def minio_init(**storage_config) -> AbstractFileSystem:
    #     """Initialises FileStorage backed up by Minio.
    #
    #     Args:
    #         storage_config : Storage config params based on the provider.
    #         Sent as-is to the provider implementation.
    #
    #     Returns:
    #         NA
    #     """
    #     try:
    #         fs = fsspec.filesystem("s3", **storage_config)
    #         logger.debug(
    #             f"Connected to {FileStorageProvider.Minio.value} file system"
    #         )
    #         return fs
    #     except KeyError as e:
    #         logger.error(
    #             f"Error in initialising {FileStorageProvider.Minio.value} "
    #             f"file system because of missing config {e}",
    #             stack_info=True,
    #             exc_info=True,
    #         )
    #         raise FileStorageError(str(e))
    #     except Exception as e:
    #         logger.error(
    #             f"Error in initialising {FileStorageProvider.Minio.value}"
    #             f" file system {e}",
    #             stack_info=True,
    #             exc_info=True,
    #         )
    #         raise FileStorageError(str(e))
