from unstract.sdk.vector_db import VectorDB


class BaseRetriever:
    def __init__(self, vector_db: VectorDB, prompt: str, doc_id: str, top_k: int):
        self.vector_db = vector_db
        self.prompt = prompt
        self.doc_id = doc_id
        self.top_k = top_k

    @staticmethod
    def retrieve() -> set[str]:
        return set()
