__version__ = "0.40.8"

import sys

from unstract.sdk.llm import LLM

sys.modules['unstract.sdk.llm'] = LLM
def get_sdk_version():
    """Returns the SDK version."""

    return __version__