import logging
from typing import Any, Optional

import requests
from requests import ConnectionError, RequestException, Response

from unstract.sdk.constants import LogLevel, MimeType, PromptStudioKeys, ToolEnv
from unstract.sdk.helper import SdkHelper
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.common_utils import log_elapsed

logger = logging.getLogger(__name__)


class PromptTool:
    """Class to handle prompt service methods for Unstract Tools."""

    def __init__(
        self,
        tool: BaseTool,
        prompt_host: str,
        prompt_port: str,
        is_public_call: bool = False,
    ) -> None:
        """
        Args:
            tool (AbstractTool): Instance of AbstractTool
            prompt_host (str): Host of platform service
            prompt_host (str): Port of platform service
        """
        self.tool = tool
        self.base_url = SdkHelper.get_platform_base_url(prompt_host, prompt_port)
        self.is_public_call = is_public_call
        if not is_public_call:
            self.bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)

    @log_elapsed(operation="ANSWER_PROMPTS")
    def answer_prompt(
        self,
        payload: dict[str, Any],
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        url_path = "answer-prompt"
        if self.is_public_call:
            url_path = "answer-prompt-public"
        return self._post_call(
            url_path=url_path, payload=payload, params=params, headers=headers
        )
    
    @log_elapsed(operation="INDEX")
    def index(
        self, 
        payload: dict[str, Any], 
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        url_path = "index"
        if self.is_public_call:
            url_path = "index-public"
        return self._post_call(
            url_path=url_path,
            payload=payload,
            params=params,
            headers=headers,
        )
    
    @log_elapsed(operation="EXTRACT")
    def extract(
        self, 
        payload: dict[str, Any], 
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        url_path = "extract"
        if self.is_public_call:
            url_path = "extract-public"
        return self._post_call(
            url_path=url_path,
            payload=payload,
            params=params,
            headers=headers,
        )

    def single_pass_extraction(
        self,
        payload: dict[str, Any],
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        return self._post_call(
            url_path="single-pass-extraction",
            payload=payload,
            params=params,
            headers=headers,
        )

    def summarize(
        self,
        payload: dict[str, Any],
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        return self._post_call(
            url_path="summarize",
            payload=payload,
            params=params,
            headers=headers,
        )

    def _post_call(
        self,
        url_path: str,
        payload: dict[str, Any],
        params: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Invokes and communicates to prompt service to fetch response for the
        prompt.

        Args:
            url_path (str): URL path to the service endpoint
            payload (dict): Payload to send in the request body
            params (dict, optional): Query parameters to include in the request
            headers (dict, optional): Headers to include in the request

        Returns:
            dict: Response from the prompt service

            Sample Response:
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
            "status_code": 500,
        }
        url: str = f"{self.base_url}/{url_path}"

        default_headers = {}

        if not self.is_public_call:
            default_headers = {"Authorization": f"Bearer {self.bearer_token}"}

        if headers:
            default_headers.update(headers)

        response: Response = Response()
        try:
            response = requests.post(
                url=url, json=payload, params=params, headers=default_headers
            )
            response.raise_for_status()
            result["status"] = "OK"
            result["structure_output"] = response.text
            result["status_code"] = 200
        except ConnectionError as connect_err:
            msg = "Unable to connect to prompt service. Please contact admin."
            self._stringify_and_stream_err(connect_err, msg)
            result["error"] = msg
        except RequestException as e:
            # Extract error information from the response if available
            error_message = str(e)
            content_type = response.headers.get("Content-Type", "").lower()
            if MimeType.JSON in content_type:
                response_json = response.json()
                if "error" in response_json:
                    error_message = response_json["error"]
            elif response.text:
                error_message = response.text
            result["error"] = error_message
            result["status_code"] = response.status_code
            self.tool.stream_log(
                f"Error while fetching response for prompt: {result['error']}",
                level=LogLevel.ERROR,
            )
        return result

    def _stringify_and_stream_err(self, err: RequestException, msg: str) -> None:
        error_message = str(err)
        trace = f"{msg}: {error_message}"
        self.tool.stream_log(trace, level=LogLevel.ERROR)
        logger.error(trace)

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
        base_url = SdkHelper.get_platform_base_url(platform_host, platform_port)
        bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)
        url = f"{base_url}/custom_tool_instance"
        query_params = {PromptStudioKeys.PROMPT_REGISTRY_ID: prompt_registry_id}
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers, params=query_params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            tool.stream_error_and_exit(
                f"Exported tool '{prompt_registry_id}' is not found"
            )
            return None
        else:
            tool.stream_error_and_exit(
                f"Error while retrieving tool metadata "
                "for the exported tool: "
                f"{prompt_registry_id} / {response.reason}"
            )
            return None
