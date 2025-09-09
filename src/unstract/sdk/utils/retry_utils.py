"""Retry utilities for handling transient failures in platform service
calls."""

import errno
import logging
import os
import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from requests.exceptions import ConnectionError, HTTPError

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Multiplier for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if initial_delay <= 0:
            raise ValueError("initial_delay must be > 0")
        if max_delay <= 0:
            raise ValueError("max_delay must be > 0")
        if backoff_factor <= 0:
            raise ValueError("backoff_factor must be > 0")
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    @classmethod
    def from_env(cls, prefix: str = "PLATFORM_SERVICE") -> "RetryConfig":
        """Create configuration from environment variables.

        Args:
            prefix: Prefix for environment variable names

        Returns:
            RetryConfig instance with values from environment
        """
        return cls(
            max_retries=int(os.getenv(f"{prefix}_MAX_RETRIES", "3")),
            initial_delay=float(os.getenv(f"{prefix}_INITIAL_DELAY", "1.0")),
            max_delay=float(os.getenv(f"{prefix}_MAX_DELAY", "60.0")),
            backoff_factor=float(os.getenv(f"{prefix}_BACKOFF_FACTOR", "2.0")),
            jitter=os.getenv(f"{prefix}_RETRY_JITTER", "true").lower() == "true",
        )


from requests.exceptions import ConnectionError, HTTPError, Timeout

def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable.

    Args:
        error: The exception to check

    Returns:
        True if the error should trigger a retry
    """
    # Requests connection and timeout errors
    if isinstance(error, (ConnectionError, Timeout)):
        return True

    # HTTP errors with specific status codes
    if isinstance(error, HTTPError):
        if hasattr(error, "response") and error.response is not None:
            status_code = error.response.status_code
            # Retry on server errors and bad gateway
            if status_code in [502, 503, 504]:
                return True

    # OS-level connection failures
    if isinstance(error, OSError) and error.errno in {
        errno.ECONNREFUSED,
        getattr(errno, "ECONNRESET", 104),
        getattr(errno, "ETIMEDOUT", 110),
        getattr(errno, "EHOSTUNREACH", 113),
        getattr(errno, "ENETUNREACH", 101),
    }:
        return True

    return False

def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for the next retry attempt.

    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds before the next retry
    """
    # Exponential backoff base calculation
    base = config.initial_delay * (config.backoff_factor ** attempt)
    delay = base

    # Add jitter if enabled (0–25% positive jitter)
    if config.jitter:
        delay = base + (base * random.uniform(0.0, 0.25))

    # Enforce the upper bound after jitter
    return min(delay, config.max_delay)


def retry_with_exponential_backoff(
    config: RetryConfig | None = None,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
    logger_instance: logging.Logger | None = None,
) -> Callable:
    """Decorator to retry functions with exponential backoff.

    Args:
        config: Retry configuration. If None, loads from environment
        retryable_exceptions: Additional exceptions to retry on
        logger_instance: Logger to use for retry messages

    Returns:
        Decorated function with retry behavior
    """
    if config is None:
        config = RetryConfig.from_env()

    if logger_instance is None:
        logger_instance = logger

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    # Try to execute the function
                    result = func(*args, **kwargs)

                    # If successful and we had retried, log success
                    if attempt > 0:
                        logger_instance.info(
                            f"Successfully completed '{func.__name__}' after "
                            f"{attempt} retry attempt(s)"
                        )

                    return result

                except Exception as e:
                    last_exception = e

                    # Check if the error is retryable
                    is_retryable = is_retryable_error(e)

                    # Check additional retryable exceptions if provided
                    if retryable_exceptions:
                        is_retryable = is_retryable or isinstance(e, retryable_exceptions)

                    # If not retryable or last attempt, raise the error
                    if not is_retryable or attempt == config.max_retries:
                        if attempt > 0:
                            logger_instance.error(
                                f"Failed '{func.__name__}' after {attempt + 1} attempt(s). "
                                f"Error: {str(e)}"
                            )
                        raise

                    # Calculate delay for next retry
                    delay = calculate_delay(attempt, config)

                    # Log retry attempt
                    max_attempts = config.max_retries + 1
                    logger_instance.warning(
                        f"Retryable error in '{func.__name__}' "
                        f"(attempt {attempt + 1}/{max_attempts}). "
                        f"Error: {str(e)}. Retrying in {delay:.2f} seconds..."
                    )

                    # Wait before retrying
                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_on_connection_error(
    func: Callable | None = None,
    *,
    retry_config: RetryConfig | None = None,
) -> Callable | Any:
    """Simplified decorator specifically for connection errors.

    Can be used with or without arguments:
        @retry_on_connection_error
        def my_function(): ...

        @retry_on_connection_error(retry_config=RetryConfig())
        def my_function(): ...

    Args:
        func: Function to decorate (when used without arguments)
        retry_config: Retry configuration to use

    Returns:
        Decorated function or decorator
    """
    if retry_config is None:
        retry_config = RetryConfig.from_env()

    # Create the decorator
    decorator = retry_with_exponential_backoff(
        config=retry_config,
        retryable_exceptions=(ConnectionError, OSError),
    )

    # Handle both @retry_on_connection_error and @retry_on_connection_error()
    if func is None:
        return decorator
    else:
        return decorator(func)
