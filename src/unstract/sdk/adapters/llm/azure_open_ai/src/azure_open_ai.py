import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.openai.utils import O1_MODELS
from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    DEPLOYMENT_NAME = "deployment_name"
    API_KEY = "api_key"
    API_VERSION = "api_version"
    MAX_RETRIES = "max_retries"
    MAX_TOKENS = "max_tokens"
    AZURE_ENDPONT = "azure_endpoint"
    API_TYPE = "azure"
    TIMEOUT = "timeout"
    DEFAULT_MODEL = "gpt-35-turbo"
    ENABLE_REASONING = "enable_reasoning"
    REASONING_EFFORT = "reasoning_effort"


class AzureOpenAILLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any], validate_urls: bool = False):
        super().__init__("AzureOpenAI")
        self.config = settings

        # Validate URLs BEFORE any network operations
        if validate_urls:
            self._validate_urls()

    SCHEMA_PATH = f"{os.path.dirname(__file__)}/static/json_schema.json"

    @staticmethod
    def get_id() -> str:
        return "azureopenai|592d84b9-fe03-4102-a17e-6b391f32850b"

    @staticmethod
    def get_name() -> str:
        return "AzureOpenAI"

    @staticmethod
    def get_description() -> str:
        return "AzureOpenAI LLM"

    @staticmethod
    def get_provider() -> str:
        return "azure"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/AzureopenAI.png"

    def get_configured_urls(self) -> list[str]:
        """Return all URLs this adapter will connect to."""
        endpoint = self.config.get("azure_endpoint")
        return [endpoint] if endpoint else []

    def get_llm_instance(self) -> LLM:
        max_retries = int(
            self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
        )
        max_tokens = self.config.get(Constants.MAX_TOKENS)
        max_tokens = int(max_tokens) if max_tokens else None
        enable_reasoning = self.config.get(Constants.ENABLE_REASONING)
        model = self.config.get(Constants.MODEL, Constants.DEFAULT_MODEL)

        llm_kwargs = {
            "model": model,
            "deployment_name": str(self.config.get(Constants.DEPLOYMENT_NAME)),
            "api_key": str(self.config.get(Constants.API_KEY)),
            "api_version": str(self.config.get(Constants.API_VERSION)),
            "azure_endpoint": str(self.config.get(Constants.AZURE_ENDPONT)),
            "api_type": Constants.API_TYPE,
            "temperature": 0,
            "timeout": float(self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)),
            "max_retries": max_retries,
        }

        if enable_reasoning:
            llm_kwargs["reasoning_effort"] = self.config.get(Constants.REASONING_EFFORT)

        if model not in O1_MODELS:
            llm_kwargs["max_completion_tokens"] = max_tokens
        else:
            llm_kwargs["max_tokens"] = max_tokens

        try:
            llm: LLM = AzureOpenAI(**llm_kwargs)
            return llm
        except Exception as e:
            raise AdapterError(str(e))
