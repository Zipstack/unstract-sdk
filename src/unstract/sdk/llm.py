import logging
import os
import re
from collections.abc import Callable
from typing import Any

from deprecated import deprecated
from llama_index.core.base.llms.types import CompletionResponseGen
from llama_index.core.llms import LLM as LlamaIndexLLM
from llama_index.core.llms import CompletionResponse
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError
from unstract.sdk.adapter import ToolAdapter
from unstract.sdk.adapters.constants import Common
from unstract.sdk.adapters.llm import adapters
from unstract.sdk.adapters.llm.exceptions import parse_llm_err
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter
from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.exceptions import LLMError, RateLimitError, SdkError
from unstract.sdk.helper import SdkHelper
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.callback_manager import CallbackManager
from unstract.sdk.utils.common_utils import capture_metrics

logger = logging.getLogger(__name__)


class LLM:
    """Interface to handle all LLM interactions."""

    json_regex = re.compile(r"\[(?:.|\n)*\]|\{(?:.|\n)*\}")
    llm_adapters = adapters
    MAX_TOKENS = 1024 * 4
    RESPONSE = "response"
    JSON_SELECTION_MARKER = os.environ.get("JSON_SELECTION_MARKER", "§§§")

    def __init__(
        self,
        tool: BaseTool,
        adapter_instance_id: str | None = None,
        usage_kwargs: dict[Any, Any] = {},
        capture_metrics: bool = False,
    ):
        """Creates an instance of this LLM class.

        Args:
            tool (BaseTool): Instance of BaseTool to expose function to stream logs
            adapter_instance_id (Optional[str], optional): UUID of the adapter in
                Unstract. Defaults to None.
            usage_kwargs (dict[Any, Any], optional): Dict to capture token usage with
                callbacks. Defaults to {}.
        """
        self._tool = tool
        self._adapter_instance_id = adapter_instance_id
        self._llm_instance: LlamaIndexLLM = None
        self._usage_kwargs = usage_kwargs
        self._capture_metrics = capture_metrics
        self._run_id = usage_kwargs.get("run_id")
        self._usage_reason = usage_kwargs.get("llm_usage_reason")
        self._metrics = {}
        self._initialise()

    def _initialise(self):
        if self._adapter_instance_id:
            self._llm_instance = self._get_llm(self._adapter_instance_id)
            self._usage_kwargs["adapter_instance_id"] = self._adapter_instance_id

            if not SdkHelper.is_public_adapter(adapter_id=self._adapter_instance_id):
                platform_api_key = self._tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)
                CallbackManager.set_callback(
                    platform_api_key=platform_api_key,
                    model=self._llm_instance,
                    kwargs=self._usage_kwargs,
                )

    @capture_metrics
    def complete(
        self,
        prompt: str,
        extract_json: bool = True,
        process_text: Callable[[str], str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generates a completion response for the given prompt and captures
        metrics if run_id is provided.

        Args:
            prompt (str): The input text prompt for generating the completion.
            extract_json (bool, optional): If set to True, the response text is
                processed using a regex to extract JSON content from it. If no JSON is
                found, the text is returned as it is. Defaults to True.
            process_text (Optional[Callable[[str], str]], optional): A callable that
                processes the generated text and extracts specific information.
                Defaults to None.
            **kwargs (Any): Additional arguments passed to the completion function.

        Returns:
            dict[str, Any]: A dictionary containing the result of the completion,
                any processed output, and the captured metrics (if applicable).
        """
        try:
            response: CompletionResponse = self._llm_instance.complete(prompt, **kwargs)
            process_text_output = {}
            if extract_json:
                response_text = response.text
                start = response_text.find(self.JSON_SELECTION_MARKER)
                if start != -1:
                    response_text = response_text[
                        start + len(self.JSON_SELECTION_MARKER) :
                    ].lstrip()
                end = response_text.rfind(self.JSON_SELECTION_MARKER)
                if end != -1:
                    response_text = response_text[:end].rstrip()
                match = LLM.json_regex.search(response_text)
                if match:
                    response.text = match.group(0)
            if process_text:
                try:
                    process_text_output = process_text(response, extract_json)
                    if not isinstance(process_text_output, dict):
                        process_text_output = {}
                except Exception as e:
                    logger.error(f"Error occurred inside function 'process_text': {e}")
                    process_text_output = {}
            response_data = {LLM.RESPONSE: response, **process_text_output}
            return response_data
        except Exception as e:
            raise parse_llm_err(e, self._llm_adapter_class) from e

    def get_metrics(self):
        return self._metrics

    def get_usage_reason(self):
        return self._usage_reason

    def stream_complete(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> CompletionResponseGen:
        try:
            response: CompletionResponseGen = self._llm_instance.stream_complete(
                prompt, **kwargs
            )
            return response
        except Exception as e:
            raise parse_llm_err(e, self._llm_adapter_class) from e

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
            self._llm_adapter_class: LLMAdapter = llm_adapter(llm_metadata)
            self._usage_kwargs["provider"] = self._llm_adapter_class.get_provider()
            llm_instance: LLM = self._llm_adapter_class.get_llm_instance()
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

    def get_model_name(self) -> str:
        """Gets the name of the LLM model.

        Args:
            NA

        Returns:
            LLM model name
        """
        return self._llm_instance.model

    @deprecated("Use LLM instead of ToolLLM")
    def get_llm(self, adapter_instance_id: str | None = None) -> LlamaIndexLLM:
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
    ) -> dict[str, Any] | None:
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
            if hasattr(e, "body") and isinstance(e.body, dict) and "message" in e.body:
                msg += e.body["message"]
            if isinstance(e, OpenAIRateLimitError):
                raise RateLimitError(msg)
            raise LLMError(msg) from e


# Legacy
ToolLLM = LLM
