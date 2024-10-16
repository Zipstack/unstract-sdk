from .no_op_llm_adapter import NoOpLLMAdapter

metadata = {
    "name": NoOpLLMAdapter.__name__,
    "version": "1.0.0",
    "adapter": NoOpLLMAdapter,
    "description": "NoOp LLM adapter",
    "is_active": True,
}

__all__ = ["NoOpLLM"]
