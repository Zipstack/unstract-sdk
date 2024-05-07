class SdkError(Exception):
    DEFAULT_MESSAGE = "Something went wrong"

    def __init__(self, message: str = DEFAULT_MESSAGE):
        super().__init__(message)
        # Make it user friendly wherever possible
        self.message = message

    def __str__(self) -> str:
        return self.message


class IndexingError(SdkError):
    def __init__(self, message: str = ""):
        if "404" in message:
            message = "Index not found. Please check vector db adapter settings."
        super().__init__(message)


class ToolLLMError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to LLM"


class ToolEmbeddingError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to embedding"


class ToolVectorDBError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to vector DB"


class RateLimitError(SdkError):
    DEFAULT_MESSAGE = "Running into rate limit errors, please try again later"
