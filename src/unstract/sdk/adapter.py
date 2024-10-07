import json
from typing import Any, Optional

import requests
from requests.exceptions import ConnectionError, HTTPError

from unstract.sdk.adapters.utils import AdapterUtils
from unstract.sdk.constants import AdapterKeys, LogLevel, ToolEnv
from unstract.sdk.exceptions import SdkError
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

    def _get_adapter_configuration(
        self,
        adapter_instance_id: str,
    ) -> dict[str, Any]:
        """Get Adapter
            1. Get the adapter config from platform service
            using the adapter_instance_id

        Args:
            adapter_instance_id (str): Adapter instance ID

        Returns:
            dict[str, Any]: Config stored for the adapter
        """
        url = f"{self.base_url}/adapter_instance"
        query_params = {AdapterKeys.ADAPTER_INSTANCE_ID: adapter_instance_id}
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        try:
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            adapter_data: dict[str, Any] = response.json()

            # Removing name and type to avoid migration for already indexed records
            adapter_name = adapter_data.pop("adapter_name", "")
            adapter_type = adapter_data.pop("adapter_type", "")
            provider = adapter_data.get("adapter_id", "").split("|")[0]
            # TODO: Print metadata after redacting sensitive information
            self.tool.stream_log(
                f"Retrieved config for '{adapter_instance_id}', type: "
                f"'{adapter_type}', provider: '{provider}', name: '{adapter_name}'",
                level=LogLevel.DEBUG,
            )
        except ConnectionError:
            raise SdkError(
                "Unable to connect to platform service, please contact the admin."
            )
        except HTTPError as e:
            default_err = (
                "Error while calling the platform service, please contact the admin."
            )
            msg = AdapterUtils.get_msg_from_request_exc(
                err=e, message_key="error", default_err=default_err
            )
            raise SdkError(f"Error retrieving adapter. {msg}")
        return adapter_data

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
            tool (AbstractTool): Instance of AbstractTool
            adapter_instance_id (str): ID of the adapter instance
        Required env variables:
            PLATFORM_HOST: Host of platform service
            PLATFORM_PORT: Port of platform service
        Returns:
            dict[str, Any]: Config stored for the adapter
        """
        # Check if the adapter ID matches any public adapter keys
        if SdkHelper.is_public_adapter(adapter_id=adapter_instance_id):
            adapter_metadata_config = tool.get_env_or_die(adapter_instance_id)
            adapter_metadata = json.loads(adapter_metadata_config)
            return adapter_metadata
        platform_host = tool.get_env_or_die(ToolEnv.PLATFORM_HOST)
        platform_port = tool.get_env_or_die(ToolEnv.PLATFORM_PORT)

        tool.stream_log(
            f"Retrieving config from DB for '{adapter_instance_id}'",
            level=LogLevel.DEBUG,
        )
        tool_adapter = ToolAdapter(
            tool=tool,
            platform_host=platform_host,
            platform_port=platform_port,
        )
        return tool_adapter._get_adapter_configuration(adapter_instance_id)
