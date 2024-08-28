import os
from typing import Any, Optional

from llama_index.core.llms import LLM
from llama_index.llms.bedrock import Bedrock

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    SECRET_ACCESS_KEY = "aws_secret_access_key"
    ACCESS_KEY_ID = "aws_access_key_id"
    REGION_NAME = "region_name"
    CONTEXT_SIZE = "context_size"
    MAX_TOKENS = "max_tokens"
    DEFAULT_MAX_TOKENS = 512  # Default at llama-index


class BedrockLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Bedrock")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "bedrock|8d18571f-5e96-4505-bd28-ad0379c64064"

    @staticmethod
    def get_name() -> str:
        return "Bedrock"

    @staticmethod
    def get_description() -> str:
        return "Bedrock LLM"

    @staticmethod
    def get_provider() -> str:
        return "bedrock"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/Bedrock.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        try:
            context_size: Optional[int] = (
                int(self.config.get(Constants.CONTEXT_SIZE, 0))
                if self.config.get(Constants.CONTEXT_SIZE)
                else None
            )
            max_tokens = int(
                self.config.get(Constants.MAX_TOKENS, Constants.DEFAULT_MAX_TOKENS)
            )
            llm: LLM = Bedrock(
                model=self.config.get(Constants.MODEL),
                aws_access_key_id=self.config.get(Constants.ACCESS_KEY_ID),
                aws_secret_access_key=self.config.get(Constants.SECRET_ACCESS_KEY),
                region_name=self.config.get(Constants.REGION_NAME),
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                max_retries=int(
                    self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                temperature=0,
                context_size=context_size,
                max_tokens=max_tokens,
            )
            return llm
        except Exception as e:
            raise AdapterError(str(e))
