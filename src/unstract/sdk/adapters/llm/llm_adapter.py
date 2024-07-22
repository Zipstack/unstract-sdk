import logging
from abc import ABC, abstractmethod
from typing import Any

from llama_index.core.llms import LLM, MockLLM

from unstract.sdk.adapters.base import Adapter
from unstract.sdk.adapters.enums import AdapterTypes

logger = logging.getLogger(__name__)


class LLMAdapter(Adapter, ABC):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name

    @staticmethod
    def get_id() -> str:
        return ""

    @staticmethod
    def get_name() -> str:
        return ""

    @staticmethod
    def get_description() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_provider() -> str:
        pass

    @staticmethod
    def get_icon() -> str:
        return ""

    @staticmethod
    def get_json_schema() -> str:
        return ""

    @staticmethod
    def get_adapter_type() -> AdapterTypes:
        return AdapterTypes.LLM

    def get_llm_instance(self) -> LLM:
        """Instantiate the llama index LLM class.

        Returns:
            LLM: llama index implementation of the LLM
            Raises exceptions for any error
        """
        return MockLLM()

    def test_connection(self, llm_metadata: dict[str, Any]) -> bool:
        return False

    def get_context_window_size(self) -> int:
        """Get the context window size supported by the LLM.

        Note: None of the derived classes implement this method

        Returns:
            int: Context window size supported by the LLM
        """
        context_window_size: int = 0
        llm = self.get_llm_instance()
        if llm:
            context_window_size = llm.metadata.context_window
        return context_window_size
