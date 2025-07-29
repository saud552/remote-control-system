"""
Advanced Crypto Cracking Module
Advanced encryption cracking with HashBuster and crypto tools integration
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
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import socket
import re
import hashlib
import hmac
import binascii
import struct
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

@dataclass
class CryptoCrackingConfig:
    """Crypto cracking configuration"""
    target_file: str
    hash_type: str
    wordlist_path: str
    attack_mode: str
    custom_options: Dict
    brute_force: bool
    dictionary_attack: bool
    rainbow_table: bool
    gpu_acceleration: bool

@dataclass
class CryptoAttack:
    """Crypto attack information"""
    attack_id: str
    config: CryptoCrackingConfig
    status: str
    start_time: float
    end_time: Optional[float]
    cracked_hashes: List[Dict]
    tool_used: str
    success_rate: float
    cracked_count: int
    total_count: int

class AdvancedCryptoCrackingModule:
    """Advanced crypto cracking module with HashBuster and crypto tools integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_attacks: Dict[str, CryptoAttack] = {}
        self.attack_history: List[Dict] = []
        
        # Crypto cracking tools configuration
        self.crypto_tools = {
            "hashbuster": {
                "path": "external_tools/hashbuster",
                "executable": "python hashbuster.py",
                "supported_attacks": ["dictionary", "brute_force", "rainbow_table"],
                "capabilities": ["hash_cracking", "password_recovery", "hash_identification"]
            },
            "john": {
                "path": "/usr/bin/john",
                "executable": "john",
                "supported_attacks": ["dictionary", "brute_force", "incremental"],
                "capabilities": ["hash_cracking", "password_recovery", "format_detection"]
            },
            "hashcat": {
                "path": "/usr/bin/hashcat",
                "executable": "hashcat",
                "supported_attacks": ["dictionary", "brute_force", "mask_attack", "hybrid"],
                "capabilities": ["hash_cracking", "gpu_acceleration", "multi_hash"]
            },
            "fcrackzip": {
                "path": "/usr/bin/fcrackzip",
                "executable": "fcrackzip",
                "supported_attacks": ["dictionary", "brute_force"],
                "capabilities": ["zip_cracking", "password_recovery"]
            }
        }
        
        # Initialize tools
        self._initialize_crypto_tools()
    
    def _initialize_crypto_tools(self):
        """Initialize crypto cracking tools"""
        for tool_name, tool_config in self.crypto_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"Crypto tool {tool_name} not found at {tool_path}")
                # Use local directory instead of system paths
                local_tool_path = f"tools/{tool_name}"
                os.makedirs(local_tool_path, exist_ok=True)
                self._clone_crypto_tool(tool_name, local_tool_path)
                # Update tool path
                self.crypto_tools[tool_name]["path"] = local_tool_path
    
    def _clone_crypto_tool(self, tool_name: str, tool_path: str):
        """Clone crypto cracking tool from repository"""
        try:
            if tool_name == "hashbuster":
                repo_url = "https://github.com/s0md3v/Hash-Buster.git"
            else:
                return
            
            # Remove existing directory if it exists
            if os.path.exists(tool_path):
                import shutil
                shutil.rmtree(tool_path)
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Setup tool
            if tool_name == "hashbuster":
                # Install dependencies
                requirements_file = os.path.join(tool_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    subprocess.run([
                        "pip", "install", "-r", requirements_file
                    ], cwd=tool_path, check=True)
                
                # Make executable
                subprocess.run([
                    "chmod", "+x", "hashbuster.py"
                ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def start_crypto_attack(self, config: CryptoCrackingConfig, tool: str = "auto") -> Dict:
        """Start crypto cracking attack"""
        try:
            # Auto-select best tool based on attack type
            if tool == "auto":
                tool = self._select_best_crypto_tool(config.attack_mode)
            
            attack_id = f"crypto_{int(time.time())}_{hashlib.md5(f'{config.target_file}_{config.attack_mode}'.encode()).hexdigest()[:8]}"
            
            # Validate configuration
            validation_result = self._validate_crypto_config(config, tool)
            if not validation_result["success"]:
                return validation_result
            
            # Create attack
            attack = CryptoAttack(
                attack_id=attack_id,
                config=config,
                status="starting",
                start_time=time.time(),
                end_time=None,
                cracked_hashes=[],
                tool_used=tool,
                success_rate=0.0,
                cracked_count=0,
                total_count=0
            )
            
            # Start attack
            start_result = await self._start_crypto_attack(attack)
            if start_result["success"]:
                attack.status = "active"
                self.active_attacks[attack_id] = attack
                
                # Log attack
                self.attack_history.append(asdict(attack))
                
                return {
                    "success": True,
                    "attack_id": attack_id,
                    "tool_used": tool,
                    "message": f"Crypto attack started successfully"
                }
            else:
                return start_result
                
        except Exception as e:
            self.logger.error(f"Error starting crypto attack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_crypto_tool(self, attack_mode: str) -> str:
        """Select best crypto tool for attack mode"""
        if attack_mode in ["dictionary", "brute_force"]:
            return "hashcat"  # Best for dictionary and brute force
        elif attack_mode in ["rainbow_table"]:
            return "hashbuster"  # Best for rainbow table attacks
        elif attack_mode in ["incremental"]:
            return "john"  # Best for incremental attacks
        elif attack_mode in ["zip_cracking"]:
            return "fcrackzip"  # Best for ZIP cracking
        else:
            return "hashcat"  # Default
    
    def _validate_crypto_config(self, config: CryptoCrackingConfig, tool: str) -> Dict:
        """Validate crypto attack configuration"""
        try:
            tool_config = self.crypto_tools[tool]
            
            # Check if attack mode is supported
            if config.attack_mode not in tool_config["supported_attacks"]:
                return {
                    "success": False,
                    "error": f"Attack mode {config.attack_mode} not supported by {tool}"
                }
            
            # Validate target file
            if not config.target_file or not os.path.exists(config.target_file):
                return {
                    "success": False,
                    "error": "Valid target file is required"
                }
            
            # Validate wordlist if required
            if config.dictionary_attack and (not config.wordlist_path or not os.path.exists(config.wordlist_path)):
                return {
                    "success": False,
                    "error": "Valid wordlist path is required for dictionary attack"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_crypto_attack(self, attack: CryptoAttack) -> Dict:
        """Start crypto attack using specific tool"""
        try:
            if attack.tool_used == "hashbuster":
                return await self._start_hashbuster_attack(attack)
            elif attack.tool_used == "john":
                return await self._start_john_attack(attack)
            elif attack.tool_used == "hashcat":
                return await self._start_hashcat_attack(attack)
            elif attack.tool_used == "fcrackzip":
                return await self._start_fcrackzip_attack(attack)
            else:
                return {
                    "success": False,
                    "error": f"Unknown crypto tool: {attack.tool_used}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_hashbuster_attack(self, attack: CryptoAttack) -> Dict:
        """Start crypto attack using HashBuster"""
        try:
            tool_path = self.crypto_tools["hashbuster"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build HashBuster command
            cmd_args = [
                "python", "hashbuster.py",
                "-f", attack.config.target_file
            ]
            
            # Add attack mode
            if attack.config.attack_mode == "dictionary":
                cmd_args.extend(["-w", attack.config.wordlist_path])
            elif attack.config.attack_mode == "brute_force":
                cmd_args.extend(["-b", "1:8"])  # Brute force 1-8 characters
            elif attack.config.attack_mode == "rainbow_table":
                cmd_args.extend(["-r", "rainbow_tables"])
            
            # Add hash type if specified
            if attack.config.hash_type:
                cmd_args.extend(["-t", attack.config.hash_type])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "HashBuster attack started successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Attack startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_john_attack(self, attack: CryptoAttack) -> Dict:
        """Start crypto attack using John the Ripper"""
        try:
            tool_path = self.crypto_tools["john"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build John command
            cmd_args = [
                "john",
                "--wordlist", attack.config.wordlist_path if attack.config.dictionary_attack else "/usr/share/wordlists/rockyou.txt"
            ]
            
            # Add attack mode
            if attack.config.attack_mode == "brute_force":
                cmd_args.extend(["--incremental"])
            elif attack.config.attack_mode == "incremental":
                cmd_args.extend(["--incremental:all"])
            
            # Add target file
            cmd_args.append(attack.config.target_file)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "John attack started successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Attack startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_hashcat_attack(self, attack: CryptoAttack) -> Dict:
        """Start crypto attack using Hashcat"""
        try:
            tool_path = self.crypto_tools["hashcat"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build Hashcat command
            cmd_args = [
                "hashcat",
                "-m", self._get_hashcat_mode(attack.config.hash_type),
                "-a", self._get_hashcat_attack_mode(attack.config.attack_mode)
            ]
            
            # Add wordlist for dictionary attack
            if attack.config.dictionary_attack:
                cmd_args.extend(["-w", attack.config.wordlist_path])
            
            # Add GPU acceleration if enabled
            if attack.config.gpu_acceleration:
                cmd_args.extend(["-d", "0"])  # Use GPU 0
            
            # Add target file
            cmd_args.append(attack.config.target_file)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "Hashcat attack started successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Attack startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_fcrackzip_attack(self, attack: CryptoAttack) -> Dict:
        """Start crypto attack using fcrackzip"""
        try:
            tool_path = self.crypto_tools["fcrackzip"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build fcrackzip command
            cmd_args = [
                "fcrackzip",
                "-u",  # Unzip
                "-D",  # Dictionary attack
                "-p", attack.config.wordlist_path if attack.config.dictionary_attack else "/usr/share/wordlists/rockyou.txt"
            ]
            
            # Add brute force if enabled
            if attack.config.brute_force:
                cmd_args.extend(["-b", "1:8"])  # Brute force 1-8 characters
            
            # Add target file
            cmd_args.append(attack.config.target_file)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "fcrackzip attack started successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Attack startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_hashcat_mode(self, hash_type: str) -> str:
        """Get Hashcat mode for hash type"""
        hash_modes = {
            "md5": "0",
            "sha1": "100",
            "sha256": "1400",
            "sha512": "1700",
            "ntlm": "1000",
            "lm": "3000",
            "mysql": "200",
            "postgres": "12",
            "oracle": "3100",
            "mssql": "131",
            "phpbb3": "400",
            "wordpress": "400",
            "drupal7": "7900",
            "wpa": "2500",
            "wpa2": "2500"
        }
        return hash_modes.get(hash_type.lower(), "0")
    
    def _get_hashcat_attack_mode(self, attack_mode: str) -> str:
        """Get Hashcat attack mode"""
        attack_modes = {
            "dictionary": "0",
            "brute_force": "3",
            "mask_attack": "3",
            "hybrid": "6"
        }
        return attack_modes.get(attack_mode, "0")
    
    async def get_cracked_hashes(self, attack_id: str) -> Dict:
        """Get cracked hashes from crypto attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Get cracked hashes based on tool
            if attack.tool_used == "hashbuster":
                cracked_hashes = await self._get_hashbuster_results(attack)
            elif attack.tool_used == "john":
                cracked_hashes = await self._get_john_results(attack)
            elif attack.tool_used == "hashcat":
                cracked_hashes = await self._get_hashcat_results(attack)
            elif attack.tool_used == "fcrackzip":
                cracked_hashes = await self._get_fcrackzip_results(attack)
            else:
                cracked_hashes = []
            
            # Update attack cracked hashes
            attack.cracked_hashes = cracked_hashes
            attack.cracked_count = len(cracked_hashes)
            
            return {
                "success": True,
                "cracked_hashes": cracked_hashes,
                "total": len(cracked_hashes)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cracked hashes: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_hashbuster_results(self, attack: CryptoAttack) -> List[Dict]:
        """Get results from HashBuster attack"""
        try:
            tool_path = self.crypto_tools["hashbuster"]["path"]
            
            # Check for results file
            results_file = os.path.join(tool_path, "results.txt")
            cracked_hashes = []
            
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                hash_value = parts[0]
                                password = parts[1]
                                cracked_hashes.append({
                                    "hash": hash_value,
                                    "password": password,
                                    "type": "hashbuster"
                                })
            
            return cracked_hashes
            
        except Exception as e:
            self.logger.error(f"Error getting HashBuster results: {str(e)}")
            return []
    
    async def _get_john_results(self, attack: CryptoAttack) -> List[Dict]:
        """Get results from John attack"""
        try:
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            cracked_hashes = []
            
            # Use John to show cracked passwords
            show_cmd = ["john", "--show", attack.config.target_file]
            
            process = await asyncio.create_subprocess_exec(
                *show_cmd,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                output = stdout.decode()
                lines = output.split('\n')
                
                for line in lines:
                    if ':' in line:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            username = parts[0]
                            password = parts[1]
                            cracked_hashes.append({
                                "username": username,
                                "password": password,
                                "type": "john"
                            })
            
            return cracked_hashes
            
        except Exception as e:
            self.logger.error(f"Error getting John results: {str(e)}")
            return []
    
    async def _get_hashcat_results(self, attack: CryptoAttack) -> List[Dict]:
        """Get results from Hashcat attack"""
        try:
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            cracked_hashes = []
            
            # Check for hashcat output file
            output_file = os.path.join(attack_dir, "hashcat.out")
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                hash_value = parts[0]
                                password = parts[1]
                                cracked_hashes.append({
                                    "hash": hash_value,
                                    "password": password,
                                    "type": "hashcat"
                                })
            
            return cracked_hashes
            
        except Exception as e:
            self.logger.error(f"Error getting Hashcat results: {str(e)}")
            return []
    
    async def _get_fcrackzip_results(self, attack: CryptoAttack) -> List[Dict]:
        """Get results from fcrackzip attack"""
        try:
            attack_dir = os.path.join("crypto_attacks", attack.attack_id)
            cracked_hashes = []
            
            # Check for fcrackzip output
            log_file = os.path.join(attack_dir, "fcrackzip.log")
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                    # Parse password from output
                    password_match = re.search(r'PASSWORD FOUND! pw == (.+)', content)
                    if password_match:
                        password = password_match.group(1)
                        cracked_hashes.append({
                            "file": attack.config.target_file,
                            "password": password,
                            "type": "fcrackzip"
                        })
            
            return cracked_hashes
            
        except Exception as e:
            self.logger.error(f"Error getting fcrackzip results: {str(e)}")
            return []
    
    def get_attack_info(self, attack_id: str) -> Dict:
        """Get attack information"""
        if attack_id not in self.active_attacks:
            return {
                "success": False,
                "error": "Attack not found"
            }
        
        attack = self.active_attacks[attack_id]
        return {
            "success": True,
            "attack": asdict(attack)
        }
    
    def get_all_attacks(self) -> Dict:
        """Get all active attacks"""
        attacks = []
        for attack_id, attack in self.active_attacks.items():
            attacks.append(asdict(attack))
        
        return {
            "success": True,
            "attacks": attacks,
            "total": len(attacks)
        }
    
    async def stop_attack(self, attack_id: str) -> Dict:
        """Stop crypto attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Stop attack based on tool
            if attack.tool_used == "hashbuster":
                result = await self._stop_hashbuster_attack(attack)
            elif attack.tool_used == "john":
                result = await self._stop_john_attack(attack)
            elif attack.tool_used == "hashcat":
                result = await self._stop_hashcat_attack(attack)
            elif attack.tool_used == "fcrackzip":
                result = await self._stop_fcrackzip_attack(attack)
            else:
                result = {"success": True}
            
            if result["success"]:
                attack.status = "stopped"
                attack.end_time = time.time()
                
                return {
                    "success": True,
                    "message": f"Attack {attack_id} stopped successfully"
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Error stopping attack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_hashbuster_attack(self, attack: CryptoAttack) -> Dict:
        """Stop HashBuster attack"""
        try:
            # Find and kill HashBuster process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'hashbuster.py' in ' '.join(proc.info['cmdline']):
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_john_attack(self, attack: CryptoAttack) -> Dict:
        """Stop John attack"""
        try:
            # Find and kill John process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'john' in proc.info['name']:
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_hashcat_attack(self, attack: CryptoAttack) -> Dict:
        """Stop Hashcat attack"""
        try:
            # Find and kill Hashcat process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'hashcat' in proc.info['name']:
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_fcrackzip_attack(self, attack: CryptoAttack) -> Dict:
        """Stop fcrackzip attack"""
        try:
            # Find and kill fcrackzip process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'fcrackzip' in proc.info['name']:
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get crypto cracking module statistics"""
        total_attacks = len(self.active_attacks)
        total_history = len(self.attack_history)
        
        # Calculate success rate
        successful_attacks = len([a for a in self.attack_history if a.get("status") == "active"])
        success_rate = (successful_attacks / total_history * 100) if total_history > 0 else 0
        
        # Calculate total cracked hashes
        total_cracked_hashes = sum(len(attack.cracked_hashes) for attack in self.active_attacks.values())
        
        return {
            "active_attacks": total_attacks,
            "total_history": total_history,
            "success_rate": success_rate,
            "total_cracked_hashes": total_cracked_hashes,
            "tools_available": list(self.crypto_tools.keys()),
            "supported_attacks": list(set([a for tool in self.crypto_tools.values() for a in tool["supported_attacks"]]))
        }