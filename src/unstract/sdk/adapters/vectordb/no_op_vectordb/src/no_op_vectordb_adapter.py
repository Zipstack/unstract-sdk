import os
import time
from typing import Any

from llama_index.core.schema import BaseNode
from llama_index.core.vector_stores.types import VectorStore

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.vectordb.constants import VectorDbConstants
from unstract.sdk.adapters.vectordb.helper import VectorDBHelper
from unstract.sdk.adapters.vectordb.no_op_vectordb.src.no_op_vectordb import (
    NoOpVectorDB,
)
from unstract.sdk.adapters.vectordb.vectordb_adapter import VectorDBAdapter


class NoOpVectorDBAdapter(VectorDBAdapter):
    def __init__(self, settings: dict[str, Any]):
        self._config = settings
        self._collection_name: str = VectorDbConstants.DEFAULT_VECTOR_DB_NAME
        self._vector_db_instance = self._get_vector_db_instance()
        super().__init__("NoOpVectorDb", self._vector_db_instance)

    @staticmethod
    def get_id() -> str:
        return "noOpVectorDb|ca4d6056-4971-4bc8-97e3-9e36290b5bc0"

    @staticmethod
    def get_name() -> str:
        return "No Op VectorDB"

    @staticmethod
    def get_description() -> str:
        return "No Op VectorDB"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/noOpVectorDb.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_vector_db_instance(self) -> VectorStore:
        return self._vector_db_instance

    def _get_vector_db_instance(self) -> VectorStore:
        try:
            dimension = self._config.get(
                VectorDbConstants.EMBEDDING_DIMENSION,
                VectorDbConstants.DEFAULT_EMBEDDING_SIZE,
            )
            self._collection_name = VectorDBHelper.get_collection_name(
                self._config.get(VectorDbConstants.VECTOR_DB_NAME),
                dimension,
            )
            vector_db: VectorStore = NoOpVectorDB(
                dim=dimension, wait_time=self._config.get(VectorDbConstants.WAIT_TIME)
            )
            if vector_db is not None:
                self._client = vector_db.client
            return vector_db
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        return True

    def close(self, **kwargs: Any) -> None:
        pass

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        time.sleep(self._config.get("wait_time"))

    def add(self, ref_doc_id: str, nodes: list[BaseNode]) -> list[str]:
        mock_result: list[str] = []
        time.sleep(self._config.get("wait_time"))
        return mock_result
