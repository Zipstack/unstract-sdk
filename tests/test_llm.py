import json
import logging
import os
import unittest
from typing import Any

from dotenv import load_dotenv
from parameterized import parameterized
from unstract.adapters.llm.helper import LLMHelper

from unstract.sdk.llm import ToolLLM
from unstract.sdk.tool.base import BaseTool

load_dotenv()

logger = logging.getLogger(__name__)


def get_test_values(env_key: str) -> list[str]:
    test_values = json.loads(os.environ.get(env_key))
    return test_values


class ToolLLMTest(unittest.TestCase):
    class MockTool(BaseTool):
        def run(
            self,
            params: dict[str, Any] = {},
            settings: dict[str, Any] = {},
            workflow_id: str = "",
        ) -> None:
            # self.stream_log("Mock tool running")
            pass

    @classmethod
    def setUpClass(cls):
        cls.tool = cls.MockTool()

    @parameterized.expand(
        get_test_values("LLM_TEST_VALUES")
        # AzureOpenAI (Works)
        # OpenAI (Works)
        # AnyScale (llm FAILS)
        # Anthropic (llm.complete FAILS)
        # 1. unsupported params: max_token, stop.
        # TypeError: create() got an unexpected keyword argument
        # 'max_tokens'
        # 2. anthropic.APIConnectionError: Connection error.
        # PaLM (Works)
        # Errors
        # 1. unexpected keyword argument 'max_tokens', 'stop'
        # Replicate (llm.complete FAILS)
        # Errors
        # 1. replicate.exceptions.ReplicateError:
        # You did not pass an authentication token
        # Mistral (llm.complete FAILS)
        # Errors
        # 1.TypeError: chat() got an unexpected keyword argument 'stop'
    )
    def test_get_llm(self, adapter_instance_id):
        tool_llm = ToolLLM(tool=self.tool)
        llm = tool_llm.get_llm(adapter_instance_id)
        self.assertIsNotNone(llm)

        result = LLMHelper.test_llm_instance(llm)
        logger.error(result)
        self.assertEqual(result, True)


if __name__ == "__main__":
    unittest.main()
