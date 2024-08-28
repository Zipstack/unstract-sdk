from .vertex_ai import VertexAILLM

metadata = {
    "name": VertexAILLM.__name__,
    "version": "1.0.0",
    "adapter": VertexAILLM,
    "description": "VertexAI LLM adapter",
    "is_active": True,
}

__all__ = ["VertexAILLM"]
