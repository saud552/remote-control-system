"""
Auto Device Discovery System
Automatically discovers and scans for devices on the network
"""

import asyncio
import ipaddress
import logging
import socket
import subprocess
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

@dataclass
class DiscoveredDevice:
    """Discovered device information"""
    ip_address: str
    hostname: Optional[str] = None
    device_type: str = "unknown"
    is_android: bool = False
    is_accessible: bool = False
    response_time: float = 0.0
    open_ports: List[int] = None
    last_seen: float = 0.0

class AutoDeviceDiscovery:
    """Automatic device discovery system"""
    
    def __init__(self):
        self.discovered_devices: Dict[str, DiscoveredDevice] = {}
        self.scan_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def scan_network(self, network_range: str = "192.168.1.0/24") -> List[DiscoveredDevice]:
        """Scan network for devices"""
        try:
            self.logger.info(f"Starting network scan for range: {network_range}")
            
            # Get network addresses
            network = ipaddress.IPv4Network(network_range, strict=False)
            addresses = [str(ip) for ip in network.hosts()]
            
            # Scan addresses concurrently
            tasks = []
            for ip in addresses:
                task = asyncio.create_task(self._scan_device(ip))
                tasks.append(task)
            
            # Wait for all scans to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful discoveries
            discovered = []
            for result in results:
                if isinstance(result, DiscoveredDevice) and result.is_accessible:
                    discovered.append(result)
                    self.discovered_devices[result.ip_address] = result
            
            self.logger.info(f"Scan completed. Found {len(discovered)} accessible devices")
            return discovered
            
        except Exception as e:
            self.logger.error(f"Error scanning network: {str(e)}")
            return []
    
    async def _scan_device(self, ip_address: str) -> Optional[DiscoveredDevice]:
        """Scan a single device"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            if not await self._test_connectivity(ip_address):
                return None
            
            # Check for Android-specific ports
            is_android = await self._check_android_ports(ip_address)
            
            # Get device information
            hostname = await self._get_hostname(ip_address)
            open_ports = await self._scan_ports(ip_address)
            
            response_time = time.time() - start_time
            
            device = DiscoveredDevice(
                ip_address=ip_address,
                hostname=hostname,
                device_type="android" if is_android else "unknown",
                is_android=is_android,
                is_accessible=True,
                response_time=response_time,
                open_ports=open_ports,
                last_seen=time.time()
            )
            
            return device
            
        except Exception as e:
            self.logger.debug(f"Error scanning device {ip_address}: {str(e)}")
            return None
    
    async def _test_connectivity(self, ip_address: str) -> bool:
        """Test basic connectivity to device"""
        try:
            # Test with ping
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                subprocess.run,
                ["ping", "-c", "1", "-W", "1", ip_address],
                subprocess.PIPE,
                subprocess.PIPE
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def _check_android_ports(self, ip_address: str) -> bool:
        """Check for Android-specific open ports"""
        android_ports = [5555, 5037, 8080, 8888]  # ADB, ADB, common Android ports
        
        for port in android_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    return True
            except Exception:
                continue
        
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
    
    async def _scan_ports(self, ip_address: str) -> List[int]:
        """Scan common ports on device"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 5555, 8080, 8888]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            except Exception:
                continue
        
        return open_ports
    
    async def scan_specific_range(self, start_ip: str, end_ip: str) -> List[DiscoveredDevice]:
        """Scan specific IP range"""
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
                task = asyncio.create_task(self._scan_device(ip))
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
    
    def get_discovered_devices(self) -> List[DiscoveredDevice]:
        """Get all discovered devices"""
        return list(self.discovered_devices.values())
    
    def get_android_devices(self) -> List[DiscoveredDevice]:
        """Get discovered Android devices"""
        return [device for device in self.discovered_devices.values() if device.is_android]
    
    def get_device_by_ip(self, ip_address: str) -> Optional[DiscoveredDevice]:
        """Get device by IP address"""
        return self.discovered_devices.get(ip_address)
    
    def clear_discovered_devices(self):
        """Clear discovered devices list"""
        self.discovered_devices.clear()
        self.logger.info("Cleared discovered devices list")
    
    def export_discovery_results(self) -> List[Dict]:
        """Export discovery results"""
        return [
            {
                "ip_address": device.ip_address,
                "hostname": device.hostname,
                "device_type": device.device_type,
                "is_android": device.is_android,
                "is_accessible": device.is_accessible,
                "response_time": device.response_time,
                "open_ports": device.open_ports,
                "last_seen": device.last_seen
            }
            for device in self.discovered_devices.values()
        ]
    
    def get_scan_statistics(self) -> Dict:
        """Get scan statistics"""
        total_devices = len(self.discovered_devices)
        android_devices = len(self.get_android_devices())
        accessible_devices = len([d for d in self.discovered_devices.values() if d.is_accessible])
        
        return {
            "total_discovered": total_devices,
            "android_devices": android_devices,
            "accessible_devices": accessible_devices,
            "android_percentage": (android_devices / total_devices * 100) if total_devices > 0 else 0,
            "accessible_percentage": (accessible_devices / total_devices * 100) if total_devices > 0 else 0
        }