from .open_ai import OpenAILLM

metadata = {
    "name": OpenAILLM.__name__,
    "version": "1.0.0",
    "adapter": OpenAILLM,
    "description": "OpenAI LLM adapter",
    "is_active": True,
}

__all__ = ["OpenAILLM"]
