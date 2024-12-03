from typing import Optional


def resolve_err_status_code(client_status_code: int) -> int:
    """Resolves the status code to return in case of errors.

    Returns a status code which should be returned from Unstract based on
    the status code from the client.

    - 502 is returned for 500 client errors
    - 4xx is returned for 4xx client errors

    Args:
        client_status_code (int): Status code from client library

    Returns:
        int: Status code that Unstract should return
    """
    if client_status_code == 500:
        return 502

    # 4xx status codes returned as is
    return client_status_code


class SdkError(Exception):
    DEFAULT_MESSAGE = "Something went wrong"
    actual_err: Optional[Exception] = None
    status_code: Optional[int] = None

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        status_code: Optional[int] = None,
        actual_err: Optional[Exception] = None,
    ):
        super().__init__(message)
        # Make it user friendly wherever possible
        self.message = message
        if actual_err:
            self.actual_err = actual_err

        # Setting status code for error
        if status_code:
            self.status_code = status_code
        elif actual_err:
            if hasattr(actual_err, "status_code"):  # Most providers
                self.status_code = resolve_err_status_code(actual_err.status_code)
            elif hasattr(actual_err, "http_status"):  # Few providers like Mistral
                self.status_code = resolve_err_status_code(actual_err.http_status)

    def __str__(self) -> str:
        return self.message


class IndexingError(SdkError):
    def __init__(self, message: str = "", **kwargs):
        if "404" in message:
            message = "Index not found. Please check vector DB settings."
        super().__init__(message, **kwargs)


class LLMError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to LLM"


class EmbeddingError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to embedding"


class VectorDBError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to vector DB"


class X2TextError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to text extractor"


class OCRError(SdkError):
    DEFAULT_MESSAGE = "Error ocurred related to OCR"


class RateLimitError(SdkError):
    DEFAULT_MESSAGE = "Running into rate limit errors, please try again later"


class FileStorageError(SdkError):
    DEFAULT_MESSAGE = (
        "Error while connecting with the storage. "
        "Please check the configuration credentials"
    )


class FileOperationError(SdkError):
    DEFAULT_MESSAGE = (
        "Error while performing operation on the file. "
        "Please check specific storage error for "
        "further information"
    )
