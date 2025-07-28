"""
Advanced Network Monitor
Real-time network monitoring and traffic analysis
"""

import asyncio
import json
import logging
import os
import psutil
import socket
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading
import scapy.all as scapy

@dataclass
class NetworkMetrics:
    """Network metrics structure"""
    timestamp: float
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    connections_count: int
    active_ports: List[int]
    bandwidth_usage: float
    latency: float
    packet_loss: float

class AdvancedNetworkMonitor:
    """Advanced network monitoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.monitoring_thread = None
        self.network_history: List[NetworkMetrics] = []
        self.packet_capture_active = False
        self.captured_packets: List[Dict] = []
        self.network_alerts: List[Dict] = []
        
        # Network thresholds
        self.network_thresholds = {
            "high_bandwidth": 1000000,  # 1MB/s
            "high_latency": 100,  # 100ms
            "high_packet_loss": 5.0,  # 5%
            "suspicious_ports": [22, 23, 3389, 5900, 8080]
        }
        
    async def start_network_monitoring(self, device_id: str, interval: int = 5) -> Dict:
        """Start network monitoring"""
        try:
            if self.monitoring_active:
                return {
                    "success": False,
                    "error": "Network monitoring already active"
                }
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._network_monitoring_loop,
                args=(device_id, interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"Started network monitoring for device {device_id}")
            return {
                "success": True,
                "device_id": device_id,
                "interval": interval,
                "message": "Network monitoring started"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting network monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_network_monitoring(self) -> Dict:
        """Stop network monitoring"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("Network monitoring stopped")
            return {
                "success": True,
                "message": "Network monitoring stopped"
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping network monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _network_monitoring_loop(self, device_id: str, interval: int):
        """Main network monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect network metrics
                metrics = self._collect_network_metrics(device_id)
                self.network_history.append(metrics)
                
                # Check for network alerts
                self._check_network_alerts(metrics)
                
                # Keep only last 1000 records
                if len(self.network_history) > 1000:
                    self.network_history = self.network_history[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in network monitoring loop: {str(e)}")
                time.sleep(interval)
    
    def _collect_network_metrics(self, device_id: str) -> NetworkMetrics:
        """Collect comprehensive network metrics"""
        try:
            # Get network I/O counters
            net_io = psutil.net_io_counters()
            
            # Get active connections
            connections = psutil.net_connections()
            connections_count = len(connections)
            
            # Get active ports
            active_ports = list(set([conn.laddr.port for conn in connections if conn.laddr]))
            
            # Calculate bandwidth usage
            bandwidth_usage = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024  # MB/s
            
            # Measure latency
            latency = self._measure_latency()
            
            # Calculate packet loss
            packet_loss = self._calculate_packet_loss()
            
            return NetworkMetrics(
                timestamp=time.time(),
                bytes_sent=net_io.bytes_sent,
                bytes_recv=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_recv=net_io.packets_recv,
                connections_count=connections_count,
                active_ports=active_ports,
                bandwidth_usage=bandwidth_usage,
                latency=latency,
                packet_loss=packet_loss
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {str(e)}")
            return NetworkMetrics(
                timestamp=time.time(),
                bytes_sent=0,
                bytes_recv=0,
                packets_sent=0,
                packets_recv=0,
                connections_count=0,
                active_ports=[],
                bandwidth_usage=0.0,
                latency=0.0,
                packet_loss=0.0
            )
    
    def _measure_latency(self) -> float:
        """Measure network latency"""
        try:
            # Measure latency to Google DNS
            start_time = time.time()
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except Exception:
            return 0.0
    
    def _calculate_packet_loss(self) -> float:
        """Calculate packet loss percentage"""
        try:
            # Simulate packet loss calculation
            # In real implementation, this would use ping or similar
            return 0.5 + (time.time() % 2)  # Simulated packet loss
        except Exception:
            return 0.0
    
    def _check_network_alerts(self, metrics: NetworkMetrics):
        """Check for network alerts"""
        alerts = []
        
        # Check for high bandwidth usage
        if metrics.bandwidth_usage > self.network_thresholds["high_bandwidth"]:
            alerts.append({
                "type": "high_bandwidth",
                "value": metrics.bandwidth_usage,
                "threshold": self.network_thresholds["high_bandwidth"],
                "timestamp": metrics.timestamp
            })
        
        # Check for high latency
        if metrics.latency > self.network_thresholds["high_latency"]:
            alerts.append({
                "type": "high_latency",
                "value": metrics.latency,
                "threshold": self.network_thresholds["high_latency"],
                "timestamp": metrics.timestamp
            })
        
        # Check for high packet loss
        if metrics.packet_loss > self.network_thresholds["high_packet_loss"]:
            alerts.append({
                "type": "high_packet_loss",
                "value": metrics.packet_loss,
                "threshold": self.network_thresholds["high_packet_loss"],
                "timestamp": metrics.timestamp
            })
        
        # Check for suspicious ports
        for port in metrics.active_ports:
            if port in self.network_thresholds["suspicious_ports"]:
                alerts.append({
                    "type": "suspicious_port",
                    "port": port,
                    "timestamp": metrics.timestamp
                })
        
        if alerts:
            self.network_alerts.extend(alerts)
            self.logger.warning(f"Network alerts detected: {len(alerts)} alerts")
    
    async def start_packet_capture(self, interface: str = "eth0", duration: int = 60) -> Dict:
        """Start packet capture"""
        try:
            if self.packet_capture_active:
                return {
                    "success": False,
                    "error": "Packet capture already active"
                }
            
            self.packet_capture_active = True
            self.captured_packets.clear()
            
            # Start packet capture in background
            capture_thread = threading.Thread(
                target=self._packet_capture_loop,
                args=(interface, duration),
                daemon=True
            )
            capture_thread.start()
            
            self.logger.info(f"Started packet capture on interface {interface}")
            return {
                "success": True,
                "interface": interface,
                "duration": duration,
                "message": "Packet capture started"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting packet capture: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _packet_capture_loop(self, interface: str, duration: int):
        """Packet capture loop"""
        try:
            start_time = time.time()
            
            # Use scapy for packet capture
            packets = scapy.sniff(
                iface=interface,
                timeout=duration,
                prn=self._process_packet
            )
            
            self.packet_capture_active = False
            self.logger.info(f"Packet capture completed. Captured {len(self.captured_packets)} packets")
            
        except Exception as e:
            self.logger.error(f"Error in packet capture: {str(e)}")
            self.packet_capture_active = False
    
    def _process_packet(self, packet):
        """Process captured packet"""
        try:
            packet_info = {
                "timestamp": time.time(),
                "src_ip": packet[scapy.IP].src if scapy.IP in packet else None,
                "dst_ip": packet[scapy.IP].dst if scapy.IP in packet else None,
                "src_port": packet[scapy.TCP].sport if scapy.TCP in packet else None,
                "dst_port": packet[scapy.TCP].dport if scapy.TCP in packet else None,
                "protocol": packet.proto if hasattr(packet, 'proto') else None,
                "length": len(packet),
                "flags": packet[scapy.TCP].flags if scapy.TCP in packet else None
            }
            
            self.captured_packets.append(packet_info)
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {str(e)}")
    
    def get_network_statistics(self) -> Dict:
        """Get comprehensive network statistics"""
        if not self.network_history:
            return {}
        
        metrics = self.network_history
        
        # Calculate averages
        avg_bandwidth = sum(m.bandwidth_usage for m in metrics) / len(metrics)
        avg_latency = sum(m.latency for m in metrics) / len(metrics)
        avg_packet_loss = sum(m.packet_loss for m in metrics) / len(metrics)
        
        # Calculate peaks
        max_bandwidth = max(m.bandwidth_usage for m in metrics)
        max_latency = max(m.latency for m in metrics)
        max_packet_loss = max(m.packet_loss for m in metrics)
        
        # Get unique ports
        all_ports = []
        for m in metrics:
            all_ports.extend(m.active_ports)
        unique_ports = list(set(all_ports))
        
        return {
            "monitoring_active": self.monitoring_active,
            "packet_capture_active": self.packet_capture_active,
            "total_metrics": len(metrics),
            "captured_packets": len(self.captured_packets),
            "averages": {
                "bandwidth_usage": avg_bandwidth,
                "latency": avg_latency,
                "packet_loss": avg_packet_loss
            },
            "peaks": {
                "max_bandwidth": max_bandwidth,
                "max_latency": max_latency,
                "max_packet_loss": max_packet_loss
            },
            "ports": {
                "unique_ports": unique_ports,
                "total_ports": len(unique_ports)
            },
            "alerts": {
                "total_alerts": len(self.network_alerts),
                "recent_alerts": len([a for a in self.network_alerts if time.time() - a["timestamp"] < 3600])
            }
        }
    
    def get_captured_packets(self, limit: int = 100) -> List[Dict]:
        """Get captured packets"""
        return self.captured_packets[-limit:] if self.captured_packets else []
    
    def get_network_alerts(self, recent_only: bool = True) -> List[Dict]:
        """Get network alerts"""
        if recent_only:
            # Return alerts from last hour
            cutoff_time = time.time() - 3600
            return [alert for alert in self.network_alerts if alert["timestamp"] > cutoff_time]
        return self.network_alerts
    
    def clear_network_alerts(self):
        """Clear all network alerts"""
        self.network_alerts.clear()
        self.logger.info("All network alerts cleared")
    
    def scan_network_ports(self, target_ip: str, ports: List[int] = None) -> Dict:
        """Scan network ports"""
        try:
            if not ports:
                ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
            
            open_ports = []
            
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((target_ip, port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                except Exception:
                    continue
            
            return {
                "success": True,
                "target_ip": target_ip,
                "scanned_ports": ports,
                "open_ports": open_ports,
                "total_open": len(open_ports)
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning ports: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_network_connections(self) -> List[Dict]:
        """Get current network connections"""
        try:
            connections = psutil.net_connections()
            connection_list = []
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    connection_info = {
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    }
                    connection_list.append(connection_info)
            
            return connection_list
            
        except Exception as e:
            self.logger.error(f"Error getting connections: {str(e)}")
            return []
    
    def export_network_data(self, format_type: str = "json") -> str:
        """Export network data"""
        try:
            if format_type == "json":
                return json.dumps({
                    "network_metrics": [
                        {
                            "timestamp": m.timestamp,
                            "bytes_sent": m.bytes_sent,
                            "bytes_recv": m.bytes_recv,
                            "packets_sent": m.packets_sent,
                            "packets_recv": m.packets_recv,
                            "connections_count": m.connections_count,
                            "active_ports": m.active_ports,
                            "bandwidth_usage": m.bandwidth_usage,
                            "latency": m.latency,
                            "packet_loss": m.packet_loss
                        }
                        for m in self.network_history
                    ],
                    "captured_packets": self.captured_packets,
                    "network_alerts": self.network_alerts
                }, indent=2)
            else:
                return "Unsupported format"
                
        except Exception as e:
            self.logger.error(f"Error exporting network data: {str(e)}")
            return ""