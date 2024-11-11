import json
import logging
import os
from typing import Any

from google.auth.transport import requests as google_requests
from google.oauth2.service_account import Credentials
from llama_index.core.llms import LLM
from llama_index.llms.vertex import Vertex
from vertexai.generative_models import Candidate, FinishReason, ResponseValidationError
from vertexai.generative_models._generative_models import (
    HarmBlockThreshold,
    HarmCategory,
)

from unstract.sdk.adapters.exceptions import LLMError
from unstract.sdk.adapters.llm.constants import LLMKeys
from unstract.sdk.adapters.llm.llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class Constants:
    MODEL = "model"
    PROJECT = "project"
    JSON_CREDENTIALS = "json_credentials"
    MAX_RETRIES = "max_retries"
    MAX_TOKENS = "max_tokens"
    DEFAULT_MAX_TOKENS = 2048
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"


class SafetySettingsConstants:
    SAFETY_SETTINGS = "safety_settings"
    DANGEROUS_CONTENT = "dangerous_content"
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SEXUAL_CONTENT = "sexual_content"
    OTHER = "other"


UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING: dict[str, HarmBlockThreshold] = {
    "HARM_BLOCK_THRESHOLD_UNSPECIFIED": HarmBlockThreshold.HARM_BLOCK_THRESHOLD_UNSPECIFIED,  # noqa: E501
    "BLOCK_LOW_AND_ABOVE": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    "BLOCK_MEDIUM_AND_ABOVE": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    "BLOCK_ONLY_HIGH": HarmBlockThreshold.BLOCK_ONLY_HIGH,
    "BLOCK_NONE": HarmBlockThreshold.BLOCK_NONE,
    "OFF": HarmBlockThreshold.OFF,
}


