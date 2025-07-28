"""
Enhanced Auto Device Discovery System
Automatically discovers and scans for devices on the network with PhoneSploit-Pro features
"""

import asyncio
import ipaddress
import json
import logging
import os
import socket
import subprocess
import time
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class DiscoveredDevice:
    """Enhanced discovered device information"""
    ip_address: str
    hostname: Optional[str] = None
    device_type: str = "unknown"
    is_android: bool = False
    is_accessible: bool = False
    response_time: float = 0.0
    open_ports: List[int] = None
    last_seen: float = 0.0
    # PhoneSploit-Pro specific fields
    adb_connected: bool = False
    usb_connected: bool = False
    device_id: Optional[str] = None
    device_model: Optional[str] = None
    android_version: Optional[str] = None
    sdk_version: Optional[str] = None
    battery_level: Optional[int] = None
    is_rooted: bool = False
    is_authorized: bool = False
    connection_type: str = "unknown"  # wifi, usb, network

class EnhancedAutoDeviceDiscovery:
    """Enhanced automatic device discovery system with PhoneSploit-Pro features"""
    
    def __init__(self):
        self.discovered_devices: Dict[str, DiscoveredDevice] = {}
        self.scan_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.adb_path = "adb"
        self.scan_in_progress = False
        
        # PhoneSploit-Pro specific settings
        self.android_ports = [5555, 5037, 8080, 8888, 4444, 5556]
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 5555, 8080, 8888]
        
    async def scan_network_enhanced(self, network_range: str = "192.168.1.0/24") -> List[DiscoveredDevice]:
        """Enhanced network scan with PhoneSploit-Pro features"""
        try:
            if self.scan_in_progress:
                self.logger.warning("Scan already in progress")
                return []
            
            self.scan_in_progress = True
            self.logger.info(f"Starting enhanced network scan for range: {network_range}")
            
            # Get network addresses
            network = ipaddress.IPv4Network(network_range, strict=False)
            addresses = [str(ip) for ip in network.hosts()]
            
            # Scan addresses concurrently with enhanced detection
            tasks = []
            for ip in addresses:
                task = asyncio.create_task(self._scan_device_enhanced(ip))
                tasks.append(task)
            
            # Wait for all scans to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful discoveries
            discovered = []
            for result in results:
                if isinstance(result, DiscoveredDevice) and result.is_accessible:
                    discovered.append(result)
                    self.discovered_devices[result.ip_address] = result
            
            # Additional PhoneSploit-Pro scans
            await self._scan_usb_devices()
            await self._scan_adb_devices()
            
            self.logger.info(f"Enhanced scan completed. Found {len(discovered)} accessible devices")
            return discovered
            
        except Exception as e:
            self.logger.error(f"Error in enhanced network scan: {str(e)}")
            return []
        finally:
            self.scan_in_progress = False
    
    async def _scan_device_enhanced(self, ip_address: str) -> Optional[DiscoveredDevice]:
        """Enhanced scan for a single device with PhoneSploit-Pro features"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            if not await self._test_connectivity(ip_address):
                return None
            
            # Enhanced Android detection
            android_info = await self._check_android_device_enhanced(ip_address)
            
            # Get device information
            hostname = await self._get_hostname(ip_address)
            open_ports = await self._scan_ports_enhanced(ip_address)
            
            response_time = time.time() - start_time
            
            device = DiscoveredDevice(
                ip_address=ip_address,
                hostname=hostname,
                device_type="android" if android_info["is_android"] else "unknown",
                is_android=android_info["is_android"],
                is_accessible=True,
                response_time=response_time,
                open_ports=open_ports,
                last_seen=time.time(),
                adb_connected=android_info["adb_connected"],
                device_id=android_info["device_id"],
                device_model=android_info["device_model"],
                android_version=android_info["android_version"],
                sdk_version=android_info["sdk_version"],
                battery_level=android_info["battery_level"],
                is_rooted=android_info["is_rooted"],
                is_authorized=android_info["is_authorized"],
                connection_type=android_info["connection_type"]
            )
            
            return device
            
        except Exception as e:
            self.logger.debug(f"Error scanning device {ip_address}: {str(e)}")
            return None
    
    async def _check_android_device_enhanced(self, ip_address: str) -> Dict:
        """Enhanced Android device detection with PhoneSploit-Pro features"""
        android_info = {
            "is_android": False,
            "adb_connected": False,
            "device_id": None,
            "device_model": None,
            "android_version": None,
            "sdk_version": None,
            "battery_level": None,
            "is_rooted": False,
            "is_authorized": False,
            "connection_type": "unknown"
        }
        
        try:
            # Check for ADB connectivity
            adb_result = await self._test_adb_connection(ip_address)
            if adb_result["connected"]:
                android_info["is_android"] = True
                android_info["adb_connected"] = True
                android_info["connection_type"] = "wifi"
                android_info["device_id"] = adb_result["device_id"]
                android_info["is_authorized"] = adb_result["authorized"]
                
                # Get detailed device information
                device_info = await self._get_device_info_enhanced(ip_address)
                android_info.update(device_info)
            
            # Check for Android-specific ports
            elif await self._check_android_ports_enhanced(ip_address):
                android_info["is_android"] = True
                android_info["connection_type"] = "network"
            
        except Exception as e:
            self.logger.debug(f"Error checking Android device {ip_address}: {str(e)}")
        
        return android_info
    
    async def _test_adb_connection(self, ip_address: str) -> Dict:
        """Test ADB connection to device"""
        try:
            # Try to connect via ADB
            connect_cmd = f"{self.adb_path} connect {ip_address}:5555"
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                connect_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0 and "connected" in result.stdout.decode().lower():
                # Get device ID
                devices_cmd = f"{self.adb_path} devices"
                devices_result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    subprocess.run,
                    devices_cmd.split(),
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE
                )
                
                devices_output = devices_result.stdout.decode()
                device_id = None
                authorized = False
                
                for line in devices_output.split('\n'):
                    if ip_address in line:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            device_id = parts[0]
                            authorized = "device" in parts[1]
                        break
                
                return {
                    "connected": True,
                    "device_id": device_id,
                    "authorized": authorized
                }
            
            return {"connected": False, "device_id": None, "authorized": False}
            
        except Exception as e:
            self.logger.debug(f"Error testing ADB connection to {ip_address}: {str(e)}")
            return {"connected": False, "device_id": None, "authorized": False}
    
    async def _get_device_info_enhanced(self, ip_address: str) -> Dict:
        """Get enhanced device information via ADB"""
        device_info = {
            "device_model": None,
            "android_version": None,
            "sdk_version": None,
            "battery_level": None,
            "is_rooted": False
        }
        
        try:
            # Get device model
            model_cmd = f"{self.adb_path} -s {ip_address}:5555 shell getprop ro.product.model"
            model_result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                model_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if model_result.returncode == 0:
                device_info["device_model"] = model_result.stdout.decode().strip()
            
            # Get Android version
            version_cmd = f"{self.adb_path} -s {ip_address}:5555 shell getprop ro.build.version.release"
            version_result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                version_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if version_result.returncode == 0:
                device_info["android_version"] = version_result.stdout.decode().strip()
            
            # Get SDK version
            sdk_cmd = f"{self.adb_path} -s {ip_address}:5555 shell getprop ro.build.version.sdk"
            sdk_result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                sdk_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if sdk_result.returncode == 0:
                device_info["sdk_version"] = sdk_result.stdout.decode().strip()
            
            # Get battery level
            battery_cmd = f"{self.adb_path} -s {ip_address}:5555 shell dumpsys battery | grep level"
            battery_result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
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
                    device_info["battery_level"] = battery_level
                except (ValueError, IndexError):
                    pass
            
            # Check if device is rooted
            root_cmd = f"{self.adb_path} -s {ip_address}:5555 shell which su"
            root_result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                root_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            device_info["is_rooted"] = root_result.returncode == 0
            
        except Exception as e:
            self.logger.debug(f"Error getting device info for {ip_address}: {str(e)}")
        
        return device_info
    
    async def _check_android_ports_enhanced(self, ip_address: str) -> bool:
        """Enhanced check for Android-specific open ports"""
        for port in self.android_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    return True
            except Exception:
                continue
        
        return False
    
    async def _scan_ports_enhanced(self, ip_address: str) -> List[int]:
        """Enhanced port scanning"""
        open_ports = []
        
        for port in self.common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            except Exception:
                continue
        
        return open_ports
    
    async def _scan_usb_devices(self):
        """Scan for USB-connected Android devices"""
        try:
            self.logger.info("Scanning for USB-connected devices...")
            
            # Get USB devices
            usb_cmd = f"{self.adb_path} devices"
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                usb_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0:
                devices_output = result.stdout.decode()
                for line in devices_output.split('\n'):
                    if '\t' in line and 'device' in line:
                        device_id = line.split('\t')[0]
                        
                        # Create device entry for USB device
                        device = DiscoveredDevice(
                            ip_address=f"USB:{device_id}",
                            device_type="android",
                            is_android=True,
                            is_accessible=True,
                            device_id=device_id,
                            connection_type="usb",
                            last_seen=time.time()
                        )
                        
                        self.discovered_devices[device.ip_address] = device
                        
        except Exception as e:
            self.logger.error(f"Error scanning USB devices: {str(e)}")
    
    async def _scan_adb_devices(self):
        """Scan for ADB-connected devices"""
        try:
            self.logger.info("Scanning for ADB-connected devices...")
            
            # Get ADB devices
            adb_cmd = f"{self.adb_path} devices -l"
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                adb_cmd.split(),
                subprocess.PIPE,
                subprocess.PIPE,
                subprocess.PIPE
            )
            
            if result.returncode == 0:
                devices_output = result.stdout.decode()
                for line in devices_output.split('\n'):
                    if '\t' in line and 'device' in line:
                        parts = line.split('\t')
                        device_id = parts[0]
                        
                        # Extract IP address if available
                        ip_address = None
                        for part in parts:
                            if ':' in part and part.count('.') == 3:
                                ip_address = part.split(':')[0]
                                break
                        
                        if ip_address:
                            # Update existing device or create new one
                            if ip_address in self.discovered_devices:
                                self.discovered_devices[ip_address].adb_connected = True
                                self.discovered_devices[ip_address].device_id = device_id
                            else:
                                device = DiscoveredDevice(
                                    ip_address=ip_address,
                                    device_type="android",
                                    is_android=True,
                                    is_accessible=True,
                                    device_id=device_id,
                                    adb_connected=True,
                                    connection_type="adb",
                                    last_seen=time.time()
                                )
                                self.discovered_devices[ip_address] = device
                        
        except Exception as e:
            self.logger.error(f"Error scanning ADB devices: {str(e)}")
    
    async def _test_connectivity(self, ip_address: str) -> bool:
        """Test basic connectivity to device"""
        try:
            # Test with ping
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                ["ping", "-c", "1", "-W", "2", ip_address],
                subprocess.PIPE,
                subprocess.PIPE
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _get_hostname(self, ip_address: str) -> Optional[str]:
        """Get hostname for IP address"""
        try:
            hostname = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                socket.gethostbyaddr,
                ip_address
            )
            return hostname[0] if hostname else None
        except Exception:
            return None
    
    async def scan_specific_range_enhanced(self, start_ip: str, end_ip: str) -> List[DiscoveredDevice]:
        """Enhanced scan for specific IP range"""
        try:
            start = ipaddress.IPv4Address(start_ip)
            end = ipaddress.IPv4Address(end_ip)
            
            addresses = []
            current = start
            while current <= end:
                addresses.append(str(current))
                current += 1
            
            # Scan addresses
            tasks = []
            for ip in addresses:
                task = asyncio.create_task(self._scan_device_enhanced(ip))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            discovered = []
            for result in results:
                if isinstance(result, DiscoveredDevice) and result.is_accessible:
                    discovered.append(result)
                    self.discovered_devices[result.ip_address] = result
            
            return discovered
            
        except Exception as e:
            self.logger.error(f"Error scanning specific range: {str(e)}")
            return []
    
    async def connect_to_device(self, ip_address: str) -> Dict:
        """Connect to device via ADB"""
        try:
            if ip_address.startswith("USB:"):
                # USB device
                device_id = ip_address.replace("USB:", "")
                return {
                    "success": True,
                    "device_id": device_id,
                    "connection_type": "usb",
                    "message": "USB device connected"
                }
            else:
                # Network device
                connect_cmd = f"{self.adb_path} connect {ip_address}:5555"
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    subprocess.run,
                    connect_cmd.split(),
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE
                )
                
                if result.returncode == 0 and "connected" in result.stdout.decode().lower():
                    return {
                        "success": True,
                        "device_id": f"{ip_address}:5555",
                        "connection_type": "wifi",
                        "message": "Device connected successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to connect to device"
                    }
                    
        except Exception as e:
            self.logger.error(f"Error connecting to device {ip_address}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_discovered_devices(self) -> List[DiscoveredDevice]:
        """Get all discovered devices"""
        return list(self.discovered_devices.values())
    
    def get_android_devices(self) -> List[DiscoveredDevice]:
        """Get discovered Android devices"""
        return [device for device in self.discovered_devices.values() if device.is_android]
    
    def get_adb_connected_devices(self) -> List[DiscoveredDevice]:
        """Get ADB-connected devices"""
        return [device for device in self.discovered_devices.values() if device.adb_connected]
    
    def get_usb_connected_devices(self) -> List[DiscoveredDevice]:
        """Get USB-connected devices"""
        return [device for device in self.discovered_devices.values() if device.usb_connected]
    
    def get_device_by_ip(self, ip_address: str) -> Optional[DiscoveredDevice]:
        """Get device by IP address"""
        return self.discovered_devices.get(ip_address)
    
    def get_device_by_id(self, device_id: str) -> Optional[DiscoveredDevice]:
        """Get device by device ID"""
        for device in self.discovered_devices.values():
            if device.device_id == device_id:
                return device
        return None
    
    def clear_discovered_devices(self):
        """Clear discovered devices list"""
        self.discovered_devices.clear()
        self.logger.info("Cleared discovered devices list")
    
    def export_discovery_results(self) -> List[Dict]:
        """Export discovery results"""
        return [asdict(device) for device in self.discovered_devices.values()]
    
    def get_scan_statistics(self) -> Dict:
        """Get enhanced scan statistics"""
        total_devices = len(self.discovered_devices)
        android_devices = len(self.get_android_devices())
        adb_connected = len(self.get_adb_connected_devices())
        usb_connected = len(self.get_usb_connected_devices())
        accessible_devices = len([d for d in self.discovered_devices.values() if d.is_accessible])
        
        return {
            "total_discovered": total_devices,
            "android_devices": android_devices,
            "adb_connected": adb_connected,
            "usb_connected": usb_connected,
            "accessible_devices": accessible_devices,
            "android_percentage": (android_devices / total_devices * 100) if total_devices > 0 else 0,
            "accessible_percentage": (accessible_devices / total_devices * 100) if total_devices > 0 else 0,
            "adb_percentage": (adb_connected / total_devices * 100) if total_devices > 0 else 0,
            "usb_percentage": (usb_connected / total_devices * 100) if total_devices > 0 else 0
        }
    
    def get_device_details(self, ip_address: str) -> Optional[Dict]:
        """Get detailed device information"""
        device = self.get_device_by_ip(ip_address)
        if device:
            return asdict(device)
        return None