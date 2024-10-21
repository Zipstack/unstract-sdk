from abc import ABC, abstractmethod
from typing import Union

from fsspec import AbstractFileSystem

from unstract.sdk.file_storage.constants import Common, FileSeekPosition


class FileStorageInterface(ABC):
    # @abstractmethod
    # def open(
    #     self,
    #     path: str,
    #     mode: str,
    #     encoding: str = Common.DEFAULT_ENCODING,
    # ) -> Union[AbstractFileSystem]:
    #     pass

    @abstractmethod
    def read_file(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        length: int = Common.FULL,
    ) -> Union[bytes, str]:
        pass

    @abstractmethod
    def write_file(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        data: Union[bytes, str] = "",
    ) -> int:
        pass

    @abstractmethod
    def seek_file(
        self,
        file_handle: Union[AbstractFileSystem],
        location: int = 0,
        position: FileSeekPosition = FileSeekPosition.START,
    ) -> int:
        pass

    @abstractmethod
    def make_dir(self, path: str, create_parents: bool):
        pass

    @abstractmethod
    def path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def list(self, path: str) -> list[str]:
        pass

    @abstractmethod
    def remove(self, path: str, recursive: bool = True):
        pass

    # @abstractmethod
    # def close(self, file_handle: Union[AbstractFileSystem]):
    #     pass
