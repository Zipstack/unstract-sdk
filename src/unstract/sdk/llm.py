import logging
import re
import time
from typing import Any, Optional

from llama_index.llms import LLM
from llama_index.llms.base import CompletionResponse
from unstract.adapters.constants import Common
from unstract.adapters.llm import adapters
from unstract.adapters.llm.llm_adapter import LLMAdapter

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolSettingsKey
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.service_context import ServiceContext

logger = logging.getLogger(__name__)


class ToolLLM:
    """Class to handle LLMs for Unstract Tools."""

    def __init__(
        self,
        tool: BaseTool,
        tool_settings: dict[str, str] = {},
    ):
        """

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
        self.llm_adapter_instance_id = tool_settings.get(
            ToolSettingsKey.LLM_ADAPTER_ID
        )

    @staticmethod
    def run_completion(
        llm: LLM,
        platform_api_key: str,
        prompt: str,
        retries: int = 3,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        ServiceContext.get_service_context(
            platform_api_key=platform_api_key, llm=llm
        )
        code_block_pattern = re.compile(r"```.*?\n(.*?)\n```", re.DOTALL)
        for i in range(retries):
            try:
                response: CompletionResponse = llm.complete(prompt, **kwargs)
                match = code_block_pattern.search(response.text)
                if match:
                    # Remove code block from response text
                    response.text = match.group(1)
                result = {
                    "response": response,
                }

                return result
            except Exception as e:
                if i == retries - 1:
                    raise e
                time.sleep(5)
        return None

    def get_llm(
        self, adapter_instance_id: Optional[str] = None
    ) -> Optional[LLM]:
        """Returns the LLM object for the tool.

        Returns:
            Optional[LLM]: The LLM object for the tool.
            (llama_index.llms.base.LLM)
        """
        adapter_instance_id = (
            adapter_instance_id
            if adapter_instance_id
            else self.llm_adapter_instance_id
        )
        # Support for get_llm using adapter_instance_id
        if adapter_instance_id is not None:
            try:
                llm_config_data = ToolAdapter.get_adapter_config(
                    self.tool, adapter_instance_id
                )
                llm_adapter_id = llm_config_data.get(Common.ADAPTER_ID)
                if llm_adapter_id in self.llm_adapters:
                    llm_adapter = self.llm_adapters[llm_adapter_id][
                        Common.METADATA
                    ][Common.ADAPTER]
                    llm_metadata = llm_config_data.get(Common.ADAPTER_METADATA)
                    llm_adapter_class: LLMAdapter = llm_adapter(llm_metadata)
                    llm_instance: Optional[
                        LLM
                    ] = llm_adapter_class.get_llm_instance()
                    return llm_instance
                else:
                    return None
            except Exception as e:
                self.tool.stream_log(
                    log=f"Unable to get llm instance: {e}", level=LogLevel.ERROR
                )
                return None
        else:
            logger.error("The adapter_instance_id parameter is None")
            return None

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
