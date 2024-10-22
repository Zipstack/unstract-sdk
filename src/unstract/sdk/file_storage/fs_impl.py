from typing import Any, Union

import fsspec

from unstract.sdk.exceptions import FileOperationError
from unstract.sdk.file_storage.constants import Common, FileSeekPosition
from unstract.sdk.file_storage.fs_interface import FileStorageInterface
from unstract.sdk.file_storage.helper import FileStorageHelper


class FileStorage(FileStorageInterface):
    # This class integrates fsspec library for file operations

    fs: fsspec  # fsspec file system handle

    def __init__(self, provider, credentials: dict[str, Any] = {}):
        self.fs = FileStorageHelper.file_storage_init(
            provider=provider, credentials=credentials
        )

    def read(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        length: int = Common.FULL,
    ) -> Union[bytes, str]:
        """Read the file pointed to by the file_handle.

        Args:
            path (str): Path to the file to be opened
            mode (str): Mode in whicg the file is to be opened. Usual options
                        include r, rb, w and wb
            encoding (str): Encoding type like utf-8 or utf-16
            seek_position (int): Position to start reading from
            length (int): Number of bytes to be read. Default is full
            file content.

        Returns:
            Union[bytes, str] - File contents in bytes/string based on the opened mode
        """
        try:
            with self.fs.open(path=path, mode=mode, encoding=encoding) as file_handle:
                if seek_position > 0:
                    file_handle.seek(seek_position)
                return file_handle.read(length)
        except Exception as e:
            raise FileOperationError(str(e))

    def write(
        self,
        path: str,
        mode: str,
        encoding: str = Common.DEFAULT_ENCODING,
        seek_position: int = 0,
        data: Union[bytes, str] = "",
    ) -> int:
        """Write data in the file pointed to by the file-handle.

        Args:
            path (str): Path to the file to be opened
            mode (str): Mode in whicg the file is to be opened. Usual options
                        include r, rb, w and wb
            encoding (str): Encoding type like utf-8 or utf-16
            seek_position (int): Position to start writing from
            data (Union[bytes, str]): Contents to be written

        Returns:
            int: Number of bytes that were successfully written to the file
        """
        try:
            with self.fs.open(path=path, mode=mode, encoding=encoding) as file_handle:
                return file_handle.write(data)
        except Exception as e:
            raise FileOperationError(str(e))

    def seek(
        self,
        path: str,
        location: int = 0,
        position: FileSeekPosition = FileSeekPosition.START,
    ) -> int:
        """Place the file pointer to the mentioned location in the file
        relative to the position.

        Args:
            path (str): path of the file
            location (int): Nth byte position. To be understood in relation to
            the arg "position"
            position (FileSeekPosition): from start of file, current location
            or end of file

        Returns:
            int: file pointer location after seeking to the mentioned position
        """
        try:
            with self.fs.open(path=path, mode="rb") as file_handle:
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
            self.fs.mkdir(path=path, create_parents=create_parents)
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
            return self.fs.rm(path=path, recursive=recursive)
        except Exception as e:
            raise FileOperationError(str(e))

    def cp(self, lpath: str, rpath: str):
        """Copies files from source(lpath) path to the destination(rpath) path.

        Args:
            lpath (str): Path to the source
            rpath (str): Path to the destination
        """
        try:
            return self.fs.put(lpath, rpath)
        except Exception as e:
            raise FileOperationError(str(e))
