import unittest
from io import StringIO
from unittest.mock import patch

from unstract.sdk.tool.mixin import ToolConfigHelper
from unstract.sdk.tool.stream import StreamMixin
from unstract.sdk.utils import ToolUtils


class UnstractSDKToolsStaticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = StreamMixin()

    def test_spec(self):
        spec = ToolUtils.json_to_str(
            ToolConfigHelper.spec(spec_file="config/tool_spec.json")
        )
        self.assertIsNotNone(spec)

    def test_stream_spec(self):
        spec = ToolUtils.json_to_str(
            ToolConfigHelper.spec(spec_file="config/tool_spec.json")
        )
        captured_output = StringIO()
        with patch("sys.stdout", new=captured_output):
            self.tool.stream_spec(spec)
        captured_output_str = captured_output.getvalue()
        # print(captured_output_str)
        self.assertIn("SPEC", captured_output_str)

    def test_properties(self):
        properties = ToolUtils.json_to_str(
            ToolConfigHelper.properties(
                properties_file="config/tool_properties.json"
            )
        )
        self.assertIsNotNone(properties)

    def test_stream_properties(self):
        properties = ToolUtils.json_to_str(
            ToolConfigHelper.properties(
                properties_file="config/tool_properties.json"
            )
        )
        captured_output = StringIO()
        with patch("sys.stdout", new=captured_output):
            self.tool.stream_properties(properties)
        captured_output_str = captured_output.getvalue()
        # print(captured_output_str)
        self.assertIn("PROPERTIES", captured_output_str)

    def test_icon(self):
        icon = ToolConfigHelper.icon(icon_file="config/icon.svg")
        self.assertIsNotNone(icon)

    def test_stream_icon(self):
        icon = ToolConfigHelper.icon(icon_file="config/icon.svg")
        captured_output = StringIO()
        with patch("sys.stdout", new=captured_output):
            self.tool.stream_icon(icon)
        captured_output_str = captured_output.getvalue()
        # print(captured_output_str)
        self.assertIn("ICON", captured_output_str)


if __name__ == "__main__":
    unittest.main()
