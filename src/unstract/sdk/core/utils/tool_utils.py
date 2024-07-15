import json
from hashlib import md5, sha256
from pathlib import Path
from typing import Any

import magic


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
    def get_hash_from_file(file_path: str) -> str:
        """Computes the hash for a file.

        Uses sha256 to compute the file hash through a buffered read.

        Args:
            file_path (str): Path to file that needs to be hashed

        Returns:
            str: SHA256 hash of the file
        """
        h = sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(file_path, "rb", buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        return str(h.hexdigest())

    @staticmethod
    def load_json(file_to_load: str) -> dict[str, Any]:
        """Loads and returns a JSON from a file.

        Args:
            file_to_load (str): Path to the file containing JSON

        Returns:
            dict[str, Any]: The JSON loaded from file
        """
        with open(file_to_load, encoding="utf-8") as f:
            loaded_json: dict[str, Any] = json.load(f)
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

    @staticmethod
    def get_file_mime_type(input_file: Path) -> str:
        """Gets the file MIME type for an input file. Uses libmagic to perform
        the same.

        Args:
            input_file (Path): Path object of the input file

        Returns:
            str: MIME type of the file
        """
        input_file_mime = ""
        with open(input_file, mode="rb") as input_file_obj:
            sample_contents = input_file_obj.read(100)
            input_file_mime = magic.from_buffer(sample_contents, mime=True)
            input_file_obj.seek(0)
        return input_file_mime
