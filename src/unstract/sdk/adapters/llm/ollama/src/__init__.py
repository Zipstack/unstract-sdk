from .ollama import OllamaLLM

metadata = {
    "name": OllamaLLM.__name__,
    "version": "1.0.0",
    "adapter": OllamaLLM,
    "description": "Ollama LLM adapter",
    "is_active": True,
}

__all__ = ["OllamaLLM"]
