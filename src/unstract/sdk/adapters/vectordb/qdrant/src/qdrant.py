import logging
import os
from typing import Any, Optional

from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.vectordb.constants import VectorDbConstants
from unstract.sdk.adapters.vectordb.helper import VectorDBHelper
from unstract.sdk.adapters.vectordb.vectordb_adapter import VectorDBAdapter

logger = logging.getLogger(__name__)


class Constants:
    URL = "url"
    API_KEY = "api_key"


class Qdrant(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        self._config = settings
        self._client: Optional[QdrantClient] = None
        self._collection_name: str = VectorDbConstants.DEFAULT_VECTOR_DB_NAME
        self._vector_db_instance = self._get_vector_db_instance()
        super().__init__("Qdrant", self._vector_db_instance)

    @staticmethod
    def get_id() -> str:
        return "qdrant|41f64fda-2e4c-4365-89fd-9ce91bee74d0"

    @staticmethod
    def get_name() -> str:
        return "Qdrant"

    @staticmethod
    def get_description() -> str:
        return "Qdrant LLM"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/qdrant.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> BasePydanticVectorStore:
        return self._vector_db_instance

    def _get_vector_db_instance(self) -> BasePydanticVectorStore:
        try:
            self._collection_name = VectorDBHelper.get_collection_name(
                self._config.get(VectorDbConstants.VECTOR_DB_NAME),
                self._config.get(VectorDbConstants.EMBEDDING_DIMENSION),
            )
            url = self._config.get(Constants.URL)
            api_key: Optional[str] = self._config.get(Constants.API_KEY, None)
            if api_key:
                self._client = QdrantClient(url=url, api_key=api_key)
            else:
                self._client = QdrantClient(url=url)
            vector_db: BasePydanticVectorStore = QdrantVectorStore(
                collection_name=self._collection_name,
                client=self._client,
                url=url,
                api_key=api_key,
            )
            return vector_db
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        vector_db = self.get_vector_db_instance()
        test_result: bool = VectorDBHelper.test_vector_db_instance(
            vector_store=vector_db
        )
        # Delete the collection that was created for testing
        if self._client is not None:
            self._client.delete_collection(self._collection_name)
        return test_result

    def close(self, **kwargs: Any) -> None:
        if self._client:
            self._client.close(**kwargs)
