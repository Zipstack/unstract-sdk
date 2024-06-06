from abc import ABCMeta
from typing import Optional

from typing_extensions import deprecated
from unstract.adapters.constants import Common
from unstract.adapters.ocr import adapters
from unstract.adapters.ocr.ocr_adapter import OCRAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.exceptions import OCRError
from unstract.sdk.tool.base import BaseTool


class OCR(metaclass=ABCMeta):
    def __init__(
        self,
        tool: BaseTool,
        adapter_instance_id: Optional[str] = None,
    ):
        self._tool = tool
        self._ocr_adapters = adapters
        self._adapter_instance_id = adapter_instance_id
        self._ocr_instance: OCRAdapter = None
        self._initialise(adapter_instance_id)

    def _initialise(self, adapter_instance_id):
        if self._adapter_instance_id:
            self._ocr_instance: OCRAdapter = self._get_ocr()

    def _get_ocr(self) -> Optional[OCRAdapter]:
        try:
            if not self._adapter_instance_id:
                raise OCRError("Adapter instance ID not set. " "Initialisation failed")
            ocr_config = ToolAdapter.get_adapter_config(
                self._tool, self._adapter_instance_id
            )
            ocr_adapter_id = ocr_config.get(Common.ADAPTER_ID)
            if ocr_adapter_id in self._ocr_adapters:
                ocr_adapter = self._ocr_adapters[ocr_adapter_id][Common.METADATA][
                    Common.ADAPTER
                ]
                ocr_metadata = ocr_config.get(Common.ADAPTER_METADATA)
                self._ocr_instance = ocr_adapter(ocr_metadata)

                return self._ocr_instance

        except Exception as e:
            self._tool.stream_log(
                log=f"Unable to get OCR adapter {self._adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            return None

    def process(
        self, input_file_path: str, output_file_path: Optional[str] = None
    ) -> str:
        return self._ocr_instance.process(input_file_path, output_file_path)

    @deprecated("Instantiate OCR and call process() instead")
    def get_x2text(self, adapter_instance_id: str) -> OCRAdapter:
        if not self._ocr_instance:
            self._adapter_instance_id = adapter_instance_id
            self._ocr_instance: OCRAdapter = self._get_ocr()
        return self._ocr_instance
