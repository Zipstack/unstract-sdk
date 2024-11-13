import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.exceptions import LLMError, RateLimitError


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    MAX_RETRIES = "max_retries"
    ADAPTER_NAME = "adapter_name"
    TIMEOUT = "timeout"
    API_BASE = "api_base"
    API_VERSION = "api_version"
    MAX_TOKENS = "max_tokens"


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
            max_tokens = self.config.get(Constants.MAX_TOKENS)
            max_tokens = int(max_tokens) if max_tokens else None
            llm: LLM = OpenAI(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                api_base=str(self.config.get(Constants.API_BASE)),
                api_version=str(self.config.get(Constants.API_VERSION)),
                max_retries=int(
                    self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                api_type="openai",
                temperature=0,
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                max_tokens=max_tokens,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))

    @staticmethod
    def parse_llm_err(e: OpenAIAPIError) -> LLMError:
        """Parse the error from OpenAI.

        Helps parse errors from OpenAI and wraps with custom exception.

        Args:
            e (OpenAIAPIError): Exception from OpenAI

        Returns:
            LLMError: Error to be sent to the user
        """
        msg = "Error from OpenAI. "
        if hasattr(e, "body") and isinstance(e.body, dict) and "message" in e.body:
            msg += e.body["message"]
        else:
            msg += e.message
        if isinstance(e, OpenAIRateLimitError):
            return RateLimitError(msg)
        return LLMError(msg)
