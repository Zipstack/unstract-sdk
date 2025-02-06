import os
from enum import Enum


class ProcessingModes(Enum):
    OCR = "ocr"
    TEXT = "text"


class Modes(Enum):
    NATIVE_TEXT = "native_text"
    LOW_COST = "low_cost"
    HIGH_QUALITY = "high_quality"
    FORM = "form"


class OutputModes(Enum):
    LINE_PRINTER = "line-printer"
    DUMP_TEXT = "dump-text"
    TEXT = "text"
    LAYOUT_PRESERVING = "layout_preserving"


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

    POLL_INTERVAL = "ADAPTER_LLMW_POLL_INTERVAL"
    MAX_POLLS = "ADAPTER_LLMW_MAX_POLLS"
    POLL_INTERVAL_V2 = "ADAPTER_LLMW_POLL_INTERVAL_V2"
    MAX_POLLS_V2 = "ADAPTER_LLMW_MAX_POLLS_V2"
    STATUS_RETRIES = "ADAPTER_LLMW_STATUS_RETRIES"


class WhispererConfig:
    """Dictionary keys used to configure LLMWhisperer service."""

    URL = "url"
    PROCESSING_MODE = "processing_mode"
    MODE = "mode"
    OUTPUT_MODE = "output_mode"
    UNSTRACT_KEY = "unstract_key"
    MEDIAN_FILTER_SIZE = "median_filter_size"
    GAUSSIAN_BLUR_RADIUS = "gaussian_blur_radius"
    FORCE_TEXT_PROCESSING = "force_text_processing"
    LINE_SPLITTER_TOLERANCE = "line_splitter_tolerance"
    LINE_SPLITTER_STRATEGY = "line_splitter_strategy"
    HORIZONTAL_STRETCH_FACTOR = "horizontal_stretch_factor"
    PAGES_TO_EXTRACT = "pages_to_extract"
    STORE_METADATA_FOR_HIGHLIGHTING = "store_metadata_for_highlighting"
    ADD_LINE_NOS = "add_line_nos"
    OUTPUT_JSON = "output_json"
    PAGE_SEPARATOR = "page_seperator"
    MARK_VERTICAL_LINES = "mark_vertical_lines"
    MARK_HORIZONTAL_LINES = "mark_horizontal_lines"
    URL_IN_POST = "url_in_post"
    TAG = "tag"
    USE_WEBHOOK = "use_webhook"
    WEBHOOK_METADATA = "webhook_metadata"
    TEXT_ONLY = "text_only"
    VERSION = "version"
    WAIT_TIMEOUT = "wait_timeout"
    WAIT_FOR_COMPLETION ="wait_for_completion"

class WhisperStatus:
    """Values returned / used by /whisper-status endpoint."""

    PROCESSING = "processing"
    PROCESSED = "processed"
    DELIVERED = "delivered"
    UNKNOWN = "unknown"
    # Used for async processing
    WHISPER_HASH = "whisper-hash"
    STATUS = "status"
    WHISPER_HASH_V2 = "whisper_hash"


class WhispererDefaults:
    """Defaults meant for LLMWhisperer."""

    MEDIAN_FILTER_SIZE = 0
    GAUSSIAN_BLUR_RADIUS = 0.0
    FORCE_TEXT_PROCESSING = False
    LINE_SPLITTER_TOLERANCE = 0.75
    LINE_SPLITTER_STRATEGY = "left-priority"
    HORIZONTAL_STRETCH_FACTOR = 1.0
    POLL_INTERVAL = int(os.getenv(WhispererEnv.POLL_INTERVAL, 30))
    MAX_POLLS = int(os.getenv(WhispererEnv.MAX_POLLS, 30))
    POLL_INTERVAL_V2 = int(os.getenv(WhispererEnv.POLL_INTERVAL_V2, 30))
    MAX_POLLS_V2 = int(os.getenv(WhispererEnv.MAX_POLLS_V2, 30))
    PAGES_TO_EXTRACT = ""
    ADD_LINE_NOS = True
    OUTPUT_JSON = True
    PAGE_SEPARATOR = "<<< >>>"
    MARK_VERTICAL_LINES = False
    MARK_HORIZONTAL_LINES = False
    STATUS_RETRIES = int(os.getenv(WhispererEnv.STATUS_RETRIES, 5))
    URL_IN_POST = False
    TAG = "default"
    TEXT_ONLY = False
    WAIT_TIMEOUT = 300
    WAIT_FOR_COMPLETION = True
