import logging
from typing import Union

from llama_index.core.vector_stores.types import BasePydanticVectorStore, VectorStore
from unstract.adapters.constants import Common
from unstract.adapters.vectordb import adapters
from unstract.adapters.vectordb.constants import VectorDbConstants

from unstract.sdk.adapters import ToolAdapter
from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.exceptions import SdkError, ToolVectorDBError
from unstract.sdk.platform import PlatformHelper
from unstract.sdk.tool.base import BaseTool

logger = logging.getLogger(__name__)


class ToolVectorDB:
    """Class to handle VectorDB for Unstract Tools."""

    def __init__(self, tool: BaseTool):
        self.tool = tool
        self.vector_db_adapters = adapters

    def __get_org_id(self) -> str:
        platform_helper = PlatformHelper(
            tool=self.tool,
            platform_host=self.tool.get_env_or_die(ToolEnv.PLATFORM_HOST),
            platform_port=int(self.tool.get_env_or_die(ToolEnv.PLATFORM_PORT)),
        )
        # fetch org id from bearer token
        platform_details = platform_helper.get_platform_details()
        if not platform_details:
            # Errors are logged by the SDK itself
            raise SdkError("Error getting platform details")
        account_id = platform_details.get("organization_id")
        return account_id

    def get_vector_db(
        self, adapter_instance_id: str, embedding_dimension: int
    ) -> Union[BasePydanticVectorStore, VectorStore]:
        """Gets an instance of LlamaIndex's VectorStore.

        Args:
            adapter_instance_id (str): UUID of the vector DB adapter
            embedding_dimension (int): Embedding dimension for the vector store

        Returns:
            Union[BasePydanticVectorStore, VectorStore]: Vector store instance
        """
        try:
            vector_db_config = ToolAdapter.get_adapter_config(
                self.tool, adapter_instance_id
            )
            vector_db_adapter_id = vector_db_config.get(Common.ADAPTER_ID)
            if vector_db_adapter_id not in self.vector_db_adapters:
                raise SdkError(
                    f"VectorDB adapter not supported : " f"{vector_db_adapter_id}"
                )

            vector_db_adapter = self.vector_db_adapters[vector_db_adapter_id][
                Common.METADATA
            ][Common.ADAPTER]
            vector_db_metadata = vector_db_config.get(Common.ADAPTER_METADATA)
            org = self.__get_org_id()
            # Adding the collection prefix and embedding type
            # to the metadata
            vector_db_metadata[VectorDbConstants.VECTOR_DB_NAME] = org
            vector_db_metadata[
                VectorDbConstants.EMBEDDING_DIMENSION
            ] = embedding_dimension

            vector_db_adapter_class = vector_db_adapter(vector_db_metadata)
            return vector_db_adapter_class.get_vector_db_instance()
        except Exception as e:
            self.tool.stream_log(
                log=f"Unable to get vector_db {adapter_instance_id}: {e}",
                level=LogLevel.ERROR,
            )
            raise ToolVectorDBError(f"Error getting vectorDB instance: {e}")
