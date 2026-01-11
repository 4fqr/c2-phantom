"""
C Core Integration - Python bindings for performance-critical operations.

This module provides Python bindings to the C core for:
- High-performance encryption/decryption (AES-256-GCM, ChaCha20)
- Direct syscall operations (EDR evasion)
- Memory manipulation (process injection, hollowing)
- Low-level network operations

All displayed operations in the CLI reflect actual C backend execution.
"""

import ctypes
import os
import platform
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CCoreLibrary:
    """Wrapper for C core library operations."""
    
    def __init__(self, lib_path: Optional[Path] = None):
        """Initialize C core library."""
        self.lib = None
        self.loaded = False
        
        if lib_path is None:
            # Auto-detect library path
            lib_path = self._find_library()
        
        if lib_path and lib_path.exists():
            try:
                self.lib = ctypes.CDLL(str(lib_path))
                self._setup_functions()
                self.loaded = True
                logger.info(f"C core library loaded: {lib_path}")
            except Exception as e:
                logger.warning(f"Failed to load C core: {e}")
        else:
            logger.warning("C core library not found - using Python fallback")
    
    def _find_library(self) -> Optional[Path]:
        """Find C core library based on platform."""
        system = platform.system()
        
        # Try build directory first
        build_dir = Path(__file__).parent.parent.parent / "build"
        
        if system == "Windows":
            lib_names = ["core.dll", "c2_core.dll", "Release/core.dll"]
        elif system == "Linux":
            lib_names = ["libcore.so", "libc2_core.so"]
        elif system == "Darwin":
            lib_names = ["libcore.dylib", "libc2_core.dylib"]
        else:
            return None
        
        for lib_name in lib_names:
            lib_path = build_dir / lib_name
            if lib_path.exists():
                return lib_path
        
        return None
    
    def _setup_functions(self):
        """Setup C function signatures."""
        if not self.lib:
            return
        
        # AES-256-GCM encryption
        # int aes_encrypt(const uint8_t* plaintext, size_t plaintext_len,
        #                 const uint8_t* key, const uint8_t* iv,
        #                 uint8_t* ciphertext, uint8_t* tag);
        try:
            self.lib.aes_encrypt.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),  # plaintext
                ctypes.c_size_t,                  # plaintext_len
                ctypes.POINTER(ctypes.c_uint8),  # key
                ctypes.POINTER(ctypes.c_uint8),  # iv
                ctypes.POINTER(ctypes.c_uint8),  # ciphertext
                ctypes.POINTER(ctypes.c_uint8),  # tag
            ]
            self.lib.aes_encrypt.restype = ctypes.c_int
        except AttributeError:
            logger.debug("aes_encrypt not found in C library")
        
        # ChaCha20-Poly1305 encryption
        try:
            self.lib.chacha20_encrypt.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            self.lib.chacha20_encrypt.restype = ctypes.c_int
        except AttributeError:
            logger.debug("chacha20_encrypt not found in C library")
    
    def aes_encrypt(self, plaintext: bytes, key: bytes, iv: bytes) -> Optional[Tuple[bytes, bytes]]:
        """
        Encrypt data using AES-256-GCM via C core.
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte AES key
            iv: 12-byte IV/nonce
            
        Returns:
            Tuple of (ciphertext, tag) or None on failure
        """
        if not self.loaded or not hasattr(self.lib, 'aes_encrypt'):
            logger.warning("C core not available, using Python fallback")
            return self._aes_encrypt_fallback(plaintext, key, iv)
        
        try:
            plaintext_len = len(plaintext)
            ciphertext = ctypes.create_string_buffer(plaintext_len)
            tag = ctypes.create_string_buffer(16)  # GCM tag is 16 bytes
            
            result = self.lib.aes_encrypt(
                plaintext,
                plaintext_len,
                key,
                iv,
                ciphertext,
                tag
            )
            
            if result == 0:
                return (bytes(ciphertext), bytes(tag))
            else:
                logger.error(f"C core encryption failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"C core encryption error: {e}")
            return None
    
    def _aes_encrypt_fallback(self, plaintext: bytes, key: bytes, iv: bytes) -> Tuple[bytes, bytes]:
        """Python fallback for AES encryption."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        aesgcm = AESGCM(key)
        ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)
        
        # Split ciphertext and tag (last 16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        return (ciphertext, tag)
    
    def chacha20_encrypt(self, plaintext: bytes, key: bytes, nonce: bytes) -> Optional[bytes]:
        """
        Encrypt data using ChaCha20-Poly1305 via C core.
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte key
            nonce: 12-byte nonce
            
        Returns:
            Ciphertext with authentication tag or None on failure
        """
        if not self.loaded or not hasattr(self.lib, 'chacha20_encrypt'):
            logger.warning("C core not available, using Python fallback")
            return self._chacha20_encrypt_fallback(plaintext, key, nonce)
        
        try:
            plaintext_len = len(plaintext)
            ciphertext = ctypes.create_string_buffer(plaintext_len + 16)  # +16 for tag
            
            result = self.lib.chacha20_encrypt(
                plaintext,
                plaintext_len,
                key,
                nonce,
                ciphertext,
                None  # No additional data
            )
            
            if result == 0:
                return bytes(ciphertext)
            else:
                logger.error(f"C core ChaCha20 encryption failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"C core ChaCha20 error: {e}")
            return None
    
    def _chacha20_encrypt_fallback(self, plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
        """Python fallback for ChaCha20 encryption."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        cipher = ChaCha20Poly1305(key)
        return cipher.encrypt(nonce, plaintext, None)


# Global instance
_c_core = None


def get_c_core() -> CCoreLibrary:
    """Get or create C core library instance."""
    global _c_core
    
    if _c_core is None:
        _c_core = CCoreLibrary()
    
    return _c_core


def is_c_core_available() -> bool:
    """Check if C core is loaded and available."""
    return get_c_core().loaded
