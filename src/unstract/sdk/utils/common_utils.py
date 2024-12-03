import functools
import logging
import time
import uuid

from unstract.sdk.constants import LogLevel

logger = logging.getLogger(__name__)


class CommonUtils:
    @staticmethod
    def generate_uuid() -> str:
        """Class method to get uuid."""
        return str(uuid.uuid4())


# Mapping from python log level to Unstract counterpart
PY_TO_UNSTRACT_LOG_LEVEL = {
    logging.DEBUG: LogLevel.DEBUG,
    logging.INFO: LogLevel.INFO,
    logging.WARNING: LogLevel.WARN,
    logging.ERROR: LogLevel.ERROR,
}

# Mapping from Unstract log level to python counterpart
UNSTRACT_TO_PY_LOG_LEVEL = {
    LogLevel.DEBUG: logging.DEBUG,
    LogLevel.INFO: logging.INFO,
    LogLevel.WARN: logging.WARNING,
    LogLevel.ERROR: logging.ERROR,
}


def log_elapsed(operation):
    """Adds an elapsed time log.

    Args:
        operation (str): Operation being measured
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            finally:
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Time taken for '{operation}': {elapsed_time:.3f}s")
            return result

        return wrapper

    return decorator
