from unstract.sdk.exceptions import SdkError


# TODO: Remove redundant AdapterError classes and use SdkError itself
class AdapterError(SdkError):
    pass


class LLMError(AdapterError):
    pass


class ExtractorError(AdapterError):
    pass
