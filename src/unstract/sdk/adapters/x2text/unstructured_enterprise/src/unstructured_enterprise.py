import logging
import os
from typing import Any, Optional

from unstract.sdk.adapters.x2text.dto import TextExtractionResult
from unstract.sdk.adapters.x2text.helper import UnstructuredHelper
from unstract.sdk.adapters.x2text.x2text_adapter import X2TextAdapter

logger = logging.getLogger(__name__)


class UnstructuredEnterprise(X2TextAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("UnstructuredIOEnterprise")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "unstructuredenterprise|eb1b6c58-221f-4db0-a4a5-e5f9cdca44e1"

    @staticmethod
    def get_name() -> str:
        return "Unstructured IO Enterprise"

    @staticmethod
    def get_description() -> str:
        return "Unstructured IO Enterprise X2Text"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/UnstructuredIO.png"

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
        **kwargs: dict[str, Any],
    ) -> TextExtractionResult:
        extracted_text: str = UnstructuredHelper.process_document(
            self.config, input_file_path, output_file_path
        )

        return TextExtractionResult(extracted_text=extracted_text)

    def test_connection(self) -> bool:
        result: bool = UnstructuredHelper.test_server_connection(self.config)
        return result
