from typing import Any, Optional

from llama_index.callbacks import TokenCountingHandler
from llama_index.callbacks.base_handler import BaseCallbackHandler
from llama_index.callbacks.schema import CBEventType
from llama_index.core.embeddings.base import BaseEmbedding
from llama_index.llms.llm import LLM
from unstract.sdk.audit import Audit
from unstract.sdk.constants import LogLevel
from unstract.sdk.tool.stream import StreamMixin


class UsageHandler(StreamMixin, BaseCallbackHandler):
    """UsageHandler class is a subclass of BaseCallbackHandler and is
    responsible for handling usage events in the LLM or Embedding models. It
    provides methods for starting and ending traces, as well as handling event
    starts and ends.

    Attributes:
        - token_counter (TokenCountingHandler): The token counter object used
          to count tokens in the LLM or Embedding models.
        - llm_model (LLM): The LLM model object.
        - embed_model (BaseEmbedding): The embedding model object.
        - workflow_id (str): The ID of the workflow.
        - execution_id (str): The ID of the execution.
        - event_starts_to_ignore (Optional[list[CBEventType]]): A list of event
          types to ignore at the start.
        - event_ends_to_ignore (Optional[list[CBEventType]]): A list of event
          types to ignore at the end.
        - verbose (bool): A flag indicating whether to print verbose output.
    """

    def __init__(
        self,
        token_counter: TokenCountingHandler,
        platform_api_key: str,
        llm_model: LLM = None,
        embed_model: BaseEmbedding = None,
        workflow_id: str = "",
        execution_id: str = "",
        event_starts_to_ignore: Optional[list[CBEventType]] = None,
        event_ends_to_ignore: Optional[list[CBEventType]] = None,
        verbose: bool = False,
        log_level: LogLevel = LogLevel.INFO,
    ) -> None:
        self._verbose = verbose
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.token_counter = token_counter
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.platform_api_key = platform_api_key
        super().__init__(
            log_level=log_level,  # StreamMixin's args
            event_starts_to_ignore=event_starts_to_ignore or [],
            event_ends_to_ignore=event_ends_to_ignore or [],
        )

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        return

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[dict[str, list[str]]] = None,
    ) -> None:
        return

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Push the usage of  LLM or Embedding to platform service."""
        if (
            event_type == CBEventType.LLM
            and event_type not in self.event_ends_to_ignore
            and payload is not None
        ):
            model_name = self.llm_model.metadata.model_name
            # Need to push the data to via platform service
            self.stream_log(log=f"Pushing llm usage llm for model {model_name}")
            Audit(log_level=self.log_level).push_usage_data(
                platform_api_key=self.platform_api_key,
                token_counter=self.token_counter,
                event_type=event_type,
                external_service=self.llm_model.metadata.model_name,
                workflow_id=self.workflow_id,
                execution_id=self.execution_id,
            )

        elif (
            event_type == CBEventType.EMBEDDING
            and event_type not in self.event_ends_to_ignore
            and payload is not None
        ):
            model_name = self.embed_model.model_name
            # Need to push the data to via platform service
            self.stream_log(log=f"Pushing llm usage llm for model {model_name}")
            Audit(log_level=self.log_level).push_usage_data(
                platform_api_key=self.platform_api_key,
                token_counter=self.token_counter,
                event_type=event_type,
                external_service=self.embed_model.model_name,
                workflow_id=self.workflow_id,
                execution_id=self.execution_id,
            )
