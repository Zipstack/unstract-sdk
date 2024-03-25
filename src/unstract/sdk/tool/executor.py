import argparse
import shutil
from json import loads
from pathlib import Path
from typing import Any

from unstract.adapters import get_adapter_version

from unstract.sdk import get_sdk_version
from unstract.sdk.constants import Command
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.tool.validator import ToolValidator


class ToolExecutor:
    """Takes care of executing a tool's intended command."""

    def __init__(self, tool: BaseTool) -> None:
        self.tool = tool

    def execute(self, args: argparse.Namespace) -> None:
        """Executes the tool with the passed arguments.

        Args:
            args (argparse.Namespace): Parsed arguments to execute with
        """
        command = str.upper(args.command)

        if command in Command.static_commands():
            self.tool.handle_static_command(command)
        elif command == Command.RUN:
            self.execute_run(args=args)
        else:
            self.tool.stream_error_and_exit(f"Command {command} not supported")

    def _setup_for_run(self) -> None:
        """Helps initialize tool execution for RUN command."""
        shutil.rmtree(self.tool.get_output_dir(), ignore_errors=True)
        Path(self.tool.get_output_dir()).mkdir(parents=True, exist_ok=True)

    def execute_run(self, args: argparse.Namespace) -> None:
        """Executes the tool's RUN command.

        Args:
            args (argparse.Namespace): Parsed arguments to execute with
        """
        if args.settings is None:
            self.tool.stream_error_and_exit(
                "--settings are required for RUN command"
            )
        settings: dict[str, Any] = loads(args.settings)

        self._setup_for_run()

        validator = ToolValidator(self.tool)
        settings = validator.validate_pre_execution(settings=settings)

        self.tool.stream_log(
            f"Running tool for "
            f"Workflow ID: {self.tool.workflow_id}, "
            f"Execution ID: {self.tool.execution_id}, "
            f"SDK Version: {get_sdk_version()}, "
            f"adapter Version: {get_adapter_version()}"
        )
        self.tool.run(
            settings=settings,
            input_file=self.tool.get_input_file(),
            output_dir=self.tool.get_output_dir(),
        )
        # TODO: Call tool method to validate if output was written
