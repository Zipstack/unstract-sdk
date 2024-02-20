import unittest
from typing import Any

from unstract.sdk.cache import ToolCache
from unstract.sdk.tool.base import BaseTool


# Requires the platform service to be run and
# PLATFORM_SERVICE_API_KEY env to be set
class UnstractToolCacheTest(unittest.TestCase):
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

    def test_set(self):
        cache = ToolCache(
            tool=self.tool, platform_host="http://localhost", platform_port=3001
        )
        result = cache.set(key="test_key", value="test_value")
        self.assertTrue(result)

    def test_get(self):
        cache = ToolCache(
            tool=self.tool, platform_host="http://localhost", platform_port=3001
        )
        cache.set(key="test_key", value="test_value")
        result = cache.get(key="test_key")
        self.assertEqual(result, "test_value")

    def test_delete(self):
        cache = ToolCache(
            tool=self.tool, platform_host="http://localhost", platform_port=3001
        )
        cache.set(key="test_key", value="test_value")
        result = cache.delete(key="test_key")
        self.assertTrue(result)
        result = cache.get(key="test_key")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
