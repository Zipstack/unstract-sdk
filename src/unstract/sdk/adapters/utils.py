from pathlib import Path

import filetype
import magic
from requests import Response
from requests.exceptions import RequestException

from unstract.sdk.adapters.constants import Common
from unstract.sdk.file_storage import FileStorage, FileStorageProvider


class AdapterUtils:
    @staticmethod
    def get_msg_from_request_exc(
        err: RequestException,
        message_key: str,
        default_err: str = Common.DEFAULT_ERR_MESSAGE,
    ) -> str:
        """Gets the message from the RequestException.

        Args:
            err_response (Response): Error response from the exception
            message_key (str): Key from response containing error message

        Returns:
            str: Error message returned by the server
        """
        if hasattr(err, "response"):
            err_response: Response = err.response  # type: ignore
            if err_response.headers["Content-Type"] == "application/json":
                err_json = err_response.json()
                if message_key in err_json:
                    return str(err_json[message_key])
            elif err_response.headers["Content-Type"] == "text/plain":
                return err_response.text  # type: ignore
        return default_err

    # ToDo: get_file_mime_type() to be removed once migrated to FileStorage
    # FileStorage has mime_type() which could be used instead.
    @staticmethod
    def get_file_mime_type(
        input_file: Path,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        """Gets the file MIME type for an input file. Uses libmagic to perform
        the same.

        Args:
            input_file (Path): Path object of the input file

        Returns:
            str: MIME type of the file
        """
        sample_contents = fs.read(path=input_file, mode="rb", length=100)
        input_file_mime = magic.from_buffer(sample_contents, mime=True)
        return input_file_mime

    @staticmethod
    def guess_extention(
        input_file_path: str,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        """Returns the extention of the file passed.

        Args:
            input_file_path (str): String holding the path

        Returns:
            str: File extention
        """
        input_file_extention = ""
        sample_contents = fs.read(path=input_file_path, mode="rb", length=100)
        if sample_contents:
            file_type = filetype.guess(sample_contents)
            input_file_extention = file_type.EXTENSION
        return input_file_extention
