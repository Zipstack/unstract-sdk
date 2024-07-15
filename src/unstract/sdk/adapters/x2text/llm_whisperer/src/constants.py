import os
from enum import Enum


class ProcessingModes(Enum):
    OCR = "ocr"
    TEXT = "text"


class OutputModes(Enum):
    LINE_PRINTER = "line-printer"
    DUMP_TEXT = "dump-text"
    TEXT = "text"


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"


class WhispererHeader:
    UNSTRACT_KEY = "unstract-key"


class WhispererEndpoint:
    """Endpoints available at LLMWhisperer service."""

    TEST_CONNECTION = "test-connection"
    WHISPER = "whisper"
    STATUS = "whisper-status"
    RETRIEVE = "whisper-retrieve"


class WhispererEnv:
    """Env variables for LLM whisperer.

    Can be used to alter behaviour at runtime.

    Attributes:
        POLL_INTERVAL: Time in seconds to wait before polling
            LLMWhisperer's status API. Defaults to 30s
        MAX_POLLS: Total number of times to poll the status API.
            Set to -1 to poll indefinitely. Defaults to -1
    """

    POLL_INTERVAL = "ADAPTER_LLMW_POLL_INTERVAL"
    MAX_POLLS = "ADAPTER_LLMW_MAX_POLLS"


class WhispererConfig:
    """Dictionary keys used to configure LLMWhisperer service."""

    URL = "url"
    PROCESSING_MODE = "processing_mode"
    OUTPUT_MODE = "output_mode"
    UNSTRACT_KEY = "unstract_key"
    MEDIAN_FILTER_SIZE = "median_filter_size"
    GAUSSIAN_BLUR_RADIUS = "gaussian_blur_radius"
    FORCE_TEXT_PROCESSING = "force_text_processing"
    LINE_SPLITTER_TOLERANCE = "line_splitter_tolerance"
    HORIZONTAL_STRETCH_FACTOR = "horizontal_stretch_factor"
    STORE_METADATA_FOR_HIGHLIGHTING = "store_metadata_for_highlighting"


class WhisperStatus:
    """Values returned / used by /whisper-status endpoint."""

    PROCESSING = "processing"
    PROCESSED = "processed"
    DELIVERED = "delivered"
    UNKNOWN = "unknown"
    # Used for async processing
    WHISPER_HASH = "whisper-hash"
    STATUS = "status"


class WhispererDefaults:
    """Defaults meant for LLM whisperer."""

    MEDIAN_FILTER_SIZE = 0
    GAUSSIAN_BLUR_RADIUS = 0.0
    FORCE_TEXT_PROCESSING = False
    LINE_SPLITTER_TOLERANCE = 0.75
    HORIZONTAL_STRETCH_FACTOR = 1.0
    POLL_INTERVAL = int(os.getenv(WhispererEnv.POLL_INTERVAL, 30))
    MAX_POLLS = int(os.getenv(WhispererEnv.MAX_POLLS, 30))
