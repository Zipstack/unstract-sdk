from typing import Any, Optional

import requests
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

    def answer_prompt(self, payload: dict) -> dict:
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
        result = {
            "status": "ERROR",
            "error": "",
            "cost": 0,
            "structure_output": "",
        }
        # TODO : Implement authorization for prompt service
        # headers = {"Authorization": f"Bearer {self.bearer_token}"}
        # Upload file to platform
        url = f"{self.base_url}/answer-prompt"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                self.tool.stream_log(
                    f"Error while fetching response: {response.text}",
                    level=LogLevel.ERROR,
                )
                result["error"] = response.text
                return result
            else:
                result["status"] = "OK"
                result["structure_output"] = response.text
        except Exception as e:
            self.tool.stream_log(
                f"Error while fetching response for prompt: {e}",
                level=LogLevel.ERROR,
            )
            result["error"] = str(e)
            return result
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
