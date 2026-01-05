"""
Base plugin class for C2 Phantom plugins.

All plugins should inherit from BasePlugin and implement required methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePlugin(ABC):
    """Base class for all C2 Phantom plugins."""

    # Plugin metadata (override in subclasses)
    name: str = "base_plugin"
    version: str = "0.0.0"
    description: str = "Base plugin"
    author: str = "Unknown"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize plugin.

        Args:
            config: Optional plugin configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"c2_phantom.plugins.{self.name}")
        self._initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize plugin resources.

        This method is called when the plugin is loaded.
        Override to perform setup operations.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.

        This method is called when the plugin is unloaded.
        Override to perform cleanup operations.
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.

        Returns:
            Dictionary containing plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "initialized": self._initialized,
        }

    def validate_config(self) -> bool:
        """
        Validate plugin configuration.

        Returns:
            True if configuration is valid

        Override to implement custom validation.
        """
        return True

    def __enter__(self) -> "BasePlugin":
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
            self._initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if self._initialized:
            self.cleanup()
            self._initialized = False

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"


class CommandPlugin(BasePlugin):
    """Base class for plugins that add commands."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize command plugin."""
        super().__init__(config)
        self.commands: Dict[str, callable] = {}

    def register_command(self, name: str, handler: callable, help_text: str = "") -> None:
        """
        Register a command handler.

        Args:
            name: Command name
            handler: Command handler function
            help_text: Help text for the command
        """
        self.commands[name] = {
            "handler": handler,
            "help": help_text,
        }
        self.logger.info(f"Registered command: {name}")

    def get_commands(self) -> Dict[str, Any]:
        """
        Get all registered commands.

        Returns:
            Dictionary of commands
        """
        return self.commands


class NetworkPlugin(BasePlugin):
    """Base class for plugins that add network protocols."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize network plugin."""
        super().__init__(config)
        self.protocol_name = "unknown"

    @abstractmethod
    async def send(self, data: bytes) -> bool:
        """
        Send data through the protocol.

        Args:
            data: Data to send

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def receive(self) -> Optional[bytes]:
        """
        Receive data through the protocol.

        Returns:
            Received data or None
        """
        pass


class EvasionPlugin(BasePlugin):
    """Base class for plugins that add evasion techniques."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize evasion plugin."""
        super().__init__(config)
        self.technique_name = "unknown"

    @abstractmethod
    def apply(self, data: bytes) -> bytes:
        """
        Apply evasion technique to data.

        Args:
            data: Original data

        Returns:
            Modified data
        """
        pass

    @abstractmethod
    def reverse(self, data: bytes) -> bytes:
        """
        Reverse evasion technique.

        Args:
            data: Modified data

        Returns:
            Original data
        """
        pass
