from typing import Any, Union

from fsspec import AbstractFileSystem

from unstract.sdk.exceptions import FileStorageError
from unstract.sdk.file_storage.constants import Common
from unstract.sdk.file_storage.fs_impl import FileStorage
from unstract.sdk.file_storage.fs_provider import FileStorageProvider


class PermanentFileStorage(FileStorage):
    SUPPORTED_FILE_STORAGE_TYPES = [
        FileStorageProvider.GCS.value,
        FileStorageProvider.S3.value,
        FileStorageProvider.Azure.value,
    ]

    def __init__(
        self,
        provider: FileStorageProvider,
        credentials: dict[str, Any] = {},
    ):
        if provider.value not in self.SUPPORTED_FILE_STORAGE_TYPES:
            raise FileStorageError(
                f"File storage provider is not supported in Permanent mode. "
                f"Supported providers: {self.SUPPORTED_FILE_STORAGE_TYPES}"
            )
        if provider == FileStorageProvider.GCS:
            super().__init__(provider, credentials)
        else:
            raise NotImplementedError

    def copy_on_write(self, path1, path2):
        self.fs.put(path1, path2)

    def open(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
    ) -> Union[AbstractFileSystem]:
        if not self.exists(path):
            local_file_storage = FileStorage(provider=FileStorageProvider.Local)
            if local_file_storage.exists(path):
                self.copy_on_write(path, path)
        return super().open(path, mode, encoding)
