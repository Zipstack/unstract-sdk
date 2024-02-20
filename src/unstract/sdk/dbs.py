from typing import Any

import requests
from unstract.connectors.constants import Common
from unstract.connectors.databases import connectors
from unstract.connectors.databases.unstract_db import UnstractDB
from unstract.sdk.constants import Connector, ConnectorKeys, LogLevel
from unstract.sdk.platform import PlatformBase
from unstract.sdk.tool.base import BaseTool


class ToolDB(PlatformBase):
    """Class to handle DB connectors for Unstract Tools.

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
        self.db_connectors = connectors

    def get_engine(self, tool_instance_id: str) -> Any:
        """Get DB engine
            1. Get the connection settings from platform service
            using the tool_instance_id
            2. Create UnstractFileSystem based object using the settings
                2.1 Find the type of the database (From Connector Registry)
                2.2 Create the object using the type
                (derived class of UnstractFileSystem)
            3. Send Object.get_fsspec_fs() to the caller

        Args:
            tool_instance_id (str): tool Instance Id

        Returns:
            Any: _description_
        """

        url = f"{self.base_url}/connector_instance/{Connector.DATABASE}"
        query_params = {
            ConnectorKeys.TOOL_INSTANCE_ID: tool_instance_id,
        }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        response = requests.get(url, headers=headers, params=query_params)
        if response.status_code == 200:
            connector_data: dict[str, Any] = response.json()
            connector_id = connector_data.get(ConnectorKeys.CONNECTOR_ID)
            connector_instance_id = connector_data.get(ConnectorKeys.ID)
            settings = connector_data.get(ConnectorKeys.CONNECTOR_METADATA)
            self.tool.stream_log(
                "Successfully retrieved connector settings "
                f"for connector: {connector_instance_id}"
            )
            if connector_id in self.db_connectors:
                connector = self.db_connectors[connector_id][Common.METADATA][
                    Common.CONNECTOR
                ]
                connector_class: UnstractDB = connector(settings)
                return connector_class.get_engine()
            else:
                self.tool.stream_log(
                    f"Engine not found for connector: {connector_id}",
                    level=LogLevel.ERROR,
                )
                return None

        elif response.status_code == 404:
            self.tool.stream_log(
                f"Connector not found for tool instance {tool_instance_id}",
                level=LogLevel.ERROR,
            )
            return None

        else:
            self.tool.stream_log(
                (
                    f"Error while retrieving connector "
                    "for tool instance: "
                    f"{tool_instance_id} / {response.reason}"
                ),
                level=LogLevel.ERROR,
            )
            return None
