"""
Advanced Security Monitor
Real-time security monitoring and threat detection
"""

import asyncio
import json
import logging
import os
import psutil
import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading
import hashlib
import hmac

@dataclass
class SecurityEvent:
    """Security event structure"""
    timestamp: float
    event_type: str
    severity: str
    description: str
    source_ip: str
    target_ip: str
    port: int
    protocol: str
    payload_size: int
    threat_signature: str

class AdvancedSecurityMonitor:
    """Advanced security monitoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.monitoring_thread = None
        self.security_events: List[SecurityEvent] = []
        self.threat_signatures: Dict[str, Dict] = {}
        self.blocked_ips: List[str] = []
        self.suspicious_activities: List[Dict] = []
        
        # Security thresholds
        self.security_thresholds = {
            "max_failed_attempts": 5,
            "max_connections_per_minute": 100,
            "suspicious_payload_size": 1000000,  # 1MB
            "max_ports_scan": 10
        }
        
        # Initialize threat signatures
        self._initialize_threat_signatures()
        
    def _initialize_threat_signatures(self):
        """Initialize known threat signatures"""
        self.threat_signatures = {
            "sql_injection": {
                "patterns": [
                    r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                    r"(--|\b(and|or)\b\s+\d+\s*=\s*\d+)",
                    r"(\b(exec|execute|eval|system)\b)"
                ],
                "severity": "high"
            },
            "xss_attack": {
                "patterns": [
                    r"(<script[^>]*>.*?</script>)",
                    r"(javascript:.*)",
                    r"(on\w+\s*=)",
                    r"(<iframe[^>]*>)"
                ],
                "severity": "high"
            },
            "directory_traversal": {
                "patterns": [
                    r"(\.\./|\.\.\\)",
                    r"(%2e%2e%2f|%2e%2e%5c)",
                    r"(\.\.%2f|\.\.%5c)"
                ],
                "severity": "medium"
            },
            "command_injection": {
                "patterns": [
                    r"(\b(cmd|command|shell|bash|powershell)\b)",
                    r"(\||&|;|`|\\$)",
                    r"(\b(wget|curl|nc|netcat)\b)"
                ],
                "severity": "high"
            },
            "port_scan": {
                "patterns": [
                    r"(nmap|masscan|angryip|zenmap)",
                    r"(\b(scan|probe|recon)\b)"
                ],
                "severity": "medium"
            },
            "brute_force": {
                "patterns": [
                    r"(admin|root|user|test|guest)",
                    r"(password|pass|pwd|123|abc)"
                ],
                "severity": "medium"
            }
        }
    
    async def start_security_monitoring(self, device_id: str, interval: int = 5) -> Dict:
        """Start security monitoring"""
        try:
            if self.monitoring_active:
                return {
                    "success": False,
                    "error": "Security monitoring already active"
                }
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._security_monitoring_loop,
                args=(device_id, interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"Started security monitoring for device {device_id}")
            return {
                "success": True,
                "device_id": device_id,
                "interval": interval,
                "message": "Security monitoring started"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting security monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_security_monitoring(self) -> Dict:
        """Stop security monitoring"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("Security monitoring stopped")
            return {
                "success": True,
                "message": "Security monitoring stopped"
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping security monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _security_monitoring_loop(self, device_id: str, interval: int):
        """Main security monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor network connections
                self._monitor_network_connections()
                
                # Monitor system processes
                self._monitor_system_processes()
                
                # Monitor file system changes
                self._monitor_file_system()
                
                # Monitor authentication attempts
                self._monitor_authentication()
                
                # Check for suspicious activities
                self._detect_suspicious_activities()
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring loop: {str(e)}")
                time.sleep(interval)
    
    def _monitor_network_connections(self):
        """Monitor network connections for suspicious activity"""
        try:
            connections = psutil.net_connections()
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    # Check for suspicious ports
                    if conn.raddr and conn.raddr.port in [22, 23, 3389, 5900, 8080]:
                        self._log_security_event(
                            "suspicious_port_connection",
                            "medium",
                            f"Connection to suspicious port {conn.raddr.port}",
                            "0.0.0.0",
                            conn.raddr.ip if conn.raddr else "unknown",
                            conn.raddr.port if conn.raddr else 0,
                            "tcp",
                            0,
                            "suspicious_port"
                        )
                    
                    # Check for multiple connections from same IP
                    if conn.raddr:
                        connections_from_ip = len([
                            c for c in connections 
                            if c.raddr and c.raddr.ip == conn.raddr.ip
                        ])
                        
                        if connections_from_ip > self.security_thresholds["max_connections_per_minute"]:
                            self._log_security_event(
                                "multiple_connections",
                                "high",
                                f"Multiple connections from {conn.raddr.ip}",
                                "0.0.0.0",
                                conn.raddr.ip,
                                0,
                                "tcp",
                                0,
                                "multiple_connections"
                            )
                            
        except Exception as e:
            self.logger.error(f"Error monitoring network connections: {str(e)}")
    
    def _monitor_system_processes(self):
        """Monitor system processes for suspicious activity"""
        try:
            processes = psutil.process_iter(['pid', 'name', 'cmdline', 'connections'])
            
            for proc in processes:
                try:
                    # Check for suspicious process names
                    suspicious_processes = [
                        'nmap', 'masscan', 'angryip', 'zenmap',
                        'wireshark', 'tcpdump', 'netcat', 'nc'
                    ]
                    
                    if proc.info['name'] and any(sp in proc.info['name'].lower() for sp in suspicious_processes):
                        self._log_security_event(
                            "suspicious_process",
                            "high",
                            f"Suspicious process detected: {proc.info['name']}",
                            "0.0.0.0",
                            "0.0.0.0",
                            0,
                            "process",
                            0,
                            "suspicious_process"
                        )
                    
                    # Check for processes with many connections
                    if proc.info['connections']:
                        if len(proc.info['connections']) > 50:
                            self._log_security_event(
                                "high_connection_process",
                                "medium",
                                f"Process with many connections: {proc.info['name']}",
                                "0.0.0.0",
                                "0.0.0.0",
                                0,
                                "process",
                                0,
                                "high_connections"
                            )
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error monitoring system processes: {str(e)}")
    
    def _monitor_file_system(self):
        """Monitor file system for suspicious changes"""
        try:
            # Check for new files in sensitive directories
            sensitive_dirs = ['/etc', '/var/log', '/home', '/root']
            
            for directory in sensitive_dirs:
                if os.path.exists(directory):
                    try:
                        files = os.listdir(directory)
                        for file in files:
                            file_path = os.path.join(directory, file)
                            
                            # Check file modification time
                            if os.path.isfile(file_path):
                                mtime = os.path.getmtime(file_path)
                                
                                # If file was modified in last 5 minutes
                                if time.time() - mtime < 300:
                                    self._log_security_event(
                                        "file_modified",
                                        "low",
                                        f"File modified: {file_path}",
                                        "0.0.0.0",
                                        "0.0.0.0",
                                        0,
                                        "file",
                                        0,
                                        "file_modified"
                                    )
                    except PermissionError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error monitoring file system: {str(e)}")
    
    def _monitor_authentication(self):
        """Monitor authentication attempts"""
        try:
            # Check for failed login attempts
            # This would typically read from auth logs
            # For now, we'll simulate this
            
            # Simulate checking auth logs
            failed_attempts = self._check_failed_auth_attempts()
            
            if failed_attempts > self.security_thresholds["max_failed_attempts"]:
                self._log_security_event(
                    "brute_force_attempt",
                    "high",
                    f"Multiple failed authentication attempts: {failed_attempts}",
                    "0.0.0.0",
                    "0.0.0.0",
                    0,
                    "auth",
                    0,
                    "brute_force"
                )
                
        except Exception as e:
            self.logger.error(f"Error monitoring authentication: {str(e)}")
    
    def _check_failed_auth_attempts(self) -> int:
        """Check for failed authentication attempts (simulated)"""
        try:
            # In real implementation, this would read from auth logs
            # For now, return a simulated value
            return int(time.time() % 10)
        except Exception:
            return 0
    
    def _detect_suspicious_activities(self):
        """Detect suspicious activities based on patterns"""
        try:
            # Monitor network traffic for suspicious patterns
            connections = psutil.net_connections()
            
            for conn in connections:
                if conn.raddr:
                    # Check for port scanning patterns
                    if self._is_port_scanning(conn.raddr.ip):
                        self._log_security_event(
                            "port_scanning",
                            "high",
                            f"Port scanning detected from {conn.raddr.ip}",
                            "0.0.0.0",
                            conn.raddr.ip,
                            conn.raddr.port,
                            "tcp",
                            0,
                            "port_scan"
                        )
                    
                    # Check for suspicious payload sizes
                    if hasattr(conn, 'bytes_sent') and conn.bytes_sent > self.security_thresholds["suspicious_payload_size"]:
                        self._log_security_event(
                            "large_payload",
                            "medium",
                            f"Large payload detected from {conn.raddr.ip}",
                            "0.0.0.0",
                            conn.raddr.ip,
                            conn.raddr.port,
                            "tcp",
                            conn.bytes_sent,
                            "large_payload"
                        )
                        
        except Exception as e:
            self.logger.error(f"Error detecting suspicious activities: {str(e)}")
    
    def _is_port_scanning(self, ip_address: str) -> bool:
        """Check if IP is performing port scanning"""
        try:
            # Count connections from this IP
            connections = psutil.net_connections()
            connections_from_ip = [
                c for c in connections 
                if c.raddr and c.raddr.ip == ip_address
            ]
            
            # If more than threshold, consider it port scanning
            return len(connections_from_ip) > self.security_thresholds["max_ports_scan"]
            
        except Exception:
            return False
    
    def _log_security_event(self, event_type: str, severity: str, description: str,
                           source_ip: str, target_ip: str, port: int, protocol: str,
                           payload_size: int, threat_signature: str):
        """Log a security event"""
        try:
            event = SecurityEvent(
                timestamp=time.time(),
                event_type=event_type,
                severity=severity,
                description=description,
                source_ip=source_ip,
                target_ip=target_ip,
                port=port,
                protocol=protocol,
                payload_size=payload_size,
                threat_signature=threat_signature
            )
            
            self.security_events.append(event)
            
            # Add to suspicious activities
            self.suspicious_activities.append({
                "timestamp": event.timestamp,
                "type": event_type,
                "severity": severity,
                "description": description,
                "source_ip": source_ip,
                "target_ip": target_ip
            })
            
            self.logger.warning(f"Security event: {event_type} - {description}")
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {str(e)}")
    
    def analyze_payload(self, payload: str) -> Dict:
        """Analyze payload for threats"""
        try:
            threats_detected = []
            
            for threat_name, threat_info in self.threat_signatures.items():
                for pattern in threat_info["patterns"]:
                    if re.search(pattern, payload, re.IGNORECASE):
                        threats_detected.append({
                            "threat_type": threat_name,
                            "severity": threat_info["severity"],
                            "pattern": pattern,
                            "matched_content": re.search(pattern, payload, re.IGNORECASE).group()
                        })
            
            return {
                "success": True,
                "threats_detected": threats_detected,
                "total_threats": len(threats_detected),
                "payload_size": len(payload),
                "is_suspicious": len(threats_detected) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def block_ip(self, ip_address: str, reason: str = "Security threat") -> Dict:
        """Block an IP address"""
        try:
            if ip_address not in self.blocked_ips:
                self.blocked_ips.append(ip_address)
                
                # In real implementation, this would add to firewall rules
                self.logger.info(f"Blocked IP: {ip_address} - {reason}")
                
                return {
                    "success": True,
                    "ip_address": ip_address,
                    "reason": reason,
                    "message": "IP blocked successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "IP already blocked"
                }
                
        except Exception as e:
            self.logger.error(f"Error blocking IP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def unblock_ip(self, ip_address: str) -> Dict:
        """Unblock an IP address"""
        try:
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)
                
                # In real implementation, this would remove from firewall rules
                self.logger.info(f"Unblocked IP: {ip_address}")
                
                return {
                    "success": True,
                    "ip_address": ip_address,
                    "message": "IP unblocked successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "IP not blocked"
                }
                
        except Exception as e:
            self.logger.error(f"Error unblocking IP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_security_statistics(self) -> Dict:
        """Get comprehensive security statistics"""
        if not self.security_events:
            return {}
        
        events = self.security_events
        
        # Count events by severity
        severity_counts = {}
        for event in events:
            severity = event.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count events by type
        type_counts = {}
        for event in events:
            event_type = event.event_type
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        # Get recent events (last hour)
        recent_cutoff = time.time() - 3600
        recent_events = [e for e in events if e.timestamp > recent_cutoff]
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_events": len(events),
            "recent_events": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_activities": len(self.suspicious_activities),
            "severity_distribution": severity_counts,
            "event_type_distribution": type_counts,
            "threat_signatures": len(self.threat_signatures)
        }
    
    def get_security_events(self, limit: int = 100, severity: str = None) -> List[Dict]:
        """Get security events"""
        events = self.security_events
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Convert to dict format
        event_list = []
        for event in events[-limit:]:
            event_list.append({
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "severity": event.severity,
                "description": event.description,
                "source_ip": event.source_ip,
                "target_ip": event.target_ip,
                "port": event.port,
                "protocol": event.protocol,
                "payload_size": event.payload_size,
                "threat_signature": event.threat_signature
            })
        
        return event_list
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IP addresses"""
        return self.blocked_ips.copy()
    
    def get_suspicious_activities(self, limit: int = 100) -> List[Dict]:
        """Get suspicious activities"""
        return self.suspicious_activities[-limit:] if self.suspicious_activities else []
    
    def clear_security_events(self):
        """Clear all security events"""
        self.security_events.clear()
        self.suspicious_activities.clear()
        self.logger.info("All security events cleared")
    
    def export_security_data(self, format_type: str = "json") -> str:
        """Export security data"""
        try:
            if format_type == "json":
                return json.dumps({
                    "security_events": [
                        {
                            "timestamp": e.timestamp,
                            "event_type": e.event_type,
                            "severity": e.severity,
                            "description": e.description,
                            "source_ip": e.source_ip,
                            "target_ip": e.target_ip,
                            "port": e.port,
                            "protocol": e.protocol,
                            "payload_size": e.payload_size,
                            "threat_signature": e.threat_signature
                        }
                        for e in self.security_events
                    ],
                    "blocked_ips": self.blocked_ips,
                    "suspicious_activities": self.suspicious_activities,
                    "threat_signatures": self.threat_signatures
                }, indent=2)
            else:
                return "Unsupported format"
                
        except Exception as e:
            self.logger.error(f"Error exporting security data: {str(e)}")
            return ""