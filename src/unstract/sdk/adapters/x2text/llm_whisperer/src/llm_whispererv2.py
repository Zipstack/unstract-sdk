import logging
from typing import Any, Optional
from io import BytesIO

from requests import Response
from unstract.sdk.adapters.exceptions import ExtractorError
from unstract.sdk.adapters.x2text.llm_whisperer.src.constants import WhispererConfig
from unstract.llmwhisperer.client_v2 import (
    LLMWhispererClientV2,
    LLMWhispererClientException,
)

logger = logging.getLogger(__name__)


class LLMWhispererV2:
    def _get_result(
        config, base_url: str, params: Optional[dict[str, Any]], data: Optional[Any]
    ) -> Response:
        """Handles v2 API requests."""
        client = LLMWhispererClientV2(
            base_url=base_url,
            api_key=config.get(WhispererConfig.UNSTRACT_KEY),
        )
        try:
            byte_file = BytesIO(data)
            whisper_result = client.whisper(**params, stream=byte_file)
            if whisper_result["status_code"] == 200:
                return whisper_result["extraction"]
            else:
                raise ExtractorError(
                    whisper_result["message"], whisper_result["status_code"]
                )
        except LLMWhispererClientException as e:
            logger.error(f"LLM Whisperer error: {e}")
            raise ExtractorError(f"LLM Whisperer error: {e}")
        except Exception as e:
            logger.error(f"Adapter error: {e}")
            raise ExtractorError(f"Adapter error: {e}")
