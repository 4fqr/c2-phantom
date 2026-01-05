"""Custom exceptions for C2 Phantom."""


class C2PhantomError(Exception):
    """Base exception for all C2 Phantom errors."""
    pass


class ConfigurationError(C2PhantomError):
    """Raised when configuration is invalid or missing."""
    pass


class EncryptionError(C2PhantomError):
    """Raised when encryption/decryption operations fail."""
    pass


class NetworkError(C2PhantomError):
    """Raised when network operations fail."""
    pass


class SessionError(C2PhantomError):
    """Raised when session operations fail."""
    pass


class PluginError(C2PhantomError):
    """Raised when plugin operations fail."""
    pass
