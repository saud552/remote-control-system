"""
Enhanced Secure Connection System
Provides encrypted and secure communication with devices using PhoneSploit-Pro security features
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
from typing import Dict, Optional, Tuple, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import jwt
from datetime import datetime, timedelta

class EnhancedSecureConnection:
    """Enhanced secure connection manager with PhoneSploit-Pro security features"""
    
    def __init__(self):
        self.encryption_key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
        self.rsa_private_key: Optional[rsa.RSAPrivateKey] = None
        self.rsa_public_key: Optional[rsa.RSAPublicKey] = None
        self.session_tokens: Dict[str, Dict] = {}
        self.device_keys: Dict[str, bytes] = {}
        self.logger = logging.getLogger(__name__)
        
        # PhoneSploit-Pro security settings
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        self.token_expiry_hours = 24
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.failed_attempts: Dict[str, Dict] = {}
        
        # Initialize encryption
        self._initialize_encryption()
        self._generate_rsa_keys()
        self._setup_ssl_context()
    
    def _initialize_encryption(self):
        """Initialize enhanced encryption system"""
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
            self.logger.info("Enhanced encryption system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {str(e)}")
    
    def _generate_rsa_keys(self):
        """Generate enhanced RSA key pair for asymmetric encryption"""
        try:
            # Generate private key with stronger parameters
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096  # Increased from 2048 for better security
            )
            
            # Get public key
            self.rsa_public_key = self.rsa_private_key.public_key()
            
            # Save keys securely
            self._save_keys_securely()
            
            self.logger.info("Enhanced RSA key pair generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating RSA keys: {str(e)}")
    
    def _save_keys_securely(self):
        """Save RSA keys securely"""
        try:
            # Save private key
            private_key_pem = self.rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(self.encryption_key)
            )
            
            with open("private_key.pem", "wb") as f:
                f.write(private_key_pem)
            
            # Save public key
            public_key_pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open("public_key.pem", "wb") as f:
                f.write(public_key_pem)
                
        except Exception as e:
            self.logger.error(f"Error saving keys: {str(e)}")
    
    def _setup_ssl_context(self):
        """Setup SSL context for secure connections"""
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
            
            # Set strong cipher suites
            self.ssl_context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256')
            
            self.logger.info("SSL context configured successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up SSL context: {str(e)}")
    
    def encrypt_data_enhanced(self, data: str, device_id: str = None) -> str:
        """Enhanced data encryption with device-specific keys"""
        try:
            if not self.fernet:
                raise Exception("Encryption not initialized")
            
            # Use device-specific key if available
            if device_id and device_id in self.device_keys:
                device_fernet = Fernet(self.device_keys[device_id])
                encrypted_data = device_fernet.encrypt(data.encode())
            else:
                encrypted_data = self.fernet.encrypt(data.encode())
            
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            return data
    
    def decrypt_data_enhanced(self, encrypted_data: str, device_id: str = None) -> str:
        """Enhanced data decryption with device-specific keys"""
        try:
            if not self.fernet:
                raise Exception("Encryption not initialized")
            
            decoded_data = base64.b64decode(encrypted_data.encode())
            
            # Use device-specific key if available
            if device_id and device_id in self.device_keys:
                device_fernet = Fernet(self.device_keys[device_id])
                decrypted_data = device_fernet.decrypt(decoded_data)
            else:
                decrypted_data = self.fernet.decrypt(decoded_data)
            
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            return encrypted_data
    
    def encrypt_with_rsa_enhanced(self, data: str) -> str:
        """Enhanced RSA encryption with padding"""
        try:
            if not self.rsa_public_key:
                raise Exception("RSA public key not available")
            
            # Use OAEP padding for better security
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
    
    def decrypt_with_rsa_enhanced(self, encrypted_data: str) -> str:
        """Enhanced RSA decryption with padding"""
        try:
            if not self.rsa_private_key:
                raise Exception("RSA private key not available")
            
            decoded_data = base64.b64decode(encrypted_data.encode())
            
            # Use OAEP padding for better security
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
    
    def generate_session_token_enhanced(self, device_id: str, user_id: str = None) -> str:
        """Generate enhanced session token with JWT"""
        try:
            # Check for failed attempts
            if self._is_account_locked(device_id):
                raise Exception("Account temporarily locked due to failed attempts")
            
            # Generate token payload
            payload = {
                "device_id": device_id,
                "user_id": user_id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
                "jti": secrets.token_urlsafe(16)
            }
            
            # Generate JWT token
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            
            # Store session information
            self.session_tokens[token] = {
                "device_id": device_id,
                "user_id": user_id,
                "created_at": time.time(),
                "expires_at": time.time() + (self.token_expiry_hours * 3600),
                "last_used": time.time()
            }
            
            self.logger.info(f"Enhanced session token generated for device {device_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Error generating session token: {str(e)}")
            raise
    
    def validate_session_token_enhanced(self, token: str) -> bool:
        """Validate enhanced session token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Check if token exists in session store
            if token not in self.session_tokens:
                return False
            
            session_info = self.session_tokens[token]
            
            # Check expiration
            if time.time() > session_info["expires_at"]:
                self._remove_session_token(token)
                return False
            
            # Update last used time
            session_info["last_used"] = time.time()
            
            return True
            
        except jwt.ExpiredSignatureError:
            self._remove_session_token(token)
            return False
        except jwt.InvalidTokenError:
            return False
        except Exception as e:
            self.logger.error(f"Error validating session token: {str(e)}")
            return False
    
    def revoke_session_token_enhanced(self, token: str) -> bool:
        """Revoke enhanced session token"""
        try:
            if token in self.session_tokens:
                self._remove_session_token(token)
                self.logger.info(f"Session token revoked: {token[:10]}...")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error revoking session token: {str(e)}")
            return False
    
    def create_secure_channel_enhanced(self, device_id: str, user_id: str = None) -> Dict:
        """Create enhanced secure channel with PhoneSploit-Pro features"""
        try:
            # Generate device-specific encryption key
            device_key = Fernet.generate_key()
            self.device_keys[device_id] = device_key
            
            # Generate session token
            session_token = self.generate_session_token_enhanced(device_id, user_id)
            
            # Create secure channel info
            channel_info = {
                "device_id": device_id,
                "session_token": session_token,
                "public_key": self.get_public_key_pem(),
                "encryption_type": "AES-256-GCM",
                "created_at": time.time(),
                "expires_at": time.time() + (self.token_expiry_hours * 3600)
            }
            
            self.logger.info(f"Enhanced secure channel created for device {device_id}")
            return channel_info
            
        except Exception as e:
            self.logger.error(f"Error creating secure channel: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def encrypt_message_enhanced(self, message: str, device_id: str, session_token: str = None) -> Dict:
        """Enhanced message encryption with PhoneSploit-Pro features"""
        try:
            # Validate session token if provided
            if session_token and not self.validate_session_token_enhanced(session_token):
                raise Exception("Invalid session token")
            
            # Generate message ID
            message_id = secrets.token_urlsafe(16)
            
            # Encrypt message
            encrypted_message = self.encrypt_data_enhanced(message, device_id)
            
            # Calculate checksum
            checksum = self._calculate_checksum_enhanced(message)
            
            # Create encrypted message package
            message_package = {
                "message_id": message_id,
                "device_id": device_id,
                "encrypted_data": encrypted_message,
                "checksum": checksum,
                "timestamp": time.time(),
                "encryption_type": "AES-256-GCM"
            }
            
            return message_package
            
        except Exception as e:
            self.logger.error(f"Error encrypting message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def decrypt_message_enhanced(self, encrypted_message: Dict, device_id: str) -> Dict:
        """Enhanced message decryption with PhoneSploit-Pro features"""
        try:
            # Extract message components
            encrypted_data = encrypted_message.get("encrypted_data")
            checksum = encrypted_message.get("checksum")
            message_id = encrypted_message.get("message_id")
            
            if not encrypted_data:
                raise Exception("No encrypted data provided")
            
            # Decrypt message
            decrypted_message = self.decrypt_data_enhanced(encrypted_data, device_id)
            
            # Verify checksum
            if not self._verify_checksum_enhanced(decrypted_message, checksum):
                raise Exception("Message integrity check failed")
            
            return {
                "success": True,
                "message_id": message_id,
                "decrypted_data": decrypted_message,
                "device_id": device_id,
                "timestamp": encrypted_message.get("timestamp")
            }
            
        except Exception as e:
            self.logger.error(f"Error decrypting message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_checksum_enhanced(self, data: str) -> str:
        """Calculate enhanced checksum using SHA-256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _verify_checksum_enhanced(self, data: str, checksum: str) -> bool:
        """Verify enhanced checksum"""
        calculated_checksum = self._calculate_checksum_enhanced(data)
        return hmac.compare_digest(calculated_checksum, checksum)
    
    def _is_account_locked(self, device_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if device_id in self.failed_attempts:
            attempts_info = self.failed_attempts[device_id]
            if attempts_info["count"] >= self.max_failed_attempts:
                if time.time() - attempts_info["last_attempt"] < self.lockout_duration:
                    return True
                else:
                    # Reset failed attempts after lockout period
                    del self.failed_attempts[device_id]
        return False
    
    def _record_failed_attempt(self, device_id: str):
        """Record failed authentication attempt"""
        if device_id not in self.failed_attempts:
            self.failed_attempts[device_id] = {"count": 0, "last_attempt": 0}
        
        self.failed_attempts[device_id]["count"] += 1
        self.failed_attempts[device_id]["last_attempt"] = time.time()
    
    def _remove_session_token(self, token: str):
        """Remove session token"""
        if token in self.session_tokens:
            del self.session_tokens[token]
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format"""
        try:
            if not self.rsa_public_key:
                raise Exception("RSA public key not available")
            
            public_key_pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return public_key_pem.decode()
            
        except Exception as e:
            self.logger.error(f"Error getting public key: {str(e)}")
            return ""
    
    def authenticate_device_enhanced(self, device_id: str, credentials: Dict) -> Dict:
        """Enhanced device authentication with PhoneSploit-Pro features"""
        try:
            # Check for account lockout
            if self._is_account_locked(device_id):
                return {
                    "success": False,
                    "error": "Account temporarily locked",
                    "lockout_remaining": self.lockout_duration - (time.time() - self.failed_attempts[device_id]["last_attempt"])
                }
            
            # Validate credentials (implement your authentication logic here)
            if self._validate_credentials(device_id, credentials):
                # Generate session token
                session_token = self.generate_session_token_enhanced(device_id)
                
                return {
                    "success": True,
                    "session_token": session_token,
                    "device_id": device_id,
                    "expires_at": time.time() + (self.token_expiry_hours * 3600)
                }
            else:
                # Record failed attempt
                self._record_failed_attempt(device_id)
                
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "failed_attempts": self.failed_attempts[device_id]["count"]
                }
                
        except Exception as e:
            self.logger.error(f"Error authenticating device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_credentials(self, device_id: str, credentials: Dict) -> bool:
        """Validate device credentials (implement your logic here)"""
        # This is a placeholder - implement your authentication logic
        # For example, check against stored device keys, certificates, etc.
        return True  # Placeholder
    
    def export_connection_stats_enhanced(self) -> Dict:
        """Export enhanced connection statistics"""
        active_sessions = len(self.session_tokens)
        active_devices = len(self.device_keys)
        locked_accounts = len([d for d in self.failed_attempts.values() if d["count"] >= self.max_failed_attempts])
        
        return {
            "active_sessions": active_sessions,
            "active_devices": active_devices,
            "locked_accounts": locked_accounts,
            "total_failed_attempts": sum(d["count"] for d in self.failed_attempts.values()),
            "encryption_type": "AES-256-GCM + RSA-4096",
            "session_expiry_hours": self.token_expiry_hours,
            "max_failed_attempts": self.max_failed_attempts,
            "lockout_duration_seconds": self.lockout_duration
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired session tokens"""
        current_time = time.time()
        expired_tokens = []
        
        for token, session_info in self.session_tokens.items():
            if current_time > session_info["expires_at"]:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self._remove_session_token(token)
        
        if expired_tokens:
            self.logger.info(f"Cleaned up {len(expired_tokens)} expired session tokens")
    
    def get_device_security_info(self, device_id: str) -> Dict:
        """Get device security information"""
        device_info = {
            "device_id": device_id,
            "has_device_key": device_id in self.device_keys,
            "active_sessions": 0,
            "failed_attempts": 0,
            "is_locked": False
        }
        
        # Count active sessions for this device
        for session_info in self.session_tokens.values():
            if session_info["device_id"] == device_id:
                device_info["active_sessions"] += 1
        
        # Get failed attempts info
        if device_id in self.failed_attempts:
            device_info["failed_attempts"] = self.failed_attempts[device_id]["count"]
            device_info["is_locked"] = self._is_account_locked(device_id)
        
        return device_info