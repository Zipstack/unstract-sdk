import json
from typing import Optional

from llama_index.core import Document
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
    VectorStoreQuery,
    VectorStoreQueryResult,
)

from unstract.sdk.adapter import ToolAdapter
from unstract.sdk.adapters.vectordb.no_op.src.no_op_custom_vectordb import (
    NoOpCustomVectorDB,
)
from unstract.sdk.constants import LogLevel
from unstract.sdk.dto import (
    ChunkingConfig,
    FileInfo,
    InstanceIdentifiers,
    ProcessingOptions,
)
from unstract.sdk.embedding import Embedding
from unstract.sdk.exceptions import IndexingError, SdkError
from unstract.sdk.file_storage.impl import FileStorage
from unstract.sdk.file_storage.provider import FileStorageProvider
from unstract.sdk.tool.stream import StreamMixin
from unstract.sdk.utils.common_utils import capture_metrics, log_elapsed
from unstract.sdk.utils.tool_utils import ToolUtils
from unstract.sdk.vector_db import VectorDB


class Index:
    def __init__(
        self,
        tool: StreamMixin,
        run_id: Optional[str] = None,
        capture_metrics: bool = False,
    ):
        # TODO: Inherit from StreamMixin and avoid using BaseTool
        self.tool = tool
        self._run_id = run_id
        self._capture_metrics = capture_metrics
        self._metrics = {}

    def generate_index_key(
        self,
        chuking_config: ChunkingConfig,
        file_info: FileInfo,
        instance_identifiers: InstanceIdentifiers,
        fs: FileStorage = FileStorage(provider=FileStorageProvider.LOCAL),
    ) -> str:
        """Generates a unique index key based on the provided configuration,
        file information, instance identifiers, and processing options.

        Args:
            chunking_config : ChunkingConfig
            file_info (FileInfo): Contains file-related 
            information such as path and hash.
            instance_identifiers (InstanceIdentifiers): Identifiers for
            embedding, vector DB, tool, etc.
            processing_options (ProcessingOptions): Options related to reindexing,
            highlighting, and processing text.
            fs (FileStorage, optional): File storage for remote storage.

        Returns:
            str: A unique index key used for indexing the document.
        """
        if not file_info.file_path and not file_info.file_hash:
            raise ValueError("One of `file_path` or `file_hash` need to be provided")

        if not file_info.file_hash:
            file_hash = fs.get_hash_from_file(path=file_info.file_path)

        # Whole adapter config is used currently even though it contains some keys
        # which might not be relevant to indexing. This is easier for now than
        # marking certain keys of the adapter config as necessary.
        index_key = {
            "file_hash": file_hash,
            "vector_db_config": ToolAdapter.get_adapter_config(
                self.tool, instance_identifiers.vector_db_instance_id
            ),
            "embedding_config": ToolAdapter.get_adapter_config(
                self.tool, instance_identifiers.embedding_instance_id
            ),
            "x2text_config": ToolAdapter.get_adapter_config(
                self.tool, instance_identifiers.x2text_instance_id
            ),
            # Typed and hashed as strings since the final hash is persisted
            # and this is required to be backward compatible
            "chunk_size": str(chuking_config.chunk_size),
            "chunk_overlap": str(chuking_config.chunk_overlap),
        }
        # JSON keys are sorted to ensure that the same key gets hashed even in
        # case where the fields are reordered.
        hashed_index_key = ToolUtils.hash_str(json.dumps(index_key, sort_keys=True))
        return hashed_index_key

    @capture_metrics
    def is_document_indexed(
        self,
        doc_id: str,
        instance_identifiers: InstanceIdentifiers,
        processing_options: ProcessingOptions,
        embedding: Embedding,
        vector_db: VectorDB,
    ) -> bool:
        """Checks if nodes are already present in the vector database for a
        given doc_id.

        Returns:
            str: The document ID.
        """
        try:
            # Checking if document is already indexed against doc_id
            doc_id_eq_filter = MetadataFilter.from_dict(
                {"key": "doc_id", "operator": FilterOperator.EQ, "value": doc_id}
            )
            filters = MetadataFilters(filters=[doc_id_eq_filter])
            q = VectorStoreQuery(
                query_embedding=embedding.get_query_embedding(" "),
                doc_ids=[doc_id],
                filters=filters,
            )

            doc_id_found = False
            try:
                n: VectorStoreQueryResult = vector_db.query(query=q)
                if len(n.nodes) > 0:
                    doc_id_found = True
                    self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
                else:
                    self.tool.stream_log(f"No nodes found for {doc_id}")
            except Exception as e:
                self.tool.stream_log(
                    f"Error querying {instance_identifiers.vector_db_instance_id}: {e},"
                    " proceeding to index",
                    level=LogLevel.ERROR,
                )

            if doc_id_found and not processing_options.reindex:
                self.tool.stream_log(f"File was indexed already under {doc_id}")
                return doc_id_found

        except Exception as e:
            self.tool.stream_log(
                f"Unexpected error during indexing check: {e}", level=LogLevel.ERROR
            )

        return doc_id_found

    @log_elapsed(operation="INDEX")
    @capture_metrics
    def perform_indexing(
        self,
        instance_identifiers: InstanceIdentifiers,
        chunking_config: ChunkingConfig,
        vector_db: VectorDB,
        doc_id: str,
        extracted_text: str,
        doc_id_found: bool,
    ):
        self._is_no_op_adapter(instance_identifiers, vector_db, doc_id)

        self.tool.stream_log("Indexing file...")
        full_text = [
            {
                "section": "full",
                "text_contents": extracted_text,
            }
        ]
        # Convert raw text to llama index usage Document
        documents = self._prepare_documents(doc_id, full_text)
        self._delete_existing_nodes_on_reindex(vector_db, doc_id, doc_id_found)
        self._trigger_indexing(chunking_config, vector_db, documents)
        return doc_id

    def _trigger_indexing(self, chunking_config, vector_db, documents):
        self.tool.stream_log("Adding nodes to vector db...")
        try:
            vector_db.index_document(
                documents,
                chunk_size=chunking_config.chunk_overlap,
                chunk_overlap=chunking_config.chunk_overlap,
                show_progress=True,
            )
            self.tool.stream_log("File has been indexed successfully")
        except Exception as e:
            self.tool.stream_log(
                f"Error adding nodes to vector db: {e}",
                level=LogLevel.ERROR,
            )
            raise IndexingError(str(e)) from e

    def _delete_existing_nodes_on_reindex(self, vector_db, doc_id, doc_id_found):
        if doc_id_found:
            # Delete the nodes for the doc_id
            try:
                vector_db.delete(ref_doc_id=doc_id)
                self.tool.stream_log(f"Deleted nodes for {doc_id}")
            except Exception as e:
                self.tool.stream_log(
                    f"Error deleting nodes for {doc_id}: {e}",
                    level=LogLevel.ERROR,
                )
                raise SdkError(f"Error deleting nodes for {doc_id}: {e}") from e

    def _prepare_documents(self, doc_id, full_text) -> list:
        documents = []
        for item in full_text:
            text = item["text_contents"]
            document = Document(
                text=text,
                doc_id=doc_id,
                metadata={"section": item["section"]},
            )
            document.id_ = doc_id
            documents.append(document)
        self.tool.stream_log(f"Number of documents: {len(documents)}")
        return documents

    def _is_no_op_adapter(
        self,
        instance_identifiers: InstanceIdentifiers,
        vector_db: VectorDB,
        doc_id: str,
    ):
        if isinstance(
            vector_db.get_vector_db(
                adapter_instance_id=instance_identifiers.vector_db_instance_id,
                embedding_dimension=1,
            ),
            (NoOpCustomVectorDB),
        ):
            return doc_id
