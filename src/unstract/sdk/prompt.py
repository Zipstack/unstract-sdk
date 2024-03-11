from typing import Any, Optional

import requests
from requests import RequestException, Response

from unstract.sdk.constants import LogLevel, PromptStudioKeys, ToolEnv
from unstract.sdk.helper import SdkHelper
from unstract.sdk.tool.base import BaseTool


class PromptTool:
    """Class to handle prompt service methods for Unstract Tools."""

    def __init__(
        self,
        tool: BaseTool,
        prompt_host: str,
        prompt_port: str,
    ) -> None:
        """
        Args:
            tool (AbstractTool): Instance of AbstractTool
            prompt_host (str): Host of platform service
            prompt_host (str): Port of platform service

        """
        self.tool = tool
        self.base_url = SdkHelper.get_platform_base_url(
            prompt_host, prompt_port
        )
        self.bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)

    def answer_prompt(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_call("answer-prompt", payload)

    def single_pass_extraction(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post_call("single-pass-extraction", payload)

    def _post_call(
        self, url_path: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Invokes and communicates to prompt service to fetch response for the
        prompt.

        Args:
            file_name (str): File in which the prompt is processed
            outputs (dict): dict of all input data for the tool
            tool_id (str): Unique ID of the tool to be processed

        Returns:
            Sample return dict:
            {
                "status": "OK",
                "error": "",
                "cost": 0,
                structure_output : {}
            }
        """
        result: dict[str, Any] = {
            "status": "ERROR",
            "error": "",
            "cost": 0,
            "structure_output": "",
        }
        url: str = f"{self.base_url}/{url_path}"
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
        try:
            # TODO: Review timeout value
            response: Response = requests.post(
                url, json=payload, headers=headers, timeout=600
            )
            response.raise_for_status()
            result["status"] = "OK"
            result["structure_output"] = response.text
        except RequestException as e:
            result["error"] = f"Error occurred: {e}"
            self.tool.stream_log(
                f"Error while fetching response for prompt: {result['error']}",
                level=LogLevel.ERROR,
            )
        return result

    @staticmethod
    def get_exported_tool(
        tool: BaseTool, prompt_registry_id: str
    ) -> Optional[dict[str, Any]]:
        """Get exported custom tool by the help of unstract DB tool.

        Args:
            prompt_registry_id (str): ID of the prompt_registry_id
            tool (AbstractTool): Instance of AbstractTool
        Required env variables:
            PLATFORM_HOST: Host of platform service
            PLATFORM_PORT: Port of platform service
        """
        platform_host = tool.get_env_or_die(ToolEnv.PLATFORM_HOST)
        platform_port = tool.get_env_or_die(ToolEnv.PLATFORM_PORT)

        tool.stream_log("Connecting to DB and getting exported tool metadata")
        base_url = SdkHelper.get_platform_base_url(platform_host, platform_port)
        bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)

        url = f"{base_url}/custom_tool_instance"
        query_params = {PromptStudioKeys.PROMPT_REGISTRY_ID: prompt_registry_id}
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers, params=query_params)
        if response.status_code == 200:
            adapter_data: dict[str, Any] = response.json()
            tool.stream_log(
                "Successfully retrieved metadata for the exported "
                f"tool: {prompt_registry_id}"
            )
            return adapter_data

        elif response.status_code == 404:
            tool.stream_error_and_exit(
                f"Exported tool {prompt_registry_id} is not found"
            )
            return None

        else:
            tool.stream_error_and_exit(
                f"Error while retrieving tool metadata "
                "for the exported tool: "
                f"{prompt_registry_id} / {response.reason}"
            )
            return None
