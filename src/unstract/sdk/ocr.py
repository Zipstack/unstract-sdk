from abc import ABCMeta
from typing import Optional

from unstract.adapters.constants import Common
from unstract.adapters.ocr import adapters
from unstract.adapters.ocr.ocr_adapter import OCRAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.base import BaseTool


class OCR(metaclass=ABCMeta):
    def __init__(self, tool: BaseTool):
        self.tool = tool
        self.ocr_adapters = adapters

    def get_ocr(self, adapter_instance_id: str) -> Optional[OCRAdapter]:
        try:
            ocr_config = ToolAdapter.get_adapter_config(
                self.tool, adapter_instance_id
            )
            ocr_adapter_id = ocr_config.get(Common.ADAPTER_ID)
            if ocr_adapter_id in self.ocr_adapters:
                ocr_adapter = self.ocr_adapters[ocr_adapter_id][
                    Common.METADATA
                ][Common.ADAPTER]
                ocr_metadata = ocr_config.get(Common.ADAPTER_METADATA)
                ocr_adapter_class = ocr_adapter(ocr_metadata)

                return ocr_adapter_class

        except Exception as e:
            self.tool.stream_log(
                log=f"Unable to get OCR adapter {adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            return None
