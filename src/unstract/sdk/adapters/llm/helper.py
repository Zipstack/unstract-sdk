import logging
import re
from typing import Optional

from llama_index.core.llms import LLM

from unstract.sdk.adapters.exceptions import AdapterError

logger = logging.getLogger(__name__)


class LLMHelper:
    @staticmethod
    def test_llm_instance(llm: Optional[LLM]) -> bool:
        try:
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
        except Exception as e:
            logger.error(f"Error occured while testing adapter {e}")
            raise AdapterError(str(e))
