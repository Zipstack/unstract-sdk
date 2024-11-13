import json
import warnings
from hashlib import md5, sha256
from pathlib import Path
from typing import Any

import magic

from unstract.sdk.file_storage import FileStorage, FileStorageProvider


class ToolUtils:
    """Class containing utility methods."""

    @staticmethod
    def hash_str(string_to_hash: Any, hash_method: str = "sha256") -> str:
        """Computes the hash for a given input string.

        Useful to hash strings needed for caching and other purposes.
        Hash method defaults to "md5"

        Args:
            string_to_hash (str): String to be hashed
            hash_method (str): Hash hash_method to use, supported ones
                - "md5"

        Returns:
            str: Hashed string
        """
        if hash_method == "md5":
            if isinstance(string_to_hash, bytes):
                return str(md5(string_to_hash).hexdigest())
            return str(md5(string_to_hash.encode()).hexdigest())
        elif hash_method == "sha256":
            if isinstance(string_to_hash, (bytes, bytearray)):
                return str(sha256(string_to_hash).hexdigest())
            return str(sha256(string_to_hash.encode()).hexdigest())
        else:
            raise ValueError(f"Unsupported hash_method: {hash_method}")

    @staticmethod
    def get_hash_from_file(
        file_path: str,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        """Computes the hash for a file.

        Uses sha256 to compute the file hash through a buffered read.

        Args:
            file_path (str): Path to file that needs to be hashed

        Returns:
            str: SHA256 hash of the file
        """

        # Adding the following DeprecationWarning manually as the package "deprecated"
        # does not support deprecation on static methods.
        warnings.warn(
            "`get_hash_from_file` is deprecated. "
            "Use `FileStorage get_hash_from_file()` instead.",
            DeprecationWarning,
        )
        return fs.get_hash_from_file(path=file_path)

    @staticmethod
    def load_json(
        file_to_load: str,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> dict[str, Any]:
        """Loads and returns a JSON from a file.

        Args:
            file_to_load (str): Path to the file containing JSON

        Returns:
            dict[str, Any]: The JSON loaded from file
        """
        file_contents: str = fs.read(path=file_to_load, mode="r", encoding="utf-8")
        loaded_json: dict[str, Any] = json.loads(file_contents)
        return loaded_json

    @staticmethod
    def json_to_str(json_to_dump: dict[str, Any]) -> str:
        """Helps convert the JSON to a string. Useful for dumping the JSON to a
        file.

        Args:
            json_to_dump (dict[str, Any]): Input JSON to dump

        Returns:
            str: String representation of the JSON
        """
        compact_json = json.dumps(json_to_dump, separators=(",", ":"))
        return compact_json

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
        input_file_mime = ""
        sample_contents = fs.read(path=input_file, mode="rb", length=100)
        input_file_mime = magic.from_buffer(sample_contents, mime=True)
        return input_file_mime

    @staticmethod
    def get_file_size(
        input_file: Path,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> int:
        """Gets the file size in bytes for an input file.
        Args:
            input_file (Path): Path object of the input file

        Returns:
            str: MIME type of the file
        """
        file_length = fs.size(path=input_file)
        return file_length

    @staticmethod
    def str_to_bool(string: str) -> bool:
        """String value of boolean to boolean.

        Useful while parsing envs to bool.

        Args:
            string (str): value like "true", "True" etc..

        Returns:
            bool
        """
        return string.lower() == "true"

    # Used the same function from LLM Whisperer
    @staticmethod
    def calculate_page_count(
        pages_string: str, max_page: int = 0, min_page: int = 1
    ) -> int:
        """Calculates the total number of pages based on the input string of
        page numbers or ranges.

        Parses the input 'pages_string' to extract individual page numbers or
        ranges separated by commas.
        Supports ranges like '1-5' or open-ended ranges like '4-'.
        The 'max_page' parameter defines the upper limit for page numbers.
        The 'min_page' parameter defines the lower limit for page numbers.

        Args:
            pages_string (str): String containing page numbers or ranges
            separated by commas
            max_page (int): Upper limit for page numbers (default is 0)
            min_page (int): Lower limit for page numbers (default is 1)

        Returns:
            int: Total count of individual pages extracted from the input string
        """
        if not pages_string:
            return max_page
        pages_list: list[int] = []
        parts = pages_string.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                if part.startswith("-"):  # e.g., "-5"
                    end = int(part[1:])
                    end = min(end, max_page)
                    pages_list.extend(range(min_page, end + 1))
                elif part.endswith("-"):  # e.g., "4-"
                    start = int(part[:-1])
                    if start < 0:
                        start = 0
                    if max_page is None:
                        raise ValueError(
                            "max_page must be defined for open-ended ranges like '4-'"
                        )
                    pages_list.extend(range(start, max_page + 1))
                else:  # e.g., "1-5"
                    start, end = map(int, part.split("-"))
                    if start < 0:
                        start = 0
                    if end > max_page:
                        end = max_page
                    pages_list.extend(range(start, end + 1))
            else:
                pages_list.append(int(part))
        return len(pages_list)
