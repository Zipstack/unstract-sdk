from openai import APIError as OpenAIAPIError
from vertexai.generative_models import ResponseValidationError

from unstract.sdk.adapters.exceptions import LLMError
from unstract.sdk.adapters.llm.open_ai.src.open_ai import OpenAILLM
from unstract.sdk.adapters.llm.vertex_ai.src.vertex_ai import VertexAILLM


def parse_llm_err(e: Exception) -> LLMError:
    """Parses the exception from LLM provider.

    Helps parse the LLM error and wraps it with our
    custom exception object to contain a user friendly message.

    Args:
        e (Exception): Error from LLM provider

    Returns:
        LLMError: Unstract's LLMError object
    """
    if isinstance(e, ResponseValidationError):
        return VertexAILLM.parse_llm_err(e)
    elif isinstance(e, OpenAIAPIError):
        return OpenAILLM.parse_llm_err(e)
    return LLMError(str(e))
