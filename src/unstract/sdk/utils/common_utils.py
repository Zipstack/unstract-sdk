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
        # Ensure the required attributes exist; if not,
        # execute the function and return its result
        if not all(
            hasattr(self, attr) for attr in ["_run_id", "_capture_metrics", "_metrics"]
        ):
            return func(self, *args, **kwargs)

        # Check if run_id exists and if metrics should be captured
        metrics_mixin = None
        time_taken_key = MetricsMixin.TIME_TAKEN_KEY
        if self._run_id and self._capture_metrics:
            metrics_mixin = MetricsMixin(run_id=self._run_id)

        try:
            result = func(self, *args, **kwargs)
        finally:
            # If metrics are being captured, collect and assign them at the end
            if metrics_mixin:
                new_metrics = metrics_mixin.collect_metrics()

                # If time_taken(s) exists in both self._metrics and new_metrics, sum it
                if (
                    self._metrics
                    and time_taken_key in self._metrics
                    and time_taken_key in new_metrics
                ):
                    previously_measured_time = self._metrics.get(time_taken_key)
                    newly_measured_time = new_metrics.get(time_taken_key)

                    # Only sum if both are valid
                    if previously_measured_time and newly_measured_time:
                        self._metrics[time_taken_key] = (
                            previously_measured_time + newly_measured_time
                        )
                    else:
                        self._metrics[time_taken_key] = None
                else:
                    # If the key isn't in self._metrics, set it to new_metrics
                    self._metrics = new_metrics

        return result

    return wrapper
