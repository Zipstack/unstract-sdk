import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, Timeout

from unstract.sdk.adapters.exceptions import ExtractorError
from unstract.sdk.adapters.utils import AdapterUtils
from unstract.sdk.adapters.x2text.constants import X2TextConstants
from unstract.sdk.adapters.x2text.dto import (
    TextExtractionMetadata,
    TextExtractionResult,
)
from unstract.sdk.adapters.x2text.llm_whisperer.src.constants import (
    HTTPMethod,
    OutputModes,
    ProcessingModes,
    WhispererConfig,
    WhispererDefaults,
    WhispererEndpoint,
    WhispererHeader,
    WhisperStatus,
)
from unstract.sdk.adapters.x2text.llm_whisperer.src.helper import LLMWhispererHelper
from unstract.sdk.adapters.x2text.x2text_adapter import X2TextAdapter
from unstract.sdk.constants import MimeType
from unstract.sdk.file_storage import FileStorage, FileStorageProvider

logger = logging.getLogger(__name__)


class LLMWhisperer(X2TextAdapter):
    _version = "v2"
    def __init__(self, settings: dict[str, Any]):
        super().__init__("LLMWhisperer")
        self.config = settings
        self.config["version"] = settings.get(WhispererConfig.VERSION, "v2")
        LLMWhisperer._version = settings.get(WhispererConfig.VERSION, "v2")
        
    V1_NAME = "LLMWhisperer"
    V1_DESCRIPTION = "LLMWhisperer X2Text"
    V1_ICON = "/icons/adapter-icons/LLMWhisperer.png"

    V2_ID = "llmwhisperer|a5e6b8af-3e1f-4a80-b006-d017e8e67f93"
    V2_NAME = "LLMWhisperer V2"
    V2_DESCRIPTION = "LLMWhisperer V2 X2Text"
    V2_ICON = "/icons/adapter-icons/LLMWhispererV2.png"

    @staticmethod
    def get_id() -> str:
        return "llmwhisperer|a5e6b8af-3e1f-4a80-b006-d017e8e67f93"

    @classmethod
    def get_name(cls) -> str:
        if cls._version == "v2":
            return cls.V2_NAME
        return cls.V1_NAME

    @classmethod
    def get_description(cls) -> str:
        if cls._version == "v2":
            return cls.V2_DESCRIPTION
        return cls.V1_DESCRIPTION

    @classmethod
    def get_icon(cls) -> str:
        if cls._version == "v2":
            return cls.V2_ICON
        return cls.V1_ICON

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def _get_request_headers(self) -> dict[str, Any]:
        """Obtains the request headers to authenticate with LLMWhisperer.

        Returns:
            str: Request headers
        """
        return {
            "accept": MimeType.JSON,
            WhispererHeader.UNSTRACT_KEY: self.config.get(WhispererConfig.UNSTRACT_KEY),
        }

    def _make_request(
        self,
        request_method: HTTPMethod,
        request_endpoint: str,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
    ) -> Response:
        """Makes a request to LLMWhisperer service.

        Args:
            request_method (HTTPMethod): HTTPMethod to call. Can be GET or POST
            request_endpoint (str): LLMWhisperer endpoint to hit
            headers (Optional[dict[str, Any]], optional): Headers to pass.
                Defaults to None.
            params (Optional[dict[str, Any]], optional): Query params to pass.
                Defaults to None.
            data (Optional[Any], optional): Data to pass in case of POST.
                Defaults to None.

        Returns:
            Response: Response from the request
        """
        # Determine version and set appropriate URL
        version = self.config.get("version", "v1")
        base_url = (f"{self.config.get(WhispererConfig.URL)}/api/v2/{request_endpoint}"
                    if version == "v2"
                    else f"{self.config.get(WhispererConfig.URL)}" f"/v1/{request_endpoint}"
                    )

        if not headers:
            headers = self._get_request_headers()

        try:
            response: Response
            if request_method == HTTPMethod.GET:
                response = requests.get(url=base_url, headers=headers, params=params)
            elif request_method == HTTPMethod.POST:
                response = requests.post(
                    url=base_url, headers=headers, params=params, data=data
                )
            else:
                raise ExtractorError(f"Unsupported request method: {request_method}")
            response.raise_for_status()
        except ConnectionError as e:
            logger.error(f"Adapter error: {e}")
            raise ExtractorError(
                "Unable to connect to LLMWhisperer service, please check the URL",
            )
        except Timeout as e:
            msg = "Request to LLMWhisperer has timed out"
            logger.error(f"{msg}: {e}")
            raise ExtractorError(msg)
        except HTTPError as e:
            logger.error(f"Adapter error: {e}")
            default_err = "Error while calling the LLMWhisperer service"
            msg = AdapterUtils.get_msg_from_request_exc(
                err=e, message_key="message", default_err=default_err
            )
            raise ExtractorError(msg)
        return response

    def _get_whisper_params(self, enable_highlight: bool = False) -> dict[str, Any]:
        """Gets query params meant for /whisper endpoint.

        The params is filled based on the configuration passed.

        Returns:
            dict[str, Any]: Query params
        """
        params = {
            WhispererConfig.PROCESSING_MODE: self.config.get(
                WhispererConfig.PROCESSING_MODE, ProcessingModes.TEXT.value
            ),
            # Not providing default value to maintain legacy compatablity
            # Providing default value will overide the params
            # processing_mode, force_text_processing
            WhispererConfig.MODE: self.config.get(WhispererConfig.MODE),
            WhispererConfig.OUTPUT_MODE: self.config.get(
                WhispererConfig.OUTPUT_MODE, OutputModes.LINE_PRINTER.value
            ),
            WhispererConfig.FORCE_TEXT_PROCESSING: self.config.get(
                WhispererConfig.FORCE_TEXT_PROCESSING,
                WhispererDefaults.FORCE_TEXT_PROCESSING,
            ),
            WhispererConfig.LINE_SPLITTER_TOLERANCE: self.config.get(
                WhispererConfig.LINE_SPLITTER_TOLERANCE,
                WhispererDefaults.LINE_SPLITTER_TOLERANCE,
            ),
            WhispererConfig.HORIZONTAL_STRETCH_FACTOR: self.config.get(
                WhispererConfig.HORIZONTAL_STRETCH_FACTOR,
                WhispererDefaults.HORIZONTAL_STRETCH_FACTOR,
            ),
            WhispererConfig.PAGES_TO_EXTRACT: self.config.get(
                WhispererConfig.PAGES_TO_EXTRACT,
                WhispererDefaults.PAGES_TO_EXTRACT,
            ),
            WhispererConfig.ADD_LINE_NOS: WhispererDefaults.ADD_LINE_NOS,
            WhispererConfig.OUTPUT_JSON: WhispererDefaults.OUTPUT_JSON,
            WhispererConfig.PAGE_SEPARATOR: self.config.get(
                WhispererConfig.PAGE_SEPARATOR,
                WhispererDefaults.PAGE_SEPARATOR,
            ),
            WhispererConfig.MARK_VERTICAL_LINES: self.config.get(
                WhispererConfig.MARK_VERTICAL_LINES,
                WhispererDefaults.MARK_VERTICAL_LINES,
            ),
            WhispererConfig.MARK_HORIZONTAL_LINES: self.config.get(
                WhispererConfig.MARK_HORIZONTAL_LINES,
                WhispererDefaults.MARK_HORIZONTAL_LINES,
            ),
        }
        if not params[WhispererConfig.FORCE_TEXT_PROCESSING]:
            params.update(
                {
                    WhispererConfig.MEDIAN_FILTER_SIZE: self.config.get(
                        WhispererConfig.MEDIAN_FILTER_SIZE,
                        WhispererDefaults.MEDIAN_FILTER_SIZE,
                    ),
                    WhispererConfig.GAUSSIAN_BLUR_RADIUS: self.config.get(
                        WhispererConfig.GAUSSIAN_BLUR_RADIUS,
                        WhispererDefaults.GAUSSIAN_BLUR_RADIUS,
                    ),
                }
            )

        if enable_highlight:
            params.update(
                {WhispererConfig.STORE_METADATA_FOR_HIGHLIGHTING: enable_highlight}
            )
        return params

    def test_connection(self) -> bool:
        self._make_request(
            request_method=HTTPMethod.GET,
            request_endpoint=WhispererEndpoint.TEST_CONNECTION,
        )
        return True

    def _check_status_until_ready(

        self,
        whisper_hash: str = "",
        headers: dict[str, Any] = None,
        params: dict[str, Any] = None,
    ) -> WhisperStatus:
        """Checks the extraction status by polling for both v1 and v2.

        Polls the /whisper-status endpoint in fixed intervals of
        env: ADAPTER_LLMW_POLL_INTERVAL for a certain number of times
        controlled by env: ADAPTER_LLMW_MAX_POLLS.

        Args:
            version (str): Version of the LLMWhisperer API (either 'v1' or 'v2')
            config (Optional[dict[str, Any]]): Configuration for v2 (None for v1)
            whisper_hash (str): Identifier for the extraction, returned by LLMWhisperer
            headers (dict[str, Any]): Headers to pass for the status check
            params (dict[str, Any]): Params to pass for the status check

        Returns:
            WhisperStatus: Status of the extraction
        """
        version = self.config['version']
        POLL_INTERVAL = WhispererDefaults.POLL_INTERVAL
        MAX_POLLS = WhispererDefaults.MAX_POLLS
        STATUS_RETRY_THRESHOLD = WhispererDefaults.STATUS_RETRIES if version == "v2" else 0
        status_retry_count = 0
        request_count = 0

        while True:
            request_count += 1
            logger.info(
                f"Checking status{' for whisper-hash ' if version == 'v2' else ''}"
                f"'{whisper_hash}' with interval: {POLL_INTERVAL}s, request count: "
                f"{request_count} [max: {MAX_POLLS}]"
            )

            # Make request based on version
            status_response = self._make_request(
                request_method=HTTPMethod.GET,
                request_endpoint=WhispererEndpoint.STATUS,
                headers=headers,
                params=params,
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get(WhisperStatus.STATUS, WhisperStatus.UNKNOWN)
                logger.info(f"Whisper status for '{whisper_hash}': {status}")
                if status in [WhisperStatus.PROCESSED, WhisperStatus.DELIVERED]:
                    break
            else:
                if version == "v2" and status_retry_count >= STATUS_RETRY_THRESHOLD:
                    raise ExtractorError(
                        f"Error checking LLMWhisperer status for whisper-hash "
                        f"'{whisper_hash}': {status_response.text}"
                    )
                elif version == "v2":
                    status_retry_count += 1
                    logger.warning(
                        f"Whisper status for '{whisper_hash}' failed "
                        f"{status_retry_count} time(s), retrying... "
                        f"[threshold: {STATUS_RETRY_THRESHOLD}]: {status_response.text}"
                    )
                else:  # v1 error handling
                    raise ExtractorError(
                        "Error checking LLMWhisperer status: "
                        f"{status_response.status_code} - {status_response.text}"
                    )

            if request_count >= MAX_POLLS:
                raise ExtractorError(
                    f"Unable to extract text for whisper-hash '{whisper_hash}' "
                    f"after attempting {request_count} times"
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
        version = self.config['version']
        headers: dict[str, Any] = self._get_request_headers()
        params =({
            WhisperStatus.WHISPER_HASH: whisper_hash,
            WhispererConfig.OUTPUT_JSON: WhispererDefaults.OUTPUT_JSON,
        } if version == 'v1'
        else {
            WhisperStatus.WHISPER_HASH_V2: whisper_hash,
            WhispererConfig.TEXT_ONLY: WhispererDefaults.TEXT_ONLY,
        })

        # Polls in fixed intervals and checks status
        self._check_status_until_ready(
            whisper_hash=whisper_hash, headers=headers, params=params
        )

        retrieve_response = self._make_request(
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

    def _send_whisper_request(
        self,
        input_file_path: str,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
        enable_highlight: bool = False,
    ) -> requests.Response:
        """Sends a whisper request for both v1 and v2.

        Args:
            version (str): Version of the LLMWhisperer API (either 'v1' or 'v2')
            input_file_path (str): Path to the input file to be processed
            fs (FileStorage): File storage object to read the file
            enable_highlight (bool): Whether to enable highlight (only for v1)

        Returns:
            requests.Response: Response from the whisper request
        """
        version = self.config['version']
        config = self.config
        params = {}
        headers = self._get_request_headers()
        if version == "v1":
            params = self._get_whisper_params(enable_highlight)
        elif version == "v2":
            params = LLMWhispererHelper.get_whisperer_params(config)
        else:
            raise ValueError("Unsupported version. Only 'v1' and 'v2' are allowed.")

        headers["Content-Type"] = "application/octet-stream"

        try:
            input_file_data = fs.read(input_file_path, "rb")
            response = self._make_request(
                request_method=HTTPMethod.POST,
                request_endpoint=WhispererEndpoint.WHISPER,
                headers=headers,
                params=params,
                data=input_file_data,
            )
        except OSError as e:
            logger.error(f"OS error while reading {input_file_path}: {e}")
            raise ExtractorError(str(e))

        return response

    def _extract_text_from_response(
        self,
        output_file_path: Optional[str],
        response: requests.Response,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        output_json = {}
        version = self.config['version']
        if response.status_code == 200:
            output_json = response.json()
        elif response.status_code == 202:
            whisper_hash_key = WhisperStatus.WHISPER_HASH_V2 if version == "v2" else WhisperStatus.WHISPER_HASH
            whisper_hash = response.json().get(whisper_hash_key)
            output_json = self._extract_async(whisper_hash=whisper_hash)
        else:
            raise ExtractorError("Couldn't extract text from file")
        if output_file_path:
            self._write_output_to_file(
                output_json=output_json, output_file_path=Path(output_file_path), fs=fs
            )
        output_key = "text" if version == "v1" else "result_text"
        return output_json.get(output_key, "")

    def _write_output_to_file(
        self,
        output_json: dict,
        output_file_path: Path,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> None:
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
            version = self.config['version']
            output_key = "text" if version == "v1" else "result_text"
            text_output = output_json.get(output_key, "")
            logger.info(f"Writing output to {output_file_path}")
            fs.write(
                path=output_file_path,
                mode="w",
                encoding="utf-8",
                data=text_output,
            )
            try:
                # Define the directory of the output file and metadata paths
                output_dir = output_file_path.parent
                metadata_dir = output_dir / "metadata"
                metadata_file_name = output_file_path.with_suffix(".json").name
                metadata_file_path = metadata_dir / metadata_file_name
                # Ensure the metadata directory exists
                fs.mkdir(str(metadata_dir), create_parents=True)
                # Remove the "text" key from the metadata
                metadata = {
                    key: value for key, value in output_json.items() if key != "text"
                }
                metadata_json = json.dumps(metadata, ensure_ascii=False, indent=4)
                logger.info(f"Writing metadata to {metadata_file_path}")

                fs.write(
                    path=metadata_file_path,
                    mode="w",
                    encoding="utf-8",
                    data=metadata_json,
                )
            except Exception as e:
                logger.error(
                    f"Error while writing metadata to {metadata_file_path}: {e}"
                )

        except Exception as e:
            logger.error(f"Error while writing {output_file_path}: {e}")
            raise ExtractorError(str(e))

    def process(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
        **kwargs: dict[Any, Any],
    ) -> TextExtractionResult:
        """Used to extract text from documents.

        Args:
            input_file_path (str): Path to file that needs to be extracted
            output_file_path (Optional[str], optional): File path to write
                extracted text into, if None doesn't write to a file.
                Defaults to None.

        Returns:
            TextExtractionResult: Extracted text along with metadata.
        """
        if self.config['version'] == "v2":
            # V2 logic
            response: requests.Response = self._send_whisper_request(
                input_file_path, fs=fs
            )
            response_text = response.text
            response_dict = json.loads(response_text)
            metadata = TextExtractionMetadata(
                whisper_hash=response_dict.get(WhisperStatus.WHISPER_HASH_V2, "")
            )
        else:
            # V1 logic
            response: requests.Response = self._send_whisper_request(
                input_file_path,
                fs,
                bool(kwargs.get(X2TextConstants.ENABLE_HIGHLIGHT, False)),
            )

            metadata = TextExtractionMetadata(
                whisper_hash=response.headers.get(X2TextConstants.WHISPER_HASH, "")
            )

        extracted_text = self._extract_text_from_response(
            output_file_path, response, fs
        )

        return TextExtractionResult(
            extracted_text=extracted_text,
            extraction_metadata=metadata,
        )
