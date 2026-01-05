"""
Test configuration and fixtures.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from c2_phantom.core.config import Config
from c2_phantom.core.session import SessionManager
from c2_phantom.crypto.keys import KeyManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration."""
    config = Config()
    config_path = temp_dir / "config.yaml"
    config.save(config_path)
    return config


@pytest.fixture
def session_manager(temp_dir):
    """Create test session manager."""
    storage_path = temp_dir / "sessions"
    return SessionManager(storage_path=storage_path)


@pytest.fixture
def key_manager(temp_dir):
    """Create test key manager."""
    storage_path = temp_dir / "keys"
    return KeyManager(storage_path=storage_path)
