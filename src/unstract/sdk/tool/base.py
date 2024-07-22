import datetime
import json
from abc import ABC, abstractmethod
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any, Union

from unstract.sdk.constants import (
    Command,
    LogLevel,
    MetadataKey,
    PropKey,
    ToolEnv,
    ToolExecKey,
)
from unstract.sdk.tool.mixin import ToolConfigHelper
from unstract.sdk.tool.parser import ToolArgsParser
from unstract.sdk.tool.stream import StreamMixin
from unstract.sdk.utils import ToolUtils


class BaseTool(ABC, StreamMixin):
    """Abstract class for Unstract tools."""

    def __init__(self, log_level: LogLevel = LogLevel.INFO) -> None:
        """Creates an UnstractTool.

        Args:
            log_level (str): Log level for the tool
                Can be one of INFO, DEBUG, WARN, ERROR, FATAL.
        """
        self.start_time = datetime.datetime.now()
        super().__init__(log_level=log_level)
        self.properties = ToolConfigHelper.properties()
        self.spec = ToolConfigHelper.spec()
        self.variables = ToolConfigHelper.variables()
        self.workflow_id = ""
        self.execution_id = ""
        self.org_id = ""
        self._exec_metadata = {}

    @classmethod
    def from_tool_args(cls, args: list[str]) -> "BaseTool":
        """Builder method to create a tool from args passed to a tool.

        Refer the tool's README to know more about the possible args

        Args:
            args (List[str]): Arguments passed to a tool

        Returns:
            AbstractTool: Abstract base tool class
        """
        parsed_args = ToolArgsParser.parse_args(args)
        tool = cls(log_level=parsed_args.log_level)
        if parsed_args.command not in Command.static_commands():
            tool._exec_metadata = tool._get_exec_metadata()
            tool.workflow_id = tool._exec_metadata.get(MetadataKey.WORKFLOW_ID)
            tool.execution_id = tool._exec_metadata.get(MetadataKey.EXECUTION_ID)
            tool.org_id = tool._exec_metadata.get(MetadataKey.ORG_ID)
        return tool

    def elapsed_time(self) -> float:
        """Returns the elapsed time since the tool was created."""
        return (datetime.datetime.now() - self.start_time).total_seconds()

    def handle_static_command(self, command: str) -> None:
        """Handles a static command.

        Used to handle commands that do not require any processing. Currently,
        the only supported static commands are
        SPEC, PROPERTIES, VARIABLES and ICON.

        This is used by the Unstract SDK to handle static commands.
        It is not intended to be used by the tool. The tool
        stub will automatically handle static commands.

        Args:
            command (str): The static command.
        Returns:
            None
        """
        if command == Command.SPEC:
            self.stream_spec(ToolUtils.json_to_str(self.spec))
        elif command == Command.PROPERTIES:
            self.stream_properties(ToolUtils.json_to_str(self.properties))
        elif command == Command.ICON:
            self.stream_icon(ToolConfigHelper.icon())
        elif command == Command.VARIABLES:
            self.stream_variables(ToolUtils.json_to_str(self.variables))
        else:
            raise ValueError(f"Unknown command {command}")

    def _get_data_dir(self) -> Path:
        """Gets the TOOL_DATA_DIR that houses the input and output files of
        tool execution.

        Returns:
            Path: Path object of the TOOL_DATA_DIR that's configured.
        """
        data_dir = self.get_env_or_die(ToolEnv.DATA_DIR)
        base_path = Path(data_dir)
        if not base_path.exists():
            self.stream_error_and_exit(f"{data_dir} does not exist")
        if not base_path.is_dir():
            self.stream_error_and_exit(f"{data_dir} is not a directory")
        return base_path.absolute()

    def _get_file_from_data_dir(self, file_to_get: str, raise_err: bool = False) -> str:
        base_path: Path = self._get_data_dir()
        file_path = base_path / file_to_get
        if raise_err and not file_path.exists():
            self.stream_error_and_exit(f"{file_to_get} is missing in TOOL_DATA_DIR")
        return str(file_path)

    def get_source_file(self) -> str:
        """Gets the absolute path to the workflow execution's input file
        (SOURCE).

        Returns:
            str: Absolute path to the source file
        """
        return self._get_file_from_data_dir(ToolExecKey.SOURCE, raise_err=True)

    def get_input_file(self) -> str:
        """Gets the absolute path to the input file that's meant for the tool
        being run (INFILE).

        Returns:
            str: Absolute path to the input file
        """
        return self._get_file_from_data_dir(ToolExecKey.INFILE, raise_err=True)

    def get_output_dir(self) -> str:
        """Get the absolute path to the output folder where the tool needs to
        place its output file. This is where the tool writes its output files
        that need to be copied into the destination (COPY_TO_FOLDER path).

        Returns:
            str: Absolute path to the output directory.
        """
        base_path: Path = self._get_data_dir()
        return str(base_path / ToolExecKey.OUTPUT_DIR)

    @property
    def get_exec_metadata(self) -> dict[str, Any]:
        """Getter for `exec_metadata` of the tool.

        Returns:
            dict[str, Any]: Contents of METADATA.json
        """
        return self._exec_metadata

    def _get_exec_metadata(self) -> dict[str, Any]:
        """Retrieve the contents from METADATA.json present in the data
        directory. This file contains metadata for the tool execution.

        Returns:
            dict[str, Any]: Contents of METADATA.json
        """
        base_path: Path = self._get_data_dir()
        metadata_path = base_path / ToolExecKey.METADATA_FILE
        metadata_json = {}
        try:
            with open(metadata_path, encoding="utf-8") as f:
                metadata_json = loads(f.read())
        except JSONDecodeError as e:
            self.stream_error_and_exit(f"JSON decode error for {metadata_path}: {e}")
        except FileNotFoundError:
            self.stream_error_and_exit(f"Metadata file not found at {metadata_path}")
        except OSError as e:
            self.stream_error_and_exit(f"OS Error while opening {metadata_path}: {e}")
        return metadata_json

    def _write_exec_metadata(self, metadata: dict[str, Any]) -> None:
        """Helps write the `METADATA.JSON` file.

        Args:
            metadata (dict[str, Any]): Metadata to write
        """
        base_path: Path = self._get_data_dir()
        metadata_path = base_path / ToolExecKey.METADATA_FILE
        with metadata_path.open("w", encoding="utf-8") as f:
            f.write(ToolUtils.json_to_str(metadata))

    def _update_exec_metadata(self) -> None:
        """Updates the execution metadata after a tool executes.

        Currently overrwrites most of the keys with the latest tool
        executed.
        """
        tool_metadata = {
            MetadataKey.TOOL_NAME: self.properties[PropKey.FUNCTION_NAME],
            MetadataKey.ELAPSED_TIME: self.elapsed_time(),
            MetadataKey.OUTPUT_TYPE: self.properties[PropKey.RESULT][PropKey.TYPE],
        }
        if MetadataKey.TOTAL_ELA_TIME not in self._exec_metadata:
            self._exec_metadata[MetadataKey.TOTAL_ELA_TIME] = self.elapsed_time()
        else:
            self._exec_metadata[MetadataKey.TOTAL_ELA_TIME] += self.elapsed_time()

        if MetadataKey.TOOL_META not in self._exec_metadata:
            self._exec_metadata[MetadataKey.TOOL_META] = [tool_metadata]
        else:
            self._exec_metadata[MetadataKey.TOOL_META].append(tool_metadata)

        self._write_exec_metadata(metadata=self._exec_metadata)

    def update_exec_metadata(self, metadata: dict[str, Any]) -> None:
        """Helps update the execution metadata with the provided metadata
        dictionary.

        This method iterates over the key-value pairs in the input metadata dictionary
        and updates the internal `_exec_metadata` dictionary of the tool instance
        accordingly. It then writes the updated metadata to the `METADATA.json`
        file in the tool's data directory.

        Args:
            metadata (dict[str, Any]): A dictionary containing the metadata
            key-value pairs to update in the execution metadata.

        Returns:
            None
        """
        for key, value in metadata.items():
            self._exec_metadata[key] = value

        self._write_exec_metadata(metadata=self._exec_metadata)

    def write_tool_result(self, data: Union[str, dict[str, Any]]) -> None:
        """Helps write contents of the tool result into TOOL_DATA_DIR.

        Args:
            data (Union[str, dict[str, Any]]): Data to be written
        """
        output_type = self.properties[PropKey.RESULT][PropKey.TYPE]
        if output_type is PropKey.OutputType.JSON and not isinstance(data, dict):
            # TODO: Validate JSON type output with output schema as well
            self.stream_error_and_exit(
                f"Expected result to have type {PropKey.OutputType.JSON} "
                f"but {type(data)} is passed"
            )

        # TODO: Review if below is necessary
        result = {
            "workflow_id": self.workflow_id,
            "elapsed_time": self.elapsed_time(),
            "output": data,
        }
        self.stream_result(result)

        self._update_exec_metadata()
        json_data = json.dumps(data)
        # INFILE is overwritten for next tool to run
        input_file_path: Path = Path(self.get_input_file())
        with input_file_path.open("w", encoding="utf-8") as f:
            f.write(json_data)

    def validate(self, input_file: str, settings: dict[str, Any]) -> None:
        """Override to implement custom validation for the tool.

        Args:
            input_file (str): Path to the file that will be used for execution.
            settings (dict[str, Any]): Settings configured for the tool.
                Defaults initialized through the tool's SPEC.
        """
        pass

    @abstractmethod
    def run(
        self,
        settings: dict[str, Any],
        input_file: str,
        output_dir: str,
    ) -> None:
        """Implements RUN command for the tool.

        Args:
            settings (dict[str, Any]): Settings for the tool
            input_file (str): Path to the input file
            output_dir (str): Path to write the tool output to which gets copied
                into the destination
        """
        pass
