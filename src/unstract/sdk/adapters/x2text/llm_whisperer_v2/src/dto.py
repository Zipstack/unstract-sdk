from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtraParams:
    """DTO for extra parameters.

    Args:
        enable_highlight: Highlight enable flag
        tag: Tag value. Can be initialized with List[str], str, or None.
             Will be converted to str | None after initialization.
    """

    tag: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.tag, list):
            self.tag = self.tag[0] if self.tag else None
