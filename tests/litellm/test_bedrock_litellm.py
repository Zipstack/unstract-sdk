"""Tests for BedrockLiteLLM adapter."""
import json
import os
import unittest
from unittest.mock import patch

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm_litellm.bedrock.src.bedrock import (
    BedrockAdapter,
    BedrockLiteLLM,
    Constants,
)


class TestBedrockLiteLLM(unittest.TestCase):
    """Test cases for BedrockLiteLLM."""

    def setUp(self):
        """Set up test fixtures."""
        with open(
            os.path.join(os.path.dirname(__file__), "litellm_config.json")
        ) as file:
            self.config = json.load(file)
        self.adapter = BedrockAdapter(self.config)

    def test_adapter_metadata(self):
        """Test adapter metadata methods."""
        self.assertEqual(
            self.adapter.get_id(),
            "bedrock_litellm|8d18571f-5e96-4505-bd28-ad0379c64064",
        )
        self.assertEqual(self.adapter.get_name(), "Bedrock (LiteLLM)")
        self.assertEqual(self.adapter.get_description(), "Bedrock LLM using LiteLLM")
        self.assertEqual(self.adapter.get_provider(), "bedrock_litellm")
        self.assertEqual(self.adapter.get_icon(), "/icons/adapter-icons/Bedrock.png")

    def test_get_llm_instance(self):
        """Test LLM instance creation."""
        llm = self.adapter.get_llm_instance()
        self.assertIsInstance(llm, BedrockLiteLLM)
        self.assertIn(self.config[Constants.MODEL], llm.config[Constants.MODEL])
        self.assertEqual(
            llm.config[Constants.ACCESS_KEY_ID], self.config[Constants.ACCESS_KEY_ID]
        )
        self.assertEqual(
            llm.config[Constants.SECRET_ACCESS_KEY],
            self.config[Constants.SECRET_ACCESS_KEY],
        )
        self.assertEqual(
            llm.config[Constants.REGION_NAME], self.config[Constants.REGION_NAME]
        )
        self.assertEqual(llm.config[Constants.TIMEOUT], self.config[Constants.TIMEOUT])
        self.assertEqual(
            llm.config[Constants.MAX_RETRIES], self.config[Constants.MAX_RETRIES]
        )
        self.assertEqual(
            llm.config[Constants.MAX_TOKENS], self.config[Constants.MAX_TOKENS]
        )

    @patch("litellm.completion")
    def test_complete(self, mock_completion):
        """Test completion method."""
        # Setup mock response
        mock_response = {
            "id": "test-id",
            "choices": [{"message": {"content": "Chennai"}}],
        }
        mock_completion.return_value = mock_response

        # Test completion
        llm = self.adapter.get_llm_instance()
        response = llm.complete("The capital of Tamil Nadu is")

        # Verify response
        self.assertEqual(response["text"], "Chennai")
        self.assertIn(self.config[Constants.MODEL], response["model"])
        self.assertEqual(response["raw"], mock_response)

        # Verify LiteLLM was called correctly
        mock_completion.assert_called_once_with(
            model=f"bedrock/{self.config[Constants.MODEL]}",
            messages=[{"role": "user", "content": "The capital of Tamil Nadu is"}],
            aws_access_key_id=self.config[Constants.ACCESS_KEY_ID],
            aws_secret_access_key=self.config[Constants.SECRET_ACCESS_KEY],
            region_name=self.config[Constants.REGION_NAME],
            temperature=0,
            max_tokens=self.config[Constants.MAX_TOKENS],
            timeout=self.config[Constants.TIMEOUT],
            max_retries=self.config[Constants.MAX_RETRIES],
        )

    @patch("litellm.completion")
    def test_stream_complete(self, mock_completion):
        """Test streaming completion."""
        # Setup mock streaming response
        mock_responses = [
            {"id": "test-id", "choices": [{"delta": {"content": chunk}}]}
            for chunk in ["Chen", "nai"]
        ]
        mock_completion.return_value = mock_responses

        # Test streaming
        llm = self.adapter.get_llm_instance()
        chunks = list(llm.stream_complete("The capital of Tamil Nadu is"))

        # Verify chunks
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["text"], "Chen")
        self.assertEqual(chunks[1]["text"], "nai")

        # Verify LiteLLM was called correctly
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args.kwargs
        self.assertTrue(call_kwargs["stream"])

    @patch("litellm.completion")
    def test_chat(self, mock_completion):
        """Test chat completion."""
        # Setup mock response
        mock_response = {
            "id": "test-id",
            "choices": [{"message": {"content": "Hello! How can I help you?"}}],
        }
        mock_completion.return_value = mock_response

        # Test chat
        llm = self.adapter.get_llm_instance()
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hi!"},
        ]
        response = llm.chat(messages)

        # Verify response
        self.assertEqual(response["text"], "Hello! How can I help you?")
        self.assertIn(self.config[Constants.MODEL], response["model"])

        # Verify LiteLLM was called correctly
        mock_completion.assert_called_once_with(
            model=f"bedrock/{self.config[Constants.MODEL]}",
            messages=messages,
            aws_access_key_id=self.config[Constants.ACCESS_KEY_ID],
            aws_secret_access_key=self.config[Constants.SECRET_ACCESS_KEY],
            region_name=self.config[Constants.REGION_NAME],
            temperature=0,
            max_tokens=self.config[Constants.MAX_TOKENS],
            timeout=self.config[Constants.TIMEOUT],
            max_retries=self.config[Constants.MAX_RETRIES],
        )

    @patch("litellm.completion")
    def test_error_handling(self, mock_completion):
        """Test error handling."""
        mock_completion.side_effect = Exception("API Error")

        llm = self.adapter.get_llm_instance()

        # Test completion error
        with self.assertRaises(AdapterError):
            llm.complete("test")

        # Test streaming error
        with self.assertRaises(AdapterError):
            list(llm.stream_complete("test"))

        # Test chat error
        with self.assertRaises(AdapterError):
            llm.chat([{"role": "user", "content": "test"}])

    @patch("litellm.completion")
    def test_connection_success(self, mock_completion):
        """Test successful connection test."""
        # Setup mock response for the test prompt
        mock_response = {
            "id": "test-id",
            "choices": [
                {"message": {"content": "Chennai is the capital of Tamil Nadu"}}
            ],
        }
        mock_completion.return_value = mock_response

        # Test connection should succeed
        self.assertTrue(self.adapter.test_connection())

        # Verify test prompt was sent
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args.kwargs
        self.assertEqual(
            call_kwargs["messages"][0]["content"], "The capital of Tamilnadu is "
        )

    @patch("litellm.completion")
    def test_connection_wrong_answer(self, mock_completion):
        """Test connection test with wrong answer."""
        # Setup mock response with incorrect answer
        mock_response = {
            "id": "test-id",
            "choices": [{"message": {"content": "Mumbai is the capital"}}],
        }
        mock_completion.return_value = mock_response

        # Test connection should fail with LLMError
        with self.assertRaises(AdapterError) as ctx:
            self.adapter.test_connection()

        self.assertIn("LLM based test failed", str(ctx.exception))

    @patch("litellm.completion")
    def test_connection_api_error(self, mock_completion):
        """Test connection test with API error."""
        # Setup mock API error
        mock_completion.side_effect = Exception("API Error")

        # Test connection should fail with AdapterError
        with self.assertRaises(AdapterError):
            self.adapter.test_connection()

    def test_invalid_config(self):
        """Test adapter with invalid config."""
        invalid_config = {}
        adapter = BedrockAdapter(invalid_config)
        with self.assertRaises(AdapterError):
            adapter.get_llm_instance()

    def test_connection_integration(self):
        """Integration test for connection test with actual Bedrock call.

        This test makes an actual API call to Bedrock. It requires valid AWS credentials
        to be set in the config.

        Note: This test will be skipped if SKIP_INTEGRATION_TESTS environment variable
        is set to 'true'.
        """
        if os.environ.get("SKIP_INTEGRATION_TESTS", "").lower() == "true":
            self.skipTest("Skipping integration test")

        try:
            # Test actual connection to Bedrock
            result = self.adapter.test_connection()
            self.assertTrue(result)
        except AdapterError as e:
            self.fail(f"Connection test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main()
