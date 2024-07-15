import logging
import os
import pathlib
from typing import Any, Optional

from httpx import ConnectError
from llama_parse import LlamaParse

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.utils import AdapterUtils
from unstract.sdk.adapters.x2text.dto import TextExtractionResult
from unstract.sdk.adapters.x2text.llama_parse.src.constants import LlamaParseConfig
from unstract.sdk.adapters.x2text.x2text_adapter import X2TextAdapter

logger = logging.getLogger(__name__)


class LlamaParseAdapter(X2TextAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("LlamaParse")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "llamaparse|78860239-b3cc-4cc5-b3de-f84315f75d14"

    @staticmethod
    def get_name() -> str:
        return "LlamaParse"

    @staticmethod
    def get_description() -> str:
        return "LlamaParse X2Text"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/llama-parse.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def _call_parser(
        self,
        input_file_path: str,
    ) -> str:

        parser = LlamaParse(
            api_key=self.config.get(LlamaParseConfig.API_KEY),
            base_url=self.config.get(LlamaParseConfig.BASE_URL),
            result_type=self.config.get(LlamaParseConfig.RESULT_TYPE),
            verbose=self.config.get(LlamaParseConfig.VERBOSE),
            language="en",
            ignore_errors=False,
        )

        try:
            file_extension = pathlib.Path(input_file_path).suffix
            if not file_extension:
                try:
                    input_file_extension = AdapterUtils.guess_extention(input_file_path)
                    input_file_path_copy = input_file_path
                    input_file_path = ".".join(
                        (input_file_path_copy, input_file_extension)
                    )
                except OSError as os_err:
                    logger.error("Exception raised while handling input file.")
                    raise AdapterError(str(os_err))

            documents = parser.load_data(input_file_path)

        except ConnectError as connec_err:
            logger.error(f"Invalid Base URL given. : {connec_err}")
            raise AdapterError(
                "Unable to connect to llama-parse`s service, "
                "please check the Base URL"
            )
        except Exception as exe:
            logger.error(
                "Seems like an invalid API Key or possible internal errors: {exe}"
            )
            raise AdapterError(str(exe))

        response_text = documents[0].text
        return response_text  # type:ignore

    def process(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        **kwargs: dict[Any, Any],
    ) -> TextExtractionResult:

        response_text = self._call_parser(input_file_path=input_file_path)
        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(response_text)

        return TextExtractionResult(extracted_text=response_text)

    def test_connection(self) -> bool:
        self._call_parser(
            input_file_path=f"{os.path.dirname(__file__)}/static/test_input.doc"
        )
        return True
