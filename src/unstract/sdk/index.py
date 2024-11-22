import json
import logging
from typing import Any, Callable, Optional

from deprecated import deprecated
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
    VectorStoreQuery,
    VectorStoreQueryResult,
)

from unstract.sdk.adapter import ToolAdapter
from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.vectordb.no_op.src.no_op_custom_vectordb import (
    NoOpCustomVectorDB,
)
from unstract.sdk.adapters.x2text.constants import X2TextConstants
from unstract.sdk.adapters.x2text.dto import TextExtractionResult
from unstract.sdk.adapters.x2text.llm_whisperer.src import LLMWhisperer
from unstract.sdk.constants import LogLevel
from unstract.sdk.embedding import Embedding
from unstract.sdk.exceptions import IndexingError, SdkError
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils import ToolUtils
from unstract.sdk.utils.common_utils import log_elapsed
from unstract.sdk.vector_db import VectorDB
from unstract.sdk.x2txt import X2Text

logger = logging.getLogger(__name__)


class Constants:
    TOP_K = 5


class Index:
    def __init__(self, tool: BaseTool):
        # TODO: Inherit from StreamMixin and avoid using BaseTool
        self.tool = tool

    def query_index(
        self,
        embedding_instance_id: str,
        vector_db_instance_id: str,
        doc_id: str,
        usage_kwargs: dict[Any, Any] = {},
    ):
        try:
            embedding = Embedding(
                tool=self.tool,
                adapter_instance_id=embedding_instance_id,
                usage_kwargs=usage_kwargs,
            )
        except SdkError as e:
            self.tool.stream_log(embedding_instance_id)
            raise SdkError(f"Error loading {embedding_instance_id}: {e}")

        try:
            vector_db = VectorDB(
                tool=self.tool,
                adapter_instance_id=vector_db_instance_id,
                embedding=embedding,
            )

        except SdkError as e:
            self.tool.stream_log(
                f"Error loading {vector_db_instance_id}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {vector_db_instance_id}: {e}")
        try:
            try:
                self.tool.stream_log(f">>> Querying {vector_db_instance_id}...")
                self.tool.stream_log(f">>> {doc_id}")
                doc_id_eq_filter = MetadataFilter.from_dict(
                    {
                        "key": "doc_id",
                        "operator": FilterOperator.EQ,
                        "value": doc_id,
                    }
                )
                filters = MetadataFilters(filters=[doc_id_eq_filter])
                q = VectorStoreQuery(
                    query_embedding=embedding.get_query_embedding(" "),
                    doc_ids=[doc_id],
                    filters=filters,
                    similarity_top_k=Constants.TOP_K,
                )
            except Exception as e:
                self.tool.stream_log(
                    f"Error building query {vector_db}: {e}", level=LogLevel.ERROR
                )
                raise SdkError(f"Error building query {vector_db}: {e}")

            n: VectorStoreQueryResult = vector_db.query(query=q)
            if len(n.nodes) > 0:
                self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
                all_text = ""
                for node in n.nodes:
                    all_text += node.get_content()
                return all_text
            else:
                self.tool.stream_log(f"No nodes found for {doc_id}")
                return None
        finally:
            vector_db.close()

    @log_elapsed(operation="EXTRACTION")
    def extract_text(
        self,
        x2text_instance_id: str,
        file_path: str,
        output_file_path: Optional[str] = None,
        enable_highlight: bool = False,
        usage_kwargs: dict[Any, Any] = {},
        process_text: Optional[Callable[[str], str]] = None,
    ) -> str:
        """Extracts text from a document.

        Uses the configured service to perform the extraction
        - LLM Whisperer
        - Unstructured IO Community / Enterprise
        - Llama Parse

        Args:
            x2text_instance_id (str): UUID of the text extractor
            file_path (str): Path to the file
            output_file_path (Optional[str], optional): File path to write
                the extracted contents into. Defaults to None.
            enable_highlight (bool, optional): Flag to provide highlighting metadata.
                Defaults to False.
            usage_kwargs (dict[Any, Any], optional): Dict to capture usage.
                Defaults to {}.
            process_text (Optional[Callable[[str], str]], optional): Optional function
                to post-process the text. Defaults to None.

        Raises:
            IndexingError: Errors during text extraction
        """
        self.tool.stream_log("Extracting text from input file")
        extracted_text = ""
        try:
            x2text = X2Text(
                tool=self.tool,
                adapter_instance_id=x2text_instance_id,
                usage_kwargs=usage_kwargs,
            )
            if enable_highlight and isinstance(x2text._x2text_instance, LLMWhisperer):
                process_response: TextExtractionResult = x2text.process(
                    input_file_path=file_path,
                    output_file_path=output_file_path,
                    enable_highlight=enable_highlight,
                )
                whisper_hash_value = process_response.extraction_metadata.whisper_hash

                metadata = {X2TextConstants.WHISPER_HASH: whisper_hash_value}

                self.tool.update_exec_metadata(metadata)

            else:
                process_response: TextExtractionResult = x2text.process(
                    input_file_path=file_path,
                    output_file_path=output_file_path,
                )

            extracted_text = process_response.extracted_text
        except AdapterError as e:
            # Wrapping AdapterErrors with SdkError
            raise IndexingError(str(e)) from e
        if process_text:
            try:
                result = process_text(extracted_text)
                if isinstance(result, str):
                    extracted_text = result
                else:
                    logger.warning("'process_text' is expected to return an 'str'")
            except Exception as e:
                logger.error(f"Error occured inside function 'process_text': {e}")
        return extracted_text

    @log_elapsed(operation="CHECK_AND_INDEX(overall)")
    def index(
        self,
        tool_id: str,
        embedding_instance_id: str,
        vector_db_instance_id: str,
        x2text_instance_id: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
        reindex: bool = False,
        file_hash: Optional[str] = None,
        output_file_path: Optional[str] = None,
        enable_highlight: bool = False,
        usage_kwargs: dict[Any, Any] = {},
        process_text: Optional[Callable[[str], str]] = None,
    ) -> str:
        """Indexes an individual file using the passed arguments.

        Args:
            tool_id (str): UUID of the tool (workflow_id in case it's called
                from workflow)
            embedding_instance_id (str): UUID of the embedding service configured
            vector_db_instance_id (str): UUID of the vector DB configured
            x2text_instance_id (str): UUID of the x2text adapter configured.
                This is to extract text from documents.
            file_path (str): Path to the file that needs to be indexed.
            chunk_size (int): Chunk size to be used for indexing
            chunk_overlap (int): Overlap in chunks to be used for indexing
            reindex (bool, optional): Flag to denote if document should be
                re-indexed if its already indexed. Defaults to False.
            file_hash (Optional[str], optional): SHA256 hash of the file.
                Defaults to None. If None, the hash is generated.
            output_file_path (Optional[str], optional): File path to write
                the extracted contents into. Defaults to None.

        Returns:
            str: A unique ID for the file and indexing arguments combination
        """
        doc_id = self.generate_index_key(
            vector_db=vector_db_instance_id,
            embedding=embedding_instance_id,
            x2text=x2text_instance_id,
            chunk_size=str(chunk_size),
            chunk_overlap=str(chunk_overlap),
            file_path=file_path,
            file_hash=file_hash,
        )
        self.tool.stream_log(f"Checking if doc_id {doc_id} exists")

        try:
            embedding = Embedding(
                tool=self.tool,
                adapter_instance_id=embedding_instance_id,
                usage_kwargs=usage_kwargs,
            )
        except SdkError as e:
            self.tool.stream_log(
                f"Error loading {embedding_instance_id}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {embedding_instance_id}: {e}")

        try:
            vector_db = VectorDB(
                tool=self.tool,
                adapter_instance_id=vector_db_instance_id,
                embedding=embedding,
            )
        except SdkError as e:
            self.tool.stream_log(
                f"Error loading {vector_db_instance_id}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {vector_db_instance_id}: {e}")

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
                    f"Error querying {vector_db_instance_id}: {e}, proceeding to index",
                    level=LogLevel.ERROR,
                )

            if doc_id_found and not reindex:
                self.tool.stream_log(f"File was indexed already under {doc_id}")
                return doc_id

            extracted_text = self.extract_text(
                x2text_instance_id=x2text_instance_id,
                file_path=file_path,
                output_file_path=output_file_path,
                enable_highlight=enable_highlight,
                usage_kwargs=usage_kwargs,
                process_text=process_text,
            )

            if not extracted_text:
                raise IndexingError("No text available to index")

            # For No-op adapters, addition of nodes to vectorDB should not happen
            # and this has to be handled in the adapter level. But there are a
            # few challenges considering callback manager and upstream Llama index
            # method invocations. Hence, making this check here and returning
            # the doc id to maintain the legacy flow of adapters.

            if isinstance(
                vector_db.get_vector_db(
                    adapter_instance_id=vector_db_instance_id, embedding_dimension=1
                ),
                (NoOpCustomVectorDB),
            ):
                return doc_id

            self.index_to_vector_db(
                vector_db=vector_db,
                embedding=embedding,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                doc_id=doc_id,
                text_to_idx=extracted_text,
                doc_id_found=doc_id_found,
            )
            return doc_id
        finally:
            vector_db.close()

    @log_elapsed(operation="INDEXING")
    def index_to_vector_db(
        self,
        vector_db: VectorDB,
        embedding: Embedding,
        chunk_size: int,
        chunk_overlap: int,
        text_to_idx: str,
        doc_id: str,
        doc_id_found: bool,
    ):
        self.tool.stream_log("Indexing file...")
        full_text = [
            {
                "section": "full",
                "text_contents": text_to_idx,
            }
        ]
        # Check if chunking is required
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

        try:
            if chunk_size == 0:
                parser = SentenceSplitter.from_defaults(
                    chunk_size=len(documents[0].text) + 10,
                    chunk_overlap=0,
                    callback_manager=embedding.get_callback_manager(),
                )
                nodes = parser.get_nodes_from_documents(documents, show_progress=True)
                node = nodes[0]
                node.embedding = embedding.get_query_embedding(" ")
                vector_db.add(doc_id, nodes=[node])
                self.tool.stream_log("Added node to vector db")
            else:
                self.tool.stream_log("Adding nodes to vector db...")
                # TODO: Phase 2:
                # Post insertion to VDB, use query using doc_id and
                # store all the VDB ids to a table against the doc_id
                # During deletion for cases where metadata filtering
                # does not work, these ids can be used for direct deletion
                # This new table will also act like an audit trail for
                # all nodes that were added to the VDB by Unstract
                # Once this is in place, the overridden implementation
                # of prefixing ids with doc_id before adding to VDB
                # can be removed
                vector_db.index_document(
                    documents,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    show_progress=True,
                )
        except Exception as e:
            self.tool.stream_log(
                f"Error adding nodes to vector db: {e}",
                level=LogLevel.ERROR,
            )
            raise IndexingError(str(e)) from e

        self.tool.stream_log("File has been indexed successfully")
        return

    def generate_index_key(
        self,
        vector_db: str,
        embedding: str,
        x2text: str,
        chunk_size: str,
        chunk_overlap: str,
        file_path: Optional[str] = None,
        file_hash: Optional[str] = None,
    ) -> str:
        """Generates a unique ID useful for identifying files during indexing.

        Args:
            vector_db (str): UUID of the vector DB adapter
            embedding (str): UUID of the embedding adapter
            x2text (str): UUID of the X2Text adapter
            chunk_size (str): Chunk size for indexing
            chunk_overlap (str): Chunk overlap for indexing
            file_path (Optional[str]): Path to the file that needs to be indexed.
                Defaults to None. One of file_path or file_hash needs to be specified.
            file_hash (Optional[str], optional): SHA256 hash of the file.
                Defaults to None. If None, the hash is generated with file_path.

        Returns:
            str: Key representing unique ID for a file
        """
        if not file_path and not file_hash:
            raise ValueError("One of `file_path` or `file_hash` need to be provided")

        if not file_hash:
            file_hash = ToolUtils.get_hash_from_file(file_path=file_path)

        # Whole adapter config is used currently even though it contains some keys
        # which might not be relevant to indexing. This is easier for now than
        # marking certain keys of the adapter config as necessary.
        index_key = {
            "file_hash": file_hash,
            "vector_db_config": ToolAdapter.get_adapter_config(self.tool, vector_db),
            "embedding_config": ToolAdapter.get_adapter_config(self.tool, embedding),
            "x2text_config": ToolAdapter.get_adapter_config(self.tool, x2text),
            # Typed and hashed as strings since the final hash is persisted
            # and this is required to be backward compatible
            "chunk_size": str(chunk_size),
            "chunk_overlap": str(chunk_overlap),
        }
        # JSON keys are sorted to ensure that the same key gets hashed even in
        # case where the fields are reordered.
        hashed_index_key = ToolUtils.hash_str(json.dumps(index_key, sort_keys=True))
        return hashed_index_key

    @deprecated(version="0.45.0", reason="Use generate_index_key() instead")
    def generate_file_id(
        self,
        tool_id: str,
        vector_db: str,
        embedding: str,
        x2text: str,
        chunk_size: str,
        chunk_overlap: str,
        file_path: Optional[str] = None,
        file_hash: Optional[str] = None,
    ) -> str:
        return self.generate_index_key(
            vector_db,
            embedding,
            x2text,
            chunk_size,
            chunk_overlap,
            file_path,
            file_hash,
        )

    def index_file(
        self,
        tool_id: str,
        embedding_type: str,
        vector_db: str,
        x2text_adapter: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
        reindex: bool = False,
        file_hash: Optional[str] = None,
        output_file_path: Optional[str] = None,
    ) -> str:
        return self.index(
            tool_id=tool_id,
            embedding_instance_id=embedding_type,
            vector_db_instance_id=vector_db,
            x2text_instance_id=x2text_adapter,
            file_path=file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            reindex=reindex,
            file_hash=file_hash,
            output_file_path=output_file_path,
        )

    @deprecated("Deprecated class and method. Use Index and query_index() instead")
    def get_text_from_index(
        self, embedding_type: str, vector_db: str, doc_id: str
    ) -> Optional[str]:
        return self.query_index(
            embedding_instance_id=embedding_type,
            vector_db_instance_id=vector_db,
            doc_id=doc_id,
        )


# Legacy
ToolIndex = Index
