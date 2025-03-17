import logging
import time

from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

from unstract.sdk.retrieval.base_retriever import BaseRetriever
from unstract.sdk.vector_db import VectorDB

logger = logging.getLogger(__name__)


class SimpleRetriever(BaseRetriever):
    def retrieve(self) -> set[str]:
        vector_query_engine: VectorStoreIndex = self.vector_db.get_vector_store_index()
        retriever = vector_query_engine.as_retriever(
            similarity_top_k=self.top_k,
            filters=MetadataFilters(
                filters=[
                    ExactMatchFilter(key="doc_id", value=self.doc_id),
                ],
            ),
        )
        nodes = retriever.retrieve(self.prompt)
        context: set[str] = set()
        for node in nodes:
            # ToDo: May have to fine-tune this value for node score or keep it
            # configurable at the adapter level
            if node.score > 0:
                context.add(node.get_content())
            else:
                logger.info(
                    "Node score is less than 0. "
                    f"Ignored: {node.node_id} with score {node.score}"
                )

        if not context:
            # UN-1288 For Pinecone, we are seeing an inconsistent case where
            # query with doc_id fails even though indexing just happened.
            # This causes the following retrieve to return no text.
            # To rule out any lag on the Pinecone vector DB write,
            # the following sleep is added
            # Note: This will not fix the issue. Since this issue is inconsistent
            # and not reproducible easily, this is just a safety net.
            time.sleep(2)
            context = self.retrieve(self.prompt, self.doc_id, self.top_k)
        return context
