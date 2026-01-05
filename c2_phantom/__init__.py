"""
C2 Phantom - Advanced C2 Framework for Red Team Training

A professional command-line tool implementing ethical command & control
framework with advanced traffic obfuscation and encryption capabilities.

Author: C2 Phantom Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "C2 Phantom Team"
__license__ = "MIT"

from c2_phantom.core.config import Config
from c2_phantom.core.session import Session, SessionManager
from c2_phantom.core.exceptions import (
    C2PhantomError,
    ConfigurationError,
    EncryptionError,
    NetworkError,
    PluginError,
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Config",
    "Session",
    "SessionManager",
    "C2PhantomError",
    "ConfigurationError",
    "EncryptionError",
    "NetworkError",
    "PluginError",
]
