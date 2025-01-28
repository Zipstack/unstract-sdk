import os
from typing import Any

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.bedrock import BedrockEmbedding

class Constants:
    MODEL = "model"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    SECRET_ACCESS_KEY = "aws_secret_access_key"
    ACCESS_KEY_ID = "aws_access_key_id"
    REGION_NAME = "region_name"

class Bedrock(BaseEmbedding):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Bedrock")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "bedrock|88199741-8d7e-4e8c-9d92-d76b0dc20c91"

    @staticmethod
    def get_name() -> str:
        return "Bedrock"

    @staticmethod
    def get_description() -> str:
        return "Bedrock Embedding"

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
    

