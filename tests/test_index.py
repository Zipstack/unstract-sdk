import json
import logging
import os
import unittest
from typing import Any, Optional
from unittest.mock import Mock, patch

from dotenv import load_dotenv
from parameterized import parameterized

from unstract.sdk.index import Index
from unstract.sdk.tool.base import BaseTool

load_dotenv()

logger = logging.getLogger(__name__)


def get_test_values(env_key: str) -> list[str]:
    test_values = json.loads(os.environ.get(env_key))
    return test_values


class ToolLLMTest(unittest.TestCase):
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

    @patch(
        "unstract.sdk.index.Index.generate_index_key",
        Mock(
            return_value="77843eb8d9e30ad56bfcb018c2633fa32feef2f0c09762b6b820c75664b64c1b"
        ),
    )
    def test_generate_file_id(self):
        expected = "77843eb8d9e30ad56bfcb018c2633fa32feef2f0c09762b6b820c75664b64c1b"
        index = Index(tool=self.tool)
        actual = index.generate_file_id(
            tool_id="8ac26867-7811-4dc7-a17b-b16d3b561583",
            vector_db="81f1f6a8-cae8-4b8e-b2a4-57f80de512f6",
            embedding="ecf998d6-ded0-4aca-acd1-372a21daf0f9",
            x2text="59bc55fc-e2a7-48dd-ae93-794b4d81d46e",
            chunk_size="1024",
            chunk_overlap="128",
            file_path="/a/b/c",
            file_hash="045b1a67824592b67426f8e60c1f8328e8d2a35139f9983e0aa0a7b6f10915c3",
        )
        assert expected == actual

    test_data = [
        {
            "vector_db": "81f1f6a8-cae8-4b8e-b2a4-57f80de512f6",
            "embedding": "ecf998d6-ded0-4aca-acd1-372a21daf0f9",
            "x2text": "59bc55fc-e2a7-48dd-ae93-794b4d81d46e",
            "chunk_size": "1024",
            "chunk_overlap": "128",
            "file_path": "/a/b/c",
        },
        {
            "vector_db": "81f1f6a8-cae8-4b8e-b2a4-57f80de512f6",
            "embedding": "ecf998d6-ded0-4aca-acd1-372a21daf0f9",
            "x2text": "59bc55fc-e2a7-48dd-ae93-794b4d81d46e",
            "chunk_size": "1024",
            "chunk_overlap": "128",
            "file_path": "/a/b/c",
            "file_hash": "045b1a67824592b67426f8e60c1f8328e8d2a35139f9983e0aa0a7b6f10915c3",
        },
    ]

    @parameterized.expand(test_data)
    @patch(
        "unstract.sdk.adapter.ToolAdapter.get_adapter_config",
        Mock(return_value={}),
    )
    @patch(
        "unstract.sdk.utils.ToolUtils.hash_str",
        Mock(
            return_value="77843eb8d9e30ad56bfcb018c2633fa32feef2f0c09762b6b820c75664b64c1b"
        ),
    )
    @patch(
        "unstract.sdk.utils.ToolUtils.get_hash_from_file",
        Mock(
            return_value="ab940bb34a60d2a7876dd8e1bd1b22f5dc85936a9e2af3c49bfc888a1d944ff0"
        ),
    )
    def test_generate_index_key(
        self,
        vector_db: str,
        embedding: str,
        x2text: str,
        chunk_size: str,
        chunk_overlap: str,
        file_path: Optional[str] = None,
        file_hash: Optional[str] = None,
    ):
        expected = "77843eb8d9e30ad56bfcb018c2633fa32feef2f0c09762b6b820c75664b64c1b"
        index = Index(tool=self.tool)
        actual = index.generate_index_key(
            vector_db,
            embedding,
            x2text,
            chunk_size,
            chunk_overlap,
            file_path,
            file_hash,
        )
        assert expected == actual


if __name__ == "__main__":
    unittest.main()
