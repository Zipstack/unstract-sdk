from dataclasses import dataclass
from typing import Optional


@dataclass
class WhispererRequestParams:
    """DTO for LLM Whisperer API request parameters.

    Args:
        tag: Tag value. Can be initialized with List[str], str, or None.
             Will be converted to str | None after initialization.
    """

    # TODO: Extend this DTO to include all Whisperer API parameters
    tag: Optional[str] = None

    def __post_init__(self) -> None:
        # TODO: Allow list of tags once its supported in LLMW v2
        if isinstance(self.tag, list):
            self.tag = self.tag[0] if self.tag else None
