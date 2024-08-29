from .azure_open_ai import AzureOpenAILLM

metadata = {
    "name": AzureOpenAILLM.__name__,
    "version": "1.0.0",
    "adapter": AzureOpenAILLM,
    "description": "AzureOpenAI LLM adapter",
    "is_active": True,
}

__all__ = ["AzureOpenAILLM"]
