"""
Tests for plugin system.
"""

import pytest
from pathlib import Path

from c2_phantom.plugins.base import BasePlugin, CommandPlugin
from c2_phantom.plugins.loader import PluginLoader


class TestPlugin(BasePlugin):
    """Test plugin for testing."""

    name = "test_plugin"
    version = "1.0.0"
    description = "Test plugin"
    author = "Test"

    def initialize(self) -> None:
        """Initialize test plugin."""
        pass

    def cleanup(self) -> None:
        """Cleanup test plugin."""
        pass


class TestBasePlugin:
    """Tests for base plugin."""

    def test_plugin_info(self):
        """Test getting plugin info."""
        plugin = TestPlugin()
        info = plugin.get_info()

        assert info["name"] == "test_plugin"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Test plugin"

    def test_context_manager(self):
        """Test plugin context manager."""
        plugin = TestPlugin()

        with plugin:
            assert plugin._initialized is True

        assert plugin._initialized is False


class TestCommandPlugin:
    """Tests for command plugin."""

    def test_register_command(self):
        """Test command registration."""

        class ConcreteCommandPlugin(CommandPlugin):
            """Concrete implementation for testing."""

            name = "test_command_plugin"
            version = "1.0.0"
            description = "Test command plugin"

            def initialize(self) -> None:
                """Initialize plugin."""
                pass

            def cleanup(self) -> None:
                """Cleanup plugin."""
                pass

        plugin = ConcreteCommandPlugin()

        def test_handler():
            return "test"

        plugin.register_command("test", test_handler, "Test command")
        commands = plugin.get_commands()

        assert "test" in commands
        assert commands["test"]["handler"] == test_handler


class TestPluginLoader:
    """Tests for plugin loader."""

    def test_discover_plugins(self, temp_dir):
        """Test plugin discovery."""
        plugin_dir = temp_dir / "plugins"
        plugin_dir.mkdir()

        # Create test plugin file
        (plugin_dir / "test_plugin.py").write_text("# Test plugin")

        loader = PluginLoader(plugin_dir)
        plugins = loader.discover_plugins()

        assert "test_plugin" in plugins

    def test_list_loaded_plugins(self, temp_dir):
        """Test listing loaded plugins."""
        loader = PluginLoader(temp_dir / "plugins")
        loaded = loader.list_loaded_plugins()

        assert isinstance(loaded, list)
