from typing import Any, Optional

import requests

from unstract.sdk.constants import LogLevel, ToolEnv
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
    ) -> None:
        """
        Args:
            tool (AbstractTool): Instance of AbstractTool
            platform_host (str): Host of platform service
            platform_port (str): Port of platform service

        Notes:
            - PLATFORM_SERVICE_API_KEY environment variable is required.
        """
        self.tool = tool
        self.base_url = SdkHelper.get_platform_base_url(
            platform_host, platform_port
        )
        self.bearer_token = tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)


class PlatformHelper(PlatformBase):
    """Implementation of `UnstractPlatformBase` to interact with platform
    service.

    Notes:
        - PLATFORM_SERVICE_API_KEY environment variable is required.
    """

    def __init__(self, tool: BaseTool, platform_host: str, platform_port: str):
        """Constructor of the implementation of `UnstractPlatformBase`

        Args:
            tool (AbstractTool): Instance of AbstractTool
            platform_host (str): Host of platform service
            platform_port (str): Port of platform service
        """
        super().__init__(
            tool=tool, platform_host=platform_host, platform_port=platform_port
        )

    def get_platform_details(self) -> Optional[dict[str, Any]]:
        """Obtains platform details associated with the platform key.

        Currently helps fetch organization ID related to the key.

        Returns:
            Optional[dict[str, Any]]: Dictionary containing the platform details
        """
        url = f"{self.base_url}/platform_details"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.tool.stream_log(
                (
                    "Error while retrieving platform details: "
                    f"[{response.status_code}] {response.reason}"
                ),
                level=LogLevel.ERROR,
            )
            return None
        else:
            platform_details: dict[str, Any] = response.json().get("details")
            self.tool.stream_log("Successfully retrieved platform settings")
            return platform_details
