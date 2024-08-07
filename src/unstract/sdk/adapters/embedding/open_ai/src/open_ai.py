import os
from typing import Any

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

from unstract.sdk.adapters.embedding.embedding_adapter import EmbeddingAdapter
from unstract.sdk.adapters.embedding.helper import EmbeddingHelper
from unstract.sdk.adapters.exceptions import AdapterError


class Constants:
    API_KEY = "api_key"
    API_BASE_VALUE = "https://api.openai.com/v1/"
    API_BASE_KEY = "api_base"
    ADAPTER_NAME = "adapter_name"
    API_TYPE = "openai"


class OpenAI(EmbeddingAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("OpenAI")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "openai|717a0b0e-3bbc-41dc-9f0c-5689437a1151"

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

    def get_embedding_instance(self) -> BaseEmbedding:
        try:
            embedding: BaseEmbedding = OpenAIEmbedding(
                api_key=str(self.config.get(Constants.API_KEY)),
                api_base=str(
                    self.config.get(Constants.API_BASE_KEY, Constants.API_BASE_VALUE)
                ),
                api_type=Constants.API_TYPE,
            )
            return embedding
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        embedding = self.get_embedding_instance()
        test_result: bool = EmbeddingHelper.test_embedding_instance(embedding)
        return test_result
