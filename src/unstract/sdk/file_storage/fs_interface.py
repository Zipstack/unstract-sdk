from abc import ABC, abstractmethod
from typing import Union

from fsspec import AbstractFileSystem

from unstract.sdk.file_storage.constants import Common, FileSeekPosition


class FileStorageInterface(ABC):
    @abstractmethod
    def read(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        length: int = Common.FULL,
    ) -> Union[bytes, str]:
        pass

    @abstractmethod
    def write(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        data: Union[bytes, str] = "",
    ) -> int:
        pass

    @abstractmethod
    def seek(
        self,
        file_handle: Union[AbstractFileSystem],
        location: int = 0,
        position: FileSeekPosition = FileSeekPosition.START,
    ) -> int:
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
    def cp(self, lpath: str, rpath: str):
        pass

    @abstractmethod
    def size(self, path: str) -> int:
        pass

    @abstractmethod
    def mime_type(self, path: str) -> str:
        pass

    @abstractmethod
    def download(self, from_path: str, to_path: str):
        pass

    @abstractmethod
    def get_hash_from_file(self, path: str) -> str:
        pass
