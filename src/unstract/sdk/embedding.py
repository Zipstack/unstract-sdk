from typing import Any, Optional

from llama_index.core.base.embeddings.base import Embedding
from llama_index.core.embeddings import BaseEmbedding
from typing_extensions import deprecated
from unstract.adapters.constants import Common
from unstract.adapters.embedding import adapters

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.exceptions import EmbeddingError, SdkError
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils.callback_manager import CallbackManager


class Embedding:
    _TEST_SNIPPET = "Hello, I am Unstract"
    MAX_TOKENS = 1024 * 16
    embedding_adapters = adapters

    def __init__(
        self,
        tool: BaseTool,
        adapter_instance_id: Optional[str] = None,
        usage_kwargs: dict[Any, Any] = {},
    ):
        self._tool = tool
        self._adapter_instance_id = adapter_instance_id
        self._embedding_instance: BaseEmbedding = None
        self._length: int = None
        self._usage_kwargs = usage_kwargs
        self._initialise()

    def _initialise(self):
        if self._adapter_instance_id:
            self._embedding_instance = self._get_embedding()
            self._length: int = self._get_embedding_length()
            self._usage_kwargs["adapter_instance_id"] = self._adapter_instance_id
            platform_api_key = self._tool.get_env_or_die(ToolEnv.PLATFORM_API_KEY)
            CallbackManager.set_callback(
                platform_api_key=platform_api_key,
                model=self._embedding_instance,
                kwargs=self._usage_kwargs,
            )

    def _get_embedding(self) -> BaseEmbedding:
        """Gets an instance of LlamaIndex's embedding object.

        Args:
            adapter_instance_id (str): UUID of the embedding adapter

        Returns:
            BaseEmbedding: Embedding instance
        """
        try:
            if not self._adapter_instance_id:
                raise EmbeddingError(
                    "Adapter instance ID not set. " "Initialisation failed"
                )
            embedding_config_data = ToolAdapter.get_adapter_config(
                self._tool, self._adapter_instance_id
            )
            embedding_adapter_id = embedding_config_data.get(Common.ADAPTER_ID)
            if embedding_adapter_id not in self.embedding_adapters:
                raise SdkError(
                    f"Embedding adapter not supported : " f"{embedding_adapter_id}"
                )

            embedding_adapter = self.embedding_adapters[embedding_adapter_id][
                Common.METADATA
            ][Common.ADAPTER]
            embedding_metadata = embedding_config_data.get(Common.ADAPTER_METADATA)
            embedding_adapter_class = embedding_adapter(embedding_metadata)
            return embedding_adapter_class.get_embedding_instance()
        except Exception as e:
            self._tool.stream_log(
                log=f"Error getting embedding: {e}", level=LogLevel.ERROR
            )
            raise EmbeddingError(f"Error getting embedding instance: {e}") from e

    def get_query_embedding(self, query: str) -> Embedding:
        return self._embedding_instance.get_query_embedding(query)

    def _get_embedding_length(self) -> int:
        embedding_list = self._embedding_instance._get_text_embedding(
            self._TEST_SNIPPET
        )
        embedding_dimension = len(embedding_list)
        return embedding_dimension

    def get_class_name(self) -> str:
        """Gets the class name of the Llama Index Embedding.

        Args:
            NA

            Returns:
                Class name
        """
        return self._embedding_instance.class_name()

    @deprecated("Use Embedding instead of ToolEmbedding")
    def get_embedding_length(self, embedding: BaseEmbedding) -> int:
        return self._get_embedding_length()

    @deprecated("Use Embedding instead of ToolEmbedding")
    def get_embedding(self, adapter_instance_id: str) -> BaseEmbedding:
        if not self._embedding_instance:
            self._adapter_instance_id = adapter_instance_id
            self._initialise()
        return self._embedding_instance


# Legacy
ToolEmbedding = Embedding
