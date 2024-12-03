import json
import logging
import os

from unstract.sdk.exceptions import FileStorageError
from unstract.sdk.file_storage.constants import CredentialKeyword, StorageType
from unstract.sdk.file_storage.impl import FileStorage
from unstract.sdk.file_storage.permanent import PermanentFileStorage
from unstract.sdk.file_storage.provider import FileStorageProvider
from unstract.sdk.file_storage.shared_temporary import SharedTemporaryFileStorage

logger = logging.getLogger(__name__)


class EnvHelper:
    @staticmethod
    def get_storage(storage_type: StorageType, env_name: str) -> FileStorage:
        try:
            file_storage_creds = json.loads(os.environ.get(env_name))
            provider = FileStorageProvider(
                file_storage_creds[CredentialKeyword.PROVIDER]
            )
            if CredentialKeyword.CREDENTIALS in file_storage_creds:
                credentials = file_storage_creds[CredentialKeyword.CREDENTIALS]
            else:
                credentials = {}

            if storage_type == StorageType.PERMANENT.value:
                file_storage = PermanentFileStorage(provider=provider, **credentials)
            elif storage_type == StorageType.TEMPORARY.value:
                file_storage = SharedTemporaryFileStorage(
                    provider=provider, **credentials
                )
            else:
                raise NotImplementedError
            return file_storage
        except KeyError as e:
            logger.error(f"Required credentials is missing in the env: {str(e)}")
            raise e
        except FileStorageError as e:
            logger.error(
                "Error while initialising storage: %s",
                e,
                stack_info=True,
                exc_info=True,
            )
