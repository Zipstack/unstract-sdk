import unittest
from typing import Any
from unittest.mock import Mock, patch

from unstract.sdk.dbs import ToolDB
from unstract.sdk.tool.base import BaseTool


class UnstractToolDBTest(unittest.TestCase):
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

    @patch("requests.get")
    def test_get_engine(self, mock_requests_get: Mock) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "connector_id": "postgresql|6db35f45-be11-4fd5-80c5-85c48183afbb",
            "connector_metadata": {
                "connection_url": "",
                "database": "test7",
                "host": "localhost",
                "password": "ascon",
                "port": "5432",
                "user": "test",
            },
            "id": "1d393032-87ff-49a2-8f37-8f8dcee7df62",
            "project_id": "3a723424-0070-44c1-a7ec-2976289542d4",
        }
        mock_requests_get.return_value = mock_response
        db = ToolDB(
            tool=self.tool,
            platform_host="http://localhost",
            platform_port="3001",
        )
        tool_instance_id = "6ad6671b-cc3a-4f71-a43c-c88b5046caae"

        engine = db.get_engine(tool_instance_id=tool_instance_id)
        self.assertIsNotNone(engine)


if __name__ == "__main__":
    unittest.main()
