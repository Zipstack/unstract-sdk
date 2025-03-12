import logging

from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from unstract.sdk.exceptions import RetrievalError
from unstract.sdk.retrieval.base_retriever import BaseRetriever
from unstract.sdk.vector_db import VectorDB

logger = logging.getLogger(__name__)


class SubquestionRetrieval(BaseRetriever):
    """SubquestionRetrieval class for querying VectorDB using LlamaIndex's
    SubQuestionQueryEngine."""

    def __init__(self, vector_db: VectorDB, prompt: str, doc_id: str, top_k: int):
        """Initialize the SubquestionRetrieval class.

        Args:
            vector_db (VectorDB): The vector database instance.
            prompt (str): The query prompt.
            doc_id (str): Document identifier for query context.
            top_k (int): Number of top results to retrieve.
        """
        self.vector_db = vector_db
        self.prompt = prompt
        self.doc_id = doc_id
        self.top_k = top_k

    def retrieve(self) -> set[str]:
        """Retrieve text chunks from the VectorDB based on the provided prompt.

        Returns:
            set[str]: A set of text chunks retrieved from the database.
        """
        try:
            vector_query_engine = (
                self.vector_db.get_vector_store_index().as_query_engine()
            )

            query_engine_tools = [
                QueryEngineTool(
                    query_engine=vector_query_engine,
                    metadata=ToolMetadata(name=self.doc_id),
                ),
            ]

            query_engine = SubQuestionQueryEngine.from_defaults(
                query_engine_tools=query_engine_tools,
                use_async=True,
            )

            response = query_engine.query(
                prompt=self.prompt,
                top_k=self.top_k,
                return_full_response=True,
            )

            chunks: set[str] = {node.text for node in response.source_nodes}
            logger.info(f"Successfully retrieved {len(chunks)} chunks.")
            return chunks

        except Exception as e:
            logger.error(f"Error during retrieving chunks {self.doc_id}: {e}")
            raise RetrievalError(str(e)) from e
