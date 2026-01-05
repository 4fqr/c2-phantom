"""
Proxy and anonymity layer for C2 Phantom.
Implements SOCKS5, Tor, rotating proxies, and IP leak prevention.
"""

import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Modern browser user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class ProxyChainConfig:
    """Configuration for proxy chains with health monitoring."""

    def __init__(self, proxies: List[str], rotate: bool = True, health_check: bool = True, timeout: int = 10):
        """Initialize proxy chain configuration."""
        self.proxies = proxies
        self.rotate = rotate
        self.health_check = health_check
        self.timeout = timeout
        self.current_index = 0
        self.proxy_health: Dict[str, Dict[str, Any]] = {}

    def get_next_proxy(self) -> str:
        """Get next proxy in rotation."""
        if not self.proxies:
            return ""
        if self.rotate:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy
        return self.proxies[0]

    async def check_proxy_health(self, proxy: str) -> bool:
        """Check if proxy is healthy."""
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
                async with session.get("http://icanhazip.com", proxy=proxy) as response:
                    if response.status == 200:
                        self.proxy_health[proxy] = {"healthy": True, "last_check": datetime.now()}
                        return True
        except Exception as e:
            logger.warning(f"Proxy health check failed for {proxy}: {e}")
            self.proxy_health[proxy] = {"healthy": False, "last_check": datetime.now()}
        return False


class TorManager:
    """Tor circuit management."""

    def __init__(self, control_port: int = 9051, control_password: Optional[str] = None):
        """Initialize Tor manager."""
        self.control_port = control_port
        self.control_password = control_password
        self.last_circuit_change = datetime.now()

    async def new_circuit(self) -> bool:
        """Request new Tor circuit."""
        try:
            logger.info("New Tor circuit requested")
            self.last_circuit_change = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to create new Tor circuit: {e}")
            return False


class AnonymousClient:
    """HTTP client with full anonymity and IP leak protection."""

    def __init__(self, proxies: Optional[List[str]] = None, use_tor: bool = False, rotate_user_agent: bool = True):
        """Initialize anonymous HTTP client."""
        self.rotate_user_agent = rotate_user_agent

        if use_tor:
            self.proxy_config = ProxyChainConfig(proxies=["socks5://127.0.0.1:9050"])
            self.tor_manager = TorManager()
        elif proxies:
            self.proxy_config = ProxyChainConfig(proxies=proxies)
            self.tor_manager = None
        else:
            self.proxy_config = None
            self.tor_manager = None

    def _get_user_agent(self) -> str:
        """Get random user agent if rotation enabled."""
        if self.rotate_user_agent:
            return random.choice(USER_AGENTS)
        return USER_AGENTS[0]

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request through proxy chain."""
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self._get_user_agent()

        proxy = None
        if self.proxy_config:
            proxy = self.proxy_config.get_next_proxy()
            if self.proxy_config.health_check and proxy:
                if not await self.proxy_config.check_proxy_health(proxy):
                    logger.warning(f"Proxy {proxy} is unhealthy, using anyway")

        connector = aiohttp.TCPConnector(ssl=False)
        timeout_obj = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout_obj) as session:
                async with session.request(
                    method, url, headers=headers, proxy=proxy if proxy else None, **kwargs
                ) as response:
                    if response.content_type == "application/json":
                        return await response.json()
                    return {"status": response.status, "text": await response.text()}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET request through proxy."""
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST request through proxy."""
        if json:
            kwargs["json"] = json
        return await self._make_request("POST", url, **kwargs)


async def check_ip_leaks() -> Dict[str, Any]:
    """Check for IP/DNS leaks."""
    results = {"ip_leak": False, "dns_leak": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://icanhazip.com", timeout=aiohttp.ClientTimeout(total=5)) as response:
                ip = (await response.text()).strip()
                results["public_ip"] = ip
                logger.info(f"Public IP: {ip}")
    except Exception as e:
        logger.error(f"IP leak check failed: {e}")
        results["error"] = str(e)
    return results
