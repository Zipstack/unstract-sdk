import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

from llama_index.core.llms import LLM, MockLLM

from unstract.sdk.adapters.base import Adapter
from unstract.sdk.adapters.enums import AdapterTypes
from unstract.sdk.adapters.exceptions import LLMError

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

    @staticmethod
    def parse_llm_err(e: Exception) -> LLMError:
        """Parse the error from an LLM provider.

        Helps parse errors from a provider and wraps with custom exception.

        Args:
            e (Exception): Exception from LLM provider

        Returns:
            LLMError: Error to be sent to the user
        """
        return LLMError(str(e))

    def get_llm_instance(self) -> LLM:
        """Instantiate the llama index LLM class.

        Returns:
            LLM: llama index implementation of the LLM
            Raises exceptions for any error
        """
        return MockLLM()

    @staticmethod
    def _test_llm_instance(llm: Optional[LLM]) -> bool:
        if llm is None:
            return False
        response = llm.complete(
            "The capital of Tamilnadu is ",
            temperature=0.003,
        )
        response_lower_case: str = response.text.lower()
        find_match = re.search("chennai", response_lower_case)
        if find_match:
            return True
        else:
            return False

    def test_connection(self) -> bool:
        try:
            llm = self.get_llm_instance()
            test_result: bool = self._test_llm_instance(llm=llm)
        except Exception as e:
            # Avoids circular import errors
            from unstract.sdk.adapters.llm.exceptions import parse_llm_err

            err = parse_llm_err(e)
            msg = f"Error while testing LLM '{self.get_name()}'. {str(err)}"
            err.message = msg
            raise err from e
        return test_result

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
