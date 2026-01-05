"""
Encrypted communication layer for C2 Phantom.

Wraps HTTP traffic with AES-256-GCM encryption for confidentiality and integrity.
"""

import json
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import logging


logger = logging.getLogger(__name__)


class SecureChannel:
    """
    Encrypted communication channel using AES-256-GCM.

    Provides encryption, decryption, and integrity protection for C2 traffic.
    """

    def __init__(self, key: Optional[bytes] = None, password: Optional[str] = None) -> None:
        """
        Initialize secure channel.

        Args:
            key: 32-byte AES key (generated if not provided)
            password: Password to derive key from (if key not provided)
        """
        if key:
            self.key = key
        elif password:
            self.key = self._derive_key(password)
        else:
            self.key = AESGCM.generate_key(bit_length=256)

        self.aesgcm = AESGCM(self.key)

    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive AES key from password using PBKDF2.

        Args:
            password: Password to derive from
            salt: Salt for key derivation

        Returns:
            32-byte derived key
        """
        if salt is None:
            salt = b"c2phantom_default_salt_v1"  # In production, use random salt

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: Dict[str, Any]) -> str:
        """
        Encrypt JSON data.

        Args:
            data: Data dictionary to encrypt

        Returns:
            Base64 encoded encrypted blob
        """
        try:
            # Serialize to JSON
            plaintext = json.dumps(data).encode()

            # Generate nonce
            nonce = os.urandom(12)

            # Encrypt with authenticated encryption
            ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)

            # Combine nonce + ciphertext
            blob = nonce + ciphertext

            # Base64 encode for transmission
            return base64.b64encode(blob).decode()

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt encrypted data.

        Args:
            encrypted_data: Base64 encoded encrypted blob

        Returns:
            Decrypted data dictionary
        """
        try:
            # Decode base64
            blob = base64.b64decode(encrypted_data)

            # Extract nonce and ciphertext
            nonce = blob[:12]
            ciphertext = blob[12:]

            # Decrypt
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)

            # Parse JSON
            return json.loads(plaintext.decode())

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def get_key_b64(self) -> str:
        """Get base64 encoded key for sharing."""
        return base64.b64encode(self.key).decode()

    @staticmethod
    def from_key_b64(key_b64: str) -> "SecureChannel":
        """Create SecureChannel from base64 encoded key."""
        key = base64.b64decode(key_b64)
        return SecureChannel(key=key)


class EncryptedHTTPWrapper:
    """
    Wraps HTTP requests/responses with encryption.

    Transparently encrypts outgoing data and decrypts incoming data.
    """

    def __init__(self, channel: SecureChannel) -> None:
        """
        Initialize encrypted HTTP wrapper.

        Args:
            channel: SecureChannel for encryption
        """
        self.channel = channel

    def encrypt_request(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Encrypt request payload.

        Args:
            data: Request data

        Returns:
            Encrypted payload wrapped in JSON
        """
        encrypted = self.channel.encrypt(data)
        return {"encrypted": encrypted}

    def decrypt_request(self, payload: Dict[str, str]) -> Dict[str, Any]:
        """
        Decrypt request payload.

        Args:
            payload: Encrypted payload

        Returns:
            Decrypted data
        """
        encrypted = payload.get("encrypted")
        if not encrypted:
            raise ValueError("No encrypted data in payload")

        return self.channel.decrypt(encrypted)

    def encrypt_response(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Encrypt response payload.

        Args:
            data: Response data

        Returns:
            Encrypted payload
        """
        encrypted = self.channel.encrypt(data)
        return {"encrypted": encrypted}

    def decrypt_response(self, payload: Dict[str, str]) -> Dict[str, Any]:
        """
        Decrypt response payload.

        Args:
            payload: Encrypted payload

        Returns:
            Decrypted data
        """
        encrypted = payload.get("encrypted")
        if not encrypted:
            raise ValueError("No encrypted data in payload")

        return self.channel.decrypt(encrypted)
