from llama_index.core.base.embeddings.base import Embedding
from llama_index.core.embeddings import BaseEmbedding
from typing_extensions import deprecated
from unstract.adapters.constants import Common
from unstract.adapters.embedding import adapters

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.exceptions import EmbeddingError, SdkError
from unstract.sdk.tool.base import BaseTool


class Embedding:
    _TEST_SNIPPET = "Hello, I am Unstract"
    MAX_TOKENS = 1024 * 16
    embedding_adapters = adapters

    def __init__(self, tool: BaseTool, adapter_intance_id: str, **usage_kwargs):
        self.tool = tool
        self.adapter_instance_id = adapter_intance_id
        self.usage_kwargs = usage_kwargs
        self.embedding_instance: BaseEmbedding = self._get_embedding()
        self.length: int = self._get_embedding_length()

    def _get_embedding(self) -> BaseEmbedding:
        """Gets an instance of LlamaIndex's embedding object.

        Args:
            adapter_instance_id (str): UUID of the embedding adapter

        Returns:
            BaseEmbedding: Embedding instance
        """
        try:
            embedding_config_data = ToolAdapter.get_adapter_config(
                self.tool, self.adapter_instance_id
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
            self.tool.stream_log(
                log=f"Error getting embedding: {e}", level=LogLevel.ERROR
            )
            raise EmbeddingError(f"Error getting embedding instance: {e}") from e

    def get_query_embedding(self, query: str) -> Embedding:
        return self.embedding_instance.get_query_embedding(query)

    def _get_embedding_length(self) -> int:
        embedding_list = self.embedding_instance._get_text_embedding(self._TEST_SNIPPET)
        embedding_dimension = len(embedding_list)
        return embedding_dimension

    @deprecated("Use the new class Embedding")
    def get_embedding_length(self, embedding: BaseEmbedding) -> int:
        return self._get_embedding_length(embedding)


# Legacy
ToolEmbedding = Embedding
