from .mistral import MistralLLM

metadata = {
    "name": MistralLLM.__name__,
    "version": "1.0.0",
    "adapter": MistralLLM,
    "description": "Mistral LLM adapter",
    "is_active": True,
}

__all__ = ["MistralLLM"]
