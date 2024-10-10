from typing import Any

from llama_index.core import MockEmbedding


class NoOpEmbedding(MockEmbedding):

    embed_dim: int

    def __init__(self, embed_dim: int, wait_time: int, **kwargs: Any) -> None:
        """Init params."""
        super().__init__(embed_dim=embed_dim, **kwargs, wait_time=wait_time)
