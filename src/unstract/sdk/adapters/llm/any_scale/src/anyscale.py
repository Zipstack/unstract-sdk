import os
from typing import Any

from llama_index.core.constants import DEFAULT_NUM_OUTPUTS
from llama_index.core.llms import LLM
from llama_index.llms.anyscale import Anyscale

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    API_BASE = "api_base"
    MAX_RETRIES = "max_retries"
    ADDITIONAL_KWARGS = "additional_kwargs"
    MAX_TOKENS = "max_tokens"


class AnyScaleLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("AnyScale")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "anyscale|adec9815-eabc-4207-9389-79cb89952639"

    @staticmethod
    def get_name() -> str:
        return "AnyScale"

    @staticmethod
    def get_description() -> str:
        return "AnyScale LLM"

    @staticmethod
    def get_provider() -> str:
        return "anyscale"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/anyscale.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        try:
            max_tokens = int(self.config.get(Constants.MAX_TOKENS, DEFAULT_NUM_OUTPUTS))
            llm: LLM = Anyscale(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                api_base=str(self.config.get(Constants.API_BASE)),
                additional_kwargs=self.config.get(Constants.ADDITIONAL_KWARGS),
                max_retries=int(
                    self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                temperature=0,
                max_tokens=max_tokens,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))
