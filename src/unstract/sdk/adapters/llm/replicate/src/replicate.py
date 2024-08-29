import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.replicate import Replicate

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    API_KEY = "api_key"


class ReplicateLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Replicate")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "replicate|2715ce84-05af-4ab4-b8e9-67ac3211b81e"

    @staticmethod
    def get_name() -> str:
        return "Replicate"

    @staticmethod
    def get_description() -> str:
        return "Replicate LLM"

    @staticmethod
    def get_provider() -> str:
        return "replicate"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/Replicate.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    @staticmethod
    def can_write() -> bool:
        return True

    @staticmethod
    def can_read() -> bool:
        return True

    def get_llm_instance(self) -> LLM:
        try:
            llm: LLM = Replicate(
                model=str(self.config.get(Constants.MODEL)),
                prompt_key=str(self.config.get(Constants.API_KEY)),
                temperature=0,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))
