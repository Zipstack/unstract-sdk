import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, Timeout

from unstract.sdk.adapters.exceptions import ExtractorError
from unstract.sdk.adapters.utils import AdapterUtils
from unstract.sdk.adapters.x2text.llm_whisperer_v2.src.constants import (
    HTTPMethod,
    Modes,
    OutputModes,
    WhispererConfig,
    WhispererDefaults,
    WhispererEndpoint,
    WhispererHeader,
    WhisperStatus,
)

logger = logging.getLogger(__name__)


class LLMWhispererHelper:

    @staticmethod
    def get_request_headers(config: dict[str, Any]) -> dict[str, Any]:
        """Obtains the request headers to authenticate with LLM Whisperer.

        Returns:
            str: Request headers
        """
        return {
            "accept": "application/json",
            WhispererHeader.UNSTRACT_KEY: config.get(WhispererConfig.UNSTRACT_KEY),
        }

    @staticmethod
    def make_request(
        config: dict[str, Any],
        request_method: HTTPMethod,
        request_endpoint: str,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
    ) -> Response:
        """Makes a request to LLM whisperer service.

        Args:
            request_method (HTTPMethod): HTTPMethod to call. Can be GET or POST
            request_endpoint (str): LLM whisperer endpoint to hit
            headers (Optional[dict[str, Any]], optional): Headers to pass.
                Defaults to None.
            params (Optional[dict[str, Any]], optional): Query params to pass.
                Defaults to None.
            data (Optional[Any], optional): Data to pass in case of POST.
                Defaults to None.

        Returns:
            Response: Response from the request
        """
        llm_whisperer_svc_url = (
            f"{config.get(WhispererConfig.URL)}" f"/api/v2/{request_endpoint}"
        )
        if not headers:
            headers = LLMWhispererHelper.get_request_headers(config=config)

        try:
            response: Response
            if request_method == HTTPMethod.GET:
                response = requests.get(
                    url=llm_whisperer_svc_url, headers=headers, params=params
                )
            elif request_method == HTTPMethod.POST:
                response = requests.post(
                    url=llm_whisperer_svc_url,
                    headers=headers,
                    params=params,
                    data=data,
                )
            else:
                raise ExtractorError(f"Unsupported request method: {request_method}")
            response.raise_for_status()
        except ConnectionError as e:
            logger.error(f"Adapter error: {e}")
            raise ExtractorError(
                "Unable to connect to LLM Whisperer service, please check the URL"
            )
        except Timeout as e:
            msg = "Request to LLM whisperer has timed out"
            logger.error(f"{msg}: {e}")
            raise ExtractorError(msg)
        except HTTPError as e:
            logger.error(f"Adapter error: {e}")
            default_err = "Error while calling the LLM Whisperer service"
            msg = AdapterUtils.get_msg_from_request_exc(
                err=e, message_key="message", default_err=default_err
            )
            raise ExtractorError(msg)
        return response

    @staticmethod
    def get_whisperer_params(config: dict[str, Any]) -> dict[str, Any]:
        """Gets query params meant for /whisper endpoint.

        The params is filled based on the configuration passed.

        Returns:
            dict[str, Any]: Query params
        """
        params = {
            WhispererConfig.MODE: config.get(WhispererConfig.MODE, Modes.FORM.value),
            WhispererConfig.OUTPUT_MODE: config.get(
                WhispererConfig.OUTPUT_MODE, OutputModes.LAYOUT_PRESERVING.value
            ),
            WhispererConfig.LINE_SPLITTER_TOLERANCE: config.get(
                WhispererConfig.LINE_SPLITTER_TOLERANCE,
                WhispererDefaults.LINE_SPLITTER_TOLERANCE,
            ),
            WhispererConfig.LINE_SPLITTER_STRATEGY: config.get(
                WhispererConfig.LINE_SPLITTER_STRATEGY,
                WhispererDefaults.LINE_SPLITTER_STRATEGY,
            ),
            WhispererConfig.HORIZONTAL_STRETCH_FACTOR: config.get(
                WhispererConfig.HORIZONTAL_STRETCH_FACTOR,
                WhispererDefaults.HORIZONTAL_STRETCH_FACTOR,
            ),
            WhispererConfig.PAGES_TO_EXTRACT: config.get(
                WhispererConfig.PAGES_TO_EXTRACT,
                WhispererDefaults.PAGES_TO_EXTRACT,
            ),
            WhispererConfig.MARK_VERTICAL_LINES: config.get(
                WhispererConfig.MARK_VERTICAL_LINES,
                WhispererDefaults.MARK_VERTICAL_LINES,
            ),
            WhispererConfig.MARK_HORIZONTAL_LINES: config.get(
                WhispererConfig.MARK_HORIZONTAL_LINES,
                WhispererDefaults.MARK_HORIZONTAL_LINES,
            ),
            WhispererConfig.URL_IN_POST: WhispererDefaults.URL_IN_POST,
            WhispererConfig.PAGE_SEPARATOR: config.get(
                WhispererConfig.PAGE_SEPARATOR,
                WhispererDefaults.PAGE_SEPARATOR,
            ),
            # Not providing default value to maintain legacy compatablity
            # these are optional params and identifiers for audit
            WhispererConfig.TAG: config.get(
                WhispererConfig.TAG,
                WhispererDefaults.TAG,
            ),
            WhispererConfig.USE_WEBHOOK: config.get(WhispererConfig.USE_WEBHOOK),
            WhispererConfig.WEBHOOK_METADATA: config.get(
                WhispererConfig.WEBHOOK_METADATA
            ),
        }
        if params[WhispererConfig.MODE] == Modes.LOW_COST.value:
            params.update(
                {
                    WhispererConfig.MEDIAN_FILTER_SIZE: config.get(
                        WhispererConfig.MEDIAN_FILTER_SIZE,
                        WhispererDefaults.MEDIAN_FILTER_SIZE,
                    ),
                    WhispererConfig.GAUSSIAN_BLUR_RADIUS: config.get(
                        WhispererConfig.GAUSSIAN_BLUR_RADIUS,
                        WhispererDefaults.GAUSSIAN_BLUR_RADIUS,
                    ),
                }
            )
        return params

    @staticmethod
    def check_status_until_ready(
        config: dict[str, Any],
        whisper_hash: str,
        headers: dict[str, Any],
        params: dict[str, Any],
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
            status_response = LLMWhispererHelper.make_request(
                config=config,
                request_method=HTTPMethod.GET,
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

    @staticmethod
    def extract_async(config: dict[str, Any], whisper_hash: str) -> dict[Any, Any]:
        """Makes an async extraction with LLMWhisperer.

        Polls and checks the status first before proceeding to retrieve once.

        Args:
            whisper_hash (str): Identifier of the extraction

        Returns:
            str: Extracted contents from the file
        """
        logger.info(f"Extracting async for whisper hash: {whisper_hash}")

        headers: dict[str, Any] = LLMWhispererHelper.get_request_headers(config)
        params = {
            WhisperStatus.WHISPER_HASH: whisper_hash,
            WhispererConfig.TEXT_ONLY: WhispererDefaults.TEXT_ONLY,
        }

        # Polls in fixed intervals and checks status
        LLMWhispererHelper.check_status_until_ready(
            config=config, whisper_hash=whisper_hash, headers=headers, params=params
        )

        retrieve_response = LLMWhispererHelper.make_request(
            config=config,
            request_method=HTTPMethod.GET,
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

    @staticmethod
    def send_whisper_request(
        input_file_path: str, config: dict[str, Any]
    ) -> requests.Response:
        headers = LLMWhispererHelper.get_request_headers(config)
        headers["Content-Type"] = "application/octet-stream"
        params = LLMWhispererHelper.get_whisperer_params(config)

        response: requests.Response
        try:
            with open(input_file_path, "rb") as input_f:
                response = LLMWhispererHelper.make_request(
                    config=config,
                    request_method=HTTPMethod.POST,
                    request_endpoint=WhispererEndpoint.WHISPER,
                    headers=headers,
                    params=params,
                    data=input_f.read(),
                )
        except OSError as e:
            logger.error(f"OS error while reading {input_file_path}: {e}")
            raise ExtractorError(str(e))
        return response

    @staticmethod
    def extract_text_from_response(
        config: dict[str, Any],
        output_file_path: Optional[str],
        response_dict: dict[str, Any],
        response: Response,
    ) -> str:
        output_json = {}
        if response.status_code == 200:
            output_json = response.json()
        elif response.status_code == 202:
            whisper_hash = response_dict.get(WhisperStatus.WHISPER_HASH)
            output_json = LLMWhispererHelper.extract_async(
                config=config, whisper_hash=whisper_hash
            )
        else:
            raise ExtractorError("Couldn't extract text from file")
        if output_file_path:
            LLMWhispererHelper.write_output_to_file(
                output_json=output_json,
                output_file_path=Path(output_file_path),
            )
        return output_json.get("result_text", "")

    @staticmethod
    def write_output_to_file(output_json: dict, output_file_path: Path) -> None:
        """Writes the extracted text and metadata to the specified output file
        and metadata file.

        Args:
            output_json (dict): The dictionary containing the extracted data,
                with "text" as the key for the main content.
            output_file_path (Path): The file path where the extracted text
                should be written.

        Raises:
            ExtractorError: If there is an error while writing the output file.
        """
        try:
            text_output = output_json.get("result_text", "")
            logger.info(f"Writing output to {output_file_path}")
            output_file_path.write_text(text_output, encoding="utf-8")
        except Exception as e:
            logger.error(f"Error while writing {output_file_path}: {e}")
            raise ExtractorError(str(e))
        try:
            # Define the directory of the output file and metadata paths
            output_dir = output_file_path.parent
            metadata_dir = output_dir / "metadata"
            metadata_file_name = output_file_path.with_suffix(".json").name
            metadata_file_path = metadata_dir / metadata_file_name
            # Ensure the metadata directory exists
            metadata_dir.mkdir(parents=True, exist_ok=True)
            # Remove the "result_text" key from the metadata
            metadata = {
                key: value for key, value in output_json.items() if key != "result_text"
            }
            metadata_json = json.dumps(metadata, ensure_ascii=False, indent=4)
            logger.info(f"Writing metadata to {metadata_file_path}")
            metadata_file_path.write_text(metadata_json, encoding="utf-8")
        except Exception as e:
            logger.warn(f"Error while writing metadata to {metadata_file_path}: {e}")
