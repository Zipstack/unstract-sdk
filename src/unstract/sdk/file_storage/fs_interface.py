from abc import ABC, abstractmethod
from typing import Union

from fsspec import AbstractFileSystem

from unstract.sdk.file_storage.constants import Common, FileSeekPosition


class FileStorageInterface(ABC):
    @abstractmethod
    def open(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
    ) -> Union[AbstractFileSystem]:
        pass

    @abstractmethod
    def read(
        self,
        file_handle: Union[AbstractFileSystem],
        length: int = Common.FULL,
    ) -> Union[bytes, str]:
        pass

    @abstractmethod
    def write(
        self,
        file_handle: Union[AbstractFileSystem],
        data: Union[bytes, str],
    ) -> int:
        pass

    @abstractmethod
    def seek(
        self,
        file_handle: Union[AbstractFileSystem],
        location: int = 0,
        position: FileSeekPosition = FileSeekPosition.START,
    ) -> Union[AbstractFileSystem]:
        pass

    @abstractmethod
    def mkdir(self, path: str, create_parents: bool):
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def ls(self, path: str) -> list[str]:
        pass

    @abstractmethod
    def rm(self, path: str, recursive: bool = True):
        pass

    @abstractmethod
    def close(self, file_handle: Union[AbstractFileSystem]):
        pass
