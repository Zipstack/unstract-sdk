import json
import logging
import os
import unittest

from dotenv import load_dotenv
from llama_index.core import MockEmbedding
from llama_index.core.vector_stores.types import (
    BasePydanticVectorStore,
    VectorStore,
)
from parameterized import parameterized
from unstract.adapters.vectordb.helper import VectorDBHelper

from unstract.sdk.tool.base import BaseTool
from unstract.sdk.vector_db import ToolVectorDB

load_dotenv()

logger = logging.getLogger(__name__)


def get_test_values(env_key: str) -> list[str]:
    test_values = json.loads(os.environ.get(env_key))
    return test_values


class ToolVectorDBTest(unittest.TestCase):
    class MockTool(BaseTool):
        def run(
            self,
        ) -> None:
            self.stream_log("Mock tool running")

    def setUp(self) -> None:
        self.tool = self.MockTool()

    @parameterized.expand(
        get_test_values("VECTOR_DB_TEST_VALUES")
        # Works for Qdrant and Postgres
    )
    def test_get_vector_db(self, adapter_instance_id: str) -> None:
        mock_embedding = MockEmbedding(embed_dim=1)
        unstract_tool_vector_db = ToolVectorDB(tool=self.tool)
        vector_store = unstract_tool_vector_db.get_vector_db(
            adapter_instance_id, mock_embedding.embed_dim
        )
        self.assertIsNotNone(vector_store)
        self.assertIsInstance(
            vector_store, (BasePydanticVectorStore, VectorStore)
        )

        result = VectorDBHelper.test_vector_db_instance(vector_store)
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
