import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.mistralai import MistralAI
from llama_index.llms.mistralai.base import DEFAULT_MISTRALAI_MAX_TOKENS
from mistralai.exceptions import MistralException

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.exceptions import LLMError


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    MAX_TOKENS = "max_tokens"


class MistralLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Mistral")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "mistral|00f766a5-6d6d-47ea-9f6c-ddb1e8a94e82"

    @staticmethod
    def get_name() -> str:
        return "Mistral AI"

    @staticmethod
    def get_description() -> str:
        return "Mistral AI LLM"

    @staticmethod
    def get_provider() -> str:
        return "mistral"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/Mistral%20AI.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        max_retries = int(
            self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
        )
        max_tokens = int(
            self.config.get(Constants.MAX_RETRIES, DEFAULT_MISTRALAI_MAX_TOKENS)
        )
        try:
            llm: LLM = MistralAI(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                temperature=0,
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                max_retries=max_retries,
                max_tokens=max_tokens,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))

    @staticmethod
    def parse_llm_err(e: MistralException) -> LLMError:
        """Parse the error from MistralAI.

        Helps parse errors from MistralAI and wraps with custom exception.

        Args:
            e (OpenAIAPIError): Exception from MistralAI

        Returns:
            LLMError: Error to be sent to the user
        """
        if e.message and e.message.find('"message":"Unauthorized"'):
            return LLMError("Incorrect API key, please check the API key provided.")
        return LLMError(f"Error from MistralAI. {e}")
