import json
import logging
import os
from typing import Any, Optional

import requests

from unstract.sdk.adapters.x2text.constants import X2TextConstants
from unstract.sdk.adapters.x2text.dto import (
    TextExtractionMetadata,
    TextExtractionResult,
)
from unstract.sdk.adapters.x2text.llm_whisperer_v2.src.constants import (
    HTTPMethod,
    WhispererEndpoint,
)
from unstract.sdk.adapters.x2text.llm_whisperer_v2.src.helper import LLMWhispererHelper
from unstract.sdk.adapters.x2text.x2text_adapter import X2TextAdapter

logger = logging.getLogger(__name__)


class LLMWhispererV2(X2TextAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("LLMWhispererV2")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "llmwhisperer|a5e6b8af-3e1f-4a80-b006-d017e8e67f93"

    @staticmethod
    def get_name() -> str:
        return "LLMWhisperer V2"

    @staticmethod
    def get_description() -> str:
        return "LLMWhisperer V2 X2Text"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/LLMWhispererV2.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def test_connection(self) -> bool:
        LLMWhispererHelper.make_request(
            config=self.config,
            request_method=HTTPMethod.GET,
            request_endpoint=WhispererEndpoint.TEST_CONNECTION,
        )
        return True

    def process(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        **kwargs: dict[Any, Any],
    ) -> TextExtractionResult:
        """Used to extract text from documents.

        Args:
            input_file_path (str): Path to file that needs to be extracted
            output_file_path (Optional[str], optional): File path to write
                extracted text into, if None doesn't write to a file.
                Defaults to None.

        Returns:
            str: Extracted text
        """

        response: requests.Response = LLMWhispererHelper.send_whisper_request(
            input_file_path, self.config
        )
        response_text = response.text
        reponse_dict = json.loads(response_text)
        metadata = TextExtractionMetadata(
            whisper_hash=reponse_dict.get(X2TextConstants.WHISPER_HASH_V2, "")
        )

        return TextExtractionResult(
            extracted_text=LLMWhispererHelper.extract_text_from_response(
                self.config, output_file_path, reponse_dict, response
            ),
            extraction_metadata=metadata,
        )
