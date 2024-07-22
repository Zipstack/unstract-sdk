from enum import Enum


class ToolEnv:
    """Environment variables used by tools.

    The 'ToolEnv' class represents a set of environment variables that are
    commonly used by tools.

    Attributes:
        PLATFORM_API_KEY (str): Platform service API key.
        PLATFORM_HOST (str): Platform service host.
        PLATFORM_PORT (str): Platform service port.
        DATA_DIR (str): The environment variable for the tool data directory.
        EXECUTION_BY_TOOL (str): Implicitly set to 1 by the SDK if its executed
            by a tool.
    """

    PLATFORM_API_KEY = "PLATFORM_SERVICE_API_KEY"
    PLATFORM_HOST = "PLATFORM_SERVICE_HOST"
    PLATFORM_PORT = "PLATFORM_SERVICE_PORT"
    DATA_DIR = "TOOL_DATA_DIR"
    EXECUTION_BY_TOOL = "EXECUTION_BY_TOOL"


class ConnectorKeys:
    ID = "id"
    PROJECT_ID = "project_id"
    CONNECTOR_ID = "connector_id"
    TOOL_INSTANCE_ID = "tool_instance_id"
    CONNECTOR_METADATA = "connector_metadata"
    CONNECTOR_TYPE = "connector_type"


class AdapterKeys:
    ADAPTER_INSTANCE_ID = "adapter_instance_id"


class PromptStudioKeys:
    PROMPT_REGISTRY_ID = "prompt_registry_id"


class ConnectorType:
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class LogType:
    LOG = "LOG"
    UPDATE = "UPDATE"


class LogStage:
    TOOL_RUN = "TOOL_RUN"


class LogState:
    """State of logs INPUT_UPDATE tag for update the FE input component
    OUTPUT_UPDATE tag for update the FE output component."""

    INPUT_UPDATE = "INPUT_UPDATE"
    OUTPUT_UPDATE = "OUTPUT_UPDATE"


class Connector:
    FILE_SYSTEM = "FILE_SYSTEM"
    DATABASE = "DATABASE"


class Command:
    SPEC = "SPEC"
    PROPERTIES = "PROPERTIES"
    ICON = "ICON"
    RUN = "RUN"
    VARIABLES = "VARIABLES"

    @classmethod
    def static_commands(cls) -> set[str]:
        return {cls.SPEC, cls.PROPERTIES, cls.ICON, cls.VARIABLES}


class UsageType:
    LLM_COMPLETE = "LLM_COMPLETE"
    RAG = "RAG"
    INDEXER = "INDEXER"


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class PropKey:
    """Keys for the properties.json of tools."""

    INPUT = "input"
    OUTPUT = "output"
    RESULT = "result"
    TYPE = "type"
    RESTRICTIONS = "restrictions"
    MAX_FILE_SIZE = "maxFileSize"
    FILE_SIZE_REGEX = r"^(\d+)\s*([KkMmGgTt]B?)$"
    ALLOWED_FILE_TYPES = "allowedFileTypes"
    FUNCTION_NAME = "functionName"

    class OutputType:
        JSON = "JSON"
        TXT = "TXT"


class ToolExecKey:
    OUTPUT_DIR = "COPY_TO_FOLDER"
    METADATA_FILE = "METADATA.json"
    INFILE = "INFILE"
    SOURCE = "SOURCE"


class MetadataKey:
    SOURCE_NAME = "source_name"
    SOURCE_HASH = "source_hash"
    WORKFLOW_ID = "workflow_id"
    EXECUTION_ID = "execution_id"
    ORG_ID = "organization_id"
    TOOL_META = "tool_metadata"
    TOOL_NAME = "tool_name"
    TOTAL_ELA_TIME = "total_elapsed_time"
    ELAPSED_TIME = "elapsed_time"
    OUTPUT = "output"
    OUTPUT_TYPE = "output_type"


class ToolSettingsKey:
    """A class representing the keys used in the tool settings.

    Attributes:
        LLM_ADAPTER_ID (str): The key for the LLM adapter ID.
        EMBEDDING_ADAPTER_ID (str): The key for the embedding adapter ID.
        VECTOR_DB_ADAPTER_ID (str): The key for the vector DB adapter ID.
        X2TEXT_ADAPTER_ID (str): The key for the X2Text adapter ID.
    """

    LLM_ADAPTER_ID = "llmAdapterId"
    EMBEDDING_ADAPTER_ID = "embeddingAdapterId"
    VECTOR_DB_ADAPTER_ID = "vectorDbAdapterId"
    X2TEXT_ADAPTER_ID = "x2TextAdapterId"
    ADAPTER_INSTANCE_ID = "adapter_instance_id"
    EMBEDDING_DIMENSION = "embedding_dimension"
    RUN_ID = "run_id"
    WORKFLOW_ID = "workflow_id"
    EXECUTION_ID = "execution_id"
