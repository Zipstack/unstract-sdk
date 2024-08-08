import logging
import os
import re
from typing import Any

from httpx import ConnectError, HTTPStatusError
from llama_index.core.llms import LLM
from llama_index.llms.ollama import Ollama

from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class Constants:
    MODEL = "model"
    API_KEY = "api_key"
    TIMEOUT = "timeout"
    BASE_URL = "base_url"
    JSON_MODE = "json_mode"
    CONTEXT_WINDOW = "context_window"
    MODEL_MISSING_ERROR = "try pulling it first"


class OllamaLLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("Ollama")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "ollama|4b8bd31a-ce42-48d4-9d69-f29c12e0f276"

    @staticmethod
    def get_name() -> str:
        return "Ollama"

    @staticmethod
    def get_description() -> str:
        return "Ollama AI LLM"

    @staticmethod
    def get_provider() -> str:
        return "ollama"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/ollama.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        try:
            llm: LLM = Ollama(
                model=str(self.config.get(Constants.MODEL)),
                base_url=str(self.config.get(Constants.BASE_URL)),
                request_timeout=float(
                    self.config.get(Constants.TIMEOUT, LLMKeys.DEFAULT_TIMEOUT)
                ),
                json_mode=False,
                context_window=int(self.config.get(Constants.CONTEXT_WINDOW, 3900)),
                temperature=0.01,
            )
            return llm

        except ConnectError as connec_err:
            logger.error(f"Ollama server not running : {connec_err}")
            raise AdapterError(
                "Unable to connect to Ollama`s Server, "
                "please check if the server is up and running or"
                "if it is accepting connections."
            )
        except Exception as exc:
            logger.error(f"Error occured while getting llm instance:{exc}")
            raise AdapterError(str(exc))

    def test_connection(self) -> bool:
        try:
            llm = self.get_llm_instance()
            if not llm:
                return False
            response = llm.complete(
                "The capital of Tamilnadu is ",
                temperature=0.003,
            )
            response_lower_case: str = response.text.lower()
            find_match = re.search("chennai", response_lower_case)
            if find_match:
                return True
            else:
                return False
        except HTTPStatusError as http_err:
            if http_err.response:
                if (
                    http_err.response.status_code == 404
                    and Constants.MODEL_MISSING_ERROR in http_err.response.text
                ):
                    logger.error(
                        f"Error occured while sending requst to the model{http_err}"
                    )
                    raise AdapterError(
                        "Model under use is not found. Try pulling it first."
                    )
            raise AdapterError(
                f"Some issue while communicating with the model. "
                f"Details : {http_err.response.text}"
            )

        except Exception as e:
            logger.error(f"Error occured while testing adapter {e}")
            raise AdapterError(str(e))
