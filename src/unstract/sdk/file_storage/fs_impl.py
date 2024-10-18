from typing import Union

import fsspec
from fsspec import AbstractFileSystem

from unstract.sdk.exceptions import FileOperationError
from unstract.sdk.file_storage.constants import Common, FileSeekPosition
from unstract.sdk.file_storage.fs_interface import FileStorageInterface
from unstract.sdk.file_storage.helper import FileStorageHelper


class FileStorage(FileStorageInterface):
    # This class integrates fsspec library for file operations

    fs: fsspec  # fsspec file system handle

    def __init__(self, provider, credentials: dict() = {}):
        self.fs = FileStorageHelper.file_storage_init(
            provider=provider, credentials=credentials
        )

    def open(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
    ) -> Union[AbstractFileSystem]:
        """Opens the specified file and returns the actual file handle based on
        the library in use to perform file operations.

        Args:
            path (str): Path to the file to be opened
            mode (str): Mode in whicg the file is to be opened. Usual options
                        include r, rb, w and wb
            encoding (str): Encoding type like utf-8 or utf-16

        Returns:
            Union[AbstractFileSystem] : Actual file handle to the file that was opened
        """
        try:
            return self.fs.open(path=path, mode=mode, encoding=encoding)
        except Exception as e:
            raise FileOperationError(str(e))

    def read(
        self,
        file_handle: Union[AbstractFileSystem],
        length: int = Common.FULL,
    ) -> Union[bytes, str]:
        """Read the file pointed to by the file_handle.

        Args:
            file_handle (Union[AbstractFileSystem]): Actual file handle of
            the file
            length (int): Number of bytes to be read. Default is full
            file content.

        Returns:
            Union[bytes, str] - File contents in bytes/string based on the opened mode
        """
        try:
            return file_handle.read(length)
        except Exception as e:
            raise FileOperationError(str(e))

    def write(
        self, file_handle: Union[AbstractFileSystem], data: Union[bytes, str]
    ) -> int:
        """Write data in the file pointed to by the file-handle.

        Args:
            file_handle (Union[AbstractFileSystem]): Actual file handle of the
            file to be written to
            data (Union[bytes, str]): Contents to be written

        Returns:
            int: Number of bytes that were successfully written to the file
        """
        try:
            return file_handle.write(data)
        except Exception as e:
            raise FileOperationError(str(e))

    def seek(
        self,
        file_handle: Union[AbstractFileSystem],
        location: int = 0,
        position: FileSeekPosition = FileSeekPosition.START,
    ) -> Union[AbstractFileSystem]:
        """Place the file pointer to the mentioned location in the file
        relative to the position.

        Args:
            file_handle (Union[AbstractFileSystem]):
            location (int): Nth byte position. To be understood in relation to
            the arg "position"
            position (FileSeekPosition): from start of file, current location
            or end of file

        Returns:
            int: file pointer after seeking to the mentioned position
        """
        try:
            return file_handle.seek(location, position)
        except Exception as e:
            raise FileOperationError(str(e))

    def mkdir(self, path: str, create_parents: bool = True):
        """Create a directory.

        Args:
            path (str): Path of the directory to be created
            create_parents (bool): Specify if parent directories to be created
            if any of the nested directory does not exist
        """
        try:
            self.fs.mkdir(path, create_parents=create_parents)
        except Exception as e:
            raise FileOperationError(str(e))

    def exists(self, path: str) -> bool:
        """Checks if a file/directory path exists.

        Args:
            path (str): File/directory path

        Returns:
            bool: If the file/directory  exists or not
        """
        try:
            return self.fs.exists(path)
        except Exception as e:
            raise FileOperationError(str(e))

    def ls(self, path: str) -> list[str]:
        """List the directory path.

        Args:
            path (str): Directory path

        Returns:
            List[str]: List of files / directories under the path
        """
        try:
            return self.fs.ls(path)
        except Exception as e:
            raise FileOperationError(str(e))

    def rm(self, path: str, recursive: bool = True):
        """Removes a file or directory mentioned in path.

        Args:
            path (str): Path to the file / directory
            recursive (bool): Whether the files and folders nested
            under path are to be removed or not

        Returns:
        """
        try:
            return self.fs.rm(path, recursive=recursive)
        except Exception as e:
            raise FileOperationError(str(e))

    # User of the API is expected to explicitly call close on
    # open files. The library will not be closing any open file
    def close(self, file_handle: Union[AbstractFileSystem]):
        """Close the file that has been opened.

        Note: User of the API is expected to explicitly call close on
            pen files. The library will not be closing any open file
        Args:
            file_handle (Union[AbstractFileSystem]): Actual file handle
            of the file to be closed

        Returns:
        """
        try:
            return file_handle.close()
        except Exception as e:
            raise FileOperationError(str(e))
