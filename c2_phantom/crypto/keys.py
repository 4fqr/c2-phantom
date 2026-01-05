"""
Key management for C2 Phantom.

Handles key generation, storage, and retrieval with secure key storage.
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

import keyring
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend

from c2_phantom.core.exceptions import EncryptionError


@dataclass
class KeyPair:
    """Represents a cryptographic key pair."""

    public_key: bytes
    private_key: bytes
    algorithm: str
    key_size: Optional[int] = None


class KeyManager:
    """Manages cryptographic keys with secure storage."""

    SERVICE_NAME = "c2-phantom"

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        """
        Initialize key manager.

        Args:
            storage_path: Optional custom storage path for keys
        """
        if storage_path is None:
            home = Path.home()
            storage_path = home / ".phantom" / "keys"

        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def generate_rsa_keypair(self, key_size: int = 4096) -> KeyPair:
        """
        Generate RSA key pair.

        Args:
            key_size: RSA key size in bits

        Returns:
            KeyPair instance
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=key_size, backend=default_backend()
            )
            public_key = private_key.public_key()

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return KeyPair(
                public_key=public_pem,
                private_key=private_pem,
                algorithm="rsa",
                key_size=key_size,
            )
        except Exception as e:
            raise EncryptionError(f"Failed to generate RSA key pair: {str(e)}")

    def generate_ecc_keypair(self, curve: ec.EllipticCurve = ec.SECP384R1()) -> KeyPair:
        """
        Generate ECC key pair.

        Args:
            curve: Elliptic curve to use

        Returns:
            KeyPair instance
        """
        try:
            private_key = ec.generate_private_key(curve, default_backend())
            public_key = private_key.public_key()

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return KeyPair(
                public_key=public_pem,
                private_key=private_pem,
                algorithm="ecc",
            )
        except Exception as e:
            raise EncryptionError(f"Failed to generate ECC key pair: {str(e)}")

    def generate_aes_key(self, key_size: int = 256) -> bytes:
        """
        Generate AES key.

        Args:
            key_size: Key size in bits (must be 256)

        Returns:
            AES key bytes
        """
        if key_size != 256:
            raise EncryptionError("Only AES-256 is supported")

        return os.urandom(32)  # 256 bits = 32 bytes

    def save_keypair(self, name: str, keypair: KeyPair, use_keyring: bool = True) -> None:
        """
        Save key pair to storage.

        Args:
            name: Key pair identifier
            keypair: KeyPair to save
            use_keyring: Use system keyring for secure storage
        """
        try:
            if use_keyring:
                # Store private key in system keyring
                keyring.set_password(
                    self.SERVICE_NAME, f"{name}_private", keypair.private_key.decode()
                )

            # Store public key and metadata to file
            metadata = {
                "algorithm": keypair.algorithm,
                "key_size": keypair.key_size,
                "public_key": keypair.public_key.decode(),
            }

            key_file = self.storage_path / f"{name}.json"
            with open(key_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            raise EncryptionError(f"Failed to save key pair: {str(e)}")

    def load_keypair(self, name: str, use_keyring: bool = True) -> KeyPair:
        """
        Load key pair from storage.

        Args:
            name: Key pair identifier
            use_keyring: Load private key from system keyring

        Returns:
            KeyPair instance
        """
        try:
            key_file = self.storage_path / f"{name}.json"
            if not key_file.exists():
                raise EncryptionError(f"Key pair '{name}' not found")

            with open(key_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            if use_keyring:
                private_key_str = keyring.get_password(self.SERVICE_NAME, f"{name}_private")
                if private_key_str is None:
                    raise EncryptionError(f"Private key for '{name}' not found in keyring")
                private_key = private_key_str.encode()
            else:
                # If not using keyring, private key should be in metadata
                private_key = metadata.get("private_key", "").encode()
                if not private_key:
                    raise EncryptionError(f"Private key for '{name}' not found")

            return KeyPair(
                public_key=metadata["public_key"].encode(),
                private_key=private_key,
                algorithm=metadata["algorithm"],
                key_size=metadata.get("key_size"),
            )
        except Exception as e:
            raise EncryptionError(f"Failed to load key pair: {str(e)}")

    def save_aes_key(self, name: str, key: bytes, use_keyring: bool = True) -> None:
        """
        Save AES key to storage.

        Args:
            name: Key identifier
            key: AES key bytes
            use_keyring: Use system keyring for secure storage
        """
        try:
            if use_keyring:
                # Store in system keyring as hex string
                keyring.set_password(self.SERVICE_NAME, f"{name}_aes", key.hex())
            else:
                # Store to file (less secure)
                key_file = self.storage_path / f"{name}_aes.key"
                with open(key_file, "wb") as f:
                    f.write(key)
        except Exception as e:
            raise EncryptionError(f"Failed to save AES key: {str(e)}")

    def load_aes_key(self, name: str, use_keyring: bool = True) -> bytes:
        """
        Load AES key from storage.

        Args:
            name: Key identifier
            use_keyring: Load from system keyring

        Returns:
            AES key bytes
        """
        try:
            if use_keyring:
                key_hex = keyring.get_password(self.SERVICE_NAME, f"{name}_aes")
                if key_hex is None:
                    raise EncryptionError(f"AES key '{name}' not found in keyring")
                return bytes.fromhex(key_hex)
            else:
                key_file = self.storage_path / f"{name}_aes.key"
                if not key_file.exists():
                    raise EncryptionError(f"AES key '{name}' not found")
                with open(key_file, "rb") as f:
                    return f.read()
        except Exception as e:
            raise EncryptionError(f"Failed to load AES key: {str(e)}")

    def delete_keypair(self, name: str, use_keyring: bool = True) -> None:
        """
        Delete key pair from storage.

        Args:
            name: Key pair identifier
            use_keyring: Delete from system keyring
        """
        try:
            # Delete from keyring
            if use_keyring:
                try:
                    keyring.delete_password(self.SERVICE_NAME, f"{name}_private")
                except keyring.errors.PasswordDeleteError:
                    pass

            # Delete metadata file
            key_file = self.storage_path / f"{name}.json"
            if key_file.exists():
                key_file.unlink()

        except Exception as e:
            raise EncryptionError(f"Failed to delete key pair: {str(e)}")

    def list_keys(self) -> list[str]:
        """
        List all stored key names.

        Returns:
            List of key names
        """
        keys = []
        for key_file in self.storage_path.glob("*.json"):
            keys.append(key_file.stem)
        return sorted(keys)
