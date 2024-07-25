import logging
from abc import ABC, abstractmethod

from unstract.sdk.adapters.enums import AdapterTypes

logger = logging.getLogger(__name__)


class Adapter(ABC):
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    @abstractmethod
    def get_id() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_description() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_icon() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_json_schema() -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_adapter_type() -> AdapterTypes:
        return ""

    @abstractmethod
    def test_connection(self) -> bool:
        """Override to test connection for a adapter.

        Returns:
            bool: Flag indicating if the credentials are valid or not
        """
        pass
