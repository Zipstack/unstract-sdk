from abc import ABCMeta
from typing import Any, Optional

from typing_extensions import deprecated
from unstract.adapters.constants import Common
from unstract.adapters.x2text import adapters
from unstract.adapters.x2text.constants import X2TextConstants
from unstract.adapters.x2text.dto import TextExtractionResult
from unstract.adapters.x2text.x2text_adapter import X2TextAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.exceptions import X2TextError
from unstract.sdk.tool.base import BaseTool


class X2Text(metaclass=ABCMeta):
    def __init__(self, tool: BaseTool, adapter_instance_id: Optional[str] = None):
        self._tool = tool
        self._x2text_adapters = adapters
        self._adapter_instance_id = adapter_instance_id
        self._x2text_instance: X2TextAdapter = None
        self._initialise()

    def _initialise(self):
        if self._adapter_instance_id:
            self._x2text_instance = self._get_x2text()

    def _get_x2text(self) -> X2TextAdapter:
        try:
            if not self._adapter_instance_id:
                raise X2TextError(
                    "Adapter instance ID not set. " "Initialisation failed"
                )
            x2text_config = ToolAdapter.get_adapter_config(
                self._tool, self._adapter_instance_id
            )
            x2text_adapter_id = x2text_config.get(Common.ADAPTER_ID)
            if x2text_adapter_id in self._x2text_adapters:
                x2text_adapter = self._x2text_adapters[x2text_adapter_id][
                    Common.METADATA
                ][Common.ADAPTER]
                x2text_metadata = x2text_config.get(Common.ADAPTER_METADATA)
                # Add x2text service host, port and platform_service_key
                x2text_metadata[
                    X2TextConstants.X2TEXT_HOST
                ] = self._tool.get_env_or_die(X2TextConstants.X2TEXT_HOST)
                x2text_metadata[
                    X2TextConstants.X2TEXT_PORT
                ] = self._tool.get_env_or_die(X2TextConstants.X2TEXT_PORT)
                x2text_metadata[
                    X2TextConstants.PLATFORM_SERVICE_API_KEY
                ] = self._tool.get_env_or_die(X2TextConstants.PLATFORM_SERVICE_API_KEY)

                self._x2text_instance = x2text_adapter(x2text_metadata)

                return self._x2text_instance

        except Exception as e:
            self._tool.stream_log(
                log=f"Unable to get x2text adapter {self._adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            raise X2TextError(f"Error getting text extractor: {e}") from e

    def process(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        **kwargs: dict[Any, Any],
    ) -> TextExtractionResult:
        return self._x2text_instance.process(
            input_file_path, output_file_path, **kwargs
        )

    @deprecated("Instantiate X2Text and call process() instead")
    def get_x2text(self, adapter_instance_id: str) -> X2TextAdapter:
        if not self._x2text_instance:
            self._adapter_instance_id = adapter_instance_id
            self._initialise()
        return self._x2text_instance
