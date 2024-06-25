from typing import Any

from llama_index.core.callbacks.schema import EventPayload
from llama_index.core.utilities.token_counting import TokenCounter


class Constants:
    KEY_USAGE = "usage"
    KEY_USAGE_METADATA = "usage_metadata"
    KEY_EVAL_COUNT = "eval_count"
    KEY_PROMPT_EVAL_COUNT = "prompt_eval_count"
    KEY_RAW_RESPONSE = "_raw_response"
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
        token_counter = TokenCounter(
            input_tokens=Constants.DEFAULT_TOKEN_COUNT,
            output_tokens=Constants.DEFAULT_TOKEN_COUNT,
        )
        if EventPayload.PROMPT in payload:
            completion_raw = payload.get(EventPayload.COMPLETION).raw
            if completion_raw:
                if completion_raw.get(Constants.KEY_USAGE):
                    token_counts: dict[
                        str, int
                    ] = TokenCounter._get_prompt_completion_tokens(completion_raw)
                    token_counter = TokenCounter(
                        input_tokens=token_counts[Constants.PROMPT_TOKENS],
                        output_tokens=token_counts[Constants.COMPLETION_TOKENS],
                    )
                elif completion_raw.get(Constants.KEY_RAW_RESPONSE):
                    if hasattr(
                        completion_raw.get(Constants.KEY_RAW_RESPONSE),
                        Constants.KEY_USAGE_METADATA,
                    ):
                        usage = completion_raw.get(
                            Constants.KEY_RAW_RESPONSE
                        ).usage_metadata
                        token_counter = TokenCounter(
                            input_tokens=usage.prompt_token_count,
                            output_tokens=usage.candidates_token_count,
                        )
                else:
                    prompt_tokens = Constants.DEFAULT_TOKEN_COUNT
                    completion_tokens = Constants.DEFAULT_TOKEN_COUNT
                    if completion_raw.get(Constants.KEY_PROMPT_EVAL_COUNT):
                        prompt_tokens = completion_raw.get(
                            Constants.KEY_PROMPT_EVAL_COUNT
                        )
                    if completion_raw.get(Constants.KEY_EVAL_COUNT):
                        completion_tokens = completion_raw.get(Constants.KEY_EVAL_COUNT)
                    token_counter = TokenCounter(
                        input_tokens=prompt_tokens,
                        output_tokens=completion_tokens,
                    )
        elif EventPayload.MESSAGES in payload:
            response_raw = payload.get(EventPayload.RESPONSE).raw
            if response_raw:
                token_counts: dict[
                    str, int
                ] = TokenCounter._get_prompt_completion_tokens(response_raw)
                token_counter = TokenCounter(
                    input_tokens=token_counts[Constants.PROMPT_TOKENS],
                    output_tokens=token_counts[Constants.COMPLETION_TOKENS],
                )

        return token_counter

    @staticmethod
    def _get_prompt_completion_tokens(response) -> dict[str, int]:
        prompt_tokens = Constants.DEFAULT_TOKEN_COUNT
        completion_tokens = Constants.DEFAULT_TOKEN_COUNT

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
