from typing import Optional

from llama_index import Document, StorageContext, VectorStoreIndex
from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import VectorStoreQuery, VectorStoreQueryResult
from unstract.adapters.exceptions import AdapterError
from unstract.adapters.x2text.x2text_adapter import X2TextAdapter

from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.embedding import ToolEmbedding
from unstract.sdk.exceptions import SdkError
from unstract.sdk.tool.base import BaseTool
from unstract.sdk.utils import ToolUtils
from unstract.sdk.utils.service_context import ServiceContext
from unstract.sdk.vector_db import ToolVectorDB
from unstract.sdk.x2txt import X2Text


class ToolIndex:
    def __init__(self, tool: BaseTool):
        # TODO: Inherit from StreamMixin and avoid using BaseTool
        self.tool = tool

    def get_text_from_index(
        self, embedding_type: str, vector_db: str, doc_id: str
    ):
        embedd_helper = ToolEmbedding(tool=self.tool)
        embedding_li = embedd_helper.get_embedding(
            adapter_instance_id=embedding_type
        )
        if embedding_li is None:
            self.tool.stream_log(
                f"Error loading {embedding_type}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {embedding_type}")
        embedding_dimension = embedd_helper.get_embedding_length(embedding_li)

        vdb_helper = ToolVectorDB(
            tool=self.tool,
        )
        vector_db_li = vdb_helper.get_vector_db(
            adapter_instance_id=vector_db,
            embedding_dimension=embedding_dimension,
        )

        if vector_db_li is None:
            self.tool.stream_log(
                f"Error loading {vector_db}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {vector_db}")

        try:
            self.tool.stream_log(f">>> Querying {vector_db}...")
            self.tool.stream_log(f">>> {doc_id}")
            q = VectorStoreQuery(
                query_embedding=embedding_li.get_query_embedding(" "),
                doc_ids=[doc_id],
                similarity_top_k=10000,
            )
        except Exception as e:
            self.tool.stream_log(
                f"Error querying {vector_db}: {e}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error querying {vector_db}: {e}")

        n: VectorStoreQueryResult = vector_db_li.query(query=q)
        if len(n.nodes) > 0:
            self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
            all_text = ""
            for node in n.nodes:
                all_text += node.get_content()
            return all_text
        else:
            self.tool.stream_log(f"No nodes found for {doc_id}")
            return None

    def _cleanup_text(self, full_text):
        # Remove text which is not requried
        full_text_lines = full_text.split("\n")
        new_context_lines = []
        empty_line_count = 0
        for line in full_text_lines:
            if line.strip() == "":
                empty_line_count += 1
            else:
                if empty_line_count >= 3:
                    empty_line_count = 3
                for i in range(empty_line_count):
                    new_context_lines.append("")
                empty_line_count = 0
                new_context_lines.append(line.rstrip())
        self.tool.stream_log(
            f"Old context length: {len(full_text_lines)}, "
            f"New context length: {len(new_context_lines)}"
        )
        return "\n".join(new_context_lines)

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
        """Indexes an individual file using the passed arguments.

        Args:
            tool_id (str): UUID of the tool (workflow_id in case its called
                from workflow)
            embedding_type (str): UUID of the embedding service configured
            vector_db (str): UUID of the vector DB configured
            x2text_adapter (str): UUID of the x2text adapter configured.
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
        # Make file content hash if not available
        if not file_hash:
            file_hash = ToolUtils.get_hash_from_file(file_path=file_path)

        doc_id = ToolIndex.generate_file_id(
            tool_id=tool_id,
            file_hash=file_hash,
            vector_db=vector_db,
            embedding=embedding_type,
            x2text=x2text_adapter,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        self.tool.stream_log(f"Checking if doc_id {doc_id} exists")

        vdb_helper = ToolVectorDB(
            tool=self.tool,
        )

        embedd_helper = ToolEmbedding(tool=self.tool)

        embedding_li = embedd_helper.get_embedding(
            adapter_instance_id=embedding_type
        )
        if embedding_li is None:
            self.tool.stream_log(
                f"Error loading {embedding_type}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {embedding_type}")

        embedding_dimension = embedd_helper.get_embedding_length(embedding_li)
        vector_db_li = vdb_helper.get_vector_db(
            adapter_instance_id=vector_db,
            embedding_dimension=embedding_dimension,
        )
        if vector_db_li is None:
            self.tool.stream_log(
                f"Error loading {vector_db}", level=LogLevel.ERROR
            )
            raise SdkError(f"Error loading {vector_db}")

        filter = [{"field_name": "doc_id", "operator": "=", "value": doc_id}]
        q = VectorStoreQuery(
            query_embedding=embedding_li.get_query_embedding(" "),
            doc_ids=[doc_id],
            filters=filter,
        )

        doc_id_not_found = True
        try:
            n: VectorStoreQueryResult = vector_db_li.query(query=q)
            if len(n.nodes) > 0:
                doc_id_not_found = False
                self.tool.stream_log(f"Found {len(n.nodes)} nodes for {doc_id}")
            else:
                self.tool.stream_log(f"No nodes found for {doc_id}")
        except Exception as e:
            self.tool.stream_log(
                f"Error querying {vector_db}: {e}", level=LogLevel.ERROR
            )

        if doc_id_not_found is False and reindex:
            # Delete the nodes for the doc_id
            try:
                vector_db_li.delete(ref_doc_id=doc_id)
                self.tool.stream_log(f"Deleted nodes for {doc_id}")
            except Exception as e:
                self.tool.stream_log(
                    f"Error deleting nodes for {doc_id}: {e}",
                    level=LogLevel.ERROR,
                )
                raise SdkError(f"Error deleting nodes for {doc_id}: {e}")
            doc_id_not_found = True

        if doc_id_not_found:
            self.tool.stream_log("Extracting text from input file")
            full_text = []
            extracted_text = ""
            try:
                x2text = X2Text(tool=self.tool)
                x2text_adapter_inst: X2TextAdapter = x2text.get_x2text(
                    adapter_instance_id=x2text_adapter
                )
                extracted_text = x2text_adapter_inst.process(
                    input_file_path=file_path, output_file_path=output_file_path
                )
            except AdapterError as e:
                # Wrapping AdapterErrors with SdkError
                raise SdkError(str(e)) from e
            full_text.append(
                {
                    "section": "full",
                    "text_contents": self._cleanup_text(extracted_text),
                }
            )

            # Check if chunking is required
            documents = []
            for item in full_text:
                text = item["text_contents"]
                self.tool.stream_log("Indexing file...")
                document = Document(
                    text=text,
                    doc_id=doc_id,
                    metadata={"section": item["section"]},
                )
                document.id_ = doc_id
                documents.append(document)
            self.tool.stream_log(f"Number of documents: {len(documents)}")
            if chunk_size == 0:
                parser = SimpleNodeParser.from_defaults(
                    chunk_size=len(documents[0].text) + 10, chunk_overlap=0
                )
                nodes = parser.get_nodes_from_documents(
                    documents, show_progress=True
                )
                node = nodes[0]
                node.embedding = embedding_li.get_query_embedding(" ")
                vector_db_li.add(nodes=[node])
                self.tool.stream_log("Added node to vector db")
            else:
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_db_li
                )
                parser = SimpleNodeParser.from_defaults(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )

                service_context = ServiceContext.get_service_context(
                    platform_api_key=self.tool.get_env_or_die(
                        ToolEnv.PLATFORM_API_KEY
                    ),
                    embed_model=embedding_li,
                    node_parser=parser,
                )

                self.tool.stream_log("Adding nodes to vector db...")
                try:
                    VectorStoreIndex.from_documents(
                        documents,
                        storage_context=storage_context,
                        show_progress=True,
                        service_context=service_context,
                    )
                except Exception as e:
                    self.tool.stream_log(
                        f"Error adding nodes to vector db: {e}",
                        level=LogLevel.ERROR,
                    )
                    raise SdkError(f"Error adding nodes to vector db: {e}")
                self.tool.stream_log("Added nodes to vector db")

            self.tool.stream_log("File has been indexed successfully")
        return doc_id

    @staticmethod
    def generate_file_id(
        tool_id: str,
        file_hash: str,
        vector_db: str,
        embedding: str,
        x2text: str,
        chunk_size: str,
        chunk_overlap: str,
    ) -> str:
        """Generates a unique ID useful for identifying files during indexing.

        Args:
            tool_id (str): Unique ID of the tool developed / exported
            file_hash (str): Hash of the file contents
            vector_db (str): UUID of the vector DB adapter
            embedding (str): UUID of the embedding adapter
            x2text (str): UUID of the X2Text adapter
            chunk_size (str): Chunk size for indexing
            chunk_overlap (str): Chunk overlap for indexing

        Returns:
            str: Key representing unique ID for a file
        """
        return (
            f"{tool_id}|{vector_db}|{embedding}|{x2text}|"
            f"{chunk_size}|{chunk_overlap}|{file_hash}"
        )
