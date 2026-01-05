"""
WebSocket channel implementation for persistent connections.

Provides WebSocket-based communication with automatic reconnection.
"""

import asyncio
import json
from typing import Optional, Callable, Any, Dict
from datetime import datetime

import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import WebSocketException

from c2_phantom.core.exceptions import NetworkError


class WebSocketChannel:
    """WebSocket channel with automatic reconnection."""

    def __init__(
        self,
        uri: str,
        timeout: int = 30,
        ping_interval: int = 20,
        ping_timeout: int = 10,
        max_reconnect_attempts: int = 5,
    ) -> None:
        """
        Initialize WebSocket channel.

        Args:
            uri: WebSocket URI (ws:// or wss://)
            timeout: Connection timeout in seconds
            ping_interval: Ping interval in seconds
            ping_timeout: Ping timeout in seconds
            max_reconnect_attempts: Maximum reconnection attempts
        """
        self.uri = uri
        self.timeout = timeout
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.max_reconnect_attempts = max_reconnect_attempts

        self._websocket: Optional[WebSocketClientProtocol] = None
        self._reconnect_attempts = 0
        self._message_handler: Optional[Callable] = None
        self._running = False

    async def connect(self) -> None:
        """
        Establish WebSocket connection.

        Raises:
            NetworkError: If connection fails
        """
        try:
            self._websocket = await websockets.connect(
                self.uri,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=self.timeout,
            )
            self._reconnect_attempts = 0
            self._running = True

        except WebSocketException as e:
            raise NetworkError(f"WebSocket connection failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._running = False
        if self._websocket is not None and not self._websocket.closed:
            await self._websocket.close()

    async def send(self, data: Dict[str, Any]) -> None:
        """
        Send data through WebSocket.

        Args:
            data: Data dictionary to send (will be JSON-encoded)

        Raises:
            NetworkError: If send fails
        """
        if self._websocket is None or self._websocket.closed:
            raise NetworkError("WebSocket not connected")

        try:
            message = json.dumps(data)
            await self._websocket.send(message)

        except WebSocketException as e:
            raise NetworkError(f"WebSocket send failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")

    async def send_bytes(self, data: bytes) -> None:
        """
        Send binary data through WebSocket.

        Args:
            data: Binary data to send

        Raises:
            NetworkError: If send fails
        """
        if self._websocket is None or self._websocket.closed:
            raise NetworkError("WebSocket not connected")

        try:
            await self._websocket.send(data)

        except WebSocketException as e:
            raise NetworkError(f"WebSocket send failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")

    async def receive(self) -> Optional[Dict[str, Any]]:
        """
        Receive data from WebSocket.

        Returns:
            Received data dictionary or None

        Raises:
            NetworkError: If receive fails
        """
        if self._websocket is None or self._websocket.closed:
            raise NetworkError("WebSocket not connected")

        try:
            message = await asyncio.wait_for(
                self._websocket.recv(),
                timeout=self.timeout,
            )

            if isinstance(message, str):
                return json.loads(message)
            else:
                return {"data": message, "type": "binary"}

        except asyncio.TimeoutError:
            return None
        except WebSocketException as e:
            raise NetworkError(f"WebSocket receive failed: {str(e)}")
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")

    async def _reconnect(self) -> bool:
        """
        Attempt to reconnect.

        Returns:
            True if reconnection successful
        """
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            return False

        self._reconnect_attempts += 1
        delay = min(2**self._reconnect_attempts, 60)  # Exponential backoff

        await asyncio.sleep(delay)

        try:
            await self.connect()
            return True
        except Exception:
            return False

    async def listen(self, message_handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Listen for incoming messages with automatic reconnection.

        Args:
            message_handler: Callback function for received messages
        """
        self._message_handler = message_handler

        while self._running:
            try:
                if self._websocket is None or self._websocket.closed:
                    if not await self._reconnect():
                        break

                message = await self.receive()
                if message and self._message_handler:
                    await asyncio.create_task(self._message_handler(message))

            except NetworkError:
                # Try to reconnect
                if not await self._reconnect():
                    break

            except Exception:
                # Unexpected error, try to reconnect
                if not await self._reconnect():
                    break

    async def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Send command through WebSocket.

        Args:
            command: Command name
            params: Optional command parameters
        """
        data = {
            "command": command,
            "params": params or {},
            "timestamp": datetime.now().isoformat(),
        }
        await self.send(data)

    async def send_file(self, file_path: str, chunk_size: int = 8192) -> None:
        """
        Send file through WebSocket in chunks.

        Args:
            file_path: Path to file to send
            chunk_size: Chunk size in bytes

        Raises:
            NetworkError: If send fails
        """
        try:
            with open(file_path, "rb") as f:
                sequence = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

                    # Send chunk with metadata
                    data = {
                        "type": "file_chunk",
                        "sequence": sequence,
                        "data": chunk.hex(),
                        "file_path": file_path,
                    }
                    await self.send(data)

                    sequence += 1

                # Send completion marker
                await self.send({
                    "type": "file_complete",
                    "file_path": file_path,
                    "total_chunks": sequence,
                })

        except FileNotFoundError:
            raise NetworkError(f"File not found: {file_path}")
        except Exception as e:
            raise NetworkError(f"File send failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check WebSocket connection health.

        Returns:
            True if connection is healthy
        """
        if self._websocket is None or self._websocket.closed:
            return False

        try:
            pong = await self._websocket.ping()
            await asyncio.wait_for(pong, timeout=5)
            return True
        except Exception:
            return False

    async def __aenter__(self) -> "WebSocketChannel":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
