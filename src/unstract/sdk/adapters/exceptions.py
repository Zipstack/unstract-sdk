from unstract.sdk.exceptions import SdkError


class AdapterError(SdkError):
    pass


class LLMError(AdapterError):
    pass


class VectorDBError(AdapterError):
    pass


class EmbeddingError(AdapterError):
    pass


class ExtractorError(AdapterError):
    pass
