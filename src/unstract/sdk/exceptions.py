from typing import Any, Optional


class SdkException(Exception):
    def __init__(
        self, *args: Any, user_message: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self._user_message = user_message

    @property
    def user_message(self) -> Optional[str]:
        return self._user_message
