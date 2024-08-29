from .anthropic import AnthropicLLM

metadata = {
    "name": AnthropicLLM.__name__,
    "version": "1.0.0",
    "adapter": AnthropicLLM,
    "description": "Anthropic LLM adapter",
    "is_active": True,
}

__all__ = ["AnthropicLLM"]
