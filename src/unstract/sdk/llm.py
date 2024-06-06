import logging
import re
from typing import Any, Optional

from llama_index.core.llms import LLM as LlamaIndexLLM
from llama_index.core.llms import CompletionResponse
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError
from typing_extensions import deprecated
from unstract.adapters.constants import Common
from unstract.adapters.llm import adapters
from unstract.adapters.llm.llm_adapter import LLMAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.exceptions import LLMError, RateLimitError, SdkError
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.callback_manager import CallbackManager

logger = logging.getLogger(__name__)


class LLM:
    """Interface to handle all LLM interactions."""

    json_regex = re.compile(r"\[(?:.|\n)*\]|\{(?:.|\n)*\}")
    llm_adapters = adapters
    MAX_TOKENS = 1024 * 4
    RESPONSE = "response"

    def __init__(
        self,
        tool: BaseTool,
        adapter_instance_id: Optional[str] = None,
        usage_kwargs: dict[Any, Any] = {},
    ):
        """

        Notes:
            - "Azure OpenAI" : Environment variables required
            OPENAI_API_KEY,OPENAI_API_BASE, OPENAI_API_VERSION,
            OPENAI_API_ENGINE, OPENAI_API_MODEL

        Args:
            tool (AbstractTool): Instance of AbstractTool
        """
        self._tool = tool
        self._adapter_instance_id = adapter_instance_id
        self._llm_instance: LlamaIndexLLM = None
        self._usage_kwargs = usage_kwargs
        self._initialise()

    def _initialise(self):
        if self._adapter_instance_id:
            self._llm_instance = self._get_llm(self._adapter_instance_id)
            self._usage_kwargs["adapter_instance_id"] = self._adapter_instance_id
            platform_api_key = self._tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)
            CallbackManager.set_callback(
                platform_api_key=platform_api_key,
                model=self._llm_instance,
                kwargs=self._usage_kwargs,
            )

    def complete(
        self,
        prompt: str,
        retries: int = 3,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        try:
            response: CompletionResponse = self._llm_instance.complete(prompt, **kwargs)
            match = LLM.json_regex.search(response.text)
            if match:
                response.text = match.group(0)
            return {LLM.RESPONSE: response}
        # TODO: Handle for all LLM providers
        except OpenAIAPIError as e:
            msg = "OpenAI error: "
            if hasattr(e, "body") and "message" in e.body:
                msg += e.body["message"]
            else:
                msg += e.message
            if isinstance(e, OpenAIRateLimitError):
                raise RateLimitError(msg)
            raise LLMError(msg) from e

    def _get_llm(self, adapter_instance_id: str) -> LlamaIndexLLM:
        """Returns the LLM object for the tool.

        Returns:
            LLM: The LLM object for the tool.
            (llama_index.llms.base.LLM)
        """
        try:
            if not self._adapter_instance_id:
                raise LLMError("Adapter instance ID not set. " "Initialisation failed")
            llm_config_data = ToolAdapter.get_adapter_config(
                self._tool, self._adapter_instance_id
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
            self._tool.stream_log(
                log=f"Unable to get llm instance: {e}", level=LogLevel.ERROR
            )
            raise LLMError(f"Error getting llm instance: {e}") from e

    def get_max_tokens(self, reserved_for_output: int = 0) -> int:
        """Returns the maximum number of tokens that can be used for the LLM.

        Args:
            reserved_for_output (int): The number of tokens reserved for the
                                        output.
                The default is 0.

            Returns:
                int: The maximum number of tokens that can be used for the LLM.
        """
        return self.MAX_TOKENS - reserved_for_output

    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the maximum number of tokens that can be used for the LLM.

        Args:
            max_tokens (int): The number of tokens to be used at the maximum

            Returns:
                None
        """
        self._llm_instance.max_tokens = max_tokens

    def get_class_name(self) -> str:
        """Gets the class name of the Llama Index LLM.

        Args:
            NA

            Returns:
                Class name
        """
        return self._llm_instance.class_name()

    @deprecated("Use LLM instead of ToolLLM")
    def get_llm(self, adapter_instance_id: Optional[str] = None) -> LlamaIndexLLM:
        if not self._llm_instance:
            self._adapter_instance_id = adapter_instance_id
            self._initialise()
        return self._llm_instance

    @classmethod
    @deprecated("Instantiate LLM and call complete() instead")
    def run_completion(
        cls,
        llm: LlamaIndexLLM,
        platform_api_key: str,
        prompt: str,
        retries: int = 3,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        # Setup callback manager to collect Usage stats
        CallbackManager.set_callback_manager(
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
            raise LLMError(msg) from e


# Legacy
ToolLLM = LLM
