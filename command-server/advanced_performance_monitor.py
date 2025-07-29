"""
Advanced Performance Monitor
Real-time monitoring of device performance and system resources
"""

import asyncio
import json
import logging
import os
import psutil
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading

@dataclass
class PerformanceMetrics:
    """Performance metrics structure"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    battery_level: float
    temperature: float
    network_activity: Dict
    storage_usage: Dict
    running_processes: int
    active_connections: int

class AdvancedPerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False
        self.monitoring_thread = None
        self.performance_history: List[PerformanceMetrics] = []
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "battery_level": 20.0,
            "temperature": 45.0
        }
        self.alerts: List[Dict] = []
        
    async def start_monitoring(self, device_id: str, interval: int = 5) -> Dict:
        """Start real-time performance monitoring"""
        try:
            if self.monitoring_active:
                return {
                    "success": False,
                    "error": "Monitoring already active"
                }
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(device_id, interval),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"Started performance monitoring for device {device_id}")
            return {
                "success": True,
                "device_id": device_id,
                "interval": interval,
                "message": "Performance monitoring started"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_monitoring(self) -> Dict:
        """Stop performance monitoring"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("Performance monitoring stopped")
            return {
                "success": True,
                "message": "Performance monitoring stopped"
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _monitoring_loop(self, device_id: str, interval: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect performance metrics
                metrics = self._collect_performance_metrics(device_id)
                self.performance_history.append(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                # Keep only last 1000 records
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval)
    
    def _collect_performance_metrics(self, device_id: str) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Battery information (simulated for now)
            battery_level = self._get_battery_level()
            temperature = self._get_temperature()
            
            # Network activity
            network_activity = self._get_network_activity()
            
            # Storage usage
            storage_usage = self._get_storage_usage()
            
            # Running processes
            running_processes = len(psutil.pids())
            
            # Active connections
            active_connections = len(psutil.net_connections())
            
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                battery_level=battery_level,
                temperature=temperature,
                network_activity=network_activity,
                storage_usage=storage_usage,
                running_processes=running_processes,
                active_connections=active_connections
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=0.0,
                memory_usage=0.0,
                battery_level=0.0,
                temperature=0.0,
                network_activity={},
                storage_usage={},
                running_processes=0,
                active_connections=0
            )
    
    def _get_battery_level(self) -> float:
        """Get battery level (simulated)"""
        try:
            # In real implementation, this would query device battery
            return 75.0 + (time.time() % 20)  # Simulated battery level
        except Exception:
            return 0.0
    
    def _get_temperature(self) -> float:
        """Get device temperature (simulated)"""
        try:
            # In real implementation, this would query device temperature
            return 35.0 + (time.time() % 10)  # Simulated temperature
        except Exception:
            return 0.0
    
    def _get_network_activity(self) -> Dict:
        """Get network activity metrics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "connections": len(psutil.net_connections())
            }
        except Exception:
            return {}
    
    def _get_storage_usage(self) -> Dict:
        """Get storage usage metrics"""
        try:
            disk_usage = psutil.disk_usage('/')
            return {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent
            }
        except Exception:
            return {}
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts"""
        alerts = []
        
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "type": "high_cpu",
                "value": metrics.cpu_usage,
                "threshold": self.alert_thresholds["cpu_usage"],
                "timestamp": metrics.timestamp
            })
        
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "high_memory",
                "value": metrics.memory_usage,
                "threshold": self.alert_thresholds["memory_usage"],
                "timestamp": metrics.timestamp
            })
        
        if metrics.battery_level < self.alert_thresholds["battery_level"]:
            alerts.append({
                "type": "low_battery",
                "value": metrics.battery_level,
                "threshold": self.alert_thresholds["battery_level"],
                "timestamp": metrics.timestamp
            })
        
        if metrics.temperature > self.alert_thresholds["temperature"]:
            alerts.append({
                "type": "high_temperature",
                "value": metrics.temperature,
                "threshold": self.alert_thresholds["temperature"],
                "timestamp": metrics.timestamp
            })
        
        if alerts:
            self.alerts.extend(alerts)
            self.logger.warning(f"Performance alerts detected: {len(alerts)} alerts")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        if self.performance_history:
            return self.performance_history[-1]
        return None
    
    def get_metrics_history(self, limit: int = 100) -> List[PerformanceMetrics]:
        """Get performance metrics history"""
        return self.performance_history[-limit:] if self.performance_history else []
    
    def get_performance_statistics(self) -> Dict:
        """Get comprehensive performance statistics"""
        if not self.performance_history:
            return {}
        
        metrics = self.performance_history
        
        # Calculate averages
        avg_cpu = sum(m.cpu_usage for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_usage for m in metrics) / len(metrics)
        avg_battery = sum(m.battery_level for m in metrics) / len(metrics)
        avg_temperature = sum(m.temperature for m in metrics) / len(metrics)
        
        # Calculate peaks
        max_cpu = max(m.cpu_usage for m in metrics)
        max_memory = max(m.memory_usage for m in metrics)
        min_battery = min(m.battery_level for m in metrics)
        max_temperature = max(m.temperature for m in metrics)
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_metrics": len(metrics),
            "monitoring_duration": metrics[-1].timestamp - metrics[0].timestamp if len(metrics) > 1 else 0,
            "averages": {
                "cpu_usage": avg_cpu,
                "memory_usage": avg_memory,
                "battery_level": avg_battery,
                "temperature": avg_temperature
            },
            "peaks": {
                "max_cpu": max_cpu,
                "max_memory": max_memory,
                "min_battery": min_battery,
                "max_temperature": max_temperature
            },
            "alerts": {
                "total_alerts": len(self.alerts),
                "recent_alerts": len([a for a in self.alerts if time.time() - a["timestamp"] < 3600])
            }
        }
    
    def set_alert_thresholds(self, thresholds: Dict) -> Dict:
        """Set alert thresholds"""
        try:
            for key, value in thresholds.items():
                if key in self.alert_thresholds:
                    self.alert_thresholds[key] = float(value)
            
            self.logger.info(f"Updated alert thresholds: {thresholds}")
            return {
                "success": True,
                "thresholds": self.alert_thresholds,
                "message": "Alert thresholds updated"
            }
            
        except Exception as e:
            self.logger.error(f"Error setting thresholds: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_alerts(self, recent_only: bool = True) -> List[Dict]:
        """Get performance alerts"""
        if recent_only:
            # Return alerts from last hour
            cutoff_time = time.time() - 3600
            return [alert for alert in self.alerts if alert["timestamp"] > cutoff_time]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.logger.info("All alerts cleared")
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export performance metrics"""
        try:
            if format_type == "json":
                return json.dumps([
                    {
                        "timestamp": m.timestamp,
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "battery_level": m.battery_level,
                        "temperature": m.temperature,
                        "network_activity": m.network_activity,
                        "storage_usage": m.storage_usage,
                        "running_processes": m.running_processes,
                        "active_connections": m.active_connections
                    }
                    for m in self.performance_history
                ], indent=2)
            else:
                return "Unsupported format"
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {str(e)}")
            return ""