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
    MODE = "mode"
    OUTPUT_MODE = "output_mode"
    UNSTRACT_KEY = "unstract_key"
    MEDIAN_FILTER_SIZE = "median_filter_size"
    GAUSSIAN_BLUR_RADIUS = "gaussian_blur_radius"
    LINE_SPLITTER_TOLERANCE = "line_splitter_tolerance"
    LINE_SPLITTER_STRATEGY = "line_splitter_strategy"
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
    """Defaults meant for LLM whisperer."""

    MEDIAN_FILTER_SIZE = 0
    GAUSSIAN_BLUR_RADIUS = 0.0
    FORCE_TEXT_PROCESSING = False
    LINE_SPLITTER_TOLERANCE = 0.75
    LINE_SPLITTER_STRATEGY = "left-priority"
    HORIZONTAL_STRETCH_FACTOR = 1.0
    POLL_INTERVAL = int(os.getenv(WhispererEnv.POLL_INTERVAL, 30))
    MAX_POLLS = int(os.getenv(WhispererEnv.MAX_POLLS, 30))
    PAGES_TO_EXTRACT = ""
    PAGE_SEPARATOR = "<<<"
    MARK_VERTICAL_LINES = False
    MARK_HORIZONTAL_LINES = False
    URL_IN_POST = False
    TAG = "default"
    TEXT_ONLY = False
