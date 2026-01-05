"""
Tests for encryption modules.
"""

import pytest

from c2_phantom.crypto.encryption import AESEncryption, RSAEncryption, ECCEncryption, EncryptionManager
from c2_phantom.core.exceptions import EncryptionError


class TestAESEncryption:
    """Tests for AES-256-GCM encryption."""

    def test_key_generation(self):
        """Test AES key generation."""
        key = AESEncryption.generate_key()
        assert len(key) == 32  # 256 bits

    def test_encryption_decryption(self):
        """Test AES encryption and decryption."""
        aes = AESEncryption()
        plaintext = b"Secret message"

        ciphertext, nonce = aes.encrypt(plaintext)
        assert ciphertext != plaintext

        decrypted = aes.decrypt(ciphertext, nonce)
        assert decrypted == plaintext

    def test_encryption_with_associated_data(self):
        """Test AES encryption with associated data."""
        aes = AESEncryption()
        plaintext = b"Secret message"
        associated_data = b"metadata"

        ciphertext, nonce = aes.encrypt(plaintext, associated_data)
        decrypted = aes.decrypt(ciphertext, nonce, associated_data)

        assert decrypted == plaintext

    def test_invalid_key_size(self):
        """Test that invalid key size raises error."""
        with pytest.raises(EncryptionError):
            AESEncryption(key=b"tooshort")

    def test_invalid_authentication(self):
        """Test that tampered ciphertext fails authentication."""
        aes = AESEncryption()
        plaintext = b"Secret message"

        ciphertext, nonce = aes.encrypt(plaintext)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 1
        tampered_ciphertext = bytes(tampered)

        with pytest.raises(EncryptionError):
            aes.decrypt(tampered_ciphertext, nonce)


class TestRSAEncryption:
    """Tests for RSA encryption."""

    def test_encryption_decryption(self):
        """Test RSA encryption and decryption."""
        rsa = RSAEncryption(key_size=2048)  # Use smaller key for speed
        plaintext = b"Secret message"

        ciphertext = rsa.encrypt(plaintext)
        assert ciphertext != plaintext

        decrypted = rsa.decrypt(ciphertext)
        assert decrypted == plaintext

    def test_pem_export(self):
        """Test PEM format export."""
        rsa = RSAEncryption(key_size=2048)

        public_pem = rsa.get_public_key_pem()
        private_pem = rsa.get_private_key_pem()

        assert b"BEGIN PUBLIC KEY" in public_pem
        assert b"BEGIN PRIVATE KEY" in private_pem


class TestECCEncryption:
    """Tests for ECC encryption."""

    def test_key_exchange(self):
        """Test ECDH key exchange."""
        alice = ECCEncryption()
        bob = ECCEncryption()

        # Both derive same shared secret
        alice_shared = alice.generate_shared_key(bob.public_key)
        bob_shared = bob.generate_shared_key(alice.public_key)

        assert alice_shared == bob_shared
        assert len(alice_shared) == 32  # 256 bits

    def test_signing_verification(self):
        """Test ECDSA signing and verification."""
        ecc = ECCEncryption()
        message = b"Important message"

        signature = ecc.sign(message)
        assert ecc.verify(message, signature, ecc.public_key)

    def test_invalid_signature(self):
        """Test that invalid signature fails verification."""
        ecc = ECCEncryption()
        message = b"Important message"

        signature = ecc.sign(message)

        # Tamper with message
        tampered_message = b"Tampered message"

        assert not ecc.verify(tampered_message, signature, ecc.public_key)


class TestEncryptionManager:
    """Tests for encryption manager."""

    def test_aes_encryption(self):
        """Test AES encryption through manager."""
        manager = EncryptionManager("aes256-gcm")
        manager.initialize()

        plaintext = b"Secret message"
        ciphertext, nonce = manager.encrypt(plaintext)

        decrypted = manager.decrypt(ciphertext, nonce)
        assert decrypted == plaintext

    def test_rsa_encryption(self):
        """Test RSA encryption through manager."""
        manager = EncryptionManager("rsa")
        manager.initialize()

        plaintext = b"Secret message"
        ciphertext, _ = manager.encrypt(plaintext)

        decrypted = manager.decrypt(ciphertext, b"")
        assert decrypted == plaintext

    def test_unsupported_algorithm(self):
        """Test that unsupported algorithm raises error."""
        manager = EncryptionManager("invalid")

        with pytest.raises(EncryptionError):
            manager.initialize()
