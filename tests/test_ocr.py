import json
import logging
import os
import unittest
from typing import Any

from dotenv import load_dotenv
from parameterized import parameterized

from unstract.sdk.ocr import OCR
from unstract.sdk.tool.base import BaseTool

load_dotenv()

logger = logging.getLogger(__name__)


def get_test_values(env_key: str) -> list[str]:
    values = json.loads(os.environ.get(env_key))
    return values


def get_env_value(env_key: str) -> str:
    value = os.environ.get(env_key)
    return value


class ToolOCRTest(unittest.TestCase):
    class MockTool(BaseTool):
        def run(
            self,
            params: dict[str, Any] = {},
            settings: dict[str, Any] = {},
            workflow_id: str = "",
        ) -> None:
            pass

    @classmethod
    def setUpClass(cls):
        cls.tool = cls.MockTool()

    @parameterized.expand(get_test_values("OCR_TEST_VALUES"))
    def test_get_ocr(self, adapter_instance_id):
        tool_ocr = OCR(tool=self.tool)
        ocr = tool_ocr.get_ocr(adapter_instance_id)
        result = ocr.test_connection()
        self.assertTrue(result)
        input_file = get_env_value("INPUT_FILE_PATH")
        output_file = get_env_value("OUTPUT_FILE_PATH")
        if os.path.isfile(output_file):
            os.remove(output_file)
        output = ocr.process(input_file, output_file)
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0)
        if os.path.isfile(output_file):
            os.remove(output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
            f.close()
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0)


if __name__ == "__main__":
    unittest.main()
