from .palm import PaLMLLM

metadata = {
    "name": PaLMLLM.__name__,
    "version": "1.0.0",
    "adapter": PaLMLLM,
    "description": "Palm LLM adapter",
    "is_active": True,
}

__all__ = ["PaLMLLM"]
