class SdkError(Exception):
    DEFAULT_MESSAGE = "Something went wrong"

    def __init__(self, message: str = DEFAULT_MESSAGE):
        super().__init__(message)
        # Make it user friendly wherever possible
        self.message = message

    def __str__(self) -> str:
        return self.message
