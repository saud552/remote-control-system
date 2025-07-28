"""
Secure Connection System
Provides encrypted and secure communication with devices
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import ssl
import time
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

class SecureConnection:
    """Secure connection manager with encryption"""
    
    def __init__(self):
        self.encryption_key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
        self.rsa_private_key: Optional[rsa.RSAPrivateKey] = None
        self.rsa_public_key: Optional[rsa.RSAPublicKey] = None
        self.session_tokens: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self._initialize_encryption()
        self._generate_rsa_keys()
    
    def _initialize_encryption(self):
        """Initialize encryption system"""
        try:
            # Generate or load encryption key
            key_file = "encryption_key.key"
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self.encryption_key)
            
            self.fernet = Fernet(self.encryption_key)
            self.logger.info("Encryption system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {str(e)}")
    
    def _generate_rsa_keys(self):
        """Generate RSA key pair for asymmetric encryption"""
        try:
            # Generate private key
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Get public key
            self.rsa_public_key = self.rsa_private_key.public_key()
            
            self.logger.info("RSA key pair generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating RSA keys: {str(e)}")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet"""
        try:
            if not self.fernet:
                raise Exception("Encryption not initialized")
            
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        try:
            if not self.fernet:
                raise Exception("Encryption not initialized")
            
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            return encrypted_data
    
    def encrypt_with_rsa(self, data: str) -> str:
        """Encrypt data using RSA public key"""
        try:
            if not self.rsa_public_key:
                raise Exception("RSA keys not initialized")
            
            encrypted_data = self.rsa_public_key.encrypt(
                data.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Error encrypting with RSA: {str(e)}")
            return data
    
    def decrypt_with_rsa(self, encrypted_data: str) -> str:
        """Decrypt data using RSA private key"""
        try:
            if not self.rsa_private_key:
                raise Exception("RSA keys not initialized")
            
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.rsa_private_key.decrypt(
                decoded_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Error decrypting with RSA: {str(e)}")
            return encrypted_data
    
    def generate_session_token(self, device_id: str) -> str:
        """Generate secure session token"""
        try:
            # Generate random token
            token = secrets.token_urlsafe(32)
            
            # Create session data
            session_data = {
                "device_id": device_id,
                "token": token,
                "created_at": time.time(),
                "expires_at": time.time() + (24 * 60 * 60),  # 24 hours
                "permissions": ["read", "write", "execute"]
            }
            
            # Store session
            self.session_tokens[token] = session_data
            
            self.logger.info(f"Generated session token for device {device_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Error generating session token: {str(e)}")
            return ""
    
    def validate_session_token(self, token: str) -> bool:
        """Validate session token"""
        try:
            if token not in self.session_tokens:
                return False
            
            session = self.session_tokens[token]
            
            # Check if token is expired
            if time.time() > session["expires_at"]:
                del self.session_tokens[token]
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating session token: {str(e)}")
            return False
    
    def revoke_session_token(self, token: str) -> bool:
        """Revoke session token"""
        try:
            if token in self.session_tokens:
                del self.session_tokens[token]
                self.logger.info(f"Revoked session token: {token}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error revoking session token: {str(e)}")
            return False
    
    def create_secure_channel(self, device_id: str) -> Dict:
        """Create secure communication channel"""
        try:
            # Generate session token
            token = self.generate_session_token(device_id)
            
            # Create channel configuration
            channel_config = {
                "device_id": device_id,
                "session_token": token,
                "encryption_type": "AES-256",
                "key_exchange": "RSA-2048",
                "created_at": time.time(),
                "expires_at": time.time() + (24 * 60 * 60),
                "protocol_version": "1.0"
            }
            
            self.logger.info(f"Created secure channel for device {device_id}")
            return channel_config
            
        except Exception as e:
            self.logger.error(f"Error creating secure channel: {str(e)}")
            return {}
    
    def encrypt_message(self, message: str, device_id: str) -> Dict:
        """Encrypt message for secure transmission"""
        try:
            # Create message envelope
            message_envelope = {
                "device_id": device_id,
                "timestamp": time.time(),
                "message_id": secrets.token_urlsafe(16),
                "data": message,
                "checksum": self._calculate_checksum(message)
            }
            
            # Encrypt the envelope
            encrypted_envelope = self.encrypt_data(json.dumps(message_envelope))
            
            return {
                "encrypted_data": encrypted_envelope,
                "timestamp": time.time(),
                "message_id": message_envelope["message_id"]
            }
            
        except Exception as e:
            self.logger.error(f"Error encrypting message: {str(e)}")
            return {"error": "Encryption failed"}
    
    def decrypt_message(self, encrypted_message: Dict) -> Dict:
        """Decrypt received message"""
        try:
            if "encrypted_data" not in encrypted_message:
                return {"error": "Invalid message format"}
            
            # Decrypt the envelope
            decrypted_envelope = self.decrypt_data(encrypted_message["encrypted_data"])
            message_envelope = json.loads(decrypted_envelope)
            
            # Verify checksum
            if not self._verify_checksum(message_envelope["data"], message_envelope["checksum"]):
                return {"error": "Message integrity check failed"}
            
            return {
                "device_id": message_envelope["device_id"],
                "timestamp": message_envelope["timestamp"],
                "message_id": message_envelope["message_id"],
                "data": message_envelope["data"]
            }
            
        except Exception as e:
            self.logger.error(f"Error decrypting message: {str(e)}")
            return {"error": "Decryption failed"}
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _verify_checksum(self, data: str, checksum: str) -> bool:
        """Verify data integrity using checksum"""
        calculated_checksum = self._calculate_checksum(data)
        return hmac.compare_digest(calculated_checksum, checksum)
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format"""
        try:
            if not self.rsa_public_key:
                return ""
            
            pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem.decode()
            
        except Exception as e:
            self.logger.error(f"Error getting public key: {str(e)}")
            return ""
    
    def export_connection_stats(self) -> Dict:
        """Export connection statistics"""
        active_sessions = len(self.session_tokens)
        expired_sessions = 0
        
        current_time = time.time()
        for session in self.session_tokens.values():
            if current_time > session["expires_at"]:
                expired_sessions += 1
        
        return {
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "total_sessions": active_sessions + expired_sessions,
            "encryption_initialized": self.fernet is not None,
            "rsa_keys_generated": self.rsa_private_key is not None
        }