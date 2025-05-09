from typing import Any

import requests
from requests import ConnectionError, RequestException, Response
from unstract.sdk.constants import (
    MimeType,
    PromptStudioKeys,
    RequestHeader,
    ToolEnv,
)
from unstract.sdk.helper import SdkHelper
from unstract.sdk.tool.base import BaseTool


class PlatformBase:
    """Base class to handle interactions with Unstract's platform service.

    Notes:
        - PLATFORM_SERVICE_API_KEY environment variable is required.
    """

    def __init__(
        self,
        tool: BaseTool,
        platform_host: str,
        platform_port: str,
        request_id: str | None = None,
    ) -> None:
        """Constructor for base class to connect to platform service.

        Args:
            tool (AbstractTool): Instance of AbstractTool
            platform_host (str): Host of platform service
            platform_port (str): Port of platform service

        Notes:
            - PLATFORM_SERVICE_API_KEY environment variable is required.
        """
        self.tool = tool
        self.base_url = SdkHelper.get_platform_base_url(platform_host, platform_port)
        self.bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)
        self.request_id = request_id


class PlatformHelper(PlatformBase):
    """Implementation of `PlatformBase`.

    Notes:
        - PLATFORM_SERVICE_API_KEY environment variable is required.
    """

    def __init__(
        self,
        tool: BaseTool,
        platform_host: str,
        platform_port: str,
        request_id: str | None = None,
    ) -> None:
        """Constructor for helper to connect to platform service.

        Args:
            tool (AbstractTool): Instance of AbstractTool
            platform_host (str): Host of platform service
            platform_port (str): Port of platform service
            request_id (str | None, optional): Request ID for the service.
                Defaults to None.
        """
        super().__init__(
            tool=tool,
            platform_host=platform_host,
            platform_port=platform_port,
            request_id=request_id,
        )

    def _get_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        """Get default headers for requests.

        Returns:
            dict[str, str]: Default headers including request ID and authorization
        """
        request_headers = {
            RequestHeader.REQUEST_ID: self.request_id,
            RequestHeader.AUTHORIZATION: f"Bearer {self.bearer_token}",
        }
        if headers:
            request_headers.update(headers)
        return request_headers

    def _call_service(
        self,
        url_path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Talks to platform-service to make GET / POST calls.

        Only GET calls are made to platform-service though functionality exists.

        Args:
            url_path (str): URL path to the service endpoint
            payload (dict, optional): Payload to send in the request body
            params (dict, optional): Query parameters to include in the request
            headers (dict, optional): Headers to include in the request
            method (str): HTTP method to use for the request (GET or POST)

        Returns:
            dict: Response from the platform service

            Sample Response:
            {
                "status": "OK",
                "error": "",
                structure_output : {}
            }
        """
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
        except ConnectionError as connect_err:
            msg = "Unable to connect to platform service. Please contact admin."
            msg += " \n" + str(connect_err)
            self.tool.stream_error_and_exit(msg)
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
            self.tool.stream_error_and_exit(
                f"Error from platform service. {error_message}"
            )
        return response.json()

    def get_platform_details(self) -> dict[str, Any] | None:
        """Obtains platform details associated with the platform key.

        Currently helps fetch organization ID related to the key.

        Returns:
            Optional[dict[str, Any]]: Dictionary containing the platform details
        """
        response = self._call_service(
            url_path="platform_details",
            payload=None,
            params=None,
            headers=None,
            method="GET",
        )
        return response.get("details")

    def get_prompt_studio_tool(self, prompt_registry_id: str) -> dict[str, Any]:
        """Get exported custom tool by the help of unstract DB tool.

        Args:
            prompt_registry_id (str): ID of the prompt_registry_id
        Required env variables:
            PLATFORM_HOST: Host of platform service
            PLATFORM_PORT: Port of platform service
        """
        query_params = {PromptStudioKeys.PROMPT_REGISTRY_ID: prompt_registry_id}
        return self._call_service(
            url_path="custom_tool_instance",
            payload=None,
            params=query_params,
            headers=None,
            method="GET",
        )
