import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.helper import LLMHelper
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.exceptions import LLMError, RateLimitError


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    MAX_RETIRES = "max_retries"
    ADAPTER_NAME = "adapter_name"
    TIMEOUT = "timeout"
    API_BASE = "api_base"
    API_VERSION = "api_version"


class OpenAILLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("OpenAI")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "openai|502ecf49-e47c-445c-9907-6d4b90c5cd17"

    @staticmethod
    def get_name() -> str:
        return "OpenAI"

    @staticmethod
    def get_description() -> str:
        return "OpenAI LLM"

    @staticmethod
    def get_provider() -> str:
        return "openai"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/OpenAI.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        try:
            llm: LLM = OpenAI(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                api_base=str(self.config.get(Constants.API_BASE)),
                api_version=str(self.config.get(Constants.API_VERSION)),
                max_retries=int(
                    self.config.get(Constants.MAX_RETIRES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                api_type="openai",
                temperature=0,
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        llm = self.get_llm_instance()
        test_result: bool = LLMHelper.test_llm_instance(llm=llm)
        return test_result

    @staticmethod
    def parse_llm_err(e: OpenAIAPIError) -> LLMError:
        """Parse the error from Open AI.

        Helps parse errors from Open AI and wraps with custom exception.

        Args:
            e (OpenAIAPIError): Exception from Open AI

        Returns:
            LLMError: Error to be sent to the user
        """
        msg = "OpenAI error: "
        if hasattr(e, "body") and "message" in e.body:
            msg += e.body["message"]
        else:
            msg += e.message
        if isinstance(e, OpenAIRateLimitError):
            return RateLimitError(msg)
        return LLMError(msg)