class VertexAILLM(LLMAdapter):
    def __init__(self, settings: dict[str, Any]):
        super().__init__("VertexAILLM")
        self.config = settings

    @staticmethod
    def get_id() -> str:
        return "vertexai|78fa17a5-a619-47d4-ac6e-3fc1698fdb55"

    @staticmethod
    def get_name() -> str:
        return "VertexAI"

    @staticmethod
    def get_description() -> str:
        return "Vertex Gemini LLM"

    @staticmethod
    def get_provider() -> str:
        return "vertex_ai"

    @staticmethod
    def get_icon() -> str:
        return "/icons/adapter-icons/VertexAI.png"

    @staticmethod
    def get_json_schema() -> str:
        f = open(f"{os.path.dirname(__file__)}/static/json_schema.json")
        schema = f.read()
        f.close()
        return schema

    def get_llm_instance(self) -> LLM:
        input_credentials = self.config.get(Constants.JSON_CREDENTIALS, "{}")
        try:
            json_credentials = json.loads(input_credentials)
        except json.JSONDecodeError:
            raise LLMError(
                "Credentials is not a valid service account JSON, "
                "please provide a valid JSON."
            )

        credentials = Credentials.from_service_account_info(
            info=json_credentials,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )  # type: ignore
        credentials.refresh(google_requests.Request())  # type: ignore
        max_retries = int(
            self.config.get(Constants.MAX_RETRIES, LLMKeys.DEFAULT_MAX_RETRIES)
        )
        max_tokens = int(
            self.config.get(Constants.MAX_TOKENS, Constants.DEFAULT_MAX_TOKENS)
        )

        safety_settings_default_config: dict[str, str] = {
            SafetySettingsConstants.DANGEROUS_CONTENT: Constants.BLOCK_ONLY_HIGH,
            SafetySettingsConstants.HATE_SPEECH: Constants.BLOCK_ONLY_HIGH,
            SafetySettingsConstants.HARASSMENT: Constants.BLOCK_ONLY_HIGH,
            SafetySettingsConstants.SEXUAL_CONTENT: Constants.BLOCK_ONLY_HIGH,
            SafetySettingsConstants.OTHER: Constants.BLOCK_ONLY_HIGH,
        }
        safety_settings_user_config: dict[str, str] = self.config.get(
            SafetySettingsConstants.SAFETY_SETTINGS,
            safety_settings_default_config,
        )

        vertex_safety_settings: dict[
            HarmCategory, HarmBlockThreshold
        ] = self._get_vertex_safety_settings(safety_settings_user_config)

        llm: LLM = Vertex(
            project=str(self.config.get(Constants.PROJECT)),
            model=str(self.config.get(Constants.MODEL)),
            credentials=credentials,
            temperature=0,
            max_retries=max_retries,
            max_tokens=max_tokens,
            safety_settings=vertex_safety_settings,
        )
        return llm

    def _get_vertex_safety_settings(
        self, safety_settings_user_config: dict[str, str]
    ) -> dict[HarmCategory, HarmBlockThreshold]:
        vertex_safety_settings: dict[HarmCategory, HarmBlockThreshold] = dict()
        vertex_safety_settings[
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
        ] = UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING[
            (
                safety_settings_user_config.get(
                    SafetySettingsConstants.DANGEROUS_CONTENT,
                    Constants.BLOCK_ONLY_HIGH,
                )
            )
        ]
        vertex_safety_settings[
            HarmCategory.HARM_CATEGORY_HATE_SPEECH
        ] = UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING[
            (
                safety_settings_user_config.get(
                    SafetySettingsConstants.HATE_SPEECH,
                    Constants.BLOCK_ONLY_HIGH,
                )
            )
        ]
        vertex_safety_settings[
            HarmCategory.HARM_CATEGORY_HARASSMENT
        ] = UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING[
            (
                safety_settings_user_config.get(
                    SafetySettingsConstants.HARASSMENT,
                    Constants.BLOCK_ONLY_HIGH,
                )
            )
        ]
        vertex_safety_settings[
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
        ] = UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING[
            (
                safety_settings_user_config.get(
                    SafetySettingsConstants.SEXUAL_CONTENT,
                    Constants.BLOCK_ONLY_HIGH,
                )
            )
        ]
        vertex_safety_settings[
            HarmCategory.HARM_CATEGORY_UNSPECIFIED
        ] = UNSTRACT_VERTEX_SAFETY_THRESHOLD_MAPPING[
            (
                safety_settings_user_config.get(
                    SafetySettingsConstants.OTHER, Constants.BLOCK_ONLY_HIGH
                )
            )
        ]
        return vertex_safety_settings

    @staticmethod
    def parse_llm_err(e: ResponseValidationError) -> LLMError:
        """Parse the error from Vertex AI.

        Helps parse and raise errors from Vertex AI.
        https://ai.google.dev/api/generate-content#generatecontentresponse

        Args:
            e (ResponseValidationError): Exception from Vertex AI

        Returns:
            LLMError: Error to be sent to the user
        """
        assert len(e.responses) == 1, (
            "Expected e.responses to contain a single element "
            "since its a completion call and not chat."
        )
        resp = e.responses[0]
        candidates: list["Candidate"] = resp.candidates
        if not candidates:
            msg = str(resp.prompt_feedback)
        reason_messages = {
            FinishReason.MAX_TOKENS: (
                "The maximum number of tokens for the LLM has been reached. Please "
                "either tweak your prompts or try using another LLM."
            ),
            FinishReason.STOP: (
                "The LLM stopped generating a response due to the natural stop "
                "point of the model or a provided stop sequence."
            ),
            FinishReason.SAFETY: "The LLM response was flagged for safety reasons.",
            FinishReason.RECITATION: (
                "The LLM response was flagged for recitation reasons."
            ),
            FinishReason.BLOCKLIST: (
                "The LLM response generation was stopped because it "
                "contains forbidden terms."
            ),
            FinishReason.PROHIBITED_CONTENT: (
                "The LLM response generation was stopped because it "
                "potentially contains prohibited content."
            ),
            FinishReason.SPII: (
                "The LLM response generation was stopped because it potentially "
                "contains Sensitive Personally Identifiable Information."
            ),
        }

        err_list = []
        for candidate in candidates:
            reason: FinishReason = candidate.finish_reason
            if candidate.finish_message:
                err_msg = candidate.finish_message
            else:
                err_msg = reason_messages.get(reason, str(candidate))
            err_list.append(err_msg)
        msg = "\n\nAnother error: \n".join(err_list)
        return LLMError(msg)
