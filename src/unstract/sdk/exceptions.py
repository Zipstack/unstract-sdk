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
