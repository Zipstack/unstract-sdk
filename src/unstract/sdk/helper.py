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
