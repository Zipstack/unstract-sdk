import json
import logging
from datetime import datetime
from hashlib import sha256
from typing import Any, Union

import fsspec
import magic
import yaml

from unstract.sdk.exceptions import FileOperationError
from unstract.sdk.file_storage.constants import FileOperationParams, FileSeekPosition
from unstract.sdk.file_storage.fs_interface import FileStorageInterface
from unstract.sdk.file_storage.fs_provider import FileStorageProvider
from unstract.sdk.file_storage.helper import FileStorageHelper

logger = logging.getLogger(__name__)


class FileStorage(FileStorageInterface):
    # This class integrates fsspec library for file operations

    fs: fsspec  # fsspec file system handle

    def __init__(self, provider: FileStorageProvider, **storage_config: dict[str, Any]):
        self.fs = FileStorageHelper.file_storage_init(provider, **storage_config)

    def read(
        self,
        path: str,
        mode: str,
        encoding: str = FileOperationParams.DEFAULT_ENCODING,
        seek_position: int = 0,
        length: int = FileOperationParams.READ_ENTIRE_LENGTH,
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
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def write(
        self,
        path: str,
        mode: str,
        encoding: str = FileOperationParams.DEFAULT_ENCODING,
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
            raise FileOperationError(str(e)) from e

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
            raise FileOperationError(str(e)) from e

    def mkdir(self, path: str, create_parents: bool = True):
        """Create a directory.

        Args:
            path (str): Path of the directory to be created
            create_parents (bool): Specify if parent directories to be created
            if any of the nested directory does not exist
        """
        try:
            self.fs.mkdir(path=path, create_parents=create_parents)
        except FileExistsError:
            logger.debug(f"Path {path} already exists.")
        except Exception as e:
            raise FileOperationError(str(e)) from e

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
            raise FileOperationError(str(e)) from e

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
            raise FileOperationError(str(e)) from e

    def rm(self, path: str, recursive: bool = True):
        """Removes a file or directory mentioned in path.

        Args:
            path (str): Path to the file / directory
            recursive (bool): Whether the files and folders nested
            under path are to be removed or not

        Returns:
            NA
        """
        try:
            return self.fs.rm(path=path, recursive=recursive)
        except FileNotFoundError as e:
            logger.debug(f"Path {path} does not exist.")
            raise e
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def cp(self, src: str, dest: str, overwrite: bool = True):
        """Copies files from source(lpath) path to the destination(rpath) path.

        Args:
            src (str): Path to the source
            dest (str): Path to the destination

        Returns:
            NA
        """
        try:
            return self.fs.cp(src, dest, overwrite=overwrite)
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def size(self, path: str) -> int:
        """Get the size of the file specified in path.

        Args:
            path (str): Path to the file

        Returns:
            int: Size of the file in bytes
        """
        try:
            file_info = self.fs.info(path)
            return file_info["size"]
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def modification_time(self, path: str) -> datetime:
        """Get the last modification time of the file specified in path.

        Args:
            path (str): Path to the file

        Returns:
            datetime: Last modified time in datetime
        """
        try:
            file_info = self.fs.info(path)
            file_mtime = file_info["mtime"]
            if not isinstance(file_mtime, datetime):
                file_mtime = datetime.fromtimestamp(file_mtime)
            return file_mtime
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def mime_type(self, path: str) -> str:
        """Gets the file MIME type for an input file. Uses libmagic to perform
        the same.

        Args:
            path (str): Path of the input file

        Returns:
            str: MIME type of the file
        """
        try:
            sample_contents = self.read(path=path, mode="rb", length=100)
            mime_type = magic.from_buffer(sample_contents, mime=True)
            return mime_type
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def download(self, from_path: str, to_path: str):
        """Downloads the file mentioned in from_path to to_path on the local
        system. The instance calling the method needs to be the FileStorage
        initialised with the remote file system.

        Args:
            from_path (str): Path of the file to be downloaded (remote)
            to_path (str): Path where the file is to be downloaded
            on local system

        Returns:
            NA
        """
        try:
            self.fs.get(rpath=from_path, lpath=to_path)
        except FileNotFoundError as e:
            logger.error(f"Path {from_path} does not exist.")
            raise e
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def upload(self, from_path: str, to_path: str):
        """Uploads the file mentioned in from_path (local system) to to_path
        (remote system). The instance calling the method needs to be the
        FileStorage initialised with the remote file system where the file
        needs to be uploaded.

        Args:
            from_path (str): Path of the file to be uploaded (local)
            to_path (str): Path where the file is to be uploaded (usually remote)

        Returns:
            NA
        """
        try:
            self.fs.put(from_path, to_path)
        except FileNotFoundError as e:
            logger.error(f"Path {from_path} does not exist.")
            raise e
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def glob(self, path: str) -> list[str]:
        """Lists files under path matching the pattern sepcified as part of
        path in the argument.

        Args:
            path (str): path to the directory where files matching the
            specified pattern is to be found
            Eg. a/b/c/*.txt will list all txt files under a/b/c/

        Returns:
            list[str]: List of file names matching any pattern specified
        """
        try:
            return self.fs.glob(path)
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def get_hash_from_file(self, path: str) -> str:
        """Computes the hash for a file.

        Uses sha256 to compute the file hash through a buffered read.

        Args:
            file_path (str): Path to file that needs to be hashed

        Returns:
            str: SHA256 hash of the file
        """

        try:
            h = sha256()
            b = bytearray(128 * 1024)
            mv = memoryview(b)
            with self.fs.open(path) as f:
                while n := f.readinto(mv):
                    h.update(mv[:n])
            return str(h.hexdigest())
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def json_dump(
        self,
        path: str,
        data: Union[str, bytes],
        **kwargs: dict[Any, Any],
    ):
        """Dumps data into the given file specified by path.

        Args:
            path (str): Path to file where JSON is to be dumped
            data (bytes|str): data to be written to the file
            **kwargs (dict): Any other additional arguments
        """
        try:
            with self.fs.open(path=path, mode="w", encoding="utf-8") as f:
                json.dump(data, f, **kwargs)
        except Exception as e:
            raise FileOperationError(str(e)) from e

    def yaml_dump(
        self,
        path: str,
        data: Union[str, bytes],
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs: dict[Any, Any],
    ):
        """Dumps data into the given file specified by path.

        Args:
            path (str): Path to file where yml is to be dumped
            data (bytes|str): data to be written to the file
            mode (str): write modes
            encoding (str): Encoding to be used while writing the file
            **kwargs (dict): Any other additional arguments
        """
        try:
            with self.fs.open(path=path, mode=mode, encoding=encoding) as f:
                yaml.dump(data, f, **kwargs)
        except Exception as e:
            raise FileOperationError(str(e)) from e
