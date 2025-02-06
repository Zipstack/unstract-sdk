from io import BytesIO
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, Timeout

from unstract.llmwhisperer.client_v2 import (
    LLMWhispererClientV2,
    LLMWhispererClientException,
)
from unstract.llmwhisperer.client import LLMWhispererClient
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

    ID = "llmwhisperer|a5e6b8af-3e1f-4a80-b006-d017e8e67f93"
    NAME = "LLMWhisperer"
    DESCRIPTION = "LLMWhisperer X2Text"
    ICON = "/icons/adapter-icons/LLMWhispererV2.png"

    @staticmethod
    def get_id() -> str:
        return LLMWhisperer.ID

    @staticmethod
    def get_name() -> str:
        return LLMWhisperer.NAME

    @staticmethod
    def get_description() -> str:
        return LLMWhisperer.DESCRIPTION

    @staticmethod
    def get_icon() -> str:
        return LLMWhisperer.ICON

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def _make_request(
        self,
        request_endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        is_test_connect: bool = False,
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
        base_url = (
            f"{self.config.get(WhispererConfig.URL)}/api/v2/{request_endpoint}"
            if version == "v2"
            else f"{self.config.get(WhispererConfig.URL)}" f"/v1/{request_endpoint}"
        )
        if is_test_connect:
            headers = {
                "accept": MimeType.JSON,
                WhispererHeader.UNSTRACT_KEY: self.config.get(
                    WhispererConfig.UNSTRACT_KEY
                ),
            }
            try:
                response = requests.get(url=base_url, headers=headers, params=params)
            except ConnectionError as e:
                logger.error(f"Adapter error: {e}")
                raise ExtractorError(
                    "Unable to connect to LLMWhisperer service, please check the URL"
                )
            except HTTPError as e:
                logger.error(f"Adapter error: {e}")
                default_err = "Error while calling the LLMWhisperer service"
                msg = AdapterUtils.get_msg_from_request_exc(
                    err=e, message_key="message", default_err=default_err
                )
                raise ExtractorError(msg)

        else:
            client = (
                LLMWhispererClientV2(
                    base_url=base_url,
                    api_key=self.config.get(WhispererConfig.UNSTRACT_KEY),
                )
                if version == "v2"
                else LLMWhispererClient(
                    base_url=base_url,
                    api_key=self.config.get(WhispererConfig.UNSTRACT_KEY),
                )
            )
            try:
                response: Any
                whisper_result = client.whisper(params, stream=data)
                if whisper_result["status_code"] == 200:
                    response = whisper_result["extraction"]
                else:
                    default_err = "Error while calling the LLMWhisperer service"
                    raise ExtractorError(
                        default_err,
                        whisper_result["status_code"],
                        whisper_result["message"],
                    )
            except LLMWhispererClientException as e:
                logger.error(f"Adapter error: {e}")
                raise ExtractorError(message=LLMWhispererClientException.error_message)

            except Exception as e:
                logger.error(f"Adapter error: {e}")
                default_err = "Error while calling the LLMWhisperer service"
                raise ExtractorError(message=default_err, actual_err=e)
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
            WhispererConfig.WAIT_FOR_COMPLETION: self.config.get(
                WhispererDefaults.WAIT_FOR_COMPLETION,
            ),
            WhispererConfig.WAIT_TIMEOUT: self.config.get(
                WhispererConfig.WAIT_TIMEOUT,
                WhispererDefaults.WAIT_TIMEOUT,
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
            request_endpoint=WhispererEndpoint.TEST_CONNECTION, is_test_connection=True
        )
        return True

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
        version = self.config["version"]
        config = self.config
        params = {}
        if version == "v1":
            params = self._get_whisper_params(enable_highlight)
        elif version == "v2":
            params = LLMWhispererHelper.get_whisperer_params(config)
        else:
            raise ValueError("Unsupported version. Only 'v1' and 'v2' are allowed.")

        try:
            input_file_data = fs.read(input_file_path, "rb")
            file_buffer = BytesIO(input_file_data.read())
            response = self._make_request(
                request_endpoint=WhispererEndpoint.WHISPER,
                params=params,
                data=file_buffer,
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
        version = self.config["version"]
        output_json = response
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
            version = self.config["version"]
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
        if self.config["version"] == "v2":
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
