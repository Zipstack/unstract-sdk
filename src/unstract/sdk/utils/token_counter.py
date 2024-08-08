from typing import Any

from llama_index.core.callbacks.schema import EventPayload
from llama_index.core.utilities.token_counting import TokenCounter
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion


class Constants:
    KEY_USAGE = "usage"
    KEY_USAGE_METADATA = "usage_metadata"
    KEY_EVAL_COUNT = "eval_count"
    KEY_PROMPT_EVAL_COUNT = "prompt_eval_count"
    KEY_RAW_RESPONSE = "_raw_response"
    KEY_TEXT_TOKEN_COUNT = "inputTextTokenCount"
    KEY_TOKEN_COUNT = "tokenCount"
    KEY_RESULTS = "results"
    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    PROMPT_TOKENS = "prompt_tokens"
    COMPLETION_TOKENS = "completion_tokens"
    DEFAULT_TOKEN_COUNT = 0


class TokenCounter:
    prompt_llm_token_count: int
    completion_llm_token_count: int
    total_llm_token_count: int = 0
    total_embedding_token_count: int = 0

    def __init__(self, input_tokens, output_tokens):
        self.prompt_llm_token_count = input_tokens
        self.completion_llm_token_count = output_tokens
        self.total_llm_token_count = (
            self.prompt_llm_token_count + self.completion_llm_token_count
        )

    @staticmethod
    def get_llm_token_counts(payload: dict[str, Any]) -> TokenCounter:
        prompt_tokens = Constants.DEFAULT_TOKEN_COUNT
        completion_tokens = Constants.DEFAULT_TOKEN_COUNT
        if EventPayload.PROMPT in payload:
            completion_raw = payload.get(EventPayload.COMPLETION).raw
            if completion_raw:
                # For Open AI models, token count is part of ChatCompletion
                if isinstance(completion_raw, ChatCompletion):
                    if hasattr(completion_raw, Constants.KEY_USAGE):
                        token_counts: dict[
                            str, int
                        ] = TokenCounter._get_prompt_completion_tokens(completion_raw)
                        prompt_tokens = token_counts[Constants.PROMPT_TOKENS]
                        completion_tokens = token_counts[Constants.COMPLETION_TOKENS]
                # For other models
                elif isinstance(completion_raw, dict):
                    # For Gemini models
                    if completion_raw.get(Constants.KEY_RAW_RESPONSE):
                        if hasattr(
                            completion_raw.get(Constants.KEY_RAW_RESPONSE),
                            Constants.KEY_USAGE_METADATA,
                        ):
                            usage = completion_raw.get(
                                Constants.KEY_RAW_RESPONSE
                            ).usage_metadata
                            prompt_tokens = usage.prompt_token_count
                            completion_tokens = usage.candidates_token_count
                    elif completion_raw.get(Constants.KEY_USAGE):
                        token_counts: dict[
                            str, int
                        ] = TokenCounter._get_prompt_completion_tokens(completion_raw)
                        prompt_tokens = token_counts[Constants.PROMPT_TOKENS]
                        completion_tokens = token_counts[Constants.COMPLETION_TOKENS]
                    # For Bedrock models
                    elif Constants.KEY_TEXT_TOKEN_COUNT in completion_raw:
                        prompt_tokens = completion_raw[Constants.KEY_TEXT_TOKEN_COUNT]
                        if Constants.KEY_RESULTS in completion_raw:
                            result_list: list = completion_raw[Constants.KEY_RESULTS]
                            if len(result_list) > 0:
                                result: dict = result_list[0]
                                if Constants.KEY_TOKEN_COUNT in result:
                                    completion_tokens = result.get(
                                        Constants.KEY_TOKEN_COUNT
                                    )
                    else:
                        if completion_raw.get(Constants.KEY_PROMPT_EVAL_COUNT):
                            prompt_tokens = completion_raw.get(
                                Constants.KEY_PROMPT_EVAL_COUNT
                            )
                        if completion_raw.get(Constants.KEY_EVAL_COUNT):
                            completion_tokens = completion_raw.get(
                                Constants.KEY_EVAL_COUNT
                            )
        # For Anthropic models
        elif EventPayload.MESSAGES in payload:
            response_raw = payload.get(EventPayload.RESPONSE).raw
            if response_raw:
                token_counts: dict[
                    str, int
                ] = TokenCounter._get_prompt_completion_tokens(response_raw)
                prompt_tokens = token_counts[Constants.PROMPT_TOKENS]
                completion_tokens = token_counts[Constants.COMPLETION_TOKENS]

        token_counter = TokenCounter(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
        )
        return token_counter

    @staticmethod
    def _get_prompt_completion_tokens(response) -> dict[str, int]:
        usage = None
        prompt_tokens = Constants.DEFAULT_TOKEN_COUNT
        completion_tokens = Constants.DEFAULT_TOKEN_COUNT
        # For OpenAI models,response is an obj of CompletionUsage
        if (
            isinstance(response, ChatCompletion)
            and hasattr(response, Constants.KEY_USAGE)
            and isinstance(response.usage, CompletionUsage)
        ):
            usage = response.usage
        # For LLM models other than OpenAI, response is a dict
        elif isinstance(response, dict) and Constants.KEY_USAGE in response:
            usage = response.get(Constants.KEY_USAGE)

        if usage:
            if hasattr(usage, Constants.INPUT_TOKENS):
                prompt_tokens = usage.input_tokens
            elif hasattr(usage, Constants.PROMPT_TOKENS):
                prompt_tokens = usage.prompt_tokens

            if hasattr(usage, Constants.OUTPUT_TOKENS):
                completion_tokens = usage.output_tokens
            elif hasattr(usage, Constants.COMPLETION_TOKENS):
                completion_tokens = usage.completion_tokens

        token_counts: dict[str, int] = dict()
        token_counts[Constants.PROMPT_TOKENS] = prompt_tokens
        token_counts[Constants.COMPLETION_TOKENS] = completion_tokens
        return token_counts
