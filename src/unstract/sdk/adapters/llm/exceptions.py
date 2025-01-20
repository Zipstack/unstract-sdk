from anthropic import APIError as AnthropicAPIError
from google.api_core.exceptions import GoogleAPICallError
from mistralai.models import SDKError as MistralError
from openai import APIError as OpenAIAPIError
from vertexai.generative_models import ResponseValidationError

from unstract.sdk.adapters.exceptions import LLMError
from unstract.sdk.adapters.llm.anthropic.src import AnthropicLLM
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.adapters.llm.mistral.src import MistralLLM
from unstract.sdk.adapters.llm.open_ai.src import OpenAILLM
from unstract.sdk.adapters.llm.palm.src import PaLMLLM
from unstract.sdk.adapters.llm.vertex_ai.src import VertexAILLM


def parse_llm_err(e: Exception, llm_adapter: LLMAdapter) -> LLMError:
    """Parses the exception from LLM provider.

    Helps parse the LLM error and wraps it with our
    custom exception object to contain a user friendly message.

    Args:
        e (Exception): Error from LLM provider

    Returns:
        LLMError: Unstract's LLMError object
    """
    # Avoid wrapping LLMError objects again
    if isinstance(e, LLMError):
        return e

    if isinstance(e, ResponseValidationError):
        err = VertexAILLM.parse_llm_err(e)
    elif isinstance(e, OpenAIAPIError):
        err = OpenAILLM.parse_llm_err(e)
    elif isinstance(e, AnthropicAPIError):
        err = AnthropicLLM.parse_llm_err(e)
    elif isinstance(e, MistralError):
        err = MistralLLM.parse_llm_err(e)
    elif isinstance(e, GoogleAPICallError):
        err = PaLMLLM.parse_llm_err(e)
    else:
        err = LLMError(str(e), actual_err=e)

    msg = f"Error from LLM provider '{llm_adapter.get_name()}'."

    # Add a code block only for errors from clients
    if err.actual_err:
        msg += f"\n```\n{str(err)}\n```"
    else:
        msg += str(err)
    err.message = msg
    return err
