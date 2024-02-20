from typing import Any, Optional

import requests
from unstract.connectors.constants import Common
from unstract.connectors.filesystems import connectors
from unstract.connectors.filesystems.unstract_file_system import (
    AbstractFileSystem,
    UnstractFileSystem,
)
from unstract.sdk.constants import (
    Connector,
    ConnectorKeys,
    ConnectorType,
    LogLevel,
    ToolEnv,
)
from unstract.sdk.platform import PlatformBase
from unstract.sdk.tool.base import BaseTool


class ToolFileSystem(PlatformBase):
    """Class to handle File connectors for Unstract Tools.

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
        self.fs_connectors = connectors

    def get_fsspec(
        self, tool_instance_id: str, connector_type: str = ConnectorType.OUTPUT
    ) -> Optional[AbstractFileSystem]:
        """Get FsSpec for fileSystem
            1. Get the connection settings from platform service
            using the tool_instance_id
            2. Create UnstractFileSystem based object using the settings
                2.1 Find the type of the database (From Connector Registry)
                2.2 Create the object using the type
                (derived class of UnstractFileSystem)
            3. Send Object.get_fsspec_fs() to the caller

        Args:
            tool_instance_id (str): tool Instance Id
            connector_type (str, optional): _description_.
                Defaults to ConnectorType.OUTPUT.

        Returns:
            Any: _description_
        """
        url = f"{self.base_url}/connector_instance/{Connector.FILE_SYSTEM}"
        query_params = {
            ConnectorKeys.TOOL_INSTANCE_ID: tool_instance_id,
            ConnectorKeys.CONNECTOR_TYPE: connector_type,
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
            if connector_id in self.fs_connectors:
                connector = self.fs_connectors[connector_id][Common.METADATA][
                    Common.CONNECTOR
                ]
                connector_class: UnstractFileSystem = connector(settings)
                return connector_class.get_fsspec_fs()
            else:
                self.tool.stream_log(
                    f"FileSystem not found for connector: {connector_id}",
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

    # TODO UN-237: Obtain fsspec object with connector instance ID
    @staticmethod
    def get_fsspec_fs(
        tool: BaseTool,
        tool_instance_id: str,
        fileType: str,
    ) -> AbstractFileSystem:
        """Get fileSystem spec by the help of unstract DB tool.

        Args:
            tool_instance_id (str): ID of the tool instance
            fileType (str): INPUT/OUTPUT
            tool (AbstractTool): Instance of AbstractTool
        Required env variables:
            PLATFORM_HOST: Host of platform service
            PLATFORM_PORT: Port of platform service
        Returns:
            Any: engine
        """
        platform_host = tool.get_env_or_die(ToolEnv.PLATFORM_HOST)
        platform_port = tool.get_env_or_die(ToolEnv.PLATFORM_PORT)

        tool.stream_log("Connecting to DB and getting table metadata")
        tool_file_system = ToolFileSystem(
            tool=tool,
            platform_host=platform_host,
            platform_port=platform_port,
        )
        fs: Optional[AbstractFileSystem] = tool_file_system.get_fsspec(
            tool_instance_id, fileType
        )
        if not fs:
            tool.stream_error_and_exit(
                f"FileSystem not found for tool_instance_id {tool_instance_id}"
            )
        return fs
