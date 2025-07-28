"""
API Server Tests
Comprehensive test suite for the advanced API server
"""

import asyncio
import json
import pytest
import time
from typing import Dict, List, Any
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

import sys
sys.path.append('../..')

from advanced_api_server import AdvancedAPIServer, APIResponse
from fastapi.testclient import TestClient
from fastapi import HTTPException

class TestAdvancedAPIServer:
    """Test suite for AdvancedAPIServer"""
    
    @pytest.fixture
    def api_server(self):
        """Create API server instance for testing"""
        return AdvancedAPIServer()
    
    @pytest.fixture
    def client(self, api_server):
        """Create test client"""
        return TestClient(api_server.app)
    
    @pytest.fixture
    def mock_device(self):
        """Mock device data"""
        return {
            "device_id": "test_device_001",
            "hostname": "test-device",
            "ip_address": "192.168.1.100",
            "device_type": "android",
            "is_connected": True,
            "last_seen": datetime.now(),
            "os_version": "Android 11",
            "battery_level": 85.5,
            "is_trusted": True
        }
    
    @pytest.fixture
    def mock_alert(self):
        """Mock alert data"""
        return {
            "alert_id": "alert_001",
            "rule_id": "high_cpu_usage",
            "timestamp": time.time(),
            "severity": "warning",
            "message": "High CPU usage detected",
            "data": {"cpu_usage": 85.5},
            "acknowledged": False,
            "resolved": False
        }
    
    def test_api_server_initialization(self, api_server):
        """Test API server initialization"""
        assert api_server.app is not None
        assert api_server.monitoring_manager is not None
        assert api_server.device_manager is not None
        assert api_server.secure_connection is not None
        assert api_server.device_discovery is not None
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "API is healthy"
        assert "status" in data["data"]
        assert "uptime" in data["data"]
        assert "version" in data["data"]
    
    def test_api_stats(self, client):
        """Test API statistics endpoint"""
        # Make a request first to generate stats
        client.get("/health")
        
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total_requests" in data["data"]
        assert "successful_requests" in data["data"]
        assert "failed_requests" in data["data"]
        assert "endpoints_called" in data["data"]
    
    @patch('advanced_api_server.DeviceManager')
    def test_get_devices(self, mock_device_manager, client, mock_device):
        """Test get devices endpoint"""
        # Mock device manager
        mock_manager = Mock()
        mock_device_obj = Mock()
        mock_device_obj.to_dict.return_value = mock_device
        mock_manager.get_all_devices.return_value = [mock_device_obj]
        
        with patch('advanced_api_server.DeviceManager', return_value=mock_manager):
            response = client.get("/api/devices")
            assert response.status_code == 200
            
            devices = response.json()
            assert len(devices) == 1
            assert devices[0]["device_id"] == mock_device["device_id"]
            assert devices[0]["ip_address"] == mock_device["ip_address"]
    
    @patch('advanced_api_server.DeviceManager')
    def test_get_device_not_found(self, mock_device_manager, client):
        """Test get specific device when not found"""
        # Mock device manager
        mock_manager = Mock()
        mock_manager.get_device.return_value = None
        
        with patch('advanced_api_server.DeviceManager', return_value=mock_manager):
            response = client.get("/api/devices/nonexistent")
            assert response.status_code == 404
            assert "Device not found" in response.json()["detail"]
    
    @patch('advanced_api_server.DeviceManager')
    def test_connect_device(self, mock_device_manager, client):
        """Test connect device endpoint"""
        # Mock device manager
        mock_manager = Mock()
        mock_manager.connect_to_device.return_value = {
            "success": True,
            "message": "Device connected successfully"
        }
        
        with patch('advanced_api_server.DeviceManager', return_value=mock_manager):
            response = client.post("/api/devices/test_device/connect")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "connected successfully" in data["message"]
    
    @patch('advanced_api_server.DeviceManager')
    def test_disconnect_device(self, mock_device_manager, client):
        """Test disconnect device endpoint"""
        # Mock device manager
        mock_manager = Mock()
        mock_manager.disconnect_from_device.return_value = {
            "success": True,
            "message": "Device disconnected successfully"
        }
        
        with patch('advanced_api_server.DeviceManager', return_value=mock_manager):
            response = client.post("/api/devices/test_device/disconnect")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "disconnected successfully" in data["message"]
    
    @patch('advanced_api_server.AutoDeviceDiscovery')
    def test_scan_network(self, mock_discovery, client):
        """Test network discovery endpoint"""
        # Mock device discovery
        mock_discovery_instance = Mock()
        
        with patch('advanced_api_server.AutoDeviceDiscovery', return_value=mock_discovery_instance):
            response = client.post("/api/discovery/scan")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Network discovery started"
            assert data["data"]["status"] == "scanning"
    
    @patch('advanced_api_server.AutoDeviceDiscovery')
    def test_get_discovery_results(self, mock_discovery, client):
        """Test get discovery results endpoint"""
        # Mock device discovery
        mock_discovery_instance = Mock()
        mock_discovery_instance.get_discovery_results.return_value = {
            "devices": [
                {
                    "ip": "192.168.1.100",
                    "hostname": "test-device",
                    "device_type": "android"
                }
            ]
        }
        
        with patch('advanced_api_server.AutoDeviceDiscovery', return_value=mock_discovery_instance):
            response = client.get("/api/discovery/results")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "devices" in data["data"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_start_monitoring(self, mock_monitoring_manager, client):
        """Test start monitoring endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.start_comprehensive_monitoring = AsyncMock(return_value={
            "success": True,
            "session_id": "session_001",
            "message": "Monitoring started successfully"
        })
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            monitoring_request = {
                "device_id": "test_device",
                "monitoring_types": ["performance", "network"],
                "interval": 5
            }
            
            response = client.post("/api/monitoring/start", json=monitoring_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "started successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_stop_monitoring(self, mock_monitoring_manager, client):
        """Test stop monitoring endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.stop_comprehensive_monitoring.return_value = {
            "success": True,
            "message": "Monitoring stopped successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/monitoring/stop?session_id=session_001")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "stopped successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_get_monitoring_status(self, mock_monitoring_manager, client):
        """Test get monitoring status endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.get_monitoring_status.return_value = {
            "monitoring_active": True,
            "active_sessions": 1,
            "total_sessions": 5
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/monitoring/status")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "monitoring_active" in data["data"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_get_monitoring_statistics(self, mock_monitoring_manager, client):
        """Test get monitoring statistics endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.get_comprehensive_statistics.return_value = {
            "performance": {"total_metrics": 100},
            "network": {"total_connections": 50},
            "security": {"total_events": 25}
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/monitoring/statistics")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "performance" in data["data"]
            assert "network" in data["data"]
            assert "security" in data["data"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_get_alerts(self, mock_monitoring_manager, client, mock_alert):
        """Test get alerts endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.get_active_alerts.return_value = [mock_alert]
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/alerts")
            assert response.status_code == 200
            
            alerts = response.json()
            assert len(alerts) == 1
            assert alerts[0]["alert_id"] == mock_alert["alert_id"]
            assert alerts[0]["severity"] == mock_alert["severity"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_acknowledge_alert(self, mock_monitoring_manager, client):
        """Test acknowledge alert endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.acknowledge_alert.return_value = {
            "success": True,
            "message": "Alert acknowledged successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/alerts/alert_001/acknowledge")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "acknowledged successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_resolve_alert(self, mock_monitoring_manager, client):
        """Test resolve alert endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.resolve_alert.return_value = {
            "success": True,
            "message": "Alert resolved successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/alerts/alert_001/resolve")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "resolved successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_get_recent_analyses(self, mock_monitoring_manager, client):
        """Test get recent analyses endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.get_recent_analyses.return_value = [
            {
                "analysis_id": "analysis_001",
                "analysis_type": "performance",
                "confidence": 0.85
            }
        ]
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/analytics/recent")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["analysis_type"] == "performance"
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_analyze_performance_data(self, mock_monitoring_manager, client):
        """Test analyze performance data endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.get_recent_data.return_value = {
            "performance": [
                {"cpu_usage": 50.0, "memory_usage": 60.0}
            ]
        }
        
        # Mock data analytics
        mock_analytics = Mock()
        mock_analytics.analyze_performance_data = AsyncMock(return_value=Mock(
            analysis_id="analysis_001",
            confidence=0.85,
            recommendations=["Optimize CPU usage"]
        ))
        mock_manager.data_analytics = mock_analytics
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/analytics/performance?device_id=test_device&hours=24")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "analysis completed" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_configure_alerts(self, mock_monitoring_manager, client):
        """Test configure alerts endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.configure_alert_rules.return_value = {
            "success": True,
            "configured_rules": 2,
            "message": "Alert rules configured successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            alert_rules = [
                {
                    "rule_id": "high_cpu",
                    "name": "High CPU Usage",
                    "description": "Alert when CPU usage is high",
                    "condition": "cpu_usage > 80",
                    "threshold": 80.0,
                    "severity": "warning",
                    "enabled": True,
                    "notification_channels": ["email"],
                    "cooldown_period": 300
                }
            ]
            
            response = client.post("/api/config/alerts", json=alert_rules)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "configured successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_configure_notifications(self, mock_monitoring_manager, client):
        """Test configure notifications endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.configure_notification_channels.return_value = {
            "success": True,
            "configured_channels": 2,
            "message": "Notification channels configured successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            notification_channels = [
                {
                    "channel_type": "email",
                    "enabled": True,
                    "config": {
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "username": "test@example.com",
                        "password": "password123",
                        "from_email": "test@example.com",
                        "to_emails": ["admin@example.com"]
                    }
                }
            ]
            
            response = client.post("/api/config/notifications", json=notification_channels)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "configured successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_block_ip(self, mock_monitoring_manager, client):
        """Test block IP endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.security_monitor = Mock()
        mock_manager.security_monitor.block_ip.return_value = {
            "success": True,
            "message": "IP blocked successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/security/block-ip?ip_address=192.168.1.100&reason=Security threat")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "blocked successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_unblock_ip(self, mock_monitoring_manager, client):
        """Test unblock IP endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.security_monitor = Mock()
        mock_manager.security_monitor.unblock_ip.return_value = {
            "success": True,
            "message": "IP unblocked successfully"
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/security/unblock-ip?ip_address=192.168.1.100")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "unblocked successfully" in data["message"]
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_get_security_events(self, mock_monitoring_manager, client):
        """Test get security events endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.security_monitor = Mock()
        mock_manager.security_monitor.get_security_events.return_value = [
            {
                "event_id": "event_001",
                "timestamp": time.time(),
                "severity": "high",
                "description": "Suspicious activity detected"
            }
        ]
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.get("/api/security/events")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["severity"] == "high"
    
    @patch('advanced_api_server.AdvancedMonitoringManager')
    def test_export_monitoring_data(self, mock_monitoring_manager, client):
        """Test export monitoring data endpoint"""
        # Mock monitoring manager
        mock_manager = Mock()
        mock_manager.export_monitoring_data.return_value = {
            "sessions": [],
            "data": {},
            "statistics": {}
        }
        
        with patch('advanced_api_server.AdvancedMonitoringManager', return_value=mock_manager):
            response = client.post("/api/export/monitoring?format_type=json")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "exported" in data["message"]
    
    def test_get_system_info(self, client):
        """Test get system info endpoint"""
        response = client.get("/api/system/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "api_version" in data["data"]
        assert "uptime" in data["data"]
        assert "total_requests" in data["data"]
        assert "success_rate" in data["data"]
    
    def test_get_system_logs(self, client):
        """Test get system logs endpoint"""
        # Make some requests first to generate logs
        client.get("/health")
        client.get("/api/stats")
        
        response = client.get("/api/system/logs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_request_tracking(self, client):
        """Test request tracking functionality"""
        # Make multiple requests
        client.get("/health")
        client.get("/api/stats")
        client.get("/api/system/info")
        
        # Check API stats
        response = client.get("/api/stats")
        data = response.json()
        
        assert data["data"]["total_requests"] >= 4
        assert "/health" in data["data"]["endpoints_called"]
        assert "/api/stats" in data["data"]["endpoints_called"]
    
    def test_error_handling(self, client):
        """Test error handling"""
        # Test invalid endpoint
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_cors_support(self, client):
        """Test CORS support"""
        response = client.options("/health")
        # CORS headers should be present
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
    
    def test_api_response_format(self, client):
        """Test API response format consistency"""
        response = client.get("/health")
        data = response.json()
        
        # Check required fields
        assert "success" in data
        assert "message" in data
        assert "timestamp" in data
        assert "request_id" in data
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        assert isinstance(data["request_id"], str)
    
    def test_generate_request_id(self, api_server):
        """Test request ID generation"""
        request_id = api_server._generate_request_id()
        assert request_id.startswith("req_")
        assert len(request_id) > 10
    
    def test_get_api_info(self, api_server):
        """Test get API info"""
        info = api_server.get_api_info()
        
        assert "title" in info
        assert "version" in info
        assert "description" in info
        assert "endpoints" in info
        assert "features" in info
        assert len(info["endpoints"]) > 0
        assert len(info["features"]) > 0

class TestAPIModels:
    """Test API data models"""
    
    def test_device_model(self):
        """Test DeviceModel validation"""
        from advanced_api_server import DeviceModel
        
        device_data = {
            "device_id": "test_device",
            "ip_address": "192.168.1.100",
            "device_type": "android",
            "is_connected": True,
            "is_trusted": False
        }
        
        device = DeviceModel(**device_data)
        assert device.device_id == "test_device"
        assert device.ip_address == "192.168.1.100"
        assert device.device_type == "android"
        assert device.is_connected is True
        assert device.is_trusted is False
    
    def test_alert_model(self):
        """Test AlertModel validation"""
        from advanced_api_server import AlertModel
        
        alert_data = {
            "alert_id": "alert_001",
            "rule_id": "high_cpu",
            "timestamp": time.time(),
            "severity": "warning",
            "message": "High CPU usage",
            "data": {"cpu_usage": 85.5},
            "acknowledged": False,
            "resolved": False
        }
        
        alert = AlertModel(**alert_data)
        assert alert.alert_id == "alert_001"
        assert alert.rule_id == "high_cpu"
        assert alert.severity == "warning"
        assert alert.message == "High CPU usage"
        assert alert.acknowledged is False
        assert alert.resolved is False
    
    def test_monitoring_request_model(self):
        """Test MonitoringRequestModel validation"""
        from advanced_api_server import MonitoringRequestModel
        
        request_data = {
            "device_id": "test_device",
            "monitoring_types": ["performance", "network"],
            "interval": 10
        }
        
        request = MonitoringRequestModel(**request_data)
        assert request.device_id == "test_device"
        assert "performance" in request.monitoring_types
        assert "network" in request.monitoring_types
        assert request.interval == 10
    
    def test_api_response_model(self):
        """Test APIResponse validation"""
        from advanced_api_server import APIResponse
        
        response_data = {
            "success": True,
            "message": "Operation successful",
            "data": {"result": "test"},
            "timestamp": datetime.now(),
            "request_id": "req_123"
        }
        
        response = APIResponse(**response_data)
        assert response.success is True
        assert response.message == "Operation successful"
        assert response.data["result"] == "test"
        assert response.request_id == "req_123"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])