import logging

from unstract.sdk.constants import PublicAdapterKeys

logger = logging.getLogger(__name__)

class SdkHelper:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_platform_base_url(platform_host: str, platform_port: str) -> str:
        """Make base url from host and port.

        Args:
            platform_host (str): Host of platform service
            platform_port (str): Port of platform service

        Returns:
            str: URL to the platform service
        """
        if platform_host[-1] == "/":
            return f"{platform_host[:-1]}:{platform_port}"
        return f"{platform_host}:{platform_port}"

    @staticmethod
    def is_public_adapter(adapter_id: str) -> bool:
        """Check if the given adapter_id is one of the public adapter keys.

        This method iterates over the attributes of the PublicAdapterKeys class
        and checks if the provided adapter_id matches any of the attribute values.

        Args:
            adapter_id (str): The ID of the adapter to check.

        Returns:
            bool: True if the adapter_id matches any public adapter key,
            False otherwise.
        """
        try:
            for attr in dir(PublicAdapterKeys):
                if getattr(PublicAdapterKeys, attr) == adapter_id:
                    return True
            return False
        except Exception as e:
            logger.warning(
                f"Unable to determine if adapter_id: {adapter_id}"
                f"is public or not: {str(e)}"
            )
            return False
