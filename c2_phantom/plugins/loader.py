"""
Plugin loader with auto-discovery.

Discovers and loads plugins from the plugins directory.
"""

import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional

from c2_phantom.plugins.base import BasePlugin
from c2_phantom.core.exceptions import PluginError
from c2_phantom.core.config import Config


class PluginLoader:
    """Loads and manages C2 Phantom plugins."""

    def __init__(self, plugin_dir: Optional[Path] = None) -> None:
        """
        Initialize plugin loader.

        Args:
            plugin_dir: Optional custom plugin directory
        """
        if plugin_dir is None:
            config_dir = Config.get_config_dir()
            plugin_dir = config_dir / "plugins"

        self.plugin_dir = plugin_dir
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directory.

        Returns:
            List of plugin names
        """
        plugins = []

        if not self.plugin_dir.exists():
            return plugins

        for file in self.plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            plugins.append(file.stem)

        return plugins

    def load_plugin_module(self, plugin_name: str) -> None:
        """
        Load plugin module dynamically.

        Args:
            plugin_name: Name of the plugin to load

        Raises:
            PluginError: If loading fails
        """
        try:
            plugin_file = self.plugin_dir / f"{plugin_name}.py"

            if not plugin_file.exists():
                raise PluginError(f"Plugin file not found: {plugin_file}")

            # Load module
            spec = importlib.util.spec_from_file_location(
                f"c2_phantom.plugins.{plugin_name}",
                plugin_file,
            )

            if spec is None or spec.loader is None:
                raise PluginError(f"Failed to load plugin spec: {plugin_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                    self.plugin_classes[obj.name] = obj

        except Exception as e:
            raise PluginError(f"Failed to load plugin '{plugin_name}': {str(e)}")

    def load_plugin(self, plugin_name: str, config: Optional[Dict] = None) -> BasePlugin:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Name of the plugin
            config: Optional plugin configuration

        Returns:
            Loaded plugin instance

        Raises:
            PluginError: If loading fails
        """
        try:
            # Check if already loaded
            if plugin_name in self.loaded_plugins:
                return self.loaded_plugins[plugin_name]

            # Load module if not loaded
            if plugin_name not in self.plugin_classes:
                self.load_plugin_module(plugin_name)

            # Get plugin class
            plugin_class = self.plugin_classes.get(plugin_name)
            if plugin_class is None:
                raise PluginError(f"Plugin class not found: {plugin_name}")

            # Instantiate and initialize
            plugin = plugin_class(config=config)

            if not plugin.validate_config():
                raise PluginError(f"Invalid configuration for plugin: {plugin_name}")

            plugin.initialize()
            plugin._initialized = True

            self.loaded_plugins[plugin_name] = plugin

            return plugin

        except Exception as e:
            raise PluginError(f"Failed to load plugin '{plugin_name}': {str(e)}")

    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Raises:
            PluginError: If unloading fails
        """
        try:
            plugin = self.loaded_plugins.get(plugin_name)
            if plugin is None:
                return

            plugin.cleanup()
            plugin._initialized = False

            del self.loaded_plugins[plugin_name]

        except Exception as e:
            raise PluginError(f"Failed to unload plugin '{plugin_name}': {str(e)}")

    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Load all discovered plugins.

        Returns:
            Dictionary of loaded plugins
        """
        plugin_names = self.discover_plugins()

        for plugin_name in plugin_names:
            try:
                self.load_plugin(plugin_name)
            except PluginError as e:
                print(f"Warning: {str(e)}")
                continue

        return self.loaded_plugins

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a loaded plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.loaded_plugins.get(plugin_name)

    def list_loaded_plugins(self) -> List[Dict]:
        """
        List all loaded plugins.

        Returns:
            List of plugin information dictionaries
        """
        return [plugin.get_info() for plugin in self.loaded_plugins.values()]

    def reload_plugin(self, plugin_name: str) -> BasePlugin:
        """
        Reload a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            Reloaded plugin instance
        """
        # Get config before unloading
        config = None
        if plugin_name in self.loaded_plugins:
            config = self.loaded_plugins[plugin_name].config

        # Unload and reload
        self.unload_plugin(plugin_name)

        # Remove from classes to force reload
        if plugin_name in self.plugin_classes:
            del self.plugin_classes[plugin_name]

        return self.load_plugin(plugin_name, config)

    def cleanup_all(self) -> None:
        """Cleanup all loaded plugins."""
        for plugin_name in list(self.loaded_plugins.keys()):
            try:
                self.unload_plugin(plugin_name)
            except Exception:
                pass
