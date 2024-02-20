import unittest
from io import StringIO
from typing import Any
from unittest.mock import patch

from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.tool.entrypoint import ToolEntrypoint


class UnstractSDKToolsEntrypointTest(unittest.TestCase):
    INFO_MESSAGE = "Running a mock tool"
    DEBUG_MESSAGE = "Example DEBUG message"

    class MockTool(BaseTool):
        def run(
            self,
            params: dict[str, Any] = {},
            settings: dict[str, Any] = {},
            workflow_id: str = "",
        ) -> None:
            self.stream_log(UnstractSDKToolsEntrypointTest.INFO_MESSAGE)
            self.stream_log(
                UnstractSDKToolsEntrypointTest.DEBUG_MESSAGE, LogLevel.DEBUG
            )

    @classmethod
    def setUpClass(cls):
        cls.tool = cls.MockTool(log_level=LogLevel.DEBUG)

    def _launch_tool(self, args: list[str]) -> str:
        captured_output = StringIO()
        with patch("sys.stdout", new=captured_output):
            ToolEntrypoint.launch(tool=self.tool, args=args)
        return captured_output.getvalue()

    def test_spec(self):
        args = [
            "--command",
            "SPEC",
            "--workflow-id",
            "00000000-0000-0000-0000-000000000000",
            "--log-level",
            "INFO",
        ]
        captured_output_str = self._launch_tool(args=args)
        self.assertIn("SPEC", captured_output_str)

    def test_properties(self):
        args = [
            "--command",
            "PROPERTIES",
            "--workflow-id",
            "00000000-0000-0000-0000-000000000000",
            "--log-level",
            "INFO",
        ]
        captured_output_str = self._launch_tool(args=args)
        self.assertIn("PROPERTIES", captured_output_str)

    def test_variables(self):
        args = [
            "--command",
            "VARIABLES",
            "--workflow-id",
            "00000000-0000-0000-0000-000000000000",
            "--log-level",
            "INFO",
        ]
        captured_output_str = self._launch_tool(args=args)
        self.assertIn("VARIABLES", captured_output_str)

    def test_run(self):
        args = [
            "--command",
            "RUN",
            "--params",
            "{}",
            "--settings",
            "{}",
            "--workflow-id",
            "00000000-0000-0000-0000-000000000000",
            "--log-level",
            "INFO",
        ]
        captured_output_str = self._launch_tool(args=args)
        self.assertIn(self.INFO_MESSAGE, captured_output_str)

    def test_run_debug(self):
        args = [
            "--command",
            "RUN",
            "--params",
            "{}",
            "--settings",
            "{}",
            "--workflow-id",
            "00000000-0000-0000-0000-000000000000",
            "--log-level",
            "DEBUG",
        ]
        captured_output_str = self._launch_tool(args=args)
        self.assertIn(self.DEBUG_MESSAGE, captured_output_str)


if __name__ == "__main__":
    unittest.main()
