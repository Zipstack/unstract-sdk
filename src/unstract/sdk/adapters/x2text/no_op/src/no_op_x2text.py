import logging
import os
import time
from typing import Any, Optional

from unstract.sdk.adapters.x2text.dto import TextExtractionResult
from unstract.sdk.adapters.x2text.x2text_adapter import X2TextAdapter

logger = logging.getLogger(__name__)


class NoOpX2Text(X2TextAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("NoOpX2Text")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "noOpX2text|mp66d1op-7100-d340-9101-846fc7115676"

    @staticmethod
    def get_name() -> str:
        return "No Op X2Text"

    @staticmethod
    def get_description() -> str:
        return "No Op X2Text Adapter"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/noOpx2Text.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def process(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        **kwargs: dict[Any, Any],
    ) -> TextExtractionResult:
        extracted_text: str = (
            "This is a No Op x2text adapter response."
            " This is a sample response and intended for testing \f"
        )
        time.sleep(self.config.get("wait_time"))
        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
        return TextExtractionResult(extracted_text=extracted_text)

    def test_connection(self) -> bool:
        time.sleep(self.config.get("wait_time"))
        return True
