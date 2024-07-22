import os
from typing import Any

from llama_index.core.llms import LLM
from llama_index.llms.palm import PaLM

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.helper import LLMHelper
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model_name"
    API_KEY = "api_key"
    NUM_OUTPUT = "num_output"
    API_TYPE = "palm"
    DEFAULT_MAX_TOKENS = 1024


class PaLMLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("PaLM")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "palm|af7c8ee7-3d01-47c5-9b81-5ffd7546014b"

    @staticmethod
    def get_name() -> str:
        return "Palm"

    @staticmethod
    def get_description() -> str:
        return "Palm LLM"

    @staticmethod
    def get_provider() -> str:
        return "palm"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/PaLM.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        try:
            num_output = (
                int(self.config.get(Constants.NUM_OUTPUT, Constants.DEFAULT_MAX_TOKENS))
                if self.config.get(Constants.NUM_OUTPUT) is not None
                else None
            )
            llm: LLM = PaLM(
                model=str(self.config.get(Constants.MODEL)),
                api_key=str(self.config.get(Constants.API_KEY)),
                num_output=num_output,
                api_type=Constants.API_TYPE,
                temperature=0,
            )

            return llm
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        llm = self.get_llm_instance()
        test_result: bool = LLMHelper.test_llm_instance(llm=llm)
        return test_result
