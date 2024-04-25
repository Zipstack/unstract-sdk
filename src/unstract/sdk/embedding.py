from llama_index.core.embeddings import BaseEmbedding
from unstract.adapters.constants import Common
from unstract.adapters.embedding import adapters

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel
from unstract.sdk.exceptions import SdkError
from unstract.sdk.tool.base import BaseTool


class ToolEmbedding:
    __TEST_SNIPPET = "Hello, I am Unstract"

    def __init__(self, tool: BaseTool):
        self.tool = tool
        self.max_tokens = 1024 * 16
        self.embedding_adapters = adapters

    def get_embedding(self, adapter_instance_id: str) -> BaseEmbedding:
        """Gets an instance of LlamaIndex's embedding object.

        Args:
            adapter_instance_id (str): UUID of the embedding adapter

        Returns:
            BaseEmbedding: Embedding instance
        """
        try:
            embedding_config_data = ToolAdapter.get_adapter_config(
                self.tool, adapter_instance_id
            )
            embedding_adapter_id = embedding_config_data.get(Common.ADAPTER_ID)
            if embedding_adapter_id not in self.embedding_adapters:
                raise SdkError(
                    f"Embedding adapter not supported : "
                    f"{embedding_adapter_id}"
                )

            embedding_adapter = self.embedding_adapters[embedding_adapter_id][
                Common.METADATA
            ][Common.ADAPTER]
            embedding_metadata = embedding_config_data.get(
                Common.ADAPTER_METADATA
            )
            embedding_adapter_class = embedding_adapter(embedding_metadata)
            return embedding_adapter_class.get_embedding_instance()
        except Exception as e:
            self.tool.stream_log(
                log=f"Error getting embedding: {e}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error getting embedding instance: {e}")

    def get_embedding_length(self, embedding: BaseEmbedding) -> int:
        embedding_list = embedding._get_text_embedding(self.__TEST_SNIPPET)
        embedding_dimension = len(embedding_list)
        return embedding_dimension
