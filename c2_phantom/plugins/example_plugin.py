"""
Example plugin for C2 Phantom.

This demonstrates how to create a custom plugin that adds new commands.
"""

from typing import Dict, Any
from c2_phantom.plugins.base import CommandPlugin


class ExamplePlugin(CommandPlugin):
    """Example plugin demonstrating the plugin API."""

    name = "example"
    version = "1.0.0"
    description = "Example plugin for C2 Phantom demonstrating plugin capabilities"
    author = "C2 Phantom Team"

    def initialize(self) -> None:
        """Initialize plugin resources."""
        self.logger.info(f"Initializing {self.name} plugin v{self.version}")

        # Register commands
        self.register_command(
            "hello",
            self.hello_command,
            "Greet someone by name"
        )

        self.register_command(
            "echo",
            self.echo_command,
            "Echo a message back to the user"
        )

        self.register_command(
            "info",
            self.info_command,
            "Display plugin information"
        )

        self.logger.info(f"Registered {len(self.commands)} commands")

    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info(f"Cleaning up {self.name} plugin")
        self.commands.clear()

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        # Add any configuration validation here
        return True

    def hello_command(self, name: str = "World") -> str:
        """
        Greet someone by name.

        Args:
            name: Name to greet (default: World)

        Returns:
            Greeting message
        """
        self.logger.debug(f"hello command called with name={name}")
        return f"Hello, {name}! Welcome to C2 Phantom."

    def echo_command(self, message: str) -> str:
        """
        Echo a message back.

        Args:
            message: Message to echo

        Returns:
            The same message
        """
        self.logger.debug(f"echo command called with message={message}")
        return f"Echo: {message}"

    def info_command(self) -> Dict[str, Any]:
        """
        Display plugin information.

        Returns:
            Plugin metadata dictionary
        """
        self.logger.debug("info command called")
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "commands": list(self.commands.keys()),
            "initialized": self._initialized,
        }


# This allows the plugin to be imported and used
plugin_class = ExamplePlugin
