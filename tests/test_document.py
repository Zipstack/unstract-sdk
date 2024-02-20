import unittest
from typing import Any

from unstract.sdk.documents import ToolDocs
from unstract.sdk.tool.base import BaseTool


class UnstractToolDocsTest(unittest.TestCase):
    class MockTool(BaseTool):
        def run(
            self,
            params: dict[str, Any] = {},
            settings: dict[str, Any] = {},
            workflow_id: str = "",
        ) -> None:
            # self.stream_log("Mock tool running")
            pass

    @classmethod
    def setUpClass(cls):
        cls.tool = cls.MockTool()

    @unittest.skip("Skipping")
    def test_insert_get_delete(self) -> None:
        docs = ToolDocs(
            tool=self.tool, platform_host="http://localhost", platform_port=3001
        )
        result = docs.insert(
            workflow_id="test",
            unique_file_id="test_unique_file_id2",
            filename="test_filename",
            filetype="test_filetype",
            summary="test_summary",
            embedding_tokens=0,
            llm_tokens=0,
            vector_db="Postgres pg_vector",
        )
        self.assertTrue(result)
        result = docs.get(
            workflow_id="test", unique_file_id="test_unique_file_id2"
        )
        print(result)
        self.assertIsNotNone(result)
        result = docs.delete(
            workflow_id="test", unique_file_id="test_unique_file_id2"
        )
        self.assertTrue(result)
        result = docs.get(
            workflow_id="test", unique_file_id="test_unique_file_id2"
        )
        self.assertIsNone(result)

    # def test_indexer(self) -> None:
    #     docs = ToolDocs(
    #         tool=self.tool, platform_host="http://localhost", platform_port=3001  # noqa: E501
    #     )
    #     result = docs.index_file(
    #         workflow_id="test2",
    #         embedding_type="Azure OpenAI",
    #         vector_db="Postgres pg_vector",
    #         file_path="/mnt/unstract/fs_input/files/Suriya cv.pdf",
    #         overwrite=True,
    #     )
    #     print(result)
    #     self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
