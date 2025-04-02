"""LiteLLM Bedrock adapter implementation."""
import os
from typing import Any

import litellm

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    SECRET_ACCESS_KEY = "aws_secret_access_key"
    ACCESS_KEY_ID = "aws_access_key_id"
    REGION_NAME = "region_name"
    CONTEXT_SIZE = "context_size"
    MAX_TOKENS = "max_tokens"
    DEFAULT_MAX_TOKENS = 512


class BedrockLiteLLM:
    """LiteLLM implementation for Bedrock."""

    @staticmethod
    def _validate_string_arg(value: str, name: str) -> None:
        """Validate a string argument.

        Args:
            value: Value to validate
            name: Name of the argument for error message

        Raises:
            AdapterError: If validation fails
        """
        if not value or not isinstance(value, str):
            raise AdapterError(f"{name} must be a non-empty string")

    @staticmethod
    def _validate_numeric_arg(
        value: float,
        name: str,
        min_val: float = None,
        max_val: float = None,
        integer: bool = False,
    ) -> None:
        """Validate a numeric argument.

        Args:
            value: Value to validate
            name: Name of the argument for error message
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            integer: Whether the value must be an integer

        Raises:
            AdapterError: If validation fails
        """
        if integer and not isinstance(value, int):
            raise AdapterError(f"{name} must be an integer")
        if not isinstance(value, (int, float)):
            raise AdapterError(f"{name} must be a number")
        if min_val is not None and value < min_val:
            raise AdapterError(f"{name} must be greater than or equal to {min_val}")
        if max_val is not None and value > max_val:
            raise AdapterError(f"{name} must be less than or equal to {max_val}")

    def __init__(
        self,
        model: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        timeout: float = LLMKeys.DEFAULT_TIMEOUT,
        max_retries: int = LLMKeys.DEFAULT_MAX_RETRIES,
        temperature: float = 0,
        max_tokens: int = Constants.DEFAULT_MAX_TOKENS,
    ):
        """Initialize Bedrock LiteLLM.

        Args:
            model: The model identifier
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens to generate

        Raises:
            AdapterError: If any argument validation fails
        """
        # Validate string arguments
        self._validate_string_arg(model, "Model name")
        self._validate_string_arg(aws_access_key_id, "AWS access key ID")
        self._validate_string_arg(aws_secret_access_key, "AWS secret access key")
        self._validate_string_arg(region_name, "AWS region name")

        # Validate numeric arguments
        self._validate_numeric_arg(timeout, "Timeout", min_val=0)
        self._validate_numeric_arg(max_retries, "Max retries", min_val=0, integer=True)
        self._validate_numeric_arg(temperature, "Temperature", min_val=0, max_val=1)
        self._validate_numeric_arg(max_tokens, "Max tokens", min_val=1, integer=True)

        self.config = {
            "model": f"bedrock/{model}",
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": region_name,
            "timeout": timeout,
            "max_retries": max_retries,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # # Configure LiteLLM AWS credentials
        # litellm.aws_access_key_id = aws_access_key_id
        # litellm.aws_secret_access_key = aws_secret_access_key
        # litellm.aws_region_name = region_name

    def _get_completion_kwargs(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Get common completion kwargs.

        Args:
            messages: List of message dictionaries

        Returns:
            Dictionary of completion arguments
        """
        completion_kwargs = self.config.copy()
        completion_kwargs["messages"] = messages
        return completion_kwargs

    def complete(self, prompt: str) -> dict[str, Any]:
        """Complete the prompt.

        Args:
            prompt: The input prompt

        Returns:
            Response dictionary containing generated text and metadata

        Raises:
            AdapterError: If completion fails
        """
        try:
            completion_kwargs = self._get_completion_kwargs(
                [{"role": "user", "content": prompt}]
            )
            response = litellm.completion(**completion_kwargs)
            return {
                "text": response["choices"][0]["message"]["content"],
                "model": self.config["model"],
                "raw": response,
            }
        except Exception as e:
            raise AdapterError(str(e))

    def stream_complete(self, prompt: str):
        """Stream complete the prompt.

        Args:
            prompt: The input prompt

        Yields:
            Response chunks containing generated text

        Raises:
            AdapterError: If streaming fails
        """
        try:
            completion_kwargs = self._get_completion_kwargs(
                [{"role": "user", "content": prompt}]
            )
            completion_kwargs["stream"] = True

            response_gen = litellm.completion(**completion_kwargs)
            for response in response_gen:
                yield {
                    "text": response["choices"][0]["delta"]["content"] or "",
                    "model": self.config["model"],
                    "raw": response,
                }
        except Exception as e:
            raise AdapterError(str(e))

    def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Chat with the model.

        Args:
            messages: List of message dictionaries with role and content

        Returns:
            Response dictionary containing generated text and metadata

        Raises:
            AdapterError: If chat fails
        """
        try:
            completion_kwargs = self._get_completion_kwargs(messages)
            response = litellm.completion(**completion_kwargs)
            return {
                "text": response["choices"][0]["message"]["content"],
                "model": self.config["model"],
                "raw": response,
            }
        except Exception as e:
            raise AdapterError(str(e))


class BedrockAdapter:
    """Bedrock adapter using LiteLLM."""

    def __init__(self, settings: dict[str, Any]):
        """Initialize adapter.

        Args:
            settings: Adapter settings dictionary
        """
        self.config = settings

    SCHEMA_PATH = f"{os.path.dirname(__file__)}/static/json_schema.json"

    @staticmethod
    def get_id() -> str:
        return "bedrock_litellm|8d18571f-5e96-4505-bd28-ad0379c64064"

    @staticmethod
    def get_name() -> str:
        return "Bedrock (LiteLLM)"

    @staticmethod
    def get_description() -> str:
        return "Bedrock LLM using LiteLLM"

    @staticmethod
    def get_provider() -> str:
        return "bedrock_litellm"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/Bedrock.png"

    def get_llm_instance(self) -> BedrockLiteLLM:
        """Get LiteLLM Bedrock instance.

        Returns:
            Configured BedrockLiteLLM instance

        Raises:
            AdapterError: If initialization fails
        """
        try:
            max_tokens = int(
                self.config.get(Constants.MAX_TOKENS, Constants.DEFAULT_MAX_TOKENS)
            )

            return BedrockLiteLLM(
                model=self.config.get(Constants.MODEL),
                aws_access_key_id=self.config.get(Constants.ACCESS_KEY_ID),
                aws_secret_access_key=self.config.get(Constants.SECRET_ACCESS_KEY),
                region_name=self.config.get(Constants.REGION_NAME),
                timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                max_retries=int(
                    self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
                ),
                temperature=0,
                max_tokens=max_tokens,
            )
        except Exception as e:
            raise AdapterError(str(e))

    def test_connection(self) -> bool:
        """Test the connection to Bedrock.

        Tests if the LLM instance can be created and if it returns a sane response
        to a test prompt.

        Returns:
            bool: True if connection test passes

        Raises:
            AdapterError: If connection test fails
        """
        try:
            # Get LLM instance
            llm = self.get_llm_instance()
            if not llm:
                raise AdapterError(
                    "Unable to connect to LLM, please recheck the configuration",
                    status_code=400,
                )

            # Test with a simple prompt
            response = llm.complete("The capital of Tamilnadu is ")
            response_text = response["text"].lower()

            # Check for expected answer
            if "chennai" in response_text:
                return True

            raise AdapterError(
                "LLM based test failed. The credentials were valid however a sane "
                "response was not obtained from the LLM provider, please recheck "
                "the configuration.",
                status_code=400,
            )

        except Exception as e:
            if isinstance(e, AdapterError):
                raise e
            raise AdapterError(str(e))
