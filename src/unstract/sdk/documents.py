from typing import Any, Optional

import requests
from unstract.connectors.filesystems.unstract_file_system import (
    AbstractFileSystem,
)
from unstract.sdk.constants import LogLevel
from unstract.sdk.platform import PlatformBase
from unstract.sdk.tool.base import BaseTool


class ToolDocs(PlatformBase):
    """Class to handle documents for Unstract Tools.

    Notes:
        - PLATFORM_SERVICE_API_KEY environment variable is required.
    """

    def __init__(self, tool: BaseTool, platform_host: str, platform_port: int):
        """
        Args:
            tool (AbstractTool): Instance of AbstractTool
            platform_host (str): The host of the platform.
            platform_port (int): The port of the platform.

        Notes:
            - PLATFORM_SERVICE_API_KEY environment variable is required.
            - The platform_host and platform_port are the host and
                port of the platform service.

        """
        super().__init__(
            tool=tool, platform_host=platform_host, platform_port=platform_port
        )

    def _upload_file(
        self, file_path: str, fsspec_obj: AbstractFileSystem
    ) -> dict[str, Any]:
        """Uploads a file to the platform service for further processing.

        Args:
            file_path (str): Path to file to upload
            fsspec_obj (AbstractFileSystem): Fsspec object that's configured
                to access the file

        Returns:
            dict: The result of the upload operation.

        Notes:
            Sample return dict:
            {
                "status": "OK",
                "error": "",
                "cost": 0,
                "unique_file_id": "9b44826ff1ed4dfd5dda762776acd4dd"
            }
        """
        result = {
            "status": "ERROR",
            "error": "",
            "cost": 0,
            "unique_file_id": "",
        }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        # Upload file to platform
        url = f"{self.base_url}/upload"
        try:
            with fsspec_obj.open(file_path, "rb") as file:
                files = {"file": (file_path, file)}
                response = requests.post(url, files=files, headers=headers)
                if response.status_code == 200:
                    self.tool.stream_log(
                        f"Successfully uploaded file: {file_path}"
                    )
                else:
                    self.tool.stream_log(
                        "Error while uploading file: "
                        f"{file_path} / {response.text}",
                        level=LogLevel.ERROR,
                    )
                    result["error"] = response.text
                    return result
                result["status"] = "OK"
                result["unique_file_id"] = response.json()["upload_file_id"]
        except Exception as e:
            self.tool.stream_log(
                f"Error while uploading file: {file_path} / {e}",
                level=LogLevel.ERROR,
            )
            result["error"] = str(e)
            return result
        self.tool.stream_log(f"Uploaded file ID: {result['unique_file_id']}")
        return result

    # def index_file(
    #     self,
    #     workflow_id: str,
    #     embedding_type: str,
    #     vector_db: str,
    #     file_path: str,
    #     fsspec_obj: AbstractFileSystem,
    #     overwrite: bool = False,
    # ) -> dict:
    #     """Indexes a file to the platform.

    #     Args:
    #         workflow_id (str): The workflow id.
    #         embedding_type (str): The embedding type.
    #             Supported values:
    #                 - "Azure OpenAI"
    #         vector_db (str): The vector db.
    #             Supported values:
    #                 - "Postgres pg_vector"
    #         file_path (str): The path to the file to index.
    #         overwrite (bool): Whether to overwrite the file if it already
    #             exists. The default is False.

    #     Returns:
    #         dict: The result of the indexing operation.

    #     Notes:
    #         Sample return dict:
    #         {
    #             "status": "OK",
    #             "error": "",
    #             "cost": 746,
    #             "unique_file_id": "9b44826ff1ed4dfd5dda762776acd4dd"
    #         }
    #     """
    #     result = {"status": "ERROR", "error": "", "cost": 0, "unique_file_id": ""}  # noqa: E501
    #     upload_result = self._upload_file(file_path=file_path, fsspec_obj=fsspec_obj) # noqa: E501
    #     if upload_result["status"] == "ERROR":
    #         return upload_result
    #     upload_file_id = upload_result["unique_file_id"]
    #     self.tool.stream_log(f"Indexing file: {file_path}")

    #     payload = {
    #         "workflow_id": workflow_id,
    #         "upload_file_id": upload_file_id,
    #         "embedding_type": embedding_type,
    #         "vector_db": vector_db,
    #         "file_path": file_path,
    #     }
    #     url = f"{self.base_url}/indexer?overwrite={overwrite}"
    #     headers = {"Authorization": f"Bearer {self.bearer_token}"}
    #     response = requests.post(url, json=payload, headers=headers)
    #     if response.status_code == 200:
    #         self.tool.stream_log(f"Successfully indexed file: {file_path}")
    #         result["status"] = "OK"
    #         result["cost"] = response.json()["cost"]
    #         result["unique_file_id"] = response.json()["unique_file_id"]
    #         return result
    #     else:
    #         self.tool.stream_log(
    #             f"Error while indexing file: {file_path} / {response.text}",
    #             level=LogLevel.ERROR,
    #         )
    #         result["error"] = response.text
    #         return result

    def insert(
        self,
        workflow_id: str,
        unique_file_id: str,
        filename: str,
        filetype: str,
        summary: str,
        embedding_tokens: int,
        llm_tokens: int,
        vector_db: str,
    ):
        """Inserts data for a document into the platform.

        Notes:
            - This method is typically called by the tool's index() method.
                It is not typically called directly.

        Args:
            workflow_id (str): The project id.
            unique_file_id (str): The unique file id.
            filename (str): The filename.
            filetype (str): The filetype. Example: "application/pdf"
            summary (str): The summary. Note: Currently not used.
            embedding_tokens (int): The number of tokens used for the embedding.
            llm_tokens (int): The number of tokens used for the LLM.
            vector_db (str): The vector db.
                Supported values:
                    - "Postgres pg_vector"

        Returns:
            bool: Whether the operation was successful.
        """
        url = f"{self.base_url}/document"
        json = {
            "workflow_id": workflow_id,
            "unique_file_id": unique_file_id,
            "filename": filename,
            "filetype": filetype,
            "summary": summary,
            "embedding_tokens": embedding_tokens,
            "llm_tokens": llm_tokens,
            "vector_db": vector_db,
        }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.post(url, json=json, headers=headers)

        if response.status_code == 200:
            self.tool.stream_log(
                f"Successfully inserted data for key: {unique_file_id}"
            )
            return True
        else:
            self.tool.stream_log(
                f"Error while inserting data for key: {unique_file_id} "
                f"/ {response.reason} / {response.text}",
                level=LogLevel.ERROR,
            )
            return False

    def get(self, workflow_id: str, unique_file_id: str) -> Optional[dict]:
        """Retrieves data for a document from the platform.

        Args:
            workflow_id (str): The project id.
            unique_file_id (str): The unique file id.

        Returns:
            Optional[dict]: The data for the document.
        """
        url = (
            f"{self.base_url}/document?workflow_id={workflow_id}"
            f"&unique_file_id={unique_file_id}"
        )
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            self.tool.stream_log(
                f"Successfully retrieved data for key: {unique_file_id}"
            )
            return response.json()
        elif response.status_code == 404:
            self.tool.stream_log(
                f"Data not found for key: {unique_file_id}", level=LogLevel.WARN
            )
            return None
        else:
            self.tool.stream_log(
                "Error while retrieving data for key: "
                f"{unique_file_id} / {response.reason}",
                level=LogLevel.ERROR,
            )
            return None

    def delete(self, workflow_id: str, unique_file_id: str):
        """Deletes data for a document from the platform.

        Notes:
            - This method is used internally. Do not call this method directly
                unless you know what you are doing.

        Args:
            workflow_id (str): The project id.
            unique_file_id (str): The unique file id.

        Returns:
            bool: Whether the operation was successful.
        """
        url = (
            f"{self.base_url}/document?workflow_id={workflow_id}"
            f"&unique_file_id={unique_file_id}"
        )
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            self.tool.stream_log(
                f"Successfully deleted data for key: {unique_file_id}"
            )
            return True
        else:
            self.tool.stream_log(
                "Error while deleting data for key: "
                f"{unique_file_id} / {response.reason}",
                level=LogLevel.ERROR,
            )
            return False

    def answer_prompt(
        self,
        workflow_id: str,
        embedding_type: str,
        vector_db: str,
        file_path: str,
        fsspec_obj: AbstractFileSystem,
        prompt: dict[str, str],
    ) -> dict:
        """Fetches answers from the indexed document for the passed questions.
        Args:
            workflow_id (str): The project id.
            embedding_type (str): The embedding type.
                Supported values:
                    - "Azure OpenAI"
            vector_db (str): The vector db.
                Supported values:
                    - "Postgres pg_vector"
            file_path (str): The path to the file to index.
            prompt (dict): Dict storing the key value pairs of the prompts
        Returns:
            Dict: Key value pairs of the question and the corresponding keys
        Notes:
            Sample return dict:
            {
                "status": "OK",
                "error": "",
                "cost": 746,
                "answers" : "",
                "unique_file_id" : "",
            }
        """
        result = {
            "status": "ERROR",
            "error": "",
            "cost": 0,
            "unique_file_id": "",
        }
        upload_result = self._upload_file(
            file_path=file_path, fsspec_obj=fsspec_obj
        )
        if upload_result["status"] == "ERROR":
            return upload_result
        # Load Index
        payload = {
            "workflow_id": workflow_id,
            "embedding_type": embedding_type,
            "vector_db": vector_db,
            "file_path": file_path,
            "prompt": prompt,
        }
        self.tool.stream_log("Loading index and Fetching answers")
        url = f"{self.base_url}/prompt-responder"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            self.tool.stream_log(
                f"Successfully fetched response for the prompt : {prompt}"
            )
            result["status"] = "OK"
            result["answers"] = response.json()["answers"]
            result["unique_file_id"] = response.json()["unique_file_id"]
            result["cost"] = response.json()["cost"]
            return result
        else:
            self.tool.stream_log(
                "Error while loading indexed file and fetching response "
                f"for the prompt: {file_path} / {response.text}",
                level="ERROR",
            )
            result["error"] = response.text
            return result
