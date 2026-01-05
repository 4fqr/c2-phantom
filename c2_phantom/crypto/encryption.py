"""
Encryption implementations for C2 Phantom.

Provides AES-256-GCM, RSA, and ECC encryption with Perfect Forward Secrecy.
"""

import os
from typing import Tuple, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

from c2_phantom.core.exceptions import EncryptionError


class AESEncryption:
    """AES-256-GCM encryption implementation."""

    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize AES encryption.

        Args:
            key: Optional 256-bit key (32 bytes). If None, generates new key.
        """
        if key is None:
            key = AESGCM.generate_key(bit_length=256)
        elif len(key) != 32:
            raise EncryptionError("AES key must be 32 bytes (256 bits)")

        self.key = key
        self.cipher = AESGCM(key)

    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data with AES-256-GCM.

        Args:
            plaintext: Data to encrypt
            associated_data: Optional associated data for authentication

        Returns:
            Tuple of (ciphertext, nonce)
        """
        try:
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            ciphertext = self.cipher.encrypt(nonce, plaintext, associated_data)
            return ciphertext, nonce
        except Exception as e:
            raise EncryptionError(f"AES encryption failed: {str(e)}")

    def decrypt(
        self, ciphertext: bytes, nonce: bytes, associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt AES-256-GCM encrypted data.

        Args:
            ciphertext: Encrypted data
            nonce: Nonce used during encryption
            associated_data: Associated data used during encryption

        Returns:
            Decrypted plaintext

        Raises:
            EncryptionError: If decryption or authentication fails
        """
        try:
            plaintext = self.cipher.decrypt(nonce, ciphertext, associated_data)
            return plaintext
        except InvalidTag:
            raise EncryptionError("AES decryption failed: Invalid authentication tag")
        except Exception as e:
            raise EncryptionError(f"AES decryption failed: {str(e)}")

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a new AES-256 key.

        Returns:
            32-byte key
        """
        return AESGCM.generate_key(bit_length=256)


class RSAEncryption:
    """RSA encryption implementation with OAEP padding."""

    def __init__(self, key_size: int = 4096) -> None:
        """
        Initialize RSA encryption.

        Args:
            key_size: RSA key size in bits (default 4096)
        """
        self.key_size = key_size
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=key_size, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt data with RSA-OAEP.

        Args:
            plaintext: Data to encrypt

        Returns:
            Encrypted ciphertext
        """
        try:
            ciphertext = self.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return ciphertext
        except Exception as e:
            raise EncryptionError(f"RSA encryption failed: {str(e)}")

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt RSA-OAEP encrypted data.

        Args:
            ciphertext: Encrypted data

        Returns:
            Decrypted plaintext
        """
        try:
            plaintext = self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return plaintext
        except Exception as e:
            raise EncryptionError(f"RSA decryption failed: {str(e)}")

    def get_public_key_pem(self) -> bytes:
        """
        Get public key in PEM format.

        Returns:
            PEM-encoded public key
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def get_private_key_pem(self, password: Optional[bytes] = None) -> bytes:
        """
        Get private key in PEM format.

        Args:
            password: Optional password for encryption

        Returns:
            PEM-encoded private key
        """
        encryption_algorithm = (
            serialization.BestAvailableEncryption(password)
            if password
            else serialization.NoEncryption()
        )

        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )


class ECCEncryption:
    """Elliptic Curve Cryptography for key exchange and signatures."""

    def __init__(self, curve: ec.EllipticCurve = ec.SECP384R1()) -> None:
        """
        Initialize ECC encryption.

        Args:
            curve: Elliptic curve to use (default SECP384R1)
        """
        self.curve = curve
        self.private_key = ec.generate_private_key(curve, default_backend())
        self.public_key = self.private_key.public_key()

    def generate_shared_key(self, peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
        """
        Generate shared secret using ECDH.

        Args:
            peer_public_key: Peer's public key

        Returns:
            Shared secret (use with KDF for encryption key)
        """
        try:
            from cryptography.hazmat.primitives.kdf.hkdf import HKDF

            shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)

            # Derive encryption key from shared secret
            derived_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b"c2-phantom-ecdh",
                backend=default_backend(),
            ).derive(shared_secret)

            return derived_key
        except Exception as e:
            raise EncryptionError(f"ECDH key exchange failed: {str(e)}")

    def sign(self, message: bytes) -> bytes:
        """
        Sign a message with ECDSA.

        Args:
            message: Message to sign

        Returns:
            Signature
        """
        try:
            signature = self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))
            return signature
        except Exception as e:
            raise EncryptionError(f"ECDSA signing failed: {str(e)}")

    def verify(self, message: bytes, signature: bytes, public_key: ec.EllipticCurvePublicKey) -> bool:
        """
        Verify an ECDSA signature.

        Args:
            message: Original message
            signature: Signature to verify
            public_key: Public key for verification

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    def get_public_key_pem(self) -> bytes:
        """
        Get public key in PEM format.

        Returns:
            PEM-encoded public key
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


class EncryptionManager:
    """Manages encryption operations with algorithm selection."""

    def __init__(self, algorithm: str = "aes256-gcm") -> None:
        """
        Initialize encryption manager.

        Args:
            algorithm: Encryption algorithm to use
        """
        self.algorithm = algorithm.lower()
        self._cipher: Optional[AESEncryption | RSAEncryption | ECCEncryption] = None

    def initialize(self) -> None:
        """Initialize the selected encryption algorithm."""
        if self.algorithm == "aes256-gcm":
            self._cipher = AESEncryption()
        elif self.algorithm == "rsa":
            self._cipher = RSAEncryption()
        elif self.algorithm == "ecc":
            self._cipher = ECCEncryption()
        else:
            raise EncryptionError(f"Unsupported encryption algorithm: {self.algorithm}")

    def encrypt(self, data: bytes, **kwargs) -> Tuple[bytes, bytes]:
        """
        Encrypt data using configured algorithm.

        Args:
            data: Data to encrypt
            **kwargs: Algorithm-specific parameters

        Returns:
            Encrypted data and metadata (e.g., nonce)
        """
        if self._cipher is None:
            self.initialize()

        if isinstance(self._cipher, AESEncryption):
            return self._cipher.encrypt(data, kwargs.get("associated_data"))
        elif isinstance(self._cipher, RSAEncryption):
            return self._cipher.encrypt(data), b""
        else:
            raise EncryptionError(f"Encryption not supported for {self.algorithm}")

    def decrypt(self, ciphertext: bytes, metadata: bytes, **kwargs) -> bytes:
        """
        Decrypt data using configured algorithm.

        Args:
            ciphertext: Encrypted data
            metadata: Encryption metadata (e.g., nonce)
            **kwargs: Algorithm-specific parameters

        Returns:
            Decrypted plaintext
        """
        if self._cipher is None:
            raise EncryptionError("Encryption manager not initialized")

        if isinstance(self._cipher, AESEncryption):
            return self._cipher.decrypt(ciphertext, metadata, kwargs.get("associated_data"))
        elif isinstance(self._cipher, RSAEncryption):
            return self._cipher.decrypt(ciphertext)
        else:
            raise EncryptionError(f"Decryption not supported for {self.algorithm}")
