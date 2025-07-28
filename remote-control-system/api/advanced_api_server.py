"""
Advanced API Server
Comprehensive REST API with documentation and testing
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import threading
from dataclasses import asdict
from functools import wraps

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import uvicorn
from starlette.requests import Request
from starlette.responses import Response

# Import monitoring systems
import sys
sys.path.append('../command-server')
from advanced_monitoring_manager import AdvancedMonitoringManager
from device_manager import DeviceManager
from secure_connection import SecureConnection
from auto_device_discovery import AutoDeviceDiscovery

# Security
security = HTTPBearer()

# Pydantic Models
class DeviceModel(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    hostname: Optional[str] = Field(None, description="Device hostname")
    ip_address: str = Field(..., description="Device IP address")
    device_type: str = Field(..., description="Device type (android, ios, etc.)")
    is_connected: bool = Field(False, description="Connection status")
    last_seen: Optional[datetime] = Field(None, description="Last connection time")
    os_version: Optional[str] = Field(None, description="Operating system version")
    battery_level: Optional[float] = Field(None, description="Battery level percentage")
    is_trusted: bool = Field(False, description="Trust status")

class MonitoringSessionModel(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    device_id: str = Field(..., description="Target device ID")
    start_time: datetime = Field(..., description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    monitoring_types: List[str] = Field(..., description="Types of monitoring")
    status: str = Field(..., description="Session status")
    data_collected: int = Field(0, description="Number of data points collected")

class AlertModel(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    rule_id: str = Field(..., description="Associated rule ID")
    timestamp: float = Field(..., description="Alert timestamp")
    severity: str = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    data: Dict = Field(..., description="Alert data")
    acknowledged: bool = Field(False, description="Acknowledgment status")
    resolved: bool = Field(False, description="Resolution status")

class PerformanceMetricsModel(BaseModel):
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    battery_level: float = Field(..., description="Battery level percentage")
    temperature: float = Field(..., description="Device temperature")
    running_processes: int = Field(..., description="Number of running processes")
    active_connections: int = Field(..., description="Number of active connections")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class NetworkMetricsModel(BaseModel):
    bandwidth_usage: float = Field(..., description="Bandwidth usage in bytes")
    latency: float = Field(..., description="Network latency in milliseconds")
    packet_loss: float = Field(..., description="Packet loss percentage")
    connections_count: int = Field(..., description="Number of network connections")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class SecurityMetricsModel(BaseModel):
    threat_level: int = Field(..., description="Threat level (0-10)")
    total_events: int = Field(..., description="Total security events")
    blocked_ips: int = Field(..., description="Number of blocked IPs")
    suspicious_activities: int = Field(..., description="Suspicious activities count")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class MonitoringRequestModel(BaseModel):
    device_id: str = Field(..., description="Target device ID")
    monitoring_types: List[str] = Field(["performance", "network", "security"], description="Types of monitoring")
    interval: int = Field(5, ge=1, le=60, description="Update interval in seconds")
    duration: Optional[int] = Field(None, ge=1, description="Monitoring duration in minutes")

class AlertRuleModel(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    condition: str = Field(..., description="Alert condition")
    threshold: float = Field(..., description="Alert threshold")
    severity: str = Field(..., description="Alert severity")
    enabled: bool = Field(True, description="Rule enabled status")
    notification_channels: List[str] = Field(..., description="Notification channels")
    cooldown_period: int = Field(300, ge=0, description="Cooldown period in seconds")

class NotificationChannelModel(BaseModel):
    channel_type: str = Field(..., description="Channel type (email, webhook, sms, slack, discord)")
    enabled: bool = Field(False, description="Channel enabled status")
    config: Dict = Field(..., description="Channel configuration")

class APIResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Unique request identifier")

class AdvancedAPIServer:
    """Advanced API server with comprehensive features"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Remote Control System API",
            description="Advanced API for remote device control and monitoring",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Initialize components
        self.monitoring_manager = AdvancedMonitoringManager()
        self.device_manager = DeviceManager()
        self.secure_connection = SecureConnection()
        self.device_discovery = AutoDeviceDiscovery()
        
        # API statistics
        self.api_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "start_time": time.time(),
            "endpoints_called": {}
        }
        
        # Request tracking
        self.request_history = []
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_middleware(self):
        """Setup middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request tracking middleware
        @self.app.middleware("http")
        async def track_requests(request: Request, call_next):
            start_time = time.time()
            
            # Track request
            self.api_stats["total_requests"] += 1
            endpoint = request.url.path
            self.api_stats["endpoints_called"][endpoint] = self.api_stats["endpoints_called"].get(endpoint, 0) + 1
            
            # Process request
            response = await call_next(request)
            
            # Track response
            duration = time.time() - start_time
            if response.status_code < 400:
                self.api_stats["successful_requests"] += 1
            else:
                self.api_stats["failed_requests"] += 1
            
            # Log request
            self.request_history.append({
                "timestamp": datetime.now(),
                "method": request.method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "client_ip": request.client.host if request.client else None
            })
            
            # Keep only last 1000 requests
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]
            
            return response
    
    def _setup_routes(self):
        """Setup API routes"""
        
        # Health check
        @self.app.get("/health", tags=["System"])
        async def health_check():
            """Check API health status"""
            return APIResponse(
                success=True,
                message="API is healthy",
                data={
                    "status": "healthy",
                    "uptime": time.time() - self.api_stats["start_time"],
                    "version": "1.0.0"
                },
                timestamp=datetime.now(),
                request_id=self._generate_request_id()
            )
        
        # API statistics
        @self.app.get("/api/stats", tags=["System"])
        async def get_api_stats():
            """Get API statistics"""
            return APIResponse(
                success=True,
                message="API statistics retrieved",
                data=self.api_stats,
                timestamp=datetime.now(),
                request_id=self._generate_request_id()
            )
        
        # Device management endpoints
        @self.app.get("/api/devices", response_model=List[DeviceModel], tags=["Devices"])
        async def get_devices():
            """Get all devices"""
            try:
                devices = self.device_manager.get_all_devices()
                return [DeviceModel(**device.to_dict()) for device in devices]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/devices/{device_id}", response_model=DeviceModel, tags=["Devices"])
        async def get_device(device_id: str):
            """Get specific device"""
            try:
                device = self.device_manager.get_device(device_id)
                if device:
                    return DeviceModel(**device.to_dict())
                else:
                    raise HTTPException(status_code=404, detail="Device not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/devices/{device_id}/connect", tags=["Devices"])
        async def connect_device(device_id: str):
            """Connect to device"""
            try:
                result = self.device_manager.connect_to_device(device_id)
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Connection attempt completed"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/devices/{device_id}/disconnect", tags=["Devices"])
        async def disconnect_device(device_id: str):
            """Disconnect from device"""
            try:
                result = self.device_manager.disconnect_from_device(device_id)
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Disconnection attempt completed"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Device discovery
        @self.app.post("/api/discovery/scan", tags=["Discovery"])
        async def scan_network(background_tasks: BackgroundTasks):
            """Scan network for devices"""
            try:
                # Start discovery in background
                background_tasks.add_task(self._run_discovery)
                
                return APIResponse(
                    success=True,
                    message="Network discovery started",
                    data={"status": "scanning"},
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/discovery/results", tags=["Discovery"])
        async def get_discovery_results():
            """Get discovery results"""
            try:
                results = self.device_discovery.get_discovery_results()
                return APIResponse(
                    success=True,
                    message="Discovery results retrieved",
                    data=results,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Monitoring endpoints
        @self.app.post("/api/monitoring/start", tags=["Monitoring"])
        async def start_monitoring(request: MonitoringRequestModel):
            """Start monitoring session"""
            try:
                result = await self.monitoring_manager.start_comprehensive_monitoring(
                    request.device_id,
                    request.monitoring_types,
                    request.interval
                )
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Monitoring started"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/monitoring/stop", tags=["Monitoring"])
        async def stop_monitoring(session_id: str):
            """Stop monitoring session"""
            try:
                result = self.monitoring_manager.stop_comprehensive_monitoring(session_id)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Monitoring stopped"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/status", tags=["Monitoring"])
        async def get_monitoring_status():
            """Get monitoring status"""
            try:
                status = self.monitoring_manager.get_monitoring_status()
                
                return APIResponse(
                    success=True,
                    message="Monitoring status retrieved",
                    data=status,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/statistics", tags=["Monitoring"])
        async def get_monitoring_statistics():
            """Get monitoring statistics"""
            try:
                stats = self.monitoring_manager.get_comprehensive_statistics()
                
                return APIResponse(
                    success=True,
                    message="Monitoring statistics retrieved",
                    data=stats,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Real-time data streaming
        @self.app.get("/api/monitoring/stream", tags=["Monitoring"])
        async def stream_monitoring_data():
            """Stream real-time monitoring data"""
            async def generate():
                while True:
                    try:
                        # Get current data
                        data = self.monitoring_manager._collect_aggregated_data()
                        
                        # Format as Server-Sent Events
                        yield f"data: {json.dumps(data)}\n\n"
                        
                        await asyncio.sleep(5)  # Update every 5 seconds
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                        break
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        # Alerts endpoints
        @self.app.get("/api/alerts", response_model=List[AlertModel], tags=["Alerts"])
        async def get_alerts(limit: int = 50, severity: Optional[str] = None):
            """Get alerts"""
            try:
                alerts = self.monitoring_manager.get_active_alerts(limit)
                
                # Filter by severity if specified
                if severity:
                    alerts = [alert for alert in alerts if alert.get("severity") == severity]
                
                return [AlertModel(**alert) for alert in alerts]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/acknowledge", tags=["Alerts"])
        async def acknowledge_alert(alert_id: str):
            """Acknowledge alert"""
            try:
                result = self.monitoring_manager.acknowledge_alert(alert_id)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Alert acknowledged"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/resolve", tags=["Alerts"])
        async def resolve_alert(alert_id: str):
            """Resolve alert"""
            try:
                result = self.monitoring_manager.resolve_alert(alert_id)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Alert resolved"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Analytics endpoints
        @self.app.get("/api/analytics/recent", tags=["Analytics"])
        async def get_recent_analyses(limit: int = 10):
            """Get recent analytics"""
            try:
                analyses = self.monitoring_manager.get_recent_analyses(limit)
                
                return APIResponse(
                    success=True,
                    message="Recent analyses retrieved",
                    data=analyses,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/analytics/performance", tags=["Analytics"])
        async def analyze_performance_data(device_id: str, hours: int = 24):
            """Analyze performance data"""
            try:
                # Get performance data for the specified period
                data = self.monitoring_manager.get_recent_data("performance", hours * 60)
                
                if data and "performance" in data:
                    result = await self.monitoring_manager.data_analytics.analyze_performance_data(
                        data["performance"]
                    )
                    
                    return APIResponse(
                        success=True,
                        message="Performance analysis completed",
                        data=asdict(result) if result else None,
                        timestamp=datetime.now(),
                        request_id=self._generate_request_id()
                    )
                else:
                    raise HTTPException(status_code=404, detail="No performance data available")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Configuration endpoints
        @self.app.post("/api/config/alerts", tags=["Configuration"])
        async def configure_alerts(rules: List[AlertRuleModel]):
            """Configure alert rules"""
            try:
                rules_data = [rule.dict() for rule in rules]
                result = self.monitoring_manager.configure_alert_rules(rules_data)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Alert rules configured"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/config/notifications", tags=["Configuration"])
        async def configure_notifications(channels: List[NotificationChannelModel]):
            """Configure notification channels"""
            try:
                channels_data = {}
                for channel in channels:
                    channels_data[channel.channel_type] = {
                        "enabled": channel.enabled,
                        **channel.config
                    }
                
                result = self.monitoring_manager.configure_notification_channels(channels_data)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "Notification channels configured"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Security endpoints
        @self.app.post("/api/security/block-ip", tags=["Security"])
        async def block_ip(ip_address: str, reason: str = "Security threat"):
            """Block IP address"""
            try:
                result = self.monitoring_manager.security_monitor.block_ip(ip_address, reason)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "IP blocked"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/security/unblock-ip", tags=["Security"])
        async def unblock_ip(ip_address: str):
            """Unblock IP address"""
            try:
                result = self.monitoring_manager.security_monitor.unblock_ip(ip_address)
                
                return APIResponse(
                    success=result.get("success", False),
                    message=result.get("message", "IP unblocked"),
                    data=result,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/security/events", tags=["Security"])
        async def get_security_events(limit: int = 100, severity: Optional[str] = None):
            """Get security events"""
            try:
                events = self.monitoring_manager.security_monitor.get_security_events(limit, severity)
                
                return APIResponse(
                    success=True,
                    message="Security events retrieved",
                    data=events,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Export endpoints
        @self.app.post("/api/export/monitoring", tags=["Export"])
        async def export_monitoring_data(session_id: Optional[str] = None, format_type: str = "json"):
            """Export monitoring data"""
            try:
                exported_data = self.monitoring_manager.export_monitoring_data(session_id, format_type)
                
                return APIResponse(
                    success=True,
                    message="Monitoring data exported",
                    data={"format": format_type, "data": exported_data},
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # System endpoints
        @self.app.get("/api/system/info", tags=["System"])
        async def get_system_info():
            """Get system information"""
            try:
                info = {
                    "api_version": "1.0.0",
                    "uptime": time.time() - self.api_stats["start_time"],
                    "total_requests": self.api_stats["total_requests"],
                    "success_rate": (
                        self.api_stats["successful_requests"] / 
                        max(self.api_stats["total_requests"], 1) * 100
                    ),
                    "active_sessions": len(self.monitoring_manager.active_sessions),
                    "connected_devices": len(self.device_manager.get_all_devices()),
                    "monitoring_active": self.monitoring_manager.monitoring_active
                }
                
                return APIResponse(
                    success=True,
                    message="System information retrieved",
                    data=info,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/system/logs", tags=["System"])
        async def get_system_logs(limit: int = 100):
            """Get system logs"""
            try:
                # Get recent request history
                logs = self.request_history[-limit:] if self.request_history else []
                
                return APIResponse(
                    success=True,
                    message="System logs retrieved",
                    data=logs,
                    timestamp=datetime.now(),
                    request_id=self._generate_request_id()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _run_discovery(self):
        """Run device discovery in background"""
        try:
            await self.device_discovery.scan_network()
        except Exception as e:
            self.logger.error(f"Discovery error: {str(e)}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time() * 1000)}_{threading.get_ident()}"
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Start the API server"""
        try:
            self.logger.info(f"Starting API server on {host}:{port}")
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                debug=debug,
                log_level="info"
            )
        except Exception as e:
            self.logger.error(f"Error starting API server: {str(e)}")
    
    def get_api_info(self) -> Dict:
        """Get API information"""
        return {
            "title": "Remote Control System API",
            "version": "1.0.0",
            "description": "Advanced API for remote device control and monitoring",
            "endpoints": [
                "/health",
                "/docs",
                "/redoc",
                "/api/devices",
                "/api/monitoring",
                "/api/alerts",
                "/api/analytics",
                "/api/security",
                "/api/config",
                "/api/export",
                "/api/system"
            ],
            "features": [
                "RESTful API",
                "Real-time streaming",
                "Comprehensive documentation",
                "Request tracking",
                "Error handling",
                "CORS support",
                "Background tasks",
                "Data validation"
            ]
        }