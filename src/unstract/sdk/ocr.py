from abc import ABCMeta
from typing import Optional

from unstract.adapters.constants import Common
from unstract.adapters.ocr import adapters
from unstract.adapters.ocr.ocr_adapter import OCRAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.base import BaseTool


class OCR(metaclass=ABCMeta):
    def __init__(
        self,
        tool: BaseTool,
        adapter_instance_id: str,
    ):
        self.tool = tool
        self.ocr_adapters = adapters
        self.adapter_instance_id = adapter_instance_id
        self.ocr_instance: OCRAdapter = self._get_ocr()

    def _get_ocr(self) -> Optional[OCRAdapter]:
        try:
            ocr_config = ToolAdapter.get_adapter_config(
                self.tool, self.adapter_instance_id
            )
            ocr_adapter_id = ocr_config.get(Common.ADAPTER_ID)
            if ocr_adapter_id in self.ocr_adapters:
                ocr_adapter = self.ocr_adapters[ocr_adapter_id][Common.METADATA][
                    Common.ADAPTER
                ]
                ocr_metadata = ocr_config.get(Common.ADAPTER_METADATA)
                self.ocr_instance = ocr_adapter(ocr_metadata)

                return self.ocr_instance

        except Exception as e:
            self.tool.stream_log(
                log=f"Unable to get OCR adapter {self.adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            return None
