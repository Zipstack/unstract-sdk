import datetime
import json
import os
from typing import Any

from deprecated import deprecated

from unstract.sdk.constants import Command, LogLevel, LogStage, ToolEnv


class StreamMixin:
    """Helper class for streaming Unstract tool commands.

    A utility class to make writing Unstract tools easier. It provides
    methods to stream the JSON schema, properties, icon, log messages,
    cost, single step messages, and results using the Unstract protocol
    to stdout.
    """

    def __init__(self, log_level: LogLevel = LogLevel.INFO, **kwargs) -> None:
        """
        Args:
            log_level (LogLevel): The log level for filtering of log messages.
            The default is INFO.
                Allowed values are DEBUG, INFO, WARN, ERROR, and FATAL.

        """
        self.log_level = log_level
        self._exec_by_tool = bool(
            os.environ.get(ToolEnv.EXECUTION_BY_TOOL, "False")
        )
        super().__init__(**kwargs)

    def stream_log(
        self,
        log: str,
        level: LogLevel = LogLevel.INFO,
        stage: str = LogStage.TOOL_RUN,
        **kwargs: Any,
    ) -> None:
        """Streams a log message using the Unstract protocol LOG to stdout.

        Args:
            log (str): The log message.
            level (LogLevel): The log level. The default is INFO.
                Allowed values are DEBUG, INFO, WARN, ERROR, and FATAL.
            stage (str): LogStage from constant default Tool_RUN
        Returns:
            None
        """
        levels = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARN,
            LogLevel.ERROR,
            LogLevel.FATAL,
        ]
        if levels.index(level) < levels.index(self.log_level):
            return

        record = {
            "type": "LOG",
            "stage": stage,
            "level": level.value,
            "log": log,
            "emitted_at": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        print(json.dumps(record))

    def stream_error_and_exit(self, message: str) -> None:
        """Stream error log and exit.

        Args:
            message (str): Error message
        """
        self.stream_log(message, level=LogLevel.ERROR)
        if self._exec_by_tool:
            exit(1)
        else:
            raise RuntimeError(
                "RuntimeError from SDK, check the above log for details"
            )

    def get_env_or_die(self, env_key: str) -> str:
        """Returns the value of an env variable.

        If its empty or None, raises an error and exits

        Args:
            env_key (str): Key to retrieve

        Returns:
            str: Value of the env
        """
        env_value = os.environ.get(env_key)
        if env_value is None or env_value == "":
            self.stream_error_and_exit(f"Env variable {env_key} is required")
        return env_value

    @staticmethod
    def stream_spec(spec: str) -> None:
        """Streams JSON schema of the tool using the Unstract protocol SPEC to
        stdout.

        Args:
            spec (str): The JSON schema of the tool.
            Typically returned by the spec() method.

        Returns:
            None
        """
        record = {
            "type": "SPEC",
            "spec": spec,
            "emitted_at": datetime.datetime.now().isoformat(),
        }
        print(json.dumps(record))

    @staticmethod
    def stream_properties(properties: str) -> None:
        """Streams the properties of the tool using the Unstract protocol
        PROPERTIES to stdout.

        Args:
            properties (str): The properties of the tool.
            Typically returned by the properties() method.
        Returns:
            None
        """
        record = {
            "type": "PROPERTIES",
            "properties": properties,
            "emitted_at": datetime.datetime.now().isoformat(),
        }
        print(json.dumps(record))

    @staticmethod
    def stream_variables(variables: str) -> None:
        """Streams JSON schema of the tool's variables using the Unstract
        protocol VARIABLES to stdout.

        Args:
            variables (str): The tool's runtime variables.
            Typically returned by the spec() method.

        Returns:
            None
        """
        record = {
            "type": Command.VARIABLES,
            "variables": variables,
            "emitted_at": datetime.datetime.now().isoformat(),
        }
        print(json.dumps(record))

    @staticmethod
    def stream_icon(icon: str) -> None:
        """Streams the icon of the tool using the Unstract protocol ICON to
        stdout.

        Args:
            icon (str): The icon of the tool.
                Typically returned by the icon() method.
        Returns:
            None
        """
        record = {
            "type": "ICON",
            "icon": icon,
            "emitted_at": datetime.datetime.now().isoformat(),
        }
        print(json.dumps(record))

    @staticmethod
    def stream_update(message: str, state: str, **kwargs: Any) -> None:
        """Streams a log message using the Unstract protocol UPDATE to stdout.

        Args:
            message (str): The log message.
            state (str): LogState from constant
        """
        record = {
            "type": "UPDATE",
            "state": state,
            "message": message,
            "emitted_at": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        print(json.dumps(record))

    @staticmethod
    @deprecated(version="0.4.4", reason="Unused in workflow execution")
    def stream_cost(cost: float, cost_units: str, **kwargs: Any) -> None:
        """Streams the cost of the tool using the Unstract protocol COST to
        stdout.

        Args:
            cost (float): The cost of the tool.
            cost_units (str): The cost units of the tool.
            **kwargs: Additional keyword arguments to include in the record.
        Returns:
            None
        """
        record = {
            "type": "COST",
            "cost": cost,
            "cost_units": cost_units,
            "emitted_at": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        print(json.dumps(record))

    @staticmethod
    @deprecated(version="0.4.4", reason="Unused in workflow execution")
    def stream_single_step_message(message: str, **kwargs: Any) -> None:
        """Streams a single step message using the Unstract protocol
        SINGLE_STEP_MESSAGE to stdout.

        Args:
            message (str): The single step message.
            **kwargs: Additional keyword arguments to include in the record.
        Returns:
            None
        """
        record = {
            "type": "SINGLE_STEP_MESSAGE",
            "message": message,
            "emitted_at": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        print(json.dumps(record))

    @staticmethod
    @deprecated(
        version="0.4.4", reason="Use `BaseTool.write_to_result()` instead"
    )
    def stream_result(result: dict[Any, Any], **kwargs: Any) -> None:
        """Streams the result of the tool using the Unstract protocol RESULT to
        stdout.

        Args:
            result (dict): The result of the tool. Refer to the
                Unstract protocol for the format of the result.
            **kwargs: Additional keyword arguments to include in the record.
        Returns:
            None
        """
        record = {
            "type": "RESULT",
            "result": result,
            "emitted_at": datetime.datetime.now().isoformat(),
            **kwargs,
        }
        print(json.dumps(record))
