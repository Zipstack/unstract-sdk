import os
from typing import Any

from anthropic import APIError
from llama_index.core.llms import LLM
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.anthropic.base import DEFAULT_ANTHROPIC_MAX_TOKENS

from unstract.sdk.adapters.exceptions import AdapterError, LLMError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    MAX_TOKENS = "max_tokens"


class AnthropicLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Anthropic")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "anthropic|90ebd4cd-2f19-4cef-a884-9eeb6ac0f203"

    @staticmethod
    def get_name() -> str:
        return "Anthropic"

    @staticmethod
    def get_description() -> str:
        return "Anthropic LLM"

    @staticmethod
    def get_provider() -> str:
        return "anthropic"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/Anthropic.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        max_tokens = int(
            self.config.get(Constants.MAX_TOKENS, DEFAULT_ANTHROPIC_MAX_TOKENS)
        )
        try:
            llm: LLM = Anthropic(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                max_retries=int(
                    self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                temperature=0,
                max_tokens=max_tokens,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))

    @staticmethod
    def parse_llm_err(e: APIError) -> LLMError:
        """Parse the error from Anthropic.

        Helps parse errors from Anthropic and wraps with custom exception.

        Args:
            e (AnthropicAPIError): Exception from Anthropic

        Returns:
            LLMError: Error to be sent to the user
        """
        msg = "Error from Anthropic. "
        if hasattr(e, "body"):
            if isinstance(e.body, dict) and "error" in e.body:
                err = e.body["error"]
                msg += err.get("message", e.message)
        else:
            msg += e.message
        return LLMError(msg)
