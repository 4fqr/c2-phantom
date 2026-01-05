"""
Session management for C2 Phantom.

Handles active sessions, connection state, and session history.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    CONNECTING = "connecting"
    FAILED = "failed"
    TERMINATED = "terminated"


class Session(BaseModel):
    """Represents a C2 session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session ID")
    target: str = Field(..., description="Target host/IP")
    protocol: str = Field(default="https", description="Connection protocol")
    status: SessionStatus = Field(default=SessionStatus.CONNECTING, description="Session status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    last_seen: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    encryption: str = Field(default="aes256-gcm", description="Encryption algorithm")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def update_last_seen(self) -> None:
        """Update last seen timestamp."""
        self.last_seen = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        data = self.model_dump()
        data["created_at"] = self.created_at.isoformat()
        data["last_seen"] = self.last_seen.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """
        Create session from dictionary.

        Args:
            data: Session data

        Returns:
            Session instance
        """
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "last_seen" in data and isinstance(data["last_seen"], str):
            data["last_seen"] = datetime.fromisoformat(data["last_seen"])
        return cls(**data)


class SessionManager:
    """Manages multiple C2 sessions."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        """
        Initialize session manager.

        Args:
            storage_path: Optional custom storage path
        """
        if storage_path is None:
            home = Path.home()
            storage_path = home / ".phantom" / "sessions"

        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Session] = {}
        self.load_sessions()

    def create_session(
        self,
        target: str,
        protocol: str = "https",
        encryption: str = "aes256-gcm",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            target: Target host/IP
            protocol: Connection protocol
            encryption: Encryption algorithm
            metadata: Additional metadata

        Returns:
            New Session instance
        """
        session = Session(
            target=target, protocol=protocol, encryption=encryption, metadata=metadata or {}
        )
        self.sessions[session.id] = session
        self.save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session instance or None
        """
        return self.sessions.get(session_id)

    def list_sessions(
        self, status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        List sessions, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of sessions
        """
        if status is None:
            return list(self.sessions.values())
        return [s for s in self.sessions.values() if s.status == status]

    def update_session(self, session_id: str, **kwargs: Any) -> Optional[Session]:
        """
        Update session attributes.

        Args:
            session_id: Session ID
            **kwargs: Attributes to update

        Returns:
            Updated Session instance or None
        """
        session = self.sessions.get(session_id)
        if session is None:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.update_last_seen()
        self.save_session(session)
        return session

    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a session.

        Args:
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if session is None:
            return False

        session.status = SessionStatus.TERMINATED
        self.save_session(session)
        return True

    def save_session(self, session: Session) -> None:
        """
        Save session to disk.

        Args:
            session: Session to save
        """
        session_file = self.storage_path / f"{session.id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_sessions(self) -> None:
        """Load all sessions from disk."""
        for session_file in self.storage_path.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = Session.from_dict(data)
                self.sessions[session.id] = session
            except Exception:
                # Skip corrupted session files
                continue

    def get_active_count(self) -> int:
        """
        Get count of active sessions.

        Returns:
            Number of active sessions
        """
        return len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE])
