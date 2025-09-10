import logging
from abc import ABC, abstractmethod

from unstract.sdk.adapters.enums import AdapterTypes
from unstract.sdk.adapters.exceptions import AdapterError
from unstract.sdk.adapters.url_validator import URLValidator

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

    @classmethod
    def get_json_schema(cls) -> str:
        schema_path = getattr(cls, "SCHEMA_PATH", None)
        if schema_path is None:
            raise ValueError(f"SCHEMA_PATH not defined for {cls.__name__}")
        with open(schema_path) as f:
            return f.read()

    @staticmethod
    @abstractmethod
    def get_adapter_type() -> AdapterTypes:
        return ""

    def get_configured_urls(self) -> list[str]:
        """Return all URLs that this adapter will connect to.

        This method should return a list of all URLs that the adapter
        uses for external connections. These URLs will be validated
        for security before allowing connection attempts.

        Returns:
            list[str]: List of URLs that will be accessed by this adapter
        """
        return []

    def _validate_urls(self) -> None:
        """Validate all configured URLs against security rules."""
        urls = self.get_configured_urls()

        for url in urls:
            if not url:  # Skip empty/None URLs
                continue

            is_valid, error_message = URLValidator.validate_url(url)
            if not is_valid:
                # Use class name as fallback when self.name isn't set yet
                adapter_name = getattr(self, "name", self.__class__.__name__)
                logger.error(
                    f"URL validation failed for adapter '{adapter_name}': {error_message}"
                )
                raise AdapterError(f"URL validation failed: {error_message}")

    @abstractmethod
    def test_connection(self) -> bool:
        """Override to test connection for a adapter.

        Returns:
            bool: Flag indicating if the credentials are valid or not
        """
        pass
