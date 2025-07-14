import logging
import signal
from typing import Any

from unstract.sdk.tool.base import BaseTool
from unstract.sdk.tool.executor import ToolExecutor
from unstract.sdk.tool.parser import ToolArgsParser

logger = logging.getLogger(__name__)

class ToolEntrypoint:
    """Class that contains methods for the entrypoint for a tool."""

    @staticmethod
    def _signal_handler(signum: int, frame: Any) -> None:
        """Handle SIGTERM and SIGINT signals."""
        sig = signal.Signals(signum)
        signal_name = sig.name
        logger.info("Received %s signal", signal_name)

    @staticmethod
    def launch(tool: BaseTool, args: list[str]) -> None:
        """Entrypoint function for a tool.

        It parses the arguments passed to a tool and executes
        the intended command.

        Args:
            tool (AbstractTool): Tool to execute
            args (List[str]): Arguments passed to a tool
        """
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, ToolEntrypoint._signal_handler)
        signal.signal(signal.SIGINT, ToolEntrypoint._signal_handler)
        
        parsed_args = ToolArgsParser.parse_args(args)
        executor = ToolExecutor(tool=tool)
        executor.execute(parsed_args)
