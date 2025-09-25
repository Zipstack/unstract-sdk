"""Generic retry utilities using backoff library with configurable prefixes."""

import errno
import logging
import os
from collections.abc import Callable
from typing import Any

import backoff
from requests.exceptions import ConnectionError, HTTPError, Timeout

logger = logging.getLogger(__name__)


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable (preserving existing logic).

    Handles:
    - ConnectionError and Timeout from requests
    - HTTPError with status codes 502, 503, 504
    - OSError with specific errno codes (ECONNREFUSED, ECONNRESET, etc.)

    Args:
        error: The exception to check

    Returns:
        True if the error should trigger a retry
    """
    # Requests connection and timeout errors
    if isinstance(error, (ConnectionError | Timeout)):
        return True

    # HTTP errors with specific status codes
    if isinstance(error, HTTPError):
        if hasattr(error, "response") and error.response is not None:
            status_code = error.response.status_code
            # Retry on server errors and bad gateway
            if status_code in [502, 503, 504]:
                return True

    # OS-level connection failures (preserving existing errno checks)
    if isinstance(error, OSError) and error.errno in {
        errno.ECONNREFUSED,  # Connection refused
        getattr(errno, "ECONNRESET", 104),  # Connection reset by peer
        getattr(errno, "ETIMEDOUT", 110),  # Connection timed out
        getattr(errno, "EHOSTUNREACH", 113),  # No route to host
        getattr(errno, "ENETUNREACH", 101),  # Network is unreachable
    }:
        return True

    return False


def create_retry_decorator(
    prefix: str = "PLATFORM_SERVICE",
    exceptions: tuple[type[Exception], ...] | None = None,
    logger_instance: logging.Logger | None = None,
) -> Callable:
    """Create a configured backoff decorator for a specific service.

    Args:
        prefix: Environment variable prefix for configuration
        logger_instance: Optional logger for retry events
        exceptions: Tuple of exception types to retry on.
                   Defaults to (ConnectionError, HTTPError, Timeout, OSError)

    Environment variables (using prefix):
        {prefix}_MAX_RETRIES: Maximum retry attempts (default: 3)
        {prefix}_MAX_TIME: Maximum total time in seconds (default: 60)
        {prefix}_BASE_DELAY: Initial delay in seconds (default: 1.0)
        {prefix}_MULTIPLIER: Backoff multiplier (default: 2.0)
        {prefix}_JITTER: Enable jitter true/false (default: true)

    Returns:
        Configured backoff decorator
    """
    # Set default exceptions if not provided
    if exceptions is None:
        exceptions = (ConnectionError, HTTPError, Timeout, OSError)

    # Load configuration from environment
    max_tries = int(os.getenv(f"{prefix}_MAX_RETRIES", "3")) + 1  # +1 for initial attempt
    max_time = float(os.getenv(f"{prefix}_MAX_TIME", "60"))
    base = float(os.getenv(f"{prefix}_BASE_DELAY", "1.0"))
    factor = float(os.getenv(f"{prefix}_MULTIPLIER", "2.0"))
    use_jitter = os.getenv(f"{prefix}_JITTER", "true").strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }

    if logger_instance is None:
        logger_instance = logger

    def on_backoff_handler(details: dict[str, Any]) -> None:
        """Log retry attempts with useful context."""
        exception = details["exception"]
        tries = details["tries"]
        wait = details.get("wait", 0)

        logger_instance.warning(
            "Retry %d/%d for %s: %s (waiting %.1fs)",
            tries,
            max_tries - 1,
            prefix,
            exception,
            wait,
        )

    def on_giveup_handler(details: dict[str, Any]) -> None:
        """Log when giving up after all retries."""
        exception = details["exception"]
        tries = details["tries"]

        logger_instance.exception(
            "Giving up after %d retries for %s: %s", tries, prefix, exception
        )

    # Create the decorator with backoff
    return backoff.on_exception(
        backoff.expo,
        exceptions,  # Use the configurable exceptions
        max_tries=max_tries,
        max_time=max_time,
        base=base,
        factor=factor,
        jitter=backoff.full_jitter if use_jitter else None,
        giveup=lambda e: not (
            is_retryable_error(e)
            or (isinstance(exceptions, tuple) and isinstance(e, exceptions))
        ),
        on_backoff=on_backoff_handler,
        on_giveup=on_giveup_handler,
    )


# Retry configured through below envs.
# - PLATFORM_SERVICE_MAX_RETRIES (default: 3)
# - PLATFORM_SERVICE_MAX_TIME (default: 60s)
# - PLATFORM_SERVICE_BASE_DELAY (default: 1.0s)
# - PLATFORM_SERVICE_MULTIPLIER (default: 2.0)
# - PLATFORM_SERVICE_JITTER (default: true)
retry_platform_service_call = create_retry_decorator("PLATFORM_SERVICE")
