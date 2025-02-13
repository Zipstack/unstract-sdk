import os
from enum import Enum


class Modes(Enum):
    NATIVE_TEXT = "native_text"
    LOW_COST = "low_cost"
    HIGH_QUALITY = "high_quality"
    FORM = "form"


class OutputModes(Enum):
    LAYOUT_PRESERVING = "layout_preserving"
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
    """Env variables for LLMWhisperer.

    Can be used to alter behaviour at runtime.

    Attributes:
        POLL_INTERVAL: Time in seconds to wait before polling
            LLMWhisperer's status API. Defaults to 30s
        MAX_POLLS: Total number of times to poll the status API.
            Set to -1 to poll indefinitely. Defaults to -1
        STATUS_RETRIES: Number of times to retry calling LLLMWhisperer's status API
            on failure during polling. Defaults to 5.
    """

    WAIT_TIMEOUT = "ADAPTER_LLMW_WAIT_TIMEOUT"
    LOG_LEVEL = "LOG_LEVEL"


class WhispererConfig:
    """Dictionary keys used to configure LLMWhisperer service."""

    URL = "url"
    MODE = "mode"
    OUTPUT_MODE = "output_mode"
    UNSTRACT_KEY = "unstract_key"
    MEDIAN_FILTER_SIZE = "median_filter_size"
    GAUSSIAN_BLUR_RADIUS = "gaussian_blur_radius"
    LINE_SPLITTER_TOLERANCE = "line_splitter_tolerance"
    LINE_SPLITTER_STRATEGY = "line_spitter_strategy"
    HORIZONTAL_STRETCH_FACTOR = "horizontal_stretch_factor"
    PAGES_TO_EXTRACT = "pages_to_extract"
    MARK_VERTICAL_LINES = "mark_vertical_lines"
    MARK_HORIZONTAL_LINES = "mark_horizontal_lines"
    PAGE_SEPARATOR = "page_seperator"
    URL_IN_POST = "url_in_post"
    TAG = "tag"
    USE_WEBHOOK = "use_webhook"
    WEBHOOK_METADATA = "webhook_metadata"
    TEXT_ONLY = "text_only"
    WAIT_TIMEOUT = "wait_timeout"
    WAIT_FOR_COMPLETION = "wait_for_completion"
    LOGGING_LEVEL = "logging_level"


class WhisperStatus:
    """Values returned / used by /whisper-status endpoint."""

    PROCESSING = "processing"
    PROCESSED = "processed"
    DELIVERED = "delivered"
    UNKNOWN = "unknown"
    # Used for async processing
    WHISPER_HASH = "whisper_hash"
    STATUS = "status"


class WhispererDefaults:
    """Defaults meant for LLMWhisperer."""

    MEDIAN_FILTER_SIZE = 0
    GAUSSIAN_BLUR_RADIUS = 0.0
    FORCE_TEXT_PROCESSING = False
    LINE_SPLITTER_TOLERANCE = 0.75
    LINE_SPLITTER_STRATEGY = "left-priority"
    HORIZONTAL_STRETCH_FACTOR = 1.0
    PAGES_TO_EXTRACT = ""
    PAGE_SEPARATOR = "<<<"
    MARK_VERTICAL_LINES = False
    MARK_HORIZONTAL_LINES = False
    URL_IN_POST = False
    TAG = "default"
    TEXT_ONLY = False
    WAIT_TIMEOUT = int(os.getenv(WhispererEnv.WAIT_TIMEOUT, 300))
    WAIT_FOR_COMPLETION = True
    LOGGING_LEVEL = os.getenv(WhispererEnv.LOG_LEVEL, "INFO")
