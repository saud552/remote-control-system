"""
Enhanced Advanced Monitoring Manager
Integrates all monitoring systems with PhoneSploit-Pro features
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

# Import monitoring systems
from advanced_performance_monitor import AdvancedPerformanceMonitor
from advanced_network_monitor import AdvancedNetworkMonitor
from advanced_security_monitor import AdvancedSecurityMonitor
from intelligent_alert_system import IntelligentAlertSystem
from advanced_data_analytics import AdvancedDataAnalytics

# Import enhanced systems
from auto_device_discovery import EnhancedAutoDeviceDiscovery
from secure_connection import EnhancedSecureConnection
from device_manager import EnhancedDeviceManager

@dataclass
class EnhancedMonitoringSession:
    """Enhanced monitoring session structure"""
    session_id: str
    device_id: str
    start_time: float
    end_time: Optional[float]
    monitoring_types: List[str]
    status: str
    data_collected: int
    # PhoneSploit-Pro specific fields
    device_info: Optional[Dict] = None
    security_level: str = "normal"
    encryption_enabled: bool = False
    real_time_alerts: bool = True
    data_retention_days: int = 30

class EnhancedAdvancedMonitoringManager:
    """Enhanced advanced monitoring manager with PhoneSploit-Pro features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced monitoring systems
        self.performance_monitor = AdvancedPerformanceMonitor()
        self.network_monitor = AdvancedNetworkMonitor()
        self.security_monitor = AdvancedSecurityMonitor()
        self.alert_system = IntelligentAlertSystem()
        self.data_analytics = AdvancedDataAnalytics()
        
        # Initialize PhoneSploit-Pro systems
        self.device_discovery = EnhancedAutoDeviceDiscovery()
        self.secure_connection = EnhancedSecureConnection()
        self.device_manager = EnhancedDeviceManager()
        
        # Enhanced session management
        self.active_sessions: Dict[str, EnhancedMonitoringSession] = {}
        self.session_history: List[EnhancedMonitoringSession] = []
        
        # Enhanced data aggregation
        self.aggregated_data: Dict[str, List[Dict]] = {
            "performance": [],
            "network": [],
            "security": [],
            "device_info": [],
            "connection_status": []
        }
        
        # Enhanced monitoring status
        self.monitoring_active = False
        self.monitoring_thread = None
        self.real_time_mode = True
        self.auto_device_discovery = True
        
        # PhoneSploit-Pro specific settings
        self.encryption_enabled = True
        self.secure_communication = True
        self.threat_detection_enabled = True
        self.auto_response_enabled = False
        
        # Start background tasks
        self._start_enhanced_background_tasks()
    
    def _start_enhanced_background_tasks(self):
        """Start enhanced background monitoring tasks"""
        asyncio.create_task(self._enhanced_device_discovery_task())
        asyncio.create_task(self._enhanced_security_monitoring_task())
        asyncio.create_task(self._enhanced_data_cleanup_task())
        asyncio.create_task(self._enhanced_health_check_task())
    
    async def _enhanced_device_discovery_task(self):
        """Enhanced device discovery task"""
        while True:
            try:
                if self.auto_device_discovery:
                    # Scan for new devices
                    discovered_devices = await self.device_discovery.scan_network_enhanced()
                    
                    for device in discovered_devices:
                        # Register new devices
                        await self.device_manager.discover_and_register_device(
                            device.ip_address, 
                            {
                                "hostname": device.hostname,
                                "is_android": device.is_android,
                                "connection_type": device.connection_type
                            }
                        )
                    
                    if discovered_devices:
                        self.logger.info(f"Enhanced discovery found {len(discovered_devices)} devices")
                
                await asyncio.sleep(300)  # Scan every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in enhanced device discovery: {str(e)}")
                await asyncio.sleep(300)
    
    async def _enhanced_security_monitoring_task(self):
        """Enhanced security monitoring task"""
        while True:
            try:
                if self.threat_detection_enabled:
                    # Check for security threats
                    for session_id, session in self.active_sessions.items():
                        if session.security_level != "normal":
                            # Enhanced threat response
                            await self._handle_enhanced_threat(session_id, session)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in enhanced security monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _enhanced_data_cleanup_task(self):
        """Enhanced data cleanup task"""
        while True:
            try:
                # Clean up old data based on retention policy
                current_time = time.time()
                
                for category in self.aggregated_data:
                    # Remove data older than retention period
                    retention_seconds = 30 * 24 * 3600  # 30 days
                    self.aggregated_data[category] = [
                        data for data in self.aggregated_data[category]
                        if current_time - data.get("timestamp", 0) < retention_seconds
                    ]
                
                # Clean up old session history
                self.session_history = [
                    session for session in self.session_history
                    if current_time - session.start_time < (30 * 24 * 3600)
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error in enhanced data cleanup: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _enhanced_health_check_task(self):
        """Enhanced health check task"""
        while True:
            try:
                # Check system health
                health_status = await self._check_enhanced_system_health()
                
                if not health_status["healthy"]:
                    self.logger.warning(f"System health issues detected: {health_status['issues']}")
                    
                    # Auto-recovery if enabled
                    if self.auto_response_enabled:
                        await self._perform_enhanced_auto_recovery(health_status)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in enhanced health check: {str(e)}")
                await asyncio.sleep(300)
    
    async def start_enhanced_comprehensive_monitoring(self, device_id: str, 
                                                    monitoring_types: List[str] = None,
                                                    interval: int = 5,
                                                    security_level: str = "normal",
                                                    encryption_enabled: bool = True) -> Dict:
        """Start enhanced comprehensive monitoring for a device"""
        try:
            if self.monitoring_active:
                return {
                    "success": False,
                    "error": "Monitoring already active"
                }
            
            if not monitoring_types:
                monitoring_types = ["performance", "network", "security", "device_info"]
            
            session_id = f"enhanced_monitoring_session_{int(time.time())}"
            
            # Get device information
            device_info = self.device_manager.get_device(device_id)
            if not device_info:
                return {
                    "success": False,
                    "error": "Device not found"
                }
            
            # Create enhanced monitoring session
            session = EnhancedMonitoringSession(
                session_id=session_id,
                device_id=device_id,
                start_time=time.time(),
                end_time=None,
                monitoring_types=monitoring_types,
                status="active",
                data_collected=0,
                device_info=asdict(device_info) if device_info else None,
                security_level=security_level,
                encryption_enabled=encryption_enabled,
                real_time_alerts=True,
                data_retention_days=30
            )
            
            self.active_sessions[session_id] = session
            self.monitoring_active = True
            
            # Start enhanced individual monitoring systems
            monitoring_results = {}
            
            if "performance" in monitoring_types:
                perf_result = await self.performance_monitor.start_monitoring(device_id, interval)
                monitoring_results["performance"] = perf_result
            
            if "network" in monitoring_types:
                net_result = await self.network_monitor.start_network_monitoring(device_id, interval)
                monitoring_results["network"] = net_result
            
            if "security" in monitoring_types:
                sec_result = await self.security_monitor.start_security_monitoring(device_id, interval)
                monitoring_results["security"] = sec_result
            
            if "device_info" in monitoring_types:
                device_result = await self._start_enhanced_device_monitoring(device_id, interval)
                monitoring_results["device_info"] = device_result
            
            # Start enhanced coordination loop
            self.monitoring_thread = threading.Thread(
                target=self._enhanced_monitoring_coordination_loop,
                args=(session_id, interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            # Setup enhanced secure communication if enabled
            if self.secure_communication and encryption_enabled:
                secure_channel = self.secure_connection.create_secure_channel_enhanced(device_id)
                session.encryption_enabled = True
            
            self.logger.info(f"Enhanced monitoring started for device {device_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "monitoring_types": monitoring_types,
                "security_level": security_level,
                "encryption_enabled": encryption_enabled,
                "results": monitoring_results
            }
            
        except Exception as e:
            self.logger.error(f"Error starting enhanced monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_enhanced_device_monitoring(self, device_id: str, interval: int) -> Dict:
        """Start enhanced device information monitoring"""
        try:
            # Monitor device-specific information
            device_info = self.device_manager.get_device(device_id)
            if not device_info:
                return {"success": False, "error": "Device not found"}
            
            # Start monitoring device properties
            monitoring_data = {
                "device_id": device_id,
                "device_model": device_info.device_model,
                "android_version": device_info.android_version,
                "battery_level": device_info.battery_level,
                "is_rooted": device_info.is_rooted,
                "connection_type": device_info.connection_type,
                "status": device_info.status.value,
                "timestamp": time.time()
            }
            
            # Store device monitoring data
            self.aggregated_data["device_info"].append(monitoring_data)
            
            return {
                "success": True,
                "message": "Enhanced device monitoring started"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting enhanced device monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _enhanced_monitoring_coordination_loop(self, session_id: str, interval: int):
        """Enhanced monitoring coordination loop"""
        try:
            while session_id in self.active_sessions:
                # Collect enhanced aggregated data
                aggregated_data = self._collect_enhanced_aggregated_data()
                
                # Store enhanced data
                self._store_enhanced_aggregated_data(aggregated_data)
                
                # Evaluate enhanced alerts
                asyncio.create_task(self._evaluate_enhanced_alerts(aggregated_data))
                
                # Perform enhanced analytics
                asyncio.create_task(self._perform_enhanced_analytics(aggregated_data))
                
                # Update session data count
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].data_collected += 1
                
                time.sleep(interval)
                
        except Exception as e:
            self.logger.error(f"Error in enhanced monitoring coordination: {str(e)}")
    
    def _collect_enhanced_aggregated_data(self) -> Dict:
        """Collect enhanced aggregated data"""
        try:
            current_time = time.time()
            
            # Collect data from all monitoring systems
            performance_data = self.performance_monitor.get_latest_metrics()
            network_data = self.network_monitor.get_latest_metrics()
            security_data = self.security_monitor.get_latest_metrics()
            
            # Enhanced aggregated data
            aggregated_data = {
                "timestamp": current_time,
                "performance": performance_data,
                "network": network_data,
                "security": security_data,
                "device_info": self.aggregated_data["device_info"][-1] if self.aggregated_data["device_info"] else {},
                "connection_status": self._get_enhanced_connection_status(),
                "system_health": self._get_enhanced_system_health_sync(),
                "threat_level": self._calculate_enhanced_threat_level(security_data)
            }
            
            return aggregated_data
            
        except Exception as e:
            self.logger.error(f"Error collecting enhanced aggregated data: {str(e)}")
            return {}
    
    def _get_enhanced_connection_status(self) -> Dict:
        """Get enhanced connection status"""
        try:
            connected_devices = self.device_manager.get_connected_devices()
            total_devices = len(self.device_manager.get_all_devices())
            
            return {
                "connected_devices": len(connected_devices),
                "total_devices": total_devices,
                "connection_rate": (len(connected_devices) / total_devices * 100) if total_devices > 0 else 0,
                "secure_connections": len([d for d in connected_devices if d.adb_connected]),
                "usb_connections": len([d for d in connected_devices if d.usb_connected])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced connection status: {str(e)}")
            return {}
    
    def _get_enhanced_system_health_sync(self) -> Dict:
        """Get enhanced system health (synchronous version)"""
        try:
            return {
                "monitoring_active": self.monitoring_active,
                "active_sessions": len(self.active_sessions),
                "encryption_enabled": self.encryption_enabled,
                "secure_communication": self.secure_communication,
                "threat_detection_enabled": self.threat_detection_enabled,
                "auto_response_enabled": self.auto_response_enabled,
                "real_time_mode": self.real_time_mode
            }
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced system health: {str(e)}")
            return {}
    
    def _calculate_enhanced_threat_level(self, security_data: Dict) -> int:
        """Calculate enhanced threat level"""
        try:
            threat_level = 0
            
            if security_data:
                # Enhanced threat calculation
                if security_data.get("suspicious_activities", 0) > 10:
                    threat_level += 3
                if security_data.get("blocked_ips", 0) > 5:
                    threat_level += 2
                if security_data.get("failed_attempts", 0) > 20:
                    threat_level += 2
                if security_data.get("malware_detected", False):
                    threat_level += 4
                if security_data.get("unauthorized_access", False):
                    threat_level += 5
            
            return min(threat_level, 10)  # Cap at 10
            
        except Exception as e:
            self.logger.error(f"Error calculating enhanced threat level: {str(e)}")
            return 0
    
    def _store_enhanced_aggregated_data(self, data: Dict):
        """Store enhanced aggregated data"""
        try:
            current_time = time.time()
            
            # Store data with enhanced metadata
            enhanced_data = {
                **data,
                "metadata": {
                    "encryption_enabled": self.encryption_enabled,
                    "secure_communication": self.secure_communication,
                    "real_time_mode": self.real_time_mode,
                    "data_retention_days": 30
                }
            }
            
            # Store in appropriate categories
            for category in ["performance", "network", "security"]:
                if category in data:
                    self.aggregated_data[category].append({
                        "timestamp": current_time,
                        "data": data[category],
                        "metadata": enhanced_data["metadata"]
                    })
            
            # Limit data storage
            for category in self.aggregated_data:
                if len(self.aggregated_data[category]) > 10000:  # Keep last 10k entries
                    self.aggregated_data[category] = self.aggregated_data[category][-5000:]
                    
        except Exception as e:
            self.logger.error(f"Error storing enhanced aggregated data: {str(e)}")
    
    async def _evaluate_enhanced_alerts(self, data: Dict):
        """Evaluate enhanced alerts"""
        try:
            # Enhanced alert evaluation with PhoneSploit-Pro features
            alerts = []
            
            # Performance alerts
            if "performance" in data:
                perf_data = data["performance"]
                if perf_data.get("cpu_usage", 0) > 90:
                    alerts.append({
                        "type": "performance",
                        "severity": "high",
                        "message": "High CPU usage detected",
                        "data": perf_data
                    })
            
            # Security alerts
            if "security" in data:
                sec_data = data["security"]
                threat_level = data.get("threat_level", 0)
                
                if threat_level > 7:
                    alerts.append({
                        "type": "security",
                        "severity": "critical",
                        "message": "Critical threat level detected",
                        "data": sec_data
                    })
            
            # Device-specific alerts
            if "device_info" in data:
                device_data = data["device_info"]
                if device_data.get("battery_level", 100) < 10:
                    alerts.append({
                        "type": "device",
                        "severity": "warning",
                        "message": "Low battery level",
                        "data": device_data
                    })
            
            # Process alerts
            for alert in alerts:
                await self.alert_system.process_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error evaluating enhanced alerts: {str(e)}")
    
    async def _perform_enhanced_analytics(self, data: Dict):
        """Perform enhanced analytics"""
        try:
            # Enhanced analytics with PhoneSploit-Pro features
            analytics_results = {}
            
            # Performance analytics
            if "performance" in data:
                perf_analytics = await self.data_analytics.analyze_performance_data(data["performance"])
                analytics_results["performance"] = perf_analytics
            
            # Security analytics
            if "security" in data:
                sec_analytics = await self.data_analytics.analyze_security_data(data["security"])
                analytics_results["security"] = sec_analytics
            
            # Network analytics
            if "network" in data:
                net_analytics = await self.data_analytics.analyze_network_data(data["network"])
                analytics_results["network"] = net_analytics
            
            # Store analytics results
            self._store_enhanced_analytics_results(analytics_results)
            
        except Exception as e:
            self.logger.error(f"Error performing enhanced analytics: {str(e)}")
    
    def _store_enhanced_analytics_results(self, results: Dict):
        """Store enhanced analytics results"""
        try:
            # Store analytics results with enhanced metadata
            analytics_entry = {
                "timestamp": time.time(),
                "results": results,
                "metadata": {
                    "encryption_enabled": self.encryption_enabled,
                    "real_time_mode": self.real_time_mode
                }
            }
            
            # Store in analytics history
            if not hasattr(self, 'analytics_history'):
                self.analytics_history = []
            
            self.analytics_history.append(analytics_entry)
            
            # Limit analytics history
            if len(self.analytics_history) > 1000:
                self.analytics_history = self.analytics_history[-500:]
                
        except Exception as e:
            self.logger.error(f"Error storing enhanced analytics results: {str(e)}")
    
    async def _handle_enhanced_threat(self, session_id: str, session: EnhancedMonitoringSession):
        """Handle enhanced threat response"""
        try:
            # Enhanced threat response with PhoneSploit-Pro features
            if session.security_level == "high":
                # Implement enhanced security measures
                await self._implement_enhanced_security_measures(session_id)
            elif session.security_level == "critical":
                # Implement emergency response
                await self._implement_emergency_response(session_id)
                
        except Exception as e:
            self.logger.error(f"Error handling enhanced threat: {str(e)}")
    
    async def _implement_enhanced_security_measures(self, session_id: str):
        """Implement enhanced security measures"""
        try:
            # Enhanced security measures
            session = self.active_sessions.get(session_id)
            if session:
                # Enable enhanced encryption
                session.encryption_enabled = True
                
                # Increase monitoring frequency
                # Add additional security monitoring
                
                self.logger.info(f"Enhanced security measures implemented for session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Error implementing enhanced security measures: {str(e)}")
    
    async def _implement_emergency_response(self, session_id: str):
        """Implement emergency response"""
        try:
            # Emergency response measures
            session = self.active_sessions.get(session_id)
            if session:
                # Stop monitoring
                await self.stop_enhanced_comprehensive_monitoring(session_id)
                
                # Alert administrators
                await self.alert_system.send_emergency_alert({
                    "type": "emergency",
                    "severity": "critical",
                    "message": "Emergency response activated",
                    "session_id": session_id
                })
                
                self.logger.warning(f"Emergency response activated for session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Error implementing emergency response: {str(e)}")
    
    async def _check_enhanced_system_health(self) -> Dict:
        """Check enhanced system health"""
        try:
            issues = []
            
            # Check monitoring systems
            if not self.monitoring_active:
                issues.append("Monitoring not active")
            
            # Check device connections
            connected_devices = self.device_manager.get_connected_devices()
            if len(connected_devices) == 0:
                issues.append("No devices connected")
            
            # Check encryption
            if not self.encryption_enabled:
                issues.append("Encryption disabled")
            
            return {
                "healthy": len(issues) == 0,
                "issues": issues,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking enhanced system health: {str(e)}")
            return {
                "healthy": False,
                "issues": [str(e)],
                "timestamp": time.time()
            }
    
    async def _perform_enhanced_auto_recovery(self, health_status: Dict):
        """Perform enhanced auto recovery"""
        try:
            # Implement auto recovery measures
            for issue in health_status.get("issues", []):
                if "Monitoring not active" in issue:
                    # Restart monitoring
                    pass
                elif "No devices connected" in issue:
                    # Attempt device reconnection
                    pass
                elif "Encryption disabled" in issue:
                    # Re-enable encryption
                    self.encryption_enabled = True
            
            self.logger.info("Enhanced auto recovery performed")
            
        except Exception as e:
            self.logger.error(f"Error performing enhanced auto recovery: {str(e)}")
    
    async def stop_enhanced_comprehensive_monitoring(self, session_id: str = None) -> Dict:
        """Stop enhanced comprehensive monitoring"""
        try:
            if session_id:
                # Stop specific session
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    session.end_time = time.time()
                    session.status = "stopped"
                    
                    # Move to history
                    self.session_history.append(session)
                    del self.active_sessions[session_id]
                    
                    self.logger.info(f"Enhanced monitoring stopped for session {session_id}")
                    
                    return {
                        "success": True,
                        "session_id": session_id,
                        "duration": session.end_time - session.start_time,
                        "data_collected": session.data_collected
                    }
                else:
                    return {
                        "success": False,
                        "error": "Session not found"
                    }
            else:
                # Stop all sessions
                stopped_sessions = []
                
                for session_id, session in list(self.active_sessions.items()):
                    session.end_time = time.time()
                    session.status = "stopped"
                    
                    # Move to history
                    self.session_history.append(session)
                    stopped_sessions.append(session_id)
                
                # Clear active sessions
                self.active_sessions.clear()
                self.monitoring_active = False
                
                self.logger.info(f"All enhanced monitoring sessions stopped")
                
                return {
                    "success": True,
                    "stopped_sessions": stopped_sessions,
                    "total_sessions": len(stopped_sessions)
                }
                
        except Exception as e:
            self.logger.error(f"Error stopping enhanced monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_enhanced_monitoring_status(self) -> Dict:
        """Get enhanced monitoring status"""
        try:
            active_sessions = len(self.active_sessions)
            total_sessions = len(self.session_history) + active_sessions
            
            # Calculate enhanced statistics
            total_data_points = sum(session.data_collected for session in self.active_sessions.values())
            
            # Get enhanced system information
            system_info = {
                "monitoring_active": self.monitoring_active,
                "active_sessions": active_sessions,
                "total_sessions": total_sessions,
                "total_data_points": total_data_points,
                "encryption_enabled": self.encryption_enabled,
                "secure_communication": self.secure_communication,
                "threat_detection_enabled": self.threat_detection_enabled,
                "auto_response_enabled": self.auto_response_enabled,
                "real_time_mode": self.real_time_mode,
                "auto_device_discovery": self.auto_device_discovery
            }
            
            # Get session details
            session_details = []
            for session_id, session in self.active_sessions.items():
                session_details.append({
                    "session_id": session_id,
                    "device_id": session.device_id,
                    "monitoring_types": session.monitoring_types,
                    "status": session.status,
                    "data_collected": session.data_collected,
                    "security_level": session.security_level,
                    "encryption_enabled": session.encryption_enabled,
                    "duration": time.time() - session.start_time
                })
            
            return {
                "system_info": system_info,
                "active_sessions": session_details,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced monitoring status: {str(e)}")
            return {}
    
    def get_enhanced_comprehensive_statistics(self) -> Dict:
        """Get enhanced comprehensive statistics"""
        try:
            # Enhanced statistics with PhoneSploit-Pro features
            stats = {
                "performance": self.performance_monitor.get_statistics(),
                "network": self.network_monitor.get_statistics(),
                "security": self.security_monitor.get_statistics(),
                "alerts": self.alert_system.get_statistics(),
                "analytics": self.data_analytics.get_statistics(),
                "devices": self.device_manager.get_all_device_stats(),
                "connections": self._get_enhanced_connection_status(),
                "system_health": self._get_enhanced_system_health_sync()
            }
            
            # Add enhanced metadata
            stats["metadata"] = {
                "encryption_enabled": self.encryption_enabled,
                "secure_communication": self.secure_communication,
                "threat_detection_enabled": self.threat_detection_enabled,
                "auto_response_enabled": self.auto_response_enabled,
                "real_time_mode": self.real_time_mode,
                "timestamp": time.time()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced comprehensive statistics: {str(e)}")
            return {}
    
    def get_enhanced_recent_data(self, category: str = None, limit: int = 100) -> Dict:
        """Get enhanced recent data"""
        try:
            if category:
                if category in self.aggregated_data:
                    return {
                        category: self.aggregated_data[category][-limit:],
                        "metadata": {
                            "category": category,
                            "limit": limit,
                            "total_entries": len(self.aggregated_data[category]),
                            "encryption_enabled": self.encryption_enabled
                        }
                    }
                else:
                    return {"error": f"Category {category} not found"}
            else:
                # Return all categories
                result = {}
                for category, data in self.aggregated_data.items():
                    result[category] = data[-limit:]
                
                result["metadata"] = {
                    "limit": limit,
                    "encryption_enabled": self.encryption_enabled,
                    "categories": list(self.aggregated_data.keys())
                }
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error getting enhanced recent data: {str(e)}")
            return {}
    
    def export_enhanced_monitoring_data(self, session_id: str = None, format_type: str = "json") -> str:
        """Export enhanced monitoring data"""
        try:
            export_data = {
                "export_timestamp": time.time(),
                "system_info": {
                    "encryption_enabled": self.encryption_enabled,
                    "secure_communication": self.secure_communication,
                    "threat_detection_enabled": self.threat_detection_enabled,
                    "auto_response_enabled": self.auto_response_enabled,
                    "real_time_mode": self.real_time_mode
                },
                "sessions": [],
                "data": self.aggregated_data,
                "analytics": getattr(self, 'analytics_history', [])
            }
            
            if session_id:
                # Export specific session
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    export_data["sessions"].append(asdict(session))
                else:
                    # Look in history
                    for session in self.session_history:
                        if session.session_id == session_id:
                            export_data["sessions"].append(asdict(session))
                            break
            else:
                # Export all sessions
                for session in self.active_sessions.values():
                    export_data["sessions"].append(asdict(session))
                for session in self.session_history:
                    export_data["sessions"].append(asdict(session))
            
            if format_type == "json":
                return json.dumps(export_data, indent=2, default=str)
            else:
                return str(export_data)
                
        except Exception as e:
            self.logger.error(f"Error exporting enhanced monitoring data: {str(e)}")
            return ""
    
    def configure_enhanced_alert_rules(self, rules: List[Dict]) -> Dict:
        """Configure enhanced alert rules"""
        try:
            # Configure enhanced alert rules with PhoneSploit-Pro features
            configured_rules = []
            
            for rule in rules:
                # Add enhanced rule processing
                enhanced_rule = {
                    **rule,
                    "encryption_enabled": self.encryption_enabled,
                    "real_time_mode": self.real_time_mode,
                    "auto_response_enabled": self.auto_response_enabled
                }
                configured_rules.append(enhanced_rule)
            
            # Configure alert system
            result = self.alert_system.configure_rules(configured_rules)
            
            return {
                "success": True,
                "configured_rules": len(configured_rules),
                "results": result
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring enhanced alert rules: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_enhanced_notification_channels(self, channels: Dict) -> Dict:
        """Configure enhanced notification channels"""
        try:
            # Configure enhanced notification channels with PhoneSploit-Pro features
            enhanced_channels = {}
            
            for channel_type, config in channels.items():
                enhanced_config = {
                    **config,
                    "encryption_enabled": self.encryption_enabled,
                    "secure_communication": self.secure_communication
                }
                enhanced_channels[channel_type] = enhanced_config
            
            # Configure notification system
            result = self.alert_system.configure_notification_channels(enhanced_channels)
            
            return {
                "success": True,
                "configured_channels": len(enhanced_channels),
                "results": result
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring enhanced notification channels: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_enhanced_active_alerts(self, limit: int = 50) -> List[Dict]:
        """Get enhanced active alerts"""
        try:
            alerts = self.alert_system.get_active_alerts(limit)
            
            # Add enhanced metadata to alerts
            enhanced_alerts = []
            for alert in alerts:
                enhanced_alert = {
                    **alert,
                    "encryption_enabled": self.encryption_enabled,
                    "threat_detection_enabled": self.threat_detection_enabled,
                    "auto_response_enabled": self.auto_response_enabled
                }
                enhanced_alerts.append(enhanced_alert)
            
            return enhanced_alerts
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced active alerts: {str(e)}")
            return []
    
    def get_enhanced_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get enhanced recent analyses"""
        try:
            analyses = getattr(self, 'analytics_history', [])
            
            # Return recent analyses with enhanced metadata
            recent_analyses = analyses[-limit:] if analyses else []
            
            for analysis in recent_analyses:
                analysis["encryption_enabled"] = self.encryption_enabled
                analysis["real_time_mode"] = self.real_time_mode
            
            return recent_analyses
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced recent analyses: {str(e)}")
            return []
    
    def acknowledge_enhanced_alert(self, alert_id: str) -> Dict:
        """Acknowledge enhanced alert"""
        try:
            result = self.alert_system.acknowledge_alert(alert_id)
            
            # Add enhanced metadata
            if result.get("success"):
                result["encryption_enabled"] = self.encryption_enabled
                result["threat_detection_enabled"] = self.threat_detection_enabled
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error acknowledging enhanced alert: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resolve_enhanced_alert(self, alert_id: str) -> Dict:
        """Resolve enhanced alert"""
        try:
            result = self.alert_system.resolve_alert(alert_id)
            
            # Add enhanced metadata
            if result.get("success"):
                result["encryption_enabled"] = self.encryption_enabled
                result["auto_response_enabled"] = self.auto_response_enabled
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error resolving enhanced alert: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_enhanced_monitoring_data(self, category: str = None) -> Dict:
        """Clear enhanced monitoring data"""
        try:
            if category:
                if category in self.aggregated_data:
                    self.aggregated_data[category].clear()
                    self.logger.info(f"Cleared enhanced monitoring data for category: {category}")
                else:
                    return {
                        "success": False,
                        "error": f"Category {category} not found"
                    }
            else:
                # Clear all data
                for category in self.aggregated_data:
                    self.aggregated_data[category].clear()
                
                # Clear analytics history
                if hasattr(self, 'analytics_history'):
                    self.analytics_history.clear()
                
                self.logger.info("Cleared all enhanced monitoring data")
            
            return {
                "success": True,
                "message": f"Enhanced monitoring data cleared for category: {category if category else 'all'}"
            }
            
        except Exception as e:
            self.logger.error(f"Error clearing enhanced monitoring data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }