import json
from typing import Any, Optional

import requests

from unstract.sdk.constants import AdapterKeys, LogLevel, PublicAdapterKeys, ToolEnv
from unstract.sdk.helper import SdkHelper
from unstract.sdk.platform import PlatformBase
from unstract.sdk.tool.base import BaseTool


class ToolAdapter(PlatformBase):
    """Class to handle Adapters for Unstract Tools.

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
            - The platform_host and platform_port are the
                host and port of the platform service.
        """
        super().__init__(
            tool=tool, platform_host=platform_host, platform_port=platform_port
        )

    def get_adapter_configuration(
        self,
        adapter_instance_id: str,
    ) -> Optional[dict[str, Any]]:
        """Get Adapter
            1. Get the adapter config from platform service
            using the adapter_instance_id

        Args:
            adapter_instance_id (str): adapter Instance Id

        Returns:
            Any: _description_
        """
        url = f"{self.base_url}/adapter_instance"
        query_params = {AdapterKeys.ADAPTER_INSTANCE_ID: adapter_instance_id}
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.get(url, headers=headers, params=query_params)
        if response.status_code == 200:
            adapter_data: dict[str, Any] = response.json()

            self.tool.stream_log(
                "Successfully retrieved adapter config "
                f"for adapter: {adapter_instance_id}"
            )

            return adapter_data

        elif response.status_code == 404:
            self.tool.stream_log(
                f"adapter not found for: for adapter instance"
                f"{adapter_instance_id}",
                level=LogLevel.ERROR,
            )
            return None

        else:
            self.tool.stream_log(
                (
                    f"Error while retrieving adapter "
                    "for adapter instance: "
                    f"{adapter_instance_id} / {response.reason}"
                ),
                level=LogLevel.ERROR,
            )
            return None

    @staticmethod
    def get_adapter_config(
        tool: BaseTool, adapter_instance_id: str
    ) -> Optional[dict[str, Any]]:
        """Get adapter spec by the help of unstract DB tool.

        This method first checks if the adapter_instance_id matches
        any of the public adapter keys. If it matches, the configuration
        is fetched from environment variables. Otherwise, it connects to the
        platform service to retrieve the configuration.

        Args:
            adapter_instance_id (str): ID of the adapter instance
            tool (AbstractTool): Instance of AbstractTool
        Required env variables:
            PLATFORM_HOST: Host of platform service
            PLATFORM_PORT: Port of platform service
        Returns:
            Any: engine
        """
        # Check if the adapter ID matches any public adapter keys
        is_public_adapter = SdkHelper.is_public_adapter(
            adapter_id=adapter_instance_id
        )
        if is_public_adapter:
            adapter_metadata_config = tool.get_env_or_die(
                getattr(PublicAdapterKeys, adapter_instance_id)
            )
            adapter_metadata = json.loads(adapter_metadata_config)
            return adapter_metadata
        platform_host = tool.get_env_or_die(ToolEnv.PLATFORM_HOST)
        platform_port = tool.get_env_or_die(ToolEnv.PLATFORM_PORT)

        tool.stream_log("Connecting to DB and getting table metadata")
        tool_adapter = ToolAdapter(
            tool=tool,
            platform_host=platform_host,
            platform_port=platform_port,
        )
        adapter_metadata: Optional[
            dict[str, Any]
        ] = tool_adapter.get_adapter_configuration(adapter_instance_id)
        if not adapter_metadata:
            tool.stream_error_and_exit(
                f"Adapter not found for "
                f"adapter instance: {adapter_instance_id}"
            )
        return adapter_metadata
