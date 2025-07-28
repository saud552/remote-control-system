"""
Enhanced Device Manager
Manages devices with PhoneSploit-Pro features and advanced device control
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

class DeviceStatus(Enum):
    """Device status enumeration"""
    OFFLINE = "offline"
    ONLINE = "online"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    BUSY = "busy"

class DeviceType(Enum):
    """Device type enumeration"""
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"

@dataclass
class DeviceInfo:
    """Enhanced device information"""
    device_id: str
    ip_address: str
    hostname: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    status: DeviceStatus = DeviceStatus.OFFLINE
    connection_type: str = "unknown"  # wifi, usb, network
    is_authorized: bool = False
    is_rooted: bool = False
    
    # PhoneSploit-Pro specific fields
    device_model: Optional[str] = None
    android_version: Optional[str] = None
    sdk_version: Optional[str] = None
    battery_level: Optional[int] = None
    storage_info: Optional[Dict] = None
    network_info: Optional[Dict] = None
    installed_apps: Optional[List[str]] = None
    
    # Connection info
    adb_connected: bool = False
    usb_connected: bool = False
    last_seen: float = 0.0
    connection_duration: float = 0.0
    
    # Performance metrics
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    temperature: Optional[float] = None
    
    # Security info
    security_level: str = "unknown"
    encryption_enabled: bool = False
    screen_locked: bool = True
    
    # User info
    user_id: Optional[str] = None
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []

class EnhancedDeviceManager:
    """Enhanced device manager with PhoneSploit-Pro features"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInfo] = {}
        self.device_groups: Dict[str, List[str]] = {}
        self.device_history: Dict[str, List[Dict]] = {}
        self.pending_commands: Dict[str, List[Dict]] = {}
        self.device_stats: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
        # PhoneSploit-Pro settings
        self.adb_path = "adb"
        self.max_retry_attempts = 3
        self.command_timeout = 30
        self.auto_reconnect = True
        
        # Load existing devices
        self._load_devices_from_storage()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _load_devices_from_storage(self):
        """Load devices from persistent storage"""
        try:
            storage_file = "devices.json"
            if os.path.exists(storage_file):
                with open(storage_file, 'r') as f:
                    devices_data = json.load(f)
                
                for device_data in devices_data:
                    device = DeviceInfo(**device_data)
                    self.devices[device.device_id] = device
                
                self.logger.info(f"Loaded {len(self.devices)} devices from storage")
                
        except Exception as e:
            self.logger.error(f"Error loading devices from storage: {str(e)}")
    
    def _save_devices_to_storage(self):
        """Save devices to persistent storage"""
        try:
            devices_data = [asdict(device) for device in self.devices.values()]
            
            with open("devices.json", 'w') as f:
                json.dump(devices_data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving devices to storage: {str(e)}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._device_monitor_task())
        asyncio.create_task(self._cleanup_task())
        asyncio.create_task(self._stats_collection_task())
    
    async def _device_monitor_task(self):
        """Monitor device status and health"""
        while True:
            try:
                for device_id, device in self.devices.items():
                    if device.status in [DeviceStatus.ONLINE, DeviceStatus.CONNECTED]:
                        # Check device health
                        health_status = await self._check_device_health(device_id)
                        if not health_status["healthy"]:
                            device.status = DeviceStatus.ERROR
                            self._add_device_event(device_id, "health_check_failed", health_status)
                        
                        # Update device info
                        await self._update_device_info(device_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in device monitor task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_task(self):
        """Clean up inactive devices and old data"""
        while True:
            try:
                current_time = time.time()
                
                # Remove devices inactive for more than 24 hours
                inactive_devices = []
                for device_id, device in self.devices.items():
                    if current_time - device.last_seen > 86400:  # 24 hours
                        inactive_devices.append(device_id)
                
                for device_id in inactive_devices:
                    self.remove_device(device_id)
                
                # Clean up old history entries
                for device_id in self.device_history:
                    if len(self.device_history[device_id]) > 1000:
                        self.device_history[device_id] = self.device_history[device_id][-500:]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _stats_collection_task(self):
        """Collect device statistics"""
        while True:
            try:
                for device_id, device in self.devices.items():
                    if device.status in [DeviceStatus.ONLINE, DeviceStatus.CONNECTED]:
                        stats = await self._collect_device_stats(device_id)
                        self.device_stats[device_id] = stats
                
                await asyncio.sleep(300)  # Collect stats every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in stats collection task: {str(e)}")
                await asyncio.sleep(300)
    
    async def discover_and_register_device(self, ip_address: str, device_info: Dict = None) -> Dict:
        """Discover and register a new device"""
        try:
            # Check if device already exists
            existing_device = self._find_device_by_ip(ip_address)
            if existing_device:
                return {
                    "success": True,
                    "device_id": existing_device.device_id,
                    "message": "Device already registered",
                    "device": asdict(existing_device)
                }
            
            # Generate device ID
            device_id = f"device_{int(time.time())}_{hash(ip_address) % 10000}"
            
            # Create device info
            device = DeviceInfo(
                device_id=device_id,
                ip_address=ip_address,
                hostname=device_info.get("hostname") if device_info else None,
                device_type=DeviceType.ANDROID if device_info.get("is_android") else DeviceType.UNKNOWN,
                status=DeviceStatus.OFFLINE,
                connection_type=device_info.get("connection_type", "unknown"),
                last_seen=time.time()
            )
            
            # Add device
            self.devices[device_id] = device
            self.device_history[device_id] = []
            self.device_stats[device_id] = {}
            
            # Add to default group
            if "default" not in self.device_groups:
                self.device_groups["default"] = []
            self.device_groups["default"].append(device_id)
            
            # Save to storage
            self._save_devices_to_storage()
            
            self._add_device_event(device_id, "registered", {"ip_address": ip_address})
            
            self.logger.info(f"Registered new device: {device_id} ({ip_address})")
            
            return {
                "success": True,
                "device_id": device_id,
                "message": "Device registered successfully",
                "device": asdict(device)
            }
            
        except Exception as e:
            self.logger.error(f"Error registering device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def connect_to_device(self, device_id: str) -> Dict:
        """Connect to a device"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return {
                    "success": False,
                    "error": "Device not found"
                }
            
            # Update status
            device.status = DeviceStatus.CONNECTING
            
            # Try to connect via ADB
            if device.device_type == DeviceType.ANDROID:
                connect_result = await self._connect_android_device(device)
                if connect_result["success"]:
                    device.status = DeviceStatus.CONNECTED
                    device.adb_connected = True
                    device.last_seen = time.time()
                    device.is_authorized = connect_result.get("authorized", False)
                    
                    # Update device info
                    await self._update_device_info(device_id)
                    
                    self._add_device_event(device_id, "connected", connect_result)
                    
                    return {
                        "success": True,
                        "message": "Device connected successfully",
                        "device": asdict(device)
                    }
                else:
                    device.status = DeviceStatus.ERROR
                    return connect_result
            
            return {
                "success": False,
                "error": "Unsupported device type"
            }
            
        except Exception as e:
            self.logger.error(f"Error connecting to device {device_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect_from_device(self, device_id: str) -> Dict:
        """Disconnect from a device"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return {
                    "success": False,
                    "error": "Device not found"
                }
            
            if device.status in [DeviceStatus.CONNECTED, DeviceStatus.ONLINE]:
                # Disconnect ADB if connected
                if device.adb_connected:
                    await self._disconnect_android_device(device)
                
                device.status = DeviceStatus.DISCONNECTED
                device.adb_connected = False
                device.usb_connected = False
                
                self._add_device_event(device_id, "disconnected", {})
                
                return {
                    "success": True,
                    "message": "Device disconnected successfully"
                }
            
            return {
                "success": False,
                "error": "Device not connected"
            }
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from device {device_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _connect_android_device(self, device: DeviceInfo) -> Dict:
        """Connect to Android device via ADB"""
        try:
            # Try to connect via ADB
            connect_cmd = f"{self.adb_path} connect {device.ip_address}:5555"
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                connect_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0 and "connected" in result.stdout.decode().lower():
                # Check if device is authorized
                devices_cmd = f"{self.adb_path} devices"
                devices_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    subprocess.run,
                    devices_cmd.split(),
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE
                )
                
                devices_output = devices_result.stdout.decode()
                authorized = False
                
                for line in devices_output.split('\n'):
                    if device.ip_address in line and "device" in line:
                        authorized = True
                        break
                
                return {
                    "success": True,
                    "authorized": authorized,
                    "connection_type": "wifi"
                }
            
            return {
                "success": False,
                "error": "Failed to connect via ADB"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _disconnect_android_device(self, device: DeviceInfo):
        """Disconnect from Android device"""
        try:
            disconnect_cmd = f"{self.adb_path} disconnect {device.ip_address}:5555"
            await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                disconnect_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
        except Exception as e:
            self.logger.error(f"Error disconnecting Android device: {str(e)}")
    
    async def _update_device_info(self, device_id: str):
        """Update device information"""
        try:
            device = self.devices.get(device_id)
            if not device or device.device_type != DeviceType.ANDROID:
                return
            
            # Get device model
            model_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell getprop ro.product.model"
            model_result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                model_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if model_result.returncode == 0:
                device.device_model = model_result.stdout.decode().strip()
            
            # Get Android version
            version_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell getprop ro.build.version.release"
            version_result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                version_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if version_result.returncode == 0:
                device.android_version = version_result.stdout.decode().strip()
            
            # Get battery level
            battery_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell dumpsys battery | grep level"
            battery_result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                battery_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if battery_result.returncode == 0:
                battery_output = battery_result.stdout.decode()
                try:
                    battery_level = int(battery_output.split(':')[1].strip())
                    device.battery_level = battery_level
                except (ValueError, IndexError):
                    pass
            
            # Check if device is rooted
            root_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell which su"
            root_result = await asyncio.get_event_loop().run_in_executor(
                None,
                subprocess.run,
                root_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            device.is_rooted = root_result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error updating device info for {device_id}: {str(e)}")
    
    async def _check_device_health(self, device_id: str) -> Dict:
        """Check device health status"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return {"healthy": False, "error": "Device not found"}
            
            if device.device_type == DeviceType.ANDROID and device.adb_connected:
                # Test ADB connection
                test_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell echo 'test'"
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    subprocess.run,
                    test_cmd.split(),
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE
                )
                
                if result.returncode == 0:
                    return {"healthy": True}
                else:
                    return {"healthy": False, "error": "ADB connection failed"}
            
            return {"healthy": True}
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _collect_device_stats(self, device_id: str) -> Dict:
        """Collect device statistics"""
        try:
            device = self.devices.get(device_id)
            if not device:
                return {}
            
            stats = {
                "device_id": device_id,
                "timestamp": time.time(),
                "status": device.status.value,
                "connection_type": device.connection_type,
                "battery_level": device.battery_level,
                "is_rooted": device.is_rooted,
                "is_authorized": device.is_authorized
            }
            
            if device.device_type == DeviceType.ANDROID and device.adb_connected:
                # Get additional stats for Android devices
                try:
                    # CPU usage
                    cpu_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell top -n 1 | grep 'CPU:'"
                    cpu_result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        subprocess.run,
                        cpu_cmd.split(),
                        subprocess.PIPE,
                        subprocess.PIPE,
                        subprocess.PIPE
                    )
                    
                    if cpu_result.returncode == 0:
                        cpu_output = cpu_result.stdout.decode()
                        # Parse CPU usage (simplified)
                        stats["cpu_usage"] = 50.0  # Placeholder
                    
                    # Memory usage
                    mem_cmd = f"{self.adb_path} -s {device.ip_address}:5555 shell dumpsys meminfo | grep 'Total RAM:'"
                    mem_result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        subprocess.run,
                        mem_cmd.split(),
                        subprocess.PIPE,
                        subprocess.PIPE,
                        subprocess.PIPE
                    )
                    
                    if mem_result.returncode == 0:
                        mem_output = mem_result.stdout.decode()
                        # Parse memory usage (simplified)
                        stats["memory_usage"] = 60.0  # Placeholder
                        
                except Exception as e:
                    self.logger.debug(f"Error collecting detailed stats: {str(e)}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error collecting device stats: {str(e)}")
            return {}
    
    def _find_device_by_ip(self, ip_address: str) -> Optional[DeviceInfo]:
        """Find device by IP address"""
        for device in self.devices.values():
            if device.ip_address == ip_address:
                return device
        return None
    
    def _add_device_event(self, device_id: str, event_type: str, data: Dict):
        """Add device event to history"""
        if device_id not in self.device_history:
            self.device_history[device_id] = []
        
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        
        self.device_history[device_id].append(event)
    
    def get_all_devices(self) -> List[DeviceInfo]:
        """Get all devices"""
        return list(self.devices.values())
    
    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """Get connected devices"""
        return [device for device in self.devices.values() 
                if device.status in [DeviceStatus.CONNECTED, DeviceStatus.ONLINE]]
    
    def get_android_devices(self) -> List[DeviceInfo]:
        """Get Android devices"""
        return [device for device in self.devices.values() 
                if device.device_type == DeviceType.ANDROID]
    
    def remove_device(self, device_id: str):
        """Remove device"""
        if device_id in self.devices:
            del self.devices[device_id]
        
        if device_id in self.device_history:
            del self.device_history[device_id]
        
        if device_id in self.device_stats:
            del self.device_stats[device_id]
        
        # Remove from groups
        for group in self.device_groups.values():
            if device_id in group:
                group.remove(device_id)
        
        self._save_devices_to_storage()
    
    def get_device_history(self, device_id: str, limit: int = 50) -> List[Dict]:
        """Get device history"""
        if device_id in self.device_history:
            return self.device_history[device_id][-limit:]
        return []
    
    def get_device_stats(self, device_id: str) -> Dict:
        """Get device statistics"""
        return self.device_stats.get(device_id, {})
    
    def get_all_device_stats(self) -> Dict:
        """Get statistics for all devices"""
        return {
            "total_devices": len(self.devices),
            "connected_devices": len(self.get_connected_devices()),
            "android_devices": len(self.get_android_devices()),
            "device_types": self._get_device_type_distribution(),
            "connection_types": self._get_connection_type_distribution()
        }
    
    def _get_device_type_distribution(self) -> Dict:
        """Get device type distribution"""
        distribution = {}
        for device in self.devices.values():
            device_type = device.device_type.value
            distribution[device_type] = distribution.get(device_type, 0) + 1
        return distribution
    
    def _get_connection_type_distribution(self) -> Dict:
        """Get connection type distribution"""
        distribution = {}
        for device in self.devices.values():
            connection_type = device.connection_type
            distribution[connection_type] = distribution.get(connection_type, 0) + 1
        return distribution