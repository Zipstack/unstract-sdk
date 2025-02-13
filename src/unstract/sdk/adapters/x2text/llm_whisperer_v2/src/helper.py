from io import BytesIO
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
)
from unstract.sdk.adapters.x2text.llm_whisperer_v2.src.dto import WhispererRequestParams
from unstract.sdk.constants import MimeType
from unstract.sdk.file_storage import FileStorage, FileStorageProvider
from unstract.llmwhisperer.client_v2 import (
    LLMWhispererClientV2,
    LLMWhispererClientException,
)

logger = logging.getLogger(__name__)


class LLMWhispererHelper:
    @staticmethod
    def get_request_headers(config: dict[str, Any]) -> dict[str, Any]:
        """Obtains the request headers to authenticate with LLMWhisperer.

        Returns:
            str: Request headers
        """
        return {
            "accept": MimeType.JSON,
            WhispererHeader.UNSTRACT_KEY: config.get(WhispererConfig.UNSTRACT_KEY),
        }

    @staticmethod
    def make_request(
        config: dict[str, Any],
        request_endpoint: str,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        data: Optional[Any] = None,
        is_test_connection: Optional[bool] = False,
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
        llm_whisperer_svc_url = f"{config.get(WhispererConfig.URL)}" f"/api/v2"
        if not headers:
            headers = LLMWhispererHelper.get_request_headers(config=config)

        try:
            response: Response
            if is_test_connection:
                url = f"{llm_whisperer_svc_url}/{request_endpoint}"
                response = requests.get(url=url, headers=headers, params=params)
                response.raise_for_status()
            else:
                client = LLMWhispererClientV2(
                    base_url=llm_whisperer_svc_url,
                    api_key=config.get(WhispererConfig.UNSTRACT_KEY),
                    logging_level=config.get(WhispererConfig.LOGGING_LEVEL),
                )
                response = client.whisper(**params, stream=data)
                if response["status_code"] == 200:
                    return response["extraction"]
                else:
                    raise ExtractorError(
                        response["message"],
                        response["status_code"],
                        actual_err=response,
                    )

        except ConnectionError as e:
            logger.error(f"Adapter error: {e}")
            raise ExtractorError(
                "Unable to connect to LLMWhisperer service, please check the URL",
                actual_err=e,
                status_code=503,
            )
        except Timeout as e:
            msg = "Request to LLMWhisperer has timed out"
            logger.error(f"{msg}: {e}")
            raise ExtractorError(msg, actual_err=e, status_code=504)
        except HTTPError as e:
            logger.error(f"Adapter error: {e}")
            default_err = "Error while calling the LLMWhisperer service"
            msg = AdapterUtils.get_msg_from_request_exc(
                err=e, message_key="message", default_err=default_err
            )
            raise ExtractorError(msg, status_code=e.response.status_code, actual_err=e)
        except LLMWhispererClientException as e:
            logger.error(f"LLM Whisperer error: {e}")
            raise ExtractorError(
                message=f"LLM Whisperer error: {e}",
                actual_err=e,
                status_code=500,
            )

        return response

    @staticmethod
    def get_whisperer_params(
        config: dict[str, Any], extra_params: WhispererRequestParams
    ) -> dict[str, Any]:
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
            WhispererConfig.PAGE_SEPARATOR: config.get(
                WhispererConfig.PAGE_SEPARATOR,
                WhispererDefaults.PAGE_SEPARATOR,
            ),
            # Not providing default value to maintain legacy compatablity
            # these are optional params and identifiers for audit
            WhispererConfig.TAG: extra_params.tag
            or config.get(
                WhispererConfig.TAG,
                WhispererDefaults.TAG,
            ),
            WhispererConfig.USE_WEBHOOK: config.get(WhispererConfig.USE_WEBHOOK),
            WhispererConfig.WEBHOOK_METADATA: config.get(
                WhispererConfig.WEBHOOK_METADATA
            ),
            WhispererConfig.WAIT_TIMEOUT: config.get(
                WhispererConfig.WAIT_TIMEOUT,
                WhispererDefaults.WAIT_TIMEOUT,
            ),
            WhispererConfig.WAIT_FOR_COMPLETION: WhispererDefaults.WAIT_FOR_COMPLETION,
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
    def send_whisper_request(
        input_file_path: str,
        config: dict[str, Any],
        extra_params: WhispererRequestParams,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> requests.Response:
        params = LLMWhispererHelper.get_whisperer_params(
            config=config, extra_params=extra_params
        )

        response: requests.Response
        try:
            input_file_data = BytesIO(fs.read(input_file_path, "rb"))
            response = LLMWhispererHelper.make_request(
                config=config,
                request_endpoint=WhispererEndpoint.WHISPER,
                params=params,
                data=input_file_data,
            )
        except OSError as e:
            logger.error(f"OS error while reading {input_file_path}: {e}")
            raise ExtractorError(str(e))
        return response

    @staticmethod
    def extract_text_from_response(
        output_file_path: Optional[str],
        response: dict[str, Any],
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        if not response:
            raise ExtractorError("Couldn't extract text from file", status_code=500)
        output_json = {}
        output_json = response
        if output_file_path:
            LLMWhispererHelper.write_output_to_file(
                output_json=output_json,
                output_file_path=Path(output_file_path),
                fs=fs,
            )
        return output_json.get("result_text", "")

    @staticmethod
    def write_output_to_file(
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
            text_output = output_json.get("result_text", "")
            logger.info(f"Writing output to {output_file_path}")
            fs.write(
                path=str(output_file_path), mode="w", data=text_output, encoding="utf-8"
            )
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
            fs.mkdir(create_parents=True, path=str(metadata_dir))
            # Remove the "result_text" key from the metadata
            metadata = {
                key: value for key, value in output_json.items() if key != "result_text"
            }
            metadata_json = json.dumps(metadata, ensure_ascii=False, indent=4)
            logger.info(f"Writing metadata to {metadata_file_path}")
            fs.write(
                path=str(metadata_file_path),
                mode="w",
                data=metadata_json,
                encoding="utf-8",
            )
        except Exception as e:
            logger.warn(f"Error while writing metadata to {metadata_file_path}: {e}")
