#!/usr/bin/env python3
"""
Encryption utilities for Decentra Chat Server
Handles encryption/decryption of sensitive data like SMTP passwords
"""

from __future__ import annotations

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        """Initialize encryption manager with a key from environment or generated."""
        # Get encryption key from environment or generate one
        self.encryption_key = self._get_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_generate_key(self) -> bytes:
        """
        Get encryption key from environment variable or generate a new one.
        
        The key is derived from DECENTRA_ENCRYPTION_KEY environment variable.
        If not set, a default key is derived from a fixed salt (NOT SECURE for production).
        
        Returns:
            bytes: Fernet encryption key
        """
        # Try to get key from environment
        env_key = os.getenv('DECENTRA_ENCRYPTION_KEY')
        
        if env_key:
            # Derive a proper Fernet key from the environment variable
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'decentra_smtp_salt',  # Fixed salt for deterministic key derivation
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(env_key.encode()))
            return key
        else:
            # For development/testing: generate a deterministic key
            # WARNING: In production, you should set DECENTRA_ENCRYPTION_KEY environment variable
            print("[Security Warning] DECENTRA_ENCRYPTION_KEY not set. Using default encryption key.")
            print("[Security Warning] Set DECENTRA_ENCRYPTION_KEY environment variable for production use.")
            
            # Use a fixed passphrase to generate a deterministic key
            # This ensures encrypted data can be decrypted across server restarts
            default_passphrase = "decentra_default_passphrase_change_in_production"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'decentra_smtp_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(default_passphrase.encode()))
            return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            str: Base64-encoded encrypted string
        """
        if not plaintext:
            return ''
        
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"[Encryption] Error encrypting data: {e}")
            return plaintext  # Fallback to plaintext on error
    
    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted: Base64-encoded encrypted string
            
        Returns:
            str: Decrypted plaintext string
        """
        if not encrypted:
            return ''
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # If decryption fails, it might be plaintext (for backward compatibility)
            print(f"[Encryption] Error decrypting data (might be plaintext): {e}")
            return encrypted  # Return as-is if decryption fails
    
    def is_encrypted(self, data: str) -> bool:
        """
        Check if data appears to be encrypted.
        
        Args:
            data: String to check
            
        Returns:
            bool: True if data appears to be encrypted
        """
        if not data:
            return False
        
        try:
            # Try to decode as base64 and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(data.encode('utf-8'))
            self.fernet.decrypt(encrypted_bytes)
            return True
        except Exception:
            return False


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """
    Get or create the global encryption manager instance.
    
    Returns:
        EncryptionManager: Global encryption manager
    """
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager
