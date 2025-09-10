import ipaddress
import logging
import os
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class WhitelistEntry:
    """Represents a whitelisted endpoint with IP range and optional port."""

    ip_network: ipaddress.IPv4Network | ipaddress.IPv6Network
    port: int | None = None


class URLValidator:
    """Validates URLs to prevent SSRF attacks by blocking private IP addresses.

    URLs are validated to block private IP addresses unless explicitly
    whitelisted via ALLOWED_ADAPTER_PRIVATE_ENDPOINTS.
    """

    ENV_VAR = "ALLOWED_ADAPTER_PRIVATE_ENDPOINTS"

    # Private IP ranges that are blocked by default (RFC 1918 + others)
    BLOCKED_PRIVATE_RANGES = [
        "127.0.0.0/8",  # Localhost
        "10.0.0.0/8",  # Class A private
        "172.16.0.0/12",  # Class B private
        "192.168.0.0/16",  # Class C private
        "169.254.0.0/16",  # Link-local
        "0.0.0.0/8",  # Current network
        "224.0.0.0/4",  # Multicast
        "240.0.0.0/4",  # Reserved
        # IPv6 ranges
        "::1/128",  # IPv6 localhost
        "fc00::/7",  # IPv6 unique local
        "fe80::/10",  # IPv6 link-local
    ]

    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, str]:
        """Validates a URL against security rules.

        Args:
            url: The URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)

            if not parsed.hostname:
                return False, f"Invalid URL: No hostname found in '{url}'"

            # Resolve hostname to IP address
            try:
                host_ip = socket.gethostbyname(parsed.hostname)
            except socket.gaierror as e:
                return (
                    False,
                    f"DNS resolution failed for '{parsed.hostname}': {str(e)}",
                )

            # Check if IP is private
            ip_obj = ipaddress.ip_address(host_ip)
            if cls._is_private_ip(ip_obj):
                # Private IP - check whitelist
                port = parsed.port
                if cls._is_whitelisted(ip_obj, port):
                    logger.info(f"Private IP {host_ip}:{port} allowed by whitelist")
                    return True, ""
                else:
                    error_msg = (
                        f"URL blocked: Private IP {host_ip}"
                        f"{':' + str(port) if port else ''} not in whitelist. "
                        f"Contact platform admin for assistance."
                    )
                    return False, error_msg

            # Public IP - allowed by default
            return True, ""

        except Exception as e:
            logger.error(f"URL validation error for '{url}': {str(e)}")
            return False, f"{str(e)}"

    @classmethod
    def _is_private_ip(cls, ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        """Check if IP address is in private ranges."""
        for range_str in cls.BLOCKED_PRIVATE_RANGES:
            try:
                network = ipaddress.ip_network(range_str)
                if ip in network:
                    return True
            except ValueError:
                continue
        return False

    @classmethod
    def _is_whitelisted(
        cls, ip: ipaddress.IPv4Address | ipaddress.IPv6Address, port: int | None
    ) -> bool:
        """Check if IP:port combination is whitelisted."""
        whitelist = cls._parse_whitelist_config()

        for entry in whitelist:
            if ip in entry.ip_network:
                # IP matches - check port
                if entry.port is None or entry.port == port:
                    return True

        return False

    @classmethod
    def _parse_whitelist_config(cls) -> list[WhitelistEntry]:
        """Parse whitelist configuration from environment variable."""
        config = os.getenv(cls.ENV_VAR, "").strip()
        if not config:
            return []

        entries = []
        for item in config.split(","):
            item = item.strip()
            if not item:
                continue

            try:
                entry = cls._parse_whitelist_entry(item)
                if entry:
                    entries.append(entry)
            except Exception as e:
                logger.warning(f"Invalid whitelist entry '{item}': {str(e)}")

        return entries

    @classmethod
    def _parse_whitelist_entry(cls, entry: str) -> WhitelistEntry | None:
        """Parse a single whitelist entry in format 'IP:PORT' or
        'IP/CIDR:PORT'."""
        port = None
        ip_part = entry

        # Check if entry has port specification
        if ":" in entry:
            parts = entry.rsplit(":", 1)
            if len(parts) == 2 and parts[1].isdigit():
                ip_part = parts[0]
                port = int(parts[1])

        # Parse IP or CIDR
        try:
            if "/" in ip_part:
                # CIDR notation
                network = ipaddress.ip_network(ip_part, strict=False)
            else:
                # Single IP - convert to /32 or /128 network
                ip = ipaddress.ip_address(ip_part)
                if isinstance(ip, ipaddress.IPv4Address):
                    network = ipaddress.IPv4Network(f"{ip}/32")
                else:
                    network = ipaddress.IPv6Network(f"{ip}/128")

            return WhitelistEntry(ip_network=network, port=port)

        except ValueError as e:
            logger.warning(f"Invalid IP/CIDR in whitelist entry '{ip_part}': {str(e)}")
            return None
