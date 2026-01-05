"""
Tests for network modules.
"""

import pytest

from c2_phantom.network.proxy import ProxyChain, ProxyConfig


class TestProxyChain:
    """Tests for proxy chaining."""

    def test_proxy_chain_creation(self):
        """Test proxy chain creation."""
        proxies = [
            ProxyConfig(url="http://proxy1.example.com:8080"),
            ProxyConfig(url="socks5://proxy2.example.com:1080"),
        ]

        chain = ProxyChain(proxies)
        assert len(chain) == 2

    def test_from_urls(self):
        """Test proxy chain creation from URLs."""
        urls = [
            "http://proxy1.example.com:8080",
            "socks5://user:pass@proxy2.example.com:1080",
        ]

        chain = ProxyChain.from_urls(urls)
        assert len(chain) == 2

    def test_get_proxy_info(self):
        """Test getting proxy information."""
        proxies = [
            ProxyConfig(url="http://proxy1.example.com:8080", username="user", password="pass"),
        ]

        chain = ProxyChain(proxies)
        info = chain.get_proxy_info(0)

        assert info["host"] == "proxy1.example.com"
        assert info["port"] == 8080
        assert info["authenticated"] is True
