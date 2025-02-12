import logging
import time
from typing import Any, Optional

from requests import HTTPError, Response, Timeout
import requests
from unstract.sdk.adapters.exceptions import ExtractorError
from unstract.sdk.adapters.utils import AdapterUtils
from unstract.sdk.adapters.x2text.llm_whisperer.src.constants import (
    WhisperStatus,
    WhispererConfig,
    WhispererDefaults,
    WhispererEndpoint,
)

logger = logging.getLogger(__name__)


class LLMWhispererV1:
    def _get_result(
        base_url: str,
        params: Optional[dict[str, Any]],
        data: Optional[Any],
        headers: Optional[Any],
    ) -> Response:
        """Handles v1 API requests."""
        headers["Content-Type"] = "application/octet-stream"
        try:
            response = requests.post(
                url=base_url, headers=headers, params=params, data=data
            )
        except ConnectionError as e:
            logger.error(f"Adapter error: {e}")
            raise ExtractorError(
                "Unable to connect to LLMWhisperer service, please check the URL"
            )
        except Timeout as e:
            msg = "Request to LLMWhisperer has timed out"
            logger.error(f"{msg}: {e}")
            raise ExtractorError(msg)
        except HTTPError as e:
            logger.error(f"Adapter error: {e}")
            default_err = "Error while calling the LLMWhisperer service"
            # TODO: to make use of this X2TextError where ever possible
            msg = AdapterUtils.get_msg_from_request_exc(
                err=e, message_key="message", default_err=default_err
            )
            raise ExtractorError(msg)
        return response

    def _check_status_until_ready(
        self, whisper_hash: str, headers: dict[str, Any], params: dict[str, Any]
    ) -> WhisperStatus:
        """Checks the extraction status by polling.

        Polls the /whisper-status endpoint in fixed intervals of
        env: ADAPTER_LLMW_POLL_INTERVAL for a certain number of times
        controlled by env: ADAPTER_LLMW_MAX_POLLS.

        Args:
            whisper_hash (str): Identifier for the extraction,
                returned by LLMWhisperer
            headers (dict[str, Any]): Headers to pass for the status check
            params (dict[str, Any]): Params to pass for the status check

        Returns:
            WhisperStatus: Status of the extraction
        """
        POLL_INTERVAL = WhispererDefaults.POLL_INTERVAL
        MAX_POLLS = WhispererDefaults.MAX_POLLS
        request_count = 0

        # Check status in fixed intervals upto max poll count.
        while True:
            request_count += 1
            logger.info(
                f"Checking status with interval: {POLL_INTERVAL}s"
                f", request count: {request_count} [max: {MAX_POLLS}]"
            )
            status_response = self._make_request(
                request_endpoint=WhispererEndpoint.STATUS,
                headers=headers,
                params=params,
            )
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get(WhisperStatus.STATUS, WhisperStatus.UNKNOWN)
                logger.info(f"Whisper status for {whisper_hash}: {status}")
                if status in [WhisperStatus.PROCESSED, WhisperStatus.DELIVERED]:
                    break
            else:
                raise ExtractorError(
                    "Error checking LLMWhisperer status: "
                    f"{status_response.status_code} - {status_response.text}"
                )

            # Exit with error if max poll count is reached
            if request_count >= MAX_POLLS:
                raise ExtractorError(
                    "Unable to extract text after attempting" f" {request_count} times"
                )
            time.sleep(POLL_INTERVAL)

        return status

    def _extract_async(self, whisper_hash: str) -> str:
        """Makes an async extraction with LLMWhisperer.

        Polls and checks the status first before proceeding to retrieve once.

        Args:
            whisper_hash (str): Identifier of the extraction

        Returns:
            str: Extracted contents from the file
        """
        logger.info(f"Extracting async for whisper hash: {whisper_hash}")
        version = self.config["version"]
        headers: dict[str, Any] = self._get_request_headers()
        params = (
            {
                WhisperStatus.WHISPER_HASH: whisper_hash,
                WhispererConfig.OUTPUT_JSON: WhispererDefaults.OUTPUT_JSON,
            }
            if version == "v1"
            else {
                WhisperStatus.WHISPER_HASH_V2: whisper_hash,
                WhispererConfig.TEXT_ONLY: WhispererDefaults.TEXT_ONLY,
            }
        )

        # Polls in fixed intervals and checks status
        self._check_status_until_ready(
            whisper_hash=whisper_hash, headers=headers, params=params
        )

        retrieve_response = self._make_request(
            request_endpoint=WhispererEndpoint.RETRIEVE,
            headers=headers,
            params=params,
        )
        if retrieve_response.status_code == 200:
            return retrieve_response.json()
        else:
            raise ExtractorError(
                "Error retrieving from LLMWhisperer: "
                f"{retrieve_response.status_code} - {retrieve_response.text}"
            )

    def _extract_async(self, whisper_hash: str) -> str:
        """Makes an async extraction with LLMWhisperer.

        Polls and checks the status first before proceeding to retrieve once.

        Args:
            whisper_hash (str): Identifier of the extraction

        Returns:
            str: Extracted contents from the file
        """
        logger.info(f"Extracting async for whisper hash: {whisper_hash}")

        headers: dict[str, Any] = self._get_request_headers()
        params = {
            WhisperStatus.WHISPER_HASH: whisper_hash,
            WhispererConfig.OUTPUT_JSON: WhispererDefaults.OUTPUT_JSON,
        }

        # Polls in fixed intervals and checks status
        self._check_status_until_ready(
            whisper_hash=whisper_hash, headers=headers, params=params
        )

        retrieve_response = self._make_request(
            request_endpoint=WhispererEndpoint.RETRIEVE,
            headers=headers,
            params=params,
        )
        if retrieve_response.status_code == 200:
            return retrieve_response.json()
        else:
            raise ExtractorError(
                "Error retrieving from LLMWhisperer: "
                f"{retrieve_response.status_code} - {retrieve_response.text}"
            )
