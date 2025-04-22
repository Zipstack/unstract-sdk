import logging
from typing import Any

import requests
from requests import ConnectionError, RequestException, Response
from unstract.sdk.constants import (
    LogLevel,
    MimeType,
    RequestHeader,
    ToolEnv,
)
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
        request_id: str | None = None,
    ) -> None:
        """Class to interact with prompt-service.

        Args:
            tool (AbstractTool): Instance of AbstractTool
            prompt_host (str): Host of platform service
            prompt_port (str): Port of platform service
            is_public_call (bool): Whether the call is public. Defaults to False
        """
        self.tool = tool
        self.base_url = SdkHelper.get_platform_base_url(prompt_host, prompt_port)
        self.is_public_call = is_public_call
        self.request_id = request_id
        if not is_public_call:
            self.bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)

    @log_elapsed(operation="ANSWER_PROMPTS")
    def answer_prompt(
        self,
        payload: dict[str, Any],
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url_path = "answer-prompt"
        if self.is_public_call:
            url_path = "answer-prompt-public"
        return self._call_service(
            url_path=url_path, payload=payload, params=params, headers=headers
        )

    @log_elapsed(operation="INDEX")
    def index(
        self,
        payload: dict[str, Any],
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url_path = "index"
        if self.is_public_call:
            url_path = "index-public"
        return self._call_service(
            url_path=url_path,
            payload=payload,
            params=params,
            headers=headers,
        )

    @log_elapsed(operation="EXTRACT")
    def extract(
        self,
        payload: dict[str, Any],
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url_path = "extract"
        if self.is_public_call:
            url_path = "extract-public"
        return self._call_service(
            url_path=url_path,
            payload=payload,
            params=params,
            headers=headers,
        )

    def single_pass_extraction(
        self,
        payload: dict[str, Any],
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self._call_service(
            url_path="single-pass-extraction",
            payload=payload,
            params=params,
            headers=headers,
        )

    def summarize(
        self,
        payload: dict[str, Any],
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self._call_service(
            url_path="summarize",
            payload=payload,
            params=params,
            headers=headers,
        )

    def _get_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        """Get default headers for requests.

        Returns:
            dict[str, str]: Default headers including request ID and authorization
        """
        request_headers = {RequestHeader.REQUEST_ID: self.request_id}
        if self.is_public_call:
            return request_headers
        request_headers.update(
            {RequestHeader.AUTHORIZATION: f"Bearer {self.bearer_token}"}
        )

        if headers:
            request_headers.update(headers)
        return request_headers

    def _call_service(
        self,
        url_path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        method: str = "POST",  # Added method parameter with default value "POST"
    ) -> dict[str, Any]:
        """Communicates to prompt service to fetch response for the prompt.

        Only POST calls are made to prompt-service though functionality exists.

        Args:
            url_path (str): URL path to the service endpoint
            payload (dict, optional): Payload to send in the request body
            params (dict, optional): Query parameters to include in the request
            headers (dict, optional): Headers to include in the request
            method (str): HTTP method to use for the request (GET or POST)

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

        req_headers = self._get_headers(headers)

        response: Response = Response()
        try:
            if method.upper() == "POST":
                response = requests.post(
                    url=url, json=payload, params=params, headers=req_headers
                )
            elif method.upper() == "GET":
                response = requests.get(url=url, params=params, headers=req_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            if method.upper() == "POST":
                result["status"] = "OK"
                result["structure_output"] = response.text
                result["status_code"] = 200
            elif method.upper() == "GET":
                return response.json()
        except ConnectionError as connect_err:
            msg = "Unable to connect to prompt service. "
            self.tool.stream_log(msg, level=LogLevel.ERROR)
            logger.error(f"{msg}: {connect_err}")
            result["error"] = msg
            result["status_code"] = response.status_code
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
