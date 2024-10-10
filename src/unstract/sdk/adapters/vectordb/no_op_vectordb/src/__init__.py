from .no_op_vectordb_adapter import NoOpVectorDBAdapter

metadata = {
    "name": NoOpVectorDBAdapter.__name__,
    "version": "1.0.0",
    "adapter": NoOpVectorDBAdapter,
    "description": "NoOpVectorDBAdapter",
    "is_active": True,
}
