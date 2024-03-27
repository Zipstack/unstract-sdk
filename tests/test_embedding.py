import json
import os
import unittest

from dotenv import load_dotenv
from llama_index.core.embeddings import BaseEmbedding
from parameterized import parameterized

from unstract.sdk.embedding import ToolEmbedding
from unstract.sdk.tool.base import BaseTool

load_dotenv()


def get_test_values(env_key: str) -> list[str]:
    test_values = json.loads(os.environ.get(env_key))
    return test_values


class ToolEmbeddingTest(unittest.TestCase):
    TEST_SNIPPET = "Hello, I am Unstract"

    class MockTool(BaseTool):
        def run(
            self,
        ) -> None:
            self.stream_log("Mock tool running")

    def setUp(self) -> None:
        self.tool = self.MockTool()

    def run_embedding_test(self, adapter_instance_id):
        embedding = ToolEmbedding(tool=self.tool)
        embed_model = embedding.get_embedding(adapter_instance_id)
        self.assertIsNotNone(embed_model)
        self.assertIsInstance(embed_model, BaseEmbedding)
        response = embed_model._get_text_embedding(
            ToolEmbeddingTest.TEST_SNIPPET
        )
        self.assertIsNotNone(response)

    @parameterized.expand(get_test_values("EMBEDDING_TEST_VALUES"))
    def test_get_embedding(self, adapter_instance_id: str) -> None:
        self.run_embedding_test(adapter_instance_id)


if __name__ == "__main__":
    unittest.main()
