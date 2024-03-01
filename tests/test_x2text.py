import json
import logging
import os
import unittest
from typing import Any

from dotenv import load_dotenv
from parameterized import parameterized

from unstract.sdk.tool.base import BaseTool
from unstract.sdk.x2txt import X2Text

load_dotenv()

logger = logging.getLogger(__name__)


def get_test_values(env_key: str) -> list[str]:
    values = json.loads(os.environ.get(env_key))
    return values


def get_env_value(env_key: str) -> str:
    value = os.environ.get(env_key)
    return value


class ToolX2TextTest(unittest.TestCase):
    class MockTool(BaseTool):
        def run(
            self,
            params: dict[str, Any] = {},
            settings: dict[str, Any] = {},
            workflow_id: str = "",
        ) -> None:
            # Dummify method for dummy tool
            pass

    @classmethod
    def setUpClass(cls):
        cls.tool = cls.MockTool()

    @parameterized.expand(get_test_values("X2TEXT_TEST_VALUES"))
    def test_get_x2text(self, adapter_instance_id):
        tool_x2text = X2Text(tool=self.tool)
        x2text = tool_x2text.get_x2text(adapter_instance_id)
        self.assertIsNotNone(x2text)
        self.assertTrue(x2text.test_connection())

        input_file = get_env_value("INPUT_FILE_PATH")
        output_file = get_env_value("OUTPUT_FILE_PATH")

        if os.path.isfile(output_file):
            os.remove(output_file)
        file_content = x2text.process(input_file, output_file)
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0)

        if os.path.isfile(output_file):
            os.remove(output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(file_content)
            f.close()
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0)


if __name__ == "__main__":
    unittest.main()
