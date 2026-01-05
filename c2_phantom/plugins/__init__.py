"""Plugin system for C2 Phantom."""

from c2_phantom.plugins.base import BasePlugin
from c2_phantom.plugins.loader import PluginLoader

__all__ = ["BasePlugin", "PluginLoader"]
