"""
C2 Client for communicating with C2 server from CLI.

Allows operators to send commands and retrieve results from the running C2 server.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import logging


logger = logging.getLogger(__name__)


class C2Client:
    """
    Client for communicating with C2 server.

    Used by CLI commands to interact with the running C2 server instance.
    """

    def __init__(self, server_url: str = "http://localhost:8443") -> None:
        """
        Initialize C2 client.

        Args:
            server_url: C2 server URL
        """
        self.server_url = server_url.rstrip("/")

    async def health_check(self) -> bool:
        """
        Check if C2 server is running.

        Returns:
            True if server is healthy
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False

    async def queue_command(self, session_id: str, command: str, command_type: str = "execute") -> Dict[str, Any]:
        """
        Queue a command for an agent.

        Args:
            session_id: Target session ID
            command: Command to execute
            command_type: Type of command (execute, upload, download)

        Returns:
            Response with task_id
        """
        try:
            payload = {"session_id": session_id, "type": command_type, "command": command}

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
        Wait for and retrieve command result.

        Args:
            session_id: Session ID
            task_id: Task ID
            timeout: Timeout in seconds

        Returns:
            Command result or None
        """
        try:
            start_time = asyncio.get_event_loop().time()

            async with aiohttp.ClientSession() as session:
                while asyncio.get_event_loop().time() - start_time < timeout:
                    async with session.get(
                        f"{self.server_url}/api/result/{session_id}/{task_id}", timeout=aiohttp.ClientTimeout(total=5)
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
        List sessions from server.

        Args:
            status: Optional status filter (active, inactive, all)

        Returns:
            List of session data
        """
        try:
            params = {}
            if status:
                params["status"] = status

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
        Upload file to agent.

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
        Download file from agent.

        Args:
            session_id: Target session ID
            remote_path: Remote file path to download

        Returns:
            Download result with task_id
        """
        try:
            payload = {"session_id": session_id, "type": "download", "path": remote_path}

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
