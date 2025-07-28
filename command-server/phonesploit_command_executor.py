"""
PhoneSploit Command Executor
Executes PhoneSploit commands with enhanced functionality
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class PhoneSploitCommandExecutor:
    """Enhanced command executor for PhoneSploit features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adb_path = "adb"
        self.current_device = None
        self.command_history = []
        self.execution_results = {}
        
    async def connect_device(self, ip_address: str, port: int = 5555) -> Dict:
        """Connect to device using ADB"""
        try:
            self.logger.info(f"Connecting to device at {ip_address}:{port}")
            
            # Kill and restart ADB server
            await self._execute_adb_command("kill-server")
            await self._execute_adb_command("start-server")
            
            # Connect to device
            result = await self._execute_adb_command(f"connect {ip_address}:{port}")
            
            if "connected" in result.lower():
                self.current_device = f"{ip_address}:{port}"
                self.logger.info(f"Successfully connected to {self.current_device}")
                return {
                    "success": True,
                    "device": self.current_device,
                    "message": "Device connected successfully"
                }
            else:
                self.logger.error(f"Failed to connect to {ip_address}:{port}")
                return {
                    "success": False,
                    "error": "Connection failed",
                    "message": result
                }
                
        except Exception as e:
            self.logger.error(f"Error connecting to device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_connected_devices(self) -> Dict:
        """List all connected devices"""
        try:
            result = await self._execute_adb_command("devices -l")
            
            devices = []
            lines = result.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        status = parts[1]
                        device_info = {
                            "device_id": device_id,
                            "status": status,
                            "details": line
                        }
                        devices.append(device_info)
            
            return {
                "success": True,
                "devices": devices,
                "count": len(devices)
            }
            
        except Exception as e:
            self.logger.error(f"Error listing devices: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect_all_devices(self) -> Dict:
        """Disconnect all devices"""
        try:
            result = await self._execute_adb_command("disconnect")
            self.current_device = None
            
            return {
                "success": True,
                "message": "All devices disconnected"
            }
            
        except Exception as e:
            self.logger.error(f"Error disconnecting devices: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_shell(self) -> Dict:
        """Get shell access to device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # This would typically open an interactive shell
            # For now, we'll return shell status
            return {
                "success": True,
                "message": "Shell access available",
                "device": self.current_device
            }
            
        except Exception as e:
            self.logger.error(f"Error getting shell: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_screenshot(self, save_path: str = None) -> Dict:
        """Take screenshot of device screen"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Take screenshot
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
                    "message": "Screenshot captured successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save screenshot"
                }
                
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_device_screen(self, duration: int = 10, save_path: str = None) -> Dict:
        """Record device screen"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenrecord_{timestamp}.mp4"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Start screen recording
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
                    "message": "Screen recording completed"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to save screen recording"
                }
                
        except Exception as e:
            self.logger.error(f"Error recording screen: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def pull_file_from_device(self, device_path: str, local_path: str = None) -> Dict:
        """Download file or folder from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not local_path:
                local_path = os.path.basename(device_path)
            
            # Pull file from device
            result = await self._execute_adb_command(f"pull {device_path} {local_path}")
            
            if os.path.exists(local_path):
                return {
                    "success": True,
                    "local_path": os.path.abspath(local_path),
                    "device_path": device_path,
                    "message": "File downloaded successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to download file"
                }
                
        except Exception as e:
            self.logger.error(f"Error pulling file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def push_file_to_device(self, local_path: str, device_path: str) -> Dict:
        """Send file or folder to device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not os.path.exists(local_path):
                return {
                    "success": False,
                    "error": "Local file does not exist"
                }
            
            # Push file to device
            result = await self._execute_adb_command(f"push {local_path} {device_path}")
            
            return {
                "success": True,
                "local_path": local_path,
                "device_path": device_path,
                "message": "File uploaded successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error pushing file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_device_files(self, path: str = "/sdcard") -> Dict:
        """List all files and folders on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            result = await self._execute_adb_command(f"shell ls -la {path}")
            
            files = []
            lines = result.strip().split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('total'):
                    parts = line.split()
                    if len(parts) >= 9:
                        file_info = {
                            "permissions": parts[0],
                            "owner": parts[2],
                            "group": parts[3],
                            "size": parts[4],
                            "date": f"{parts[5]} {parts[6]} {parts[7]}",
                            "name": parts[8]
                        }
                        files.append(file_info)
            
            return {
                "success": True,
                "path": path,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def install_apk_on_device(self, apk_path: str) -> Dict:
        """Install APK file on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not os.path.exists(apk_path):
                return {
                    "success": False,
                    "error": "APK file does not exist"
                }
            
            # Disable app verification
            await self._execute_adb_command("shell settings put global package_verifier_enable 0")
            await self._execute_adb_command("shell settings put global verifier_verify_adb_installs 0")
            
            # Install APK
            result = await self._execute_adb_command(f"install -r {apk_path}")
            
            if "Success" in result:
                return {
                    "success": True,
                    "apk_path": apk_path,
                    "message": "APK installed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to install APK",
                    "message": result
                }
                
        except Exception as e:
            self.logger.error(f"Error installing APK: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def uninstall_app_from_device(self, package_name: str) -> Dict:
        """Uninstall app from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            result = await self._execute_adb_command(f"uninstall {package_name}")
            
            if "Success" in result:
                return {
                    "success": True,
                    "package_name": package_name,
                    "message": "App uninstalled successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to uninstall app",
                    "message": result
                }
                
        except Exception as e:
            self.logger.error(f"Error uninstalling app: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def launch_app_on_device(self, package_name: str) -> Dict:
        """Launch app on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            result = await self._execute_adb_command(f"shell monkey -p {package_name} 1")
            
            return {
                "success": True,
                "package_name": package_name,
                "message": "App launched successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error launching app: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_installed_apps(self) -> Dict:
        """List all installed apps on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            result = await self._execute_adb_command("shell pm list packages -3")
            
            apps = []
            lines = result.strip().split('\n')
            
            for line in lines:
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    apps.append(package_name)
            
            return {
                "success": True,
                "apps": apps,
                "count": len(apps)
            }
            
        except Exception as e:
            self.logger.error(f"Error listing apps: {str(e)}")
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
            
            # Log command in history
            self.command_history.append({
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
    
    def get_command_history(self) -> List[Dict]:
        """Get command execution history"""
        return self.command_history
    
    def clear_command_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.logger.info("Command history cleared")
    
    def get_execution_statistics(self) -> Dict:
        """Get command execution statistics"""
        total_commands = len(self.command_history)
        successful_commands = len([cmd for cmd in self.command_history if cmd["return_code"] == 0])
        failed_commands = total_commands - successful_commands
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "failed_commands": failed_commands,
            "success_rate": (successful_commands / total_commands * 100) if total_commands > 0 else 0
        }