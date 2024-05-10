import logging
import re
from typing import Any, Optional

from llama_index.core.llms import LLM, CompletionResponse
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError
from unstract.adapters.constants import Common
from unstract.adapters.llm import adapters
from unstract.adapters.llm.llm_adapter import LLMAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.exceptions import RateLimitError, SdkError, ToolLLMError
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.callback_manager import CallbackManager as UNCallbackManager

logger = logging.getLogger(__name__)


class ToolLLM:
    """Class to handle LLMs for Unstract Tools."""

    json_regex = re.compile(r"\[(?:.|\n)*\]|\{(?:.|\n)*\}")

    def __init__(self, tool: BaseTool):
        """ToolLLM constructor.

        Notes:
            - "Azure OpenAI" : Environment variables required
            OPENAI_API_KEY,OPENAI_API_BASE, OPENAI_API_VERSION,
            OPENAI_API_ENGINE, OPENAI_API_MODEL

        Args:
            tool (AbstractTool): Instance of AbstractTool
        """
        self.tool = tool
        self.max_tokens = 1024 * 4
        self.llm_adapters = adapters
        self.llm_config_data: Optional[dict[str, Any]] = None

    @classmethod
    def run_completion(
        cls,
        llm: LLM,
        platform_api_key: str,
        prompt: str,
        retries: int = 3,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        # Setup callback manager to collect Usage stats
        UNCallbackManager.set_callback_manager(
            platform_api_key=platform_api_key, llm=llm, **kwargs
        )
        # Removing specific keys from kwargs
        new_kwargs = kwargs.copy()
        for key in [
            "workflow_id",
            "execution_id",
            "adapter_instance_id",
            "run_id",
        ]:
            new_kwargs.pop(key, None)

        try:
            response: CompletionResponse = llm.complete(prompt, **new_kwargs)
            match = cls.json_regex.search(response.text)
            if match:
                response.text = match.group(0)
            return {"response": response}
        # TODO: Handle for all LLM providers
        except OpenAIAPIError as e:
            msg = "OpenAI error: "
            msg += e.message
            if hasattr(e, "body") and "message" in e.body:
                msg += e.body["message"]
            if isinstance(e, OpenAIRateLimitError):
                raise RateLimitError(msg)
            raise ToolLLMError(msg) from e

    def get_llm(self, adapter_instance_id: str) -> LLM:
        """Returns the LLM object for the tool.

        Returns:
            LLM: The LLM object for the tool.
            (llama_index.llms.base.LLM)
        """
        try:
            llm_config_data = ToolAdapter.get_adapter_config(
                self.tool, adapter_instance_id
            )
            llm_adapter_id = llm_config_data.get(Common.ADAPTER_ID)
            if llm_adapter_id not in self.llm_adapters:
                raise SdkError(f"LLM adapter not supported : " f"{llm_adapter_id}")

            llm_adapter = self.llm_adapters[llm_adapter_id][Common.METADATA][
                Common.ADAPTER
            ]
            llm_metadata = llm_config_data.get(Common.ADAPTER_METADATA)
            llm_adapter_class: LLMAdapter = llm_adapter(llm_metadata)
            llm_instance: LLM = llm_adapter_class.get_llm_instance()
            return llm_instance
        except Exception as e:
            self.tool.stream_log(
                log=f"Unable to get llm instance: {e}", level=LogLevel.ERROR
            )
            raise ToolLLMError(f"Error getting llm instance: {e}") from e

    def get_max_tokens(self, reserved_for_output: int = 0) -> int:
        """Returns the maximum number of tokens that can be used for the LLM.

        Args:
            reserved_for_output (int): The number of tokens reserved for the
                                        output.
                The default is 0.

            Returns:
                int: The maximum number of tokens that can be used for the LLM.
        """
        return self.max_tokens - reserved_for_output
