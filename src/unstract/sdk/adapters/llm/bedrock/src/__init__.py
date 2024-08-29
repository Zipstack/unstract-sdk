from .bedrock import BedrockLLM

metadata = {
    "name": BedrockLLM.__name__,
    "version": "1.0.0",
    "adapter": BedrockLLM,
    "description": "Bedrock LLM adapter",
    "is_active": True,
}

__all__ = ["BedrockLLM"]
