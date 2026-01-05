"""
Proxy chaining implementation for multi-hop evasion.

Supports SOCKS4, SOCKS5, and HTTP proxies with chaining capability.
"""

from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from dataclasses import dataclass

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType

from c2_phantom.core.exceptions import NetworkError


@dataclass
class ProxyConfig:
    """Proxy configuration."""

    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http, socks4, socks5


class ProxyChain:
    """Proxy chaining for multi-hop evasion."""

    def __init__(self, proxies: List[ProxyConfig]) -> None:
        """
        Initialize proxy chain.

        Args:
            proxies: List of proxy configurations
        """
        self.proxies = proxies
        self._validate_proxies()

    def _validate_proxies(self) -> None:
        """Validate proxy configurations."""
        if not self.proxies:
            raise NetworkError("At least one proxy required")

        for proxy in self.proxies:
            parsed = urlparse(proxy.url)
            if not parsed.scheme or not parsed.hostname:
                raise NetworkError(f"Invalid proxy URL: {proxy.url}")

    def _get_proxy_type(self, proxy_type: str) -> ProxyType:
        """
        Convert proxy type string to ProxyType enum.

        Args:
            proxy_type: Proxy type string

        Returns:
            ProxyType enum value
        """
        type_map = {
            "http": ProxyType.HTTP,
            "socks4": ProxyType.SOCKS4,
            "socks5": ProxyType.SOCKS5,
        }

        return type_map.get(proxy_type.lower(), ProxyType.HTTP)

    def create_connector(self, proxy_index: int = 0) -> ProxyConnector:
        """
        Create proxy connector for a specific proxy in the chain.

        Args:
            proxy_index: Index of proxy to use

        Returns:
            ProxyConnector instance
        """
        if proxy_index >= len(self.proxies):
            raise NetworkError(f"Invalid proxy index: {proxy_index}")

        proxy = self.proxies[proxy_index]
        proxy_type = self._get_proxy_type(proxy.proxy_type)

        # Create connector
        connector = ProxyConnector.from_url(
            proxy.url,
            username=proxy.username,
            password=proxy.password,
        )

        return connector

    async def test_proxy(self, proxy_index: int = 0, test_url: str = "https://www.google.com") -> bool:
        """
        Test if a proxy is working.

        Args:
            proxy_index: Index of proxy to test
            test_url: URL to test connectivity

        Returns:
            True if proxy is working
        """
        try:
            connector = self.create_connector(proxy_index)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200

        except Exception:
            return False

    async def test_all_proxies(self, test_url: str = "https://www.google.com") -> Dict[int, bool]:
        """
        Test all proxies in the chain.

        Args:
            test_url: URL to test connectivity

        Returns:
            Dictionary mapping proxy index to test result
        """
        results = {}
        for i in range(len(self.proxies)):
            results[i] = await self.test_proxy(i, test_url)
        return results

    async def get_working_proxy_index(self) -> Optional[int]:
        """
        Get index of first working proxy.

        Returns:
            Index of working proxy or None
        """
        for i in range(len(self.proxies)):
            if await self.test_proxy(i):
                return i
        return None

    def get_proxy_url(self, proxy_index: int = 0) -> str:
        """
        Get proxy URL by index.

        Args:
            proxy_index: Proxy index

        Returns:
            Proxy URL string
        """
        if proxy_index >= len(self.proxies):
            raise NetworkError(f"Invalid proxy index: {proxy_index}")

        return self.proxies[proxy_index].url

    def get_proxy_info(self, proxy_index: int = 0) -> Dict[str, Any]:
        """
        Get proxy information.

        Args:
            proxy_index: Proxy index

        Returns:
            Proxy information dictionary
        """
        if proxy_index >= len(self.proxies):
            raise NetworkError(f"Invalid proxy index: {proxy_index}")

        proxy = self.proxies[proxy_index]
        parsed = urlparse(proxy.url)

        return {
            "url": proxy.url,
            "type": proxy.proxy_type,
            "host": parsed.hostname,
            "port": parsed.port,
            "authenticated": bool(proxy.username),
        }

    @classmethod
    def from_urls(cls, proxy_urls: List[str]) -> "ProxyChain":
        """
        Create proxy chain from list of URLs.

        Args:
            proxy_urls: List of proxy URLs

        Returns:
            ProxyChain instance
        """
        proxies = []
        for url in proxy_urls:
            parsed = urlparse(url)

            # Determine proxy type from scheme
            proxy_type = "http"
            if parsed.scheme in ["socks4", "socks5"]:
                proxy_type = parsed.scheme

            proxies.append(
                ProxyConfig(
                    url=url,
                    username=parsed.username,
                    password=parsed.password,
                    proxy_type=proxy_type,
                )
            )

        return cls(proxies)

    def __len__(self) -> int:
        """Get number of proxies in chain."""
        return len(self.proxies)

    def __repr__(self) -> str:
        """String representation."""
        return f"ProxyChain(proxies={len(self.proxies)})"
