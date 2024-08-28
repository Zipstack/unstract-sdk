from .anyscale import AnyScaleLLM

metadata = {
    "name": AnyScaleLLM.__name__,
    "version": "1.0.0",
    "adapter": AnyScaleLLM,
    "description": "AnyScale LLM adapter",
    "is_active": True,
}

__all__ = ["AnyScaleLLM"]
