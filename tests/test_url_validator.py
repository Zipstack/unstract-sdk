import os
import unittest
from unittest.mock import patch

from unstract.sdk.adapters.url_validator import URLValidator


class TestURLValidator(unittest.TestCase):
    """Test cases for URL validation functionality."""

    def setUp(self):
        """Set up test environment."""
        # Clear any existing environment variables
        if URLValidator.ENV_VAR in os.environ:
            del os.environ[URLValidator.ENV_VAR]

    def tearDown(self):
        """Clean up after tests."""
        # Clear environment variables
        if URLValidator.ENV_VAR in os.environ:
            del os.environ[URLValidator.ENV_VAR]

    @patch("socket.gethostbyname", return_value="1.1.1.1")
    def test_public_urls_allowed(self, _):
        """Test that public URLs are allowed by default."""
        test_cases = [
            "https://api.openai.com/v1/chat/completions",
            "https://google.com",
            "http://example.com",
            "https://1.1.1.1:8080",  # Public IP with port
        ]

        for url in test_cases:
            with self.subTest(url=url):
                is_valid, error = URLValidator.validate_url(url)
                self.assertTrue(
                    is_valid, f"Public URL should be valid: {url}, Error: {error}"
                )
    @patch("socket.gethostbyname")
    def test_private_ips_blocked_by_default(self, mock_gethostbyname):
        """Test that private IPs are blocked when not whitelisted."""
        test_cases = [
            ("https://192.168.1.100", "192.168.1.100"),  # Private class C
            ("https://10.0.0.5:8080", "10.0.0.5"),  # Private class A with port
            ("https://172.16.5.10", "172.16.5.10"),  # Private class B
            ("https://127.0.0.1", "127.0.0.1"),  # Localhost
            ("https://169.254.169.254", "169.254.169.254"),  # Link-local (AWS metadata)
        ]

        for url, ip in test_cases:
            with self.subTest(url=url):
                mock_gethostbyname.return_value = ip
                is_valid, error = URLValidator.validate_url(url)
                self.assertFalse(is_valid, f"Private IP should be blocked: {url}")
                self.assertIn("not in", error)
                self.assertIn("whitelist", error)

    @patch("socket.gethostbyname")
    def test_whitelisted_private_ips_allowed(self, mock_gethostbyname):
        """Test that whitelisted private IPs are allowed."""
        # Set whitelist environment variable
        os.environ[URLValidator.ENV_VAR] = "192.168.1.100:8080,10.0.0.0/8"

        test_cases = [
            ("https://192.168.1.100:8080", "192.168.1.100"),  # Exact IP:port match
            ("https://10.0.0.5:9200", "10.0.0.5"),  # CIDR range match
            ("https://10.255.255.255", "10.255.255.255"),  # CIDR range edge
        ]

        for url, ip in test_cases:
            with self.subTest(url=url):
                mock_gethostbyname.return_value = ip
                is_valid, error = URLValidator.validate_url(url)
                self.assertTrue(
                    is_valid, f"Whitelisted IP should be allowed: {url}, Error: {error}"
                )

    @patch("socket.gethostbyname")
    def test_port_specific_whitelist(self, mock_gethostbyname):
        """Test port-specific whitelisting."""
        os.environ[URLValidator.ENV_VAR] = "192.168.1.100:8080"
        mock_gethostbyname.return_value = "192.168.1.100"

        # Port match - should be allowed
        is_valid, error = URLValidator.validate_url("https://192.168.1.100:8080")
        self.assertTrue(is_valid, "Matching port should be allowed")

        # Port mismatch - should be blocked
        is_valid, error = URLValidator.validate_url("https://192.168.1.100:9000")
        self.assertFalse(is_valid, "Non-matching port should be blocked")

    @patch("socket.gethostbyname")
    def test_cidr_range_matching(self, mock_gethostbyname):
        """Test CIDR range matching in whitelist."""
        os.environ[URLValidator.ENV_VAR] = "192.168.1.0/24:8080"

        test_cases = [
            ("192.168.1.1", True),  # In range
            ("192.168.1.255", True),  # In range (edge)
            ("192.168.2.1", False),  # Out of range
            ("192.168.0.255", False),  # Out of range
        ]

        for ip, should_be_valid in test_cases:
            with self.subTest(ip=ip):
                mock_gethostbyname.return_value = ip
                is_valid, error = URLValidator.validate_url(f"https://{ip}:8080")
                self.assertEqual(
                    is_valid, should_be_valid, f"CIDR matching failed for {ip}: {error}"
                )

    def test_whitelist_parsing(self):
        """Test whitelist configuration parsing."""
        # Test various whitelist formats
        os.environ[URLValidator.ENV_VAR] = (
            "192.168.1.100:8080,10.0.0.0/8,172.16.5.100:3000"
        )

        entries = URLValidator._parse_whitelist_config()

        self.assertEqual(len(entries), 3)

        # Check first entry (single IP with port)
        self.assertEqual(str(entries[0].ip_network), "192.168.1.100/32")
        self.assertEqual(entries[0].port, 8080)

        # Check second entry (CIDR without port)
        self.assertEqual(str(entries[1].ip_network), "10.0.0.0/8")
        self.assertIsNone(entries[1].port)

        # Check third entry (single IP with port)
        self.assertEqual(str(entries[2].ip_network), "172.16.5.100/32")
        self.assertEqual(entries[2].port, 3000)

    def test_invalid_whitelist_entries_ignored(self):
        """Test that invalid whitelist entries are ignored gracefully."""
        os.environ[URLValidator.ENV_VAR] = (
            "192.168.1.100:8080,invalid-ip,10.0.0.0/8,bad-cidr/35"
        )

        entries = URLValidator._parse_whitelist_config()

        # Only valid entries should be parsed
        self.assertEqual(len(entries), 2)
        self.assertEqual(str(entries[0].ip_network), "192.168.1.100/32")
        self.assertEqual(str(entries[1].ip_network), "10.0.0.0/8")

    def test_empty_whitelist_config(self):
        """Test behavior with empty whitelist configuration."""
        os.environ[URLValidator.ENV_VAR] = ""

        entries = URLValidator._parse_whitelist_config()
        self.assertEqual(len(entries), 0)

    @patch("socket.gethostbyname")
    def test_dns_resolution_failure(self, mock_gethostbyname):
        """Test handling of DNS resolution failures."""
        mock_gethostbyname.side_effect = Exception("DNS resolution failed")

        is_valid, error = URLValidator.validate_url("https://nonexistent.example.com")
        self.assertFalse(is_valid)
        self.assertIn("DNS resolution failed", error)

    def test_invalid_url_handling(self):
        """Test handling of invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "https://",  # No hostname
            "",  # Empty URL
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                is_valid, error = URLValidator.validate_url(url)
                self.assertFalse(is_valid)
                self.assertTrue(len(error) > 0)

    @patch("socket.gethostbyname")
    def test_localhost_blocked_by_default(self, mock_gethostbyname):
        """Test that localhost is blocked when not explicitly whitelisted."""
        # No whitelist configured - localhost should be blocked

        localhost_ips = ["127.0.0.1", "127.0.0.2", "127.255.255.255"]

        for ip in localhost_ips:
            with self.subTest(ip=ip):
                mock_gethostbyname.return_value = ip
                is_valid, error = URLValidator.validate_url(f"https://{ip}")
                self.assertFalse(
                    is_valid, f"Localhost IP should be blocked by default: {ip}"
                )
                self.assertIn("not in", error)

    @patch("socket.gethostbyname")
    def test_metadata_service_blocked(self, mock_gethostbyname):
        """Test that cloud metadata services are blocked."""
        # AWS/Azure metadata service
        mock_gethostbyname.return_value = "169.254.169.254"

        is_valid, error = URLValidator.validate_url(
            "https://169.254.169.254/latest/meta-data"
        )
        self.assertFalse(is_valid)
        self.assertIn("not in", error)


if __name__ == "__main__":
    unittest.main()
