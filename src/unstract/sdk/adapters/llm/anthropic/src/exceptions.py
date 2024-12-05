from typing import Any


class ErrorType:
    AUTH_ERR = "authentication_error"
    PERMISSION_ERR = "permission_error"
    NOT_FOUND_ERR = "not_found_error"
    API_ERR = "api_error"
    OVERLOADED_ERR = "overloaded_error"
    RATE_LIMIT_ERR = "rate_limit_error"
    LARGE_REQUEST_ERR = "request_too_large"


def parse_anthropic_err(err_body: dict[str, Any]) -> str:
    """Parses error from Anthropic.

    Refer https://docs.anthropic.com/en/api/errors#http-errors

    Args:
        err_body (dict[str, Any]): Error from Anthropic to parse

    Returns:
        str: Parsed error from Anthropic
    """
    err_type = err_body.get("type")
    msg: str

    if err_type == ErrorType.AUTH_ERR:
        msg = "Authentication error, please check the provided API key"
    elif err_type == ErrorType.PERMISSION_ERR:
        msg = "Your API key does not have permission to use the specified resource"
    elif err_type == ErrorType.NOT_FOUND_ERR:
        err_msg = err_body.get("message")
        msg = f"The requested resource was not found, '{err_msg}'"
    elif err_type == ErrorType.RATE_LIMIT_ERR:
        msg = (
            "Your Anthropic account has hit a rate limit, "
            "please try again after some time"
        )
    elif err_type == ErrorType.LARGE_REQUEST_ERR:
        err_msg = err_body.get("message")
        msg = (
            f"Request exceeded the maximum allowed number of bytes, '{err_msg}'. "
            "Try reducing the number of prompts or reduce the context size by chunking."
        )
    elif err_type == ErrorType.API_ERR:
        msg = "An unexpected error has occurred internal to Anthropic's systems"
    elif err_type == ErrorType.OVERLOADED_ERR:
        msg = (
            "Anthropic's API is temporarily overloaded, please "
            "try again after some time"
        )
    else:
        msg = err_body.get("message", "Anthropic error")
    return msg
