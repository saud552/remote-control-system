"""
Enhanced Connection Manager for Multiple Devices
Supports multiple device connections with advanced management
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeviceInfo:
    """Device information structure"""
    device_id: str
    ip_address: str
    port: int = 5555
    status: str = "disconnected"
    last_seen: Optional[datetime] = None
    capabilities: List[str] = None
    device_info: Dict = None
    connection_quality: float = 0.0
    is_trusted: bool = False

class EnhancedConnectionManager:
    """Enhanced connection manager for multiple devices"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInfo] = {}
        self.active_connections: Dict[str, any] = {}
        self.connection_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        
    async def connect_device(self, ip_address: str, port: int = 5555) -> bool:
        """Connect to a device with enhanced error handling"""
        try:
            device_id = f"DEV-{int(time.time())}-{hash(ip_address) % 10000}"
            
            # Create device info
            device = DeviceInfo(
                device_id=device_id,
                ip_address=ip_address,
                port=port,
                status="connecting",
                last_seen=datetime.now(),
                capabilities=[],
                device_info={},
                connection_quality=0.0,
                is_trusted=False
            )
            
            # Test connection
            if await self._test_connection(ip_address, port):
                device.status = "connected"
                device.connection_quality = await self._measure_connection_quality(ip_address, port)
                self.devices[device_id] = device
                self.active_connections[device_id] = {
                    "ip": ip_address,
                    "port": port,
                    "connected_at": datetime.now()
                }
                
                self.logger.info(f"Successfully connected to device {device_id} at {ip_address}:{port}")
                return True
            else:
                self.logger.error(f"Failed to connect to device at {ip_address}:{port}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to device: {str(e)}")
            return False
    
    async def _test_connection(self, ip_address: str, port: int) -> bool:
        """Test connection to device"""
        try:
            # Simulate connection test
            await asyncio.sleep(0.1)
            return True
        except Exception:
            return False
    
    async def _measure_connection_quality(self, ip_address: str, port: int) -> float:
        """Measure connection quality (0.0 to 1.0)"""
        try:
            # Simulate quality measurement
            await asyncio.sleep(0.05)
            return 0.85  # Simulated quality score
        except Exception:
            return 0.0
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect a specific device"""
        try:
            if device_id in self.devices:
                self.devices[device_id].status = "disconnected"
                if device_id in self.active_connections:
                    del self.active_connections[device_id]
                self.logger.info(f"Disconnected device {device_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disconnecting device {device_id}: {str(e)}")
            return False
    
    def disconnect_all_devices(self) -> bool:
        """Disconnect all devices"""
        try:
            for device_id in list(self.devices.keys()):
                self.disconnect_device(device_id)
            self.logger.info("Disconnected all devices")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting all devices: {str(e)}")
            return False
    
    def get_connected_devices(self) -> List[DeviceInfo]:
        """Get list of connected devices"""
        return [device for device in self.devices.values() if device.status == "connected"]
    
    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get information about a specific device"""
        return self.devices.get(device_id)
    
    def update_device_status(self, device_id: str, status: str) -> bool:
        """Update device status"""
        try:
            if device_id in self.devices:
                self.devices[device_id].status = status
                self.devices[device_id].last_seen = datetime.now()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating device status: {str(e)}")
            return False
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        connected_count = len(self.get_connected_devices())
        total_count = len(self.devices)
        
        return {
            "connected_devices": connected_count,
            "total_devices": total_count,
            "connection_rate": connected_count / total_count if total_count > 0 else 0,
            "average_quality": sum(d.connection_quality for d in self.get_connected_devices()) / connected_count if connected_count > 0 else 0
        }
    
    def export_device_list(self) -> List[Dict]:
        """Export device list for external use"""
        return [
            {
                "device_id": device.device_id,
                "ip_address": device.ip_address,
                "port": device.port,
                "status": device.status,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "capabilities": device.capabilities,
                "connection_quality": device.connection_quality,
                "is_trusted": device.is_trusted
            }
            for device in self.devices.values()
        ]
    
    def import_device_list(self, device_list: List[Dict]) -> bool:
        """Import device list from external source"""
        try:
            for device_data in device_list:
                device = DeviceInfo(
                    device_id=device_data.get("device_id"),
                    ip_address=device_data.get("ip_address"),
                    port=device_data.get("port", 5555),
                    status=device_data.get("status", "disconnected"),
                    last_seen=datetime.fromisoformat(device_data["last_seen"]) if device_data.get("last_seen") else None,
                    capabilities=device_data.get("capabilities", []),
                    connection_quality=device_data.get("connection_quality", 0.0),
                    is_trusted=device_data.get("is_trusted", False)
                )
                self.devices[device.device_id] = device
            
            self.logger.info(f"Imported {len(device_list)} devices")
            return True
        except Exception as e:
            self.logger.error(f"Error importing device list: {str(e)}")
            return False