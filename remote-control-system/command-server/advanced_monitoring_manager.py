"""
Advanced Monitoring Manager
Integrates all monitoring systems and provides unified interface
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading

# Import monitoring systems
from advanced_performance_monitor import AdvancedPerformanceMonitor
from advanced_network_monitor import AdvancedNetworkMonitor
from advanced_security_monitor import AdvancedSecurityMonitor
from intelligent_alert_system import IntelligentAlertSystem
from advanced_data_analytics import AdvancedDataAnalytics

@dataclass
class MonitoringSession:
    """Monitoring session structure"""
    session_id: str
    device_id: str
    start_time: float
    end_time: Optional[float]
    monitoring_types: List[str]
    status: str
    data_collected: int

class AdvancedMonitoringManager:
    """Advanced monitoring manager that integrates all monitoring systems"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring systems
        self.performance_monitor = AdvancedPerformanceMonitor()
        self.network_monitor = AdvancedNetworkMonitor()
        self.security_monitor = AdvancedSecurityMonitor()
        self.alert_system = IntelligentAlertSystem()
        self.data_analytics = AdvancedDataAnalytics()
        
        # Session management
        self.active_sessions: Dict[str, MonitoringSession] = {}
        self.session_history: List[MonitoringSession] = []
        
        # Data aggregation
        self.aggregated_data: Dict[str, List[Dict]] = {
            "performance": [],
            "network": [],
            "security": []
        }
        
        # Monitoring status
        self.monitoring_active = False
        self.monitoring_thread = None
        
    async def start_comprehensive_monitoring(self, device_id: str, 
                                          monitoring_types: List[str] = None,
                                          interval: int = 5) -> Dict:
        """Start comprehensive monitoring for a device"""
        try:
            if self.monitoring_active:
                return {
                    "success": False,
                    "error": "Monitoring already active"
                }
            
            if not monitoring_types:
                monitoring_types = ["performance", "network", "security"]
            
            session_id = f"monitoring_session_{int(time.time())}"
            
            # Create monitoring session
            session = MonitoringSession(
                session_id=session_id,
                device_id=device_id,
                start_time=time.time(),
                end_time=None,
                monitoring_types=monitoring_types,
                status="active",
                data_collected=0
            )
            
            self.active_sessions[session_id] = session
            self.monitoring_active = True
            
            # Start individual monitoring systems
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
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_coordination_loop,
                args=(session_id, interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"Started comprehensive monitoring for device {device_id}")
            return {
                "success": True,
                "session_id": session_id,
                "device_id": device_id,
                "monitoring_types": monitoring_types,
                "interval": interval,
                "monitoring_results": monitoring_results,
                "message": "Comprehensive monitoring started successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting comprehensive monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_comprehensive_monitoring(self, session_id: str = None) -> Dict:
        """Stop comprehensive monitoring"""
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
                    
                    # Stop individual monitors
                    self.performance_monitor.stop_monitoring()
                    self.network_monitor.stop_network_monitoring()
                    self.security_monitor.stop_security_monitoring()
                    
                    self.logger.info(f"Stopped monitoring session: {session_id}")
                    return {
                        "success": True,
                        "session_id": session_id,
                        "message": "Monitoring session stopped successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Session not found"
                    }
            else:
                # Stop all monitoring
                self.monitoring_active = False
                
                # Stop all sessions
                for session_id in list(self.active_sessions.keys()):
                    session = self.active_sessions[session_id]
                    session.end_time = time.time()
                    session.status = "stopped"
                    self.session_history.append(session)
                
                self.active_sessions.clear()
                
                # Stop individual monitors
                self.performance_monitor.stop_monitoring()
                self.network_monitor.stop_network_monitoring()
                self.security_monitor.stop_security_monitoring()
                
                self.logger.info("Stopped all monitoring")
                return {
                    "success": True,
                    "message": "All monitoring stopped successfully"
                }
                
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _monitoring_coordination_loop(self, session_id: str, interval: int):
        """Main monitoring coordination loop"""
        while self.monitoring_active and session_id in self.active_sessions:
            try:
                # Collect data from all monitoring systems
                aggregated_data = self._collect_aggregated_data()
                
                # Store aggregated data
                self._store_aggregated_data(aggregated_data)
                
                # Update session data count
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    session.data_collected += len(aggregated_data)
                
                # Evaluate alert rules
                await self._evaluate_alerts(aggregated_data)
                
                # Perform analytics
                await self._perform_analytics(aggregated_data)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring coordination loop: {str(e)}")
                time.sleep(interval)
    
    def _collect_aggregated_data(self) -> Dict:
        """Collect data from all monitoring systems"""
        aggregated_data = {
            "timestamp": time.time(),
            "performance": {},
            "network": {},
            "security": {}
        }
        
        try:
            # Collect performance data
            perf_metrics = self.performance_monitor.get_current_metrics()
            if perf_metrics:
                aggregated_data["performance"] = {
                    "cpu_usage": perf_metrics.cpu_usage,
                    "memory_usage": perf_metrics.memory_usage,
                    "battery_level": perf_metrics.battery_level,
                    "temperature": perf_metrics.temperature,
                    "running_processes": perf_metrics.running_processes,
                    "active_connections": perf_metrics.active_connections
                }
            
            # Collect network data
            net_stats = self.network_monitor.get_network_statistics()
            if net_stats:
                aggregated_data["network"] = {
                    "bandwidth_usage": net_stats.get("averages", {}).get("bandwidth_usage", 0),
                    "latency": net_stats.get("averages", {}).get("latency", 0),
                    "packet_loss": net_stats.get("averages", {}).get("packet_loss", 0),
                    "connections_count": net_stats.get("ports", {}).get("total_ports", 0)
                }
            
            # Collect security data
            sec_stats = self.security_monitor.get_security_statistics()
            if sec_stats:
                aggregated_data["security"] = {
                    "total_events": sec_stats.get("total_events", 0),
                    "recent_events": sec_stats.get("recent_events", 0),
                    "blocked_ips": sec_stats.get("blocked_ips", 0),
                    "threat_level": self._calculate_threat_level(sec_stats)
                }
                
        except Exception as e:
            self.logger.error(f"Error collecting aggregated data: {str(e)}")
        
        return aggregated_data
    
    def _calculate_threat_level(self, security_stats: Dict) -> int:
        """Calculate overall threat level (0-10)"""
        try:
            threat_level = 0
            
            # Base threat level
            total_events = security_stats.get("total_events", 0)
            recent_events = security_stats.get("recent_events", 0)
            blocked_ips = security_stats.get("blocked_ips", 0)
            
            # Calculate threat level based on events
            if total_events > 100:
                threat_level += 3
            elif total_events > 50:
                threat_level += 2
            elif total_events > 10:
                threat_level += 1
            
            # Recent events have higher weight
            if recent_events > 20:
                threat_level += 4
            elif recent_events > 10:
                threat_level += 2
            elif recent_events > 5:
                threat_level += 1
            
            # Blocked IPs indicate active threats
            if blocked_ips > 10:
                threat_level += 3
            elif blocked_ips > 5:
                threat_level += 2
            elif blocked_ips > 0:
                threat_level += 1
            
            return min(threat_level, 10)  # Cap at 10
            
        except Exception:
            return 0
    
    def _store_aggregated_data(self, data: Dict):
        """Store aggregated data in appropriate categories"""
        try:
            timestamp = data.get("timestamp", time.time())
            
            # Store performance data
            if data.get("performance"):
                self.aggregated_data["performance"].append({
                    "timestamp": timestamp,
                    **data["performance"]
                })
            
            # Store network data
            if data.get("network"):
                self.aggregated_data["network"].append({
                    "timestamp": timestamp,
                    **data["network"]
                })
            
            # Store security data
            if data.get("security"):
                self.aggregated_data["security"].append({
                    "timestamp": timestamp,
                    **data["security"]
                })
            
            # Keep only last 1000 records per category
            for category in self.aggregated_data:
                if len(self.aggregated_data[category]) > 1000:
                    self.aggregated_data[category] = self.aggregated_data[category][-1000:]
                    
        except Exception as e:
            self.logger.error(f"Error storing aggregated data: {str(e)}")
    
    async def _evaluate_alerts(self, data: Dict):
        """Evaluate alert rules against current data"""
        try:
            # Prepare metrics for alert evaluation
            metrics = {
                "cpu_usage": data.get("performance", {}).get("cpu_usage", 0),
                "memory_usage": data.get("performance", {}).get("memory_usage", 0),
                "battery_level": data.get("performance", {}).get("battery_level", 100),
                "temperature": data.get("performance", {}).get("temperature", 0),
                "bandwidth_usage": data.get("network", {}).get("bandwidth_usage", 0),
                "latency": data.get("network", {}).get("latency", 0),
                "packet_loss": data.get("network", {}).get("packet_loss", 0),
                "threat_level": data.get("security", {}).get("threat_level", 0),
                "security_events": data.get("security", {}).get("total_events", 0)
            }
            
            # Evaluate alert rules
            triggered_alerts = await self.alert_system.evaluate_alert_rules(metrics)
            
            if triggered_alerts:
                self.logger.info(f"Triggered {len(triggered_alerts)} alerts")
                
        except Exception as e:
            self.logger.error(f"Error evaluating alerts: {str(e)}")
    
    async def _perform_analytics(self, data: Dict):
        """Perform analytics on collected data"""
        try:
            # Perform analytics periodically (every 10 data points)
            for category in ["performance", "network", "security"]:
                category_data = self.aggregated_data[category]
                
                if len(category_data) >= 10 and len(category_data) % 10 == 0:
                    if category == "performance":
                        await self.data_analytics.analyze_performance_data(category_data)
                    elif category == "network":
                        await self.data_analytics.analyze_network_data(category_data)
                    elif category == "security":
                        await self.data_analytics.analyze_security_data(category_data)
                        
        except Exception as e:
            self.logger.error(f"Error performing analytics: {str(e)}")
    
    def get_monitoring_status(self) -> Dict:
        """Get comprehensive monitoring status"""
        try:
            active_sessions = len(self.active_sessions)
            total_sessions = len(self.session_history) + active_sessions
            
            # Get data statistics
            data_stats = {}
            for category, data in self.aggregated_data.items():
                data_stats[category] = {
                    "total_records": len(data),
                    "latest_timestamp": data[-1]["timestamp"] if data else 0,
                    "data_points": len(data)
                }
            
            # Get individual system status
            system_status = {
                "performance_monitor": {
                    "active": self.performance_monitor.monitoring_active,
                    "metrics_count": len(self.performance_monitor.performance_history)
                },
                "network_monitor": {
                    "active": self.network_monitor.monitoring_active,
                    "metrics_count": len(self.network_monitor.network_history)
                },
                "security_monitor": {
                    "active": self.security_monitor.monitoring_active,
                    "events_count": len(self.security_monitor.security_events)
                },
                "alert_system": {
                    "rules_count": len(self.alert_system.alert_rules),
                    "active_alerts": len(self.alert_system.get_active_alerts())
                },
                "data_analytics": {
                    "analyses_count": len(self.data_analytics.analytics_results),
                    "ml_models": len(self.data_analytics.ml_models)
                }
            }
            
            return {
                "monitoring_active": self.monitoring_active,
                "active_sessions": active_sessions,
                "total_sessions": total_sessions,
                "data_statistics": data_stats,
                "system_status": system_status,
                "session_history": [
                    {
                        "session_id": session.session_id,
                        "device_id": session.device_id,
                        "start_time": session.start_time,
                        "end_time": session.end_time,
                        "monitoring_types": session.monitoring_types,
                        "status": session.status,
                        "data_collected": session.data_collected
                    }
                    for session in self.session_history[-10:]  # Last 10 sessions
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring status: {str(e)}")
            return {}
    
    def get_comprehensive_statistics(self) -> Dict:
        """Get comprehensive statistics from all monitoring systems"""
        try:
            # Get statistics from each system
            perf_stats = self.performance_monitor.get_performance_statistics()
            net_stats = self.network_monitor.get_network_statistics()
            sec_stats = self.security_monitor.get_security_statistics()
            alert_stats = self.alert_system.get_alert_statistics()
            analytics_stats = self.data_analytics.get_analytics_statistics()
            
            return {
                "performance": perf_stats,
                "network": net_stats,
                "security": sec_stats,
                "alerts": alert_stats,
                "analytics": analytics_stats,
                "aggregated_data": {
                    "performance_records": len(self.aggregated_data["performance"]),
                    "network_records": len(self.aggregated_data["network"]),
                    "security_records": len(self.aggregated_data["security"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive statistics: {str(e)}")
            return {}
    
    def get_recent_data(self, category: str = None, limit: int = 100) -> Dict:
        """Get recent monitoring data"""
        try:
            if category:
                if category in self.aggregated_data:
                    return {
                        "category": category,
                        "data": self.aggregated_data[category][-limit:]
                    }
                else:
                    return {
                        "error": f"Category '{category}' not found"
                    }
            else:
                # Return all categories
                result = {}
                for cat, data in self.aggregated_data.items():
                    result[cat] = data[-limit:]
                return result
                
        except Exception as e:
            self.logger.error(f"Error getting recent data: {str(e)}")
            return {"error": str(e)}
    
    def export_monitoring_data(self, session_id: str = None, format_type: str = "json") -> str:
        """Export monitoring data"""
        try:
            if format_type == "json":
                export_data = {
                    "monitoring_sessions": [
                        {
                            "session_id": session.session_id,
                            "device_id": session.device_id,
                            "start_time": session.start_time,
                            "end_time": session.end_time,
                            "monitoring_types": session.monitoring_types,
                            "status": session.status,
                            "data_collected": session.data_collected
                        }
                        for session in self.session_history
                    ],
                    "aggregated_data": self.aggregated_data,
                    "system_statistics": self.get_comprehensive_statistics()
                }
                
                if session_id:
                    # Filter for specific session
                    session_data = [s for s in self.session_history if s.session_id == session_id]
                    if session_data:
                        export_data["monitoring_sessions"] = session_data
                
                return json.dumps(export_data, indent=2)
            else:
                return "Unsupported format"
                
        except Exception as e:
            self.logger.error(f"Error exporting monitoring data: {str(e)}")
            return ""
    
    def configure_alert_rules(self, rules: List[Dict]) -> Dict:
        """Configure alert rules"""
        try:
            results = []
            for rule_data in rules:
                result = self.alert_system.add_alert_rule(rule_data)
                results.append(result)
            
            success_count = len([r for r in results if r["success"]])
            
            return {
                "success": success_count > 0,
                "configured_rules": success_count,
                "total_rules": len(rules),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring alert rules: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_notification_channels(self, channels: Dict) -> Dict:
        """Configure notification channels"""
        try:
            results = []
            for channel, config in channels.items():
                result = self.alert_system.configure_notification_channel(channel, config)
                results.append(result)
            
            success_count = len([r for r in results if r["success"]])
            
            return {
                "success": success_count > 0,
                "configured_channels": success_count,
                "total_channels": len(channels),
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring notification channels: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_alerts(self, limit: int = 50) -> List[Dict]:
        """Get active alerts"""
        return self.alert_system.get_active_alerts(limit)
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get recent analytics results"""
        return self.data_analytics.get_recent_analyses(limit)
    
    def acknowledge_alert(self, alert_id: str) -> Dict:
        """Acknowledge an alert"""
        return self.alert_system.acknowledge_alert(alert_id)
    
    def resolve_alert(self, alert_id: str) -> Dict:
        """Resolve an alert"""
        return self.alert_system.resolve_alert(alert_id)
    
    def clear_monitoring_data(self, category: str = None) -> Dict:
        """Clear monitoring data"""
        try:
            if category:
                if category in self.aggregated_data:
                    original_count = len(self.aggregated_data[category])
                    self.aggregated_data[category].clear()
                    
                    self.logger.info(f"Cleared {original_count} records from {category}")
                    return {
                        "success": True,
                        "category": category,
                        "cleared_records": original_count,
                        "message": f"Cleared {original_count} records from {category}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Category '{category}' not found"
                    }
            else:
                # Clear all data
                total_records = sum(len(data) for data in self.aggregated_data.values())
                for category in self.aggregated_data:
                    self.aggregated_data[category].clear()
                
                self.logger.info(f"Cleared {total_records} total records")
                return {
                    "success": True,
                    "cleared_records": total_records,
                    "message": f"Cleared {total_records} total records"
                }
                
        except Exception as e:
            self.logger.error(f"Error clearing monitoring data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }