"""
Configuration management for C2 Phantom.

Handles loading, validation, and management of configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=443, ge=1, le=65535, description="Server port")
    tls_enabled: bool = Field(default=True, description="Enable TLS")
    certificate: Optional[str] = Field(default=None, description="TLS certificate path")
    key: Optional[str] = Field(default=None, description="TLS key path")


class EncryptionConfig(BaseModel):
    """Encryption configuration."""

    default_algorithm: str = Field(default="aes256-gcm", description="Default algorithm")
    key_size: int = Field(default=256, description="Encryption key size in bits")
    forward_secrecy: bool = Field(default=True, description="Enable Perfect Forward Secrecy")


class NetworkConfig(BaseModel):
    """Network configuration."""

    protocols: List[str] = Field(default_factory=lambda: ["https", "dns", "websocket"], description="Enabled protocols")
    user_agents: List[str] = Field(
        default_factory=lambda: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ],
        description="User agent strings",
    )
    randomize_headers: bool = Field(default=True, description="Randomize HTTP headers")
    jitter_min: int = Field(default=500, description="Minimum jitter in milliseconds")
    jitter_max: int = Field(default=2000, description="Maximum jitter in milliseconds")


class EvasionConfig(BaseModel):
    """Evasion techniques configuration."""

    domain_fronting: bool = Field(default=True, description="Enable domain fronting")
    payload_fragmentation: bool = Field(default=True, description="Enable payload fragmentation")
    protocol_fingerprinting_evasion: bool = Field(default=True, description="Enable protocol fingerprinting evasion")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    file: Optional[str] = Field(default=None, description="Log file path")
    max_size: str = Field(default="10MB", description="Maximum log file size")
    backup_count: int = Field(default=5, description="Number of backup log files")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.upper()


class PluginsConfig(BaseModel):
    """Plugins configuration."""

    directory: Optional[str] = Field(default=None, description="Plugins directory")
    auto_load: bool = Field(default=True, description="Auto-load plugins on startup")


class Config(BaseModel):
    """Main configuration model."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    encryption: EncryptionConfig = Field(default_factory=EncryptionConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    evasion: EvasionConfig = Field(default_factory=EvasionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory path."""
        home = Path.home()
        config_dir = home / ".phantom"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def get_config_path(cls) -> Path:
        """Get configuration file path."""
        return cls.get_config_dir() / "config.yaml"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from file.

        Args:
            config_path: Optional custom config path

        Returns:
            Config instance
        """
        if config_path is None:
            config_path = cls.get_config_path()

        if not config_path.exists():
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(**data) if data else cls()

    def save(self, config_path: Optional[Path] = None) -> None:
        """
        Save configuration to file.

        Args:
            config_path: Optional custom config path
        """
        if config_path is None:
            config_path = self.get_config_path()

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()


def create_default_config() -> Config:
    """
    Create and save default configuration.

    Returns:
        Default Config instance
    """
    config = Config()
    config.save()
    return config
