"""
Core exceptions for C2 Phantom framework.
"""

from typing import Optional


class C2PhantomError(Exception):
    """Base exception for all C2 Phantom errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(C2PhantomError):
    """Configuration related errors."""

    pass


class EncryptionError(C2PhantomError):
    """Encryption and cryptography errors."""

    pass


class NetworkError(C2PhantomError):
    """Network communication errors."""

    pass


class SessionError(C2PhantomError):
    """Session management errors."""

    pass


class PluginError(C2PhantomError):
    """Plugin loading and execution errors."""

    pass


class ValidationError(C2PhantomError):
    """Input validation errors."""

    pass


class AuthenticationError(C2PhantomError):
    """Authentication and authorization errors."""

    pass


class PersistenceError(C2PhantomError):
    """Persistence mechanism errors."""

    pass
