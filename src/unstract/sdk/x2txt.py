from abc import ABCMeta
from typing import Optional

from unstract.adapters.constants import Common
from unstract.adapters.x2text import adapters
from unstract.adapters.x2text.constants import X2TextConstants
from unstract.adapters.x2text.x2text_adapter import X2TextAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.base import BaseTool


class X2Text(metaclass=ABCMeta):
    def __init__(self, tool: BaseTool):
        self.tool = tool
        self.x2text_adapters = adapters

    def get_x2text(self, adapter_instance_id: str) -> Optional[X2TextAdapter]:
        try:
            x2text_config = ToolAdapter.get_adapter_config(
                self.tool, adapter_instance_id
            )
            x2text_adapter_id = x2text_config.get(Common.ADAPTER_ID)
            if x2text_adapter_id in self.x2text_adapters:
                x2text_adapter = self.x2text_adapters[x2text_adapter_id][
                    Common.METADATA
                ][Common.ADAPTER]
                x2text_metadata = x2text_config.get(Common.ADAPTER_METADATA)
                # Add x2text service host, port and platform_service_key
                x2text_metadata[
                    X2TextConstants.X2TEXT_HOST
                ] = self.tool.get_env_or_die(X2TextConstants.X2TEXT_HOST)
                x2text_metadata[
                    X2TextConstants.X2TEXT_PORT
                ] = self.tool.get_env_or_die(X2TextConstants.X2TEXT_PORT)
                x2text_metadata[
                    X2TextConstants.PLATFORM_SERVICE_API_KEY
                ] = self.tool.get_env_or_die(
                    X2TextConstants.PLATFORM_SERVICE_API_KEY
                )

                x2text_adapter_class = x2text_adapter(x2text_metadata)

                return x2text_adapter_class

        except Exception as e:
            self.tool.stream_log(
                log=f"Unable to get x2text adapter {adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            return None
