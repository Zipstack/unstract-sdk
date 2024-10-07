from .replicate import ReplicateLLM

metadata = {
    "name": ReplicateLLM.__name__,
    "version": "1.0.0",
    "adapter": ReplicateLLM,
    "description": "Replicate LLM adapter",
    "is_active": True,
}

__all__ = ["ReplicateLLM"]
