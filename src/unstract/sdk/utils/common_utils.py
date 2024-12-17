import functools
import logging
import time
import uuid

from unstract.sdk.constants import LogLevel
from unstract.sdk.metrics_mixin import MetricsMixin

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


def capture_metrics(func):
    """Decorator to capture metrics at the start and end of a function."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        metrics_mixin = None
        TIME_TAKEN_KEY = "time_taken(s)"
        # Check if run_id exists and if metrics should be captured
        if self._run_id and self._capture_metrics:
            metrics_mixin = MetricsMixin(run_id=self._run_id)

        try:
            result = func(self, *args, **kwargs)
        finally:
            # If metrics are being captured, collect and assign them at the end
            if metrics_mixin:
                new_metrics = metrics_mixin.collect_metrics()
                # If self._metrics already exists, sum time_taken
                if (
                    self._metrics
                    and TIME_TAKEN_KEY in self._metrics
                    and TIME_TAKEN_KEY in new_metrics
                ):
                    self._metrics[TIME_TAKEN_KEY] += new_metrics[TIME_TAKEN_KEY]
                else:
                    self._metrics = new_metrics

        return result

    return wrapper
