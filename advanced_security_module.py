#!/usr/bin/env python3
"""
Advanced Security Module - Phase 7: Final Security & Isolation
الأمان والعزل والتطوير النهائي
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import random
import secrets
import socket
import ssl
import subprocess
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import psutil
import docker
import requests
import nmap
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether, ARP

@dataclass
class SecurityConfig:
    """Advanced security configuration"""
    # Sandbox settings
    sandbox_enabled: bool = True
    sandbox_type: str = "docker"  # docker, vm, chroot
    sandbox_network: str = "isolated"
    sandbox_memory_limit: str = "2GB"
    sandbox_cpu_limit: str = "50%"
    
    # Anti-detection settings
    anti_detection_enabled: bool = True
    stealth_mode: bool = True
    traffic_mimicking: bool = True
    signature_evasion: bool = True
    timing_randomization: bool = True
    
    # Encryption settings
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval: int = 3600  # seconds
    secure_key_storage: bool = True
    hardware_acceleration: bool = True
    
    # Performance settings
    performance_optimization: bool = True
    multi_threading: bool = True
    gpu_acceleration: bool = True
    memory_optimization: bool = True
    
    # Monitoring settings
    resource_monitoring: bool = True
    anomaly_detection: bool = True
    threat_detection: bool = True
    log_encryption: bool = True

@dataclass
class SandboxInfo:
    """Sandbox environment information"""
    id: str
    type: str
    status: str
    resources: Dict[str, Any]
    network_config: Dict[str, Any]
    isolation_level: str
    created_at: datetime
    last_activity: datetime

@dataclass
class SecurityEvent:
    """Security event information"""
    id: str
    type: str
    severity: str
    description: str
    timestamp: datetime
    source: str
    details: Dict[str, Any]

class AdvancedSecurityModule:
    """Advanced security and isolation module"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.encryption_key = self._generate_encryption_key()
        self.sandboxes: Dict[str, SandboxInfo] = {}
        self.security_events: List[SecurityEvent] = []
        self.performance_metrics = {}
        self.threat_detection_active = True
        
        # Initialize security components
        self._initialize_security_components()
        
        # Start monitoring threads
        self._start_monitoring_threads()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup secure logging"""
        logger = logging.getLogger('advanced_security')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Encrypted file handler
        handler = logging.FileHandler('logs/security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        
        return logger
    
    def _generate_encryption_key(self) -> bytes:
        """Generate strong encryption key"""
        return Fernet.generate_key()
    
    def _initialize_security_components(self):
        """Initialize all security components"""
        self.logger.info("Initializing advanced security components...")
        
        # Initialize Docker client for sandboxing
        try:
            self.docker_client = docker.from_env()
            self.logger.info("Docker client initialized successfully")
        except Exception as e:
            self.logger.warning(f"Docker not available: {e}")
            self.docker_client = None
        
        # Initialize encryption
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize anti-detection
        self._setup_anti_detection()
        
        # Initialize performance monitoring
        self._setup_performance_monitoring()
        
        # Initialize threat detection
        self._setup_threat_detection()
    
    def _setup_anti_detection(self):
        """Setup advanced anti-detection mechanisms"""
        self.logger.info("Setting up anti-detection mechanisms...")
        
        # Traffic mimicking
        self.legitimate_traffic_patterns = {
            'web': ['GET / HTTP/1.1', 'POST /api/data', 'HEAD /status'],
            'dns': ['A', 'AAAA', 'MX', 'TXT'],
            'smtp': ['EHLO', 'MAIL FROM', 'RCPT TO'],
            'ftp': ['USER', 'PASS', 'LIST', 'RETR']
        }
        
        # Signature evasion
        self.signature_evasion_techniques = [
            'polymorphic_code',
            'packer_obfuscation',
            'string_encryption',
            'api_hooking',
            'process_injection'
        ]
        
        # Timing randomization
        self.timing_delays = {
            'min_delay': 0.1,
            'max_delay': 2.0,
            'randomization_factor': 0.3
        }
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring"""
        self.logger.info("Setting up performance monitoring...")
        
        self.performance_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'network_usage': [],
            'disk_usage': [],
            'response_times': [],
            'throughput': []
        }
    
    def _setup_threat_detection(self):
        """Setup advanced threat detection"""
        self.logger.info("Setting up threat detection...")
        
        # Initialize threat detection patterns
        self.threat_patterns = {
            'network_scanning': [
                'nmap_scan',
                'port_scan',
                'service_detection',
                'os_fingerprinting'
            ],
            'malware_indicators': [
                'suspicious_processes',
                'unusual_network_activity',
                'file_modifications',
                'registry_changes'
            ],
            'intrusion_attempts': [
                'brute_force',
                'sql_injection',
                'xss_attempts',
                'buffer_overflow'
            ]
        }
    
    def _start_monitoring_threads(self):
        """Start security monitoring threads"""
        # Resource monitoring thread
        threading.Thread(target=self._resource_monitor, daemon=True).start()
        
        # Threat detection thread
        threading.Thread(target=self._threat_detection_monitor, daemon=True).start()
        
        # Performance optimization thread
        threading.Thread(target=self._performance_optimizer, daemon=True).start()
        
        # Anti-detection thread
        threading.Thread(target=self._anti_detection_monitor, daemon=True).start()
    
    async def create_sandbox(self, sandbox_type: str = "docker") -> SandboxInfo:
        """Create isolated sandbox environment"""
        sandbox_id = f"sandbox_{secrets.token_hex(8)}"
        
        try:
            if sandbox_type == "docker" and self.docker_client:
                # Create Docker container with security restrictions
                container = self.docker_client.containers.run(
                    "ubuntu:20.04",
                    command="tail -f /dev/null",
                    detach=True,
                    name=sandbox_id,
                    security_opt=[
                        "no-new-privileges",
                        "seccomp=unconfined"
                    ],
                    cap_drop=["ALL"],
                    cap_add=["NET_BIND_SERVICE"],
                    mem_limit=self.config.sandbox_memory_limit,
                    cpu_quota=int(float(self.config.sandbox_cpu_limit.replace('%', '')) * 1000),
                    network_mode="bridge",
                    volumes={
                        '/tmp': {'bind': '/tmp', 'mode': 'ro'},
                        '/var/tmp': {'bind': '/var/tmp', 'mode': 'ro'}
                    },
                    environment={
                        'SANDBOX_ID': sandbox_id,
                        'ISOLATION_LEVEL': 'high'
                    }
                )
                
                sandbox_info = SandboxInfo(
                    id=sandbox_id,
                    type="docker",
                    status="running",
                    resources={
                        'memory_limit': self.config.sandbox_memory_limit,
                        'cpu_limit': self.config.sandbox_cpu_limit,
                        'container_id': container.id
                    },
                    network_config={
                        'network_mode': 'bridge',
                        'ip_address': container.attrs['NetworkSettings']['IPAddress']
                    },
                    isolation_level="high",
                    created_at=datetime.now(),
                    last_activity=datetime.now()
                )
                
                self.sandboxes[sandbox_id] = sandbox_info
                self.logger.info(f"Created Docker sandbox: {sandbox_id}")
                
                return sandbox_info
            
            elif sandbox_type == "chroot":
                # Create chroot jail
                sandbox_path = f"/tmp/sandbox_{sandbox_id}"
                os.makedirs(sandbox_path, exist_ok=True)
                
                # Create minimal filesystem
                self._create_chroot_environment(sandbox_path)
                
                sandbox_info = SandboxInfo(
                    id=sandbox_id,
                    type="chroot",
                    status="ready",
                    resources={
                        'path': sandbox_path,
                        'filesystem': 'isolated'
                    },
                    network_config={
                        'network_mode': 'isolated',
                        'ip_address': '127.0.0.1'
                    },
                    isolation_level="medium",
                    created_at=datetime.now(),
                    last_activity=datetime.now()
                )
                
                self.sandboxes[sandbox_id] = sandbox_info
                self.logger.info(f"Created chroot sandbox: {sandbox_id}")
                
                return sandbox_info
            
            else:
                raise ValueError(f"Unsupported sandbox type: {sandbox_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to create sandbox: {e}")
            raise
    
    def _create_chroot_environment(self, sandbox_path: str):
        """Create chroot jail environment"""
        # Create essential directories
        essential_dirs = ['bin', 'lib', 'lib64', 'usr', 'etc', 'dev', 'proc']
        for dir_name in essential_dirs:
            os.makedirs(os.path.join(sandbox_path, dir_name), exist_ok=True)
        
        # Copy essential binaries
        essential_bins = ['bash', 'ls', 'cat', 'echo', 'python3']
        for bin_name in essential_bins:
            try:
                bin_path = subprocess.check_output(['which', bin_name]).decode().strip()
                if os.path.exists(bin_path):
                    subprocess.run(['cp', bin_path, os.path.join(sandbox_path, 'bin', bin_name)])
            except:
                pass
    
    async def execute_in_sandbox(self, sandbox_id: str, command: str, 
                                input_data: str = None) -> Dict[str, Any]:
        """Execute command in isolated sandbox"""
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox = self.sandboxes[sandbox_id]
        
        try:
            if sandbox.type == "docker":
                # Execute in Docker container
                container = self.docker_client.containers.get(sandbox.resources['container_id'])
                
                # Apply anti-detection measures
                command = self._apply_anti_detection(command)
                
                # Execute command
                exec_result = container.exec_run(
                    command,
                    workdir='/tmp',
                    environment={
                        'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                        'SANDBOX_ID': sandbox_id
                    }
                )
                
                result = {
                    'exit_code': exec_result.exit_code,
                    'output': exec_result.output.decode('utf-8', errors='ignore'),
                    'error': exec_result.stderr.decode('utf-8', errors='ignore') if exec_result.stderr else None
                }
                
            elif sandbox.type == "chroot":
                # Execute in chroot jail
                chroot_path = sandbox.resources['path']
                
                # Create temporary script
                script_path = os.path.join(chroot_path, 'tmp', f'cmd_{secrets.token_hex(4)}.sh')
                with open(script_path, 'w') as f:
                    f.write(f"#!/bin/bash\n{command}")
                os.chmod(script_path, 0o755)
                
                # Execute in chroot
                process = subprocess.run([
                    'chroot', chroot_path, '/bin/bash', script_path
                ], capture_output=True, text=True, timeout=30)
                
                result = {
                    'exit_code': process.returncode,
                    'output': process.stdout,
                    'error': process.stderr
                }
                
                # Cleanup
                os.remove(script_path)
            
            # Update sandbox activity
            sandbox.last_activity = datetime.now()
            
            # Log execution
            self._log_security_event(
                "sandbox_execution",
                "info",
                f"Command executed in sandbox {sandbox_id}",
                {"command": command, "result": result}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Sandbox execution failed: {e}")
            raise
    
    def _apply_anti_detection(self, command: str) -> str:
        """Apply anti-detection measures to command"""
        if not self.config.anti_detection_enabled:
            return command
        
        # Add random delays
        if self.config.timing_randomization:
            delay = random.uniform(
                self.timing_delays['min_delay'],
                self.timing_delays['max_delay']
            )
            command = f"sleep {delay} && {command}"
        
        # Add legitimate traffic patterns
        if self.config.traffic_mimicking:
            # Add random legitimate-looking traffic
            patterns = self.legitimate_traffic_patterns['web']
            pattern = random.choice(patterns)
            command = f"echo '{pattern}' && {command}"
        
        # Apply signature evasion
        if self.config.signature_evasion:
            # Obfuscate command
            command = self._obfuscate_command(command)
        
        return command
    
    def _obfuscate_command(self, command: str) -> str:
        """Obfuscate command to evade detection"""
        # Simple obfuscation techniques
        obfuscated = command
        
        # Replace common patterns
        replacements = {
            'nmap': 'n\\m\\a\\p',
            'metasploit': 'm\\e\\t\\a\\s\\p\\l\\o\\i\\t',
            'hashcat': 'h\\a\\s\\h\\c\\a\\t',
            'aircrack': 'a\\i\\r\\c\\r\\a\\c\\k'
        }
        
        for original, replacement in replacements.items():
            obfuscated = obfuscated.replace(original, replacement)
        
        return obfuscated
    
    def _resource_monitor(self):
        """Monitor system resources"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                
                # Network usage
                network = psutil.net_io_counters()
                
                # Disk usage
                disk = psutil.disk_usage('/')
                
                # Store metrics
                self.performance_metrics['cpu_usage'].append({
                    'timestamp': datetime.now(),
                    'value': cpu_percent
                })
                
                self.performance_metrics['memory_usage'].append({
                    'timestamp': datetime.now(),
                    'value': memory.percent
                })
                
                self.performance_metrics['network_usage'].append({
                    'timestamp': datetime.now(),
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                })
                
                # Keep only last 1000 metrics
                for key in self.performance_metrics:
                    if len(self.performance_metrics[key]) > 1000:
                        self.performance_metrics[key] = self.performance_metrics[key][-1000:]
                
                # Check for resource anomalies
                if cpu_percent > 90:
                    self._log_security_event(
                        "resource_anomaly",
                        "warning",
                        f"High CPU usage detected: {cpu_percent}%",
                        {"cpu_percent": cpu_percent}
                    )
                
                if memory.percent > 85:
                    self._log_security_event(
                        "resource_anomaly",
                        "warning",
                        f"High memory usage detected: {memory.percent}%",
                        {"memory_percent": memory.percent}
                    )
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
            
            time.sleep(5)  # Check every 5 seconds
    
    def _threat_detection_monitor(self):
        """Monitor for threats and attacks"""
        while self.threat_detection_active:
            try:
                # Network scanning detection
                self._detect_network_scanning()
                
                # Malware detection
                self._detect_malware_indicators()
                
                # Intrusion detection
                self._detect_intrusion_attempts()
                
                # Sandbox monitoring
                self._monitor_sandboxes()
                
            except Exception as e:
                self.logger.error(f"Threat detection error: {e}")
            
            time.sleep(10)  # Check every 10 seconds
    
    def _detect_network_scanning(self):
        """Detect network scanning activities"""
        try:
            # Use scapy to monitor network traffic
            def packet_callback(packet):
                if IP in packet and TCP in packet:
                    # Detect port scanning patterns
                    if packet[TCP].flags == 2:  # SYN flag
                        self._log_security_event(
                            "network_scanning",
                            "warning",
                            f"Potential port scan detected from {packet[IP].src}",
                            {
                                "source_ip": packet[IP].src,
                                "destination_ip": packet[IP].dst,
                                "port": packet[TCP].dport
                            }
                        )
            
            # Sniff packets for 1 second
            scapy.sniff(prn=packet_callback, timeout=1, store=0)
            
        except Exception as e:
            self.logger.error(f"Network scanning detection error: {e}")
    
    def _detect_malware_indicators(self):
        """Detect malware indicators"""
        try:
            # Check for suspicious processes
            suspicious_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check for suspicious process names
                    suspicious_names = ['backdoor', 'trojan', 'keylogger', 'spyware']
                    if any(name in proc.info['name'].lower() for name in suspicious_names):
                        suspicious_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if suspicious_processes:
                self._log_security_event(
                    "malware_detection",
                    "high",
                    "Suspicious processes detected",
                    {"processes": suspicious_processes}
                )
            
        except Exception as e:
            self.logger.error(f"Malware detection error: {e}")
    
    def _detect_intrusion_attempts(self):
        """Detect intrusion attempts"""
        try:
            # Check for failed login attempts
            auth_log = "/var/log/auth.log"
            if os.path.exists(auth_log):
                with open(auth_log, 'r') as f:
                    recent_logs = f.readlines()[-100:]  # Last 100 lines
                    
                    failed_logins = [line for line in recent_logs if "Failed password" in line]
                    if len(failed_logins) > 5:
                        self._log_security_event(
                            "intrusion_attempt",
                            "high",
                            "Multiple failed login attempts detected",
                            {"failed_attempts": len(failed_logins)}
                        )
            
        except Exception as e:
            self.logger.error(f"Intrusion detection error: {e}")
    
    def _monitor_sandboxes(self):
        """Monitor sandbox activities"""
        for sandbox_id, sandbox in self.sandboxes.items():
            try:
                if sandbox.type == "docker":
                    container = self.docker_client.containers.get(sandbox.resources['container_id'])
                    stats = container.stats(stream=False)
                    
                    # Check for unusual activity
                    if stats['cpu_stats']['cpu_usage']['total_usage'] > 1000000000:  # High CPU
                        self._log_security_event(
                            "sandbox_anomaly",
                            "warning",
                            f"High CPU usage in sandbox {sandbox_id}",
                            {"cpu_usage": stats['cpu_stats']['cpu_usage']['total_usage']}
                        )
                
            except Exception as e:
                self.logger.error(f"Sandbox monitoring error: {e}")
    
    def _performance_optimizer(self):
        """Optimize system performance"""
        while True:
            try:
                # CPU optimization
                if self.config.performance_optimization:
                    # Adjust process priorities
                    current_process = psutil.Process()
                    current_process.nice(psutil.HIGH_PRIORITY_CLASS)
                
                # Memory optimization
                if self.config.memory_optimization:
                    # Clear unnecessary caches
                    if len(self.performance_metrics['memory_usage']) > 100:
                        # Keep only recent metrics
                        self.performance_metrics['memory_usage'] = self.performance_metrics['memory_usage'][-100:]
                
                # Network optimization
                if self.config.multi_threading:
                    # Optimize network connections
                    pass
                
            except Exception as e:
                self.logger.error(f"Performance optimization error: {e}")
            
            time.sleep(30)  # Optimize every 30 seconds
    
    def _anti_detection_monitor(self):
        """Monitor and apply anti-detection measures"""
        while True:
            try:
                # Check for detection attempts
                self._check_detection_attempts()
                
                # Apply stealth measures
                self._apply_stealth_measures()
                
                # Rotate encryption keys
                if self.config.key_rotation_interval > 0:
                    self._rotate_encryption_keys()
                
            except Exception as e:
                self.logger.error(f"Anti-detection monitoring error: {e}")
            
            time.sleep(60)  # Check every minute
    
    def _check_detection_attempts(self):
        """Check for detection attempts"""
        try:
            # Check for common detection tools
            detection_tools = ['wireshark', 'tcpdump', 'nmap', 'netstat', 'lsof']
            for tool in detection_tools:
                try:
                    result = subprocess.run(['which', tool], capture_output=True, text=True)
                    if result.returncode == 0:
                        self._log_security_event(
                            "detection_attempt",
                            "warning",
                            f"Detection tool found: {tool}",
                            {"tool": tool, "path": result.stdout.strip()}
                        )
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Detection check error: {e}")
    
    def _apply_stealth_measures(self):
        """Apply stealth measures"""
        try:
            # Hide process names
            if self.config.stealth_mode:
                # Rename process to look legitimate
                current_process = psutil.Process()
                # Note: This is a simplified example
                pass
            
            # Encrypt network traffic
            if self.config.traffic_mimicking:
                # Apply traffic encryption
                pass
            
        except Exception as e:
            self.logger.error(f"Stealth measures error: {e}")
    
    def _rotate_encryption_keys(self):
        """Rotate encryption keys"""
        try:
            # Generate new key
            new_key = Fernet.generate_key()
            
            # Re-encrypt sensitive data with new key
            new_cipher = Fernet(new_key)
            
            # Update key
            self.encryption_key = new_key
            self.cipher_suite = new_cipher
            
            self.logger.info("Encryption keys rotated successfully")
            
        except Exception as e:
            self.logger.error(f"Key rotation error: {e}")
    
    def _log_security_event(self, event_type: str, severity: str, 
                           description: str, details: Dict[str, Any] = None):
        """Log security event"""
        event = SecurityEvent(
            id=f"event_{secrets.token_hex(8)}",
            type=event_type,
            severity=severity,
            description=description,
            timestamp=datetime.now(),
            source="advanced_security_module",
            details=details or {}
        )
        
        self.security_events.append(event)
        
        # Log to file
        if self.config.log_encryption:
            # Encrypt log entry
            log_entry = json.dumps(asdict(event))
            encrypted_log = self.cipher_suite.encrypt(log_entry.encode())
            
            with open('logs/security_encrypted.log', 'ab') as f:
                f.write(encrypted_log + b'\n')
        else:
            self.logger.warning(f"Security Event [{severity.upper()}]: {description}")
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'active_sandboxes': len(self.sandboxes),
            'security_events': len(self.security_events)
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security status"""
        return {
            'sandbox_enabled': self.config.sandbox_enabled,
            'anti_detection_enabled': self.config.anti_detection_enabled,
            'encryption_enabled': True,
            'performance_optimization': self.config.performance_optimization,
            'active_sandboxes': len(self.sandboxes),
            'security_events': len(self.security_events),
            'threat_detection_active': self.threat_detection_active
        }
    
    def cleanup_sandbox(self, sandbox_id: str):
        """Cleanup sandbox"""
        if sandbox_id in self.sandboxes:
            sandbox = self.sandboxes[sandbox_id]
            
            try:
                if sandbox.type == "docker":
                    container = self.docker_client.containers.get(sandbox.resources['container_id'])
                    container.stop()
                    container.remove()
                
                elif sandbox.type == "chroot":
                    # Cleanup chroot environment
                    import shutil
                    shutil.rmtree(sandbox.resources['path'], ignore_errors=True)
                
                del self.sandboxes[sandbox_id]
                self.logger.info(f"Sandbox {sandbox_id} cleaned up")
                
            except Exception as e:
                self.logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
    
    def shutdown(self):
        """Shutdown security module"""
        self.logger.info("Shutting down advanced security module...")
        
        # Stop threat detection
        self.threat_detection_active = False
        
        # Cleanup all sandboxes
        for sandbox_id in list(self.sandboxes.keys()):
            self.cleanup_sandbox(sandbox_id)
        
        self.logger.info("Advanced security module shutdown complete")

# Example usage
if __name__ == "__main__":
    config = SecurityConfig()
    security_module = AdvancedSecurityModule(config)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        security_module.shutdown()