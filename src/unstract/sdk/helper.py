from unstract.sdk.constants import PublicAdapterKeys


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
            bool: True if the adapter_id matches any public adapter key, False otherwise.
        """
        try:
            # Retrieve all attribute names from the PublicAdapterKeys class
            attributes = dir(PublicAdapterKeys)
            public_adapter_keys = {getattr(PublicAdapterKeys, attr) for attr in attributes}
            return adapter_id in public_adapter_keys
        except Exception:
            return False
