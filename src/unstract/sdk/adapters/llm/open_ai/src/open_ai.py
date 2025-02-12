import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai.utils import O1_MODELS
from openai import APIError as OpenAIAPIError

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.exceptions import LLMError

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

    SCHEMA_PATH = f"{os.path.dirname(__file__)}/static/json_schema.json"

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

    def get_llm_instance(self) -> LLM:
        try:
            max_tokens = self.config.get(Constants.MAX_TOKENS)
            max_tokens = int(max_tokens) if max_tokens else None
            model = str(self.config.get(Constants.MODEL))

            llm_kwargs = {
                "model": model,
                "api_key": str(self.config.get(Constants.API_KEY)),
                "api_base": str(self.config.get(Constants.API_BASE)),
                "api_version": str(self.config.get(Constants.API_VERSION)),
                "max_retries": int(self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)),
                "api_type": "openai",
                "timeout": float(self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)),
                "max_tokens": max_tokens,
            }

            # O-series models default to temperature=1, ignoring passed values, so it's not set explicitly.
            if model not in O1_MODELS:
                llm_kwargs["temperature"] = 0

            llm = OpenAI(**llm_kwargs)
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
        if hasattr(e, "body") and isinstance(e.body, dict) and "message" in e.body:
            msg = e.body["message"]
        else:
            msg = e.message

        status_code = e.status_code if hasattr(e, "status_code") else None
        return LLMError(msg, actual_err=e, status_code=status_code)
