"""
Advanced Web Server
Modern web interface for remote control system
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# Import monitoring systems
import sys
sys.path.append('../command-server')
from advanced_monitoring_manager import AdvancedMonitoringManager
from device_manager import DeviceManager
from secure_connection import SecureConnection

class AdvancedWebServer:
    """Advanced web server with real-time monitoring and control"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your-secret-key-here'
        self.app.config['SESSION_TYPE'] = 'filesystem'
        
        # Initialize SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Enable CORS
        CORS(self.app)
        
        # Initialize components
        self.monitoring_manager = AdvancedMonitoringManager()
        self.device_manager = DeviceManager()
        self.secure_connection = SecureConnection()
        
        # User management
        self.users = {
            "admin": {
                "password_hash": generate_password_hash("admin123"),
                "role": "admin",
                "permissions": ["read", "write", "execute", "admin"]
            }
        }
        
        # Active sessions
        self.active_sessions = {}
        
        # Setup routes
        self._setup_routes()
        self._setup_socket_events()
        
        self.logger = logging.getLogger(__name__)
        
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('dashboard.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page"""
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if self._authenticate_user(username, password):
                    session['user_id'] = username
                    session['role'] = self.users[username]['role']
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error="Invalid credentials")
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """Logout user"""
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/devices')
        def get_devices():
            """Get all devices"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            devices = self.device_manager.get_all_devices()
            return jsonify({
                "success": True,
                "devices": [device.to_dict() for device in devices]
            })
        
        @self.app.route('/api/devices/<device_id>')
        def get_device(device_id):
            """Get specific device"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            device = self.device_manager.get_device(device_id)
            if device:
                return jsonify({
                    "success": True,
                    "device": device.to_dict()
                })
            else:
                return jsonify({"error": "Device not found"}), 404
        
        @self.app.route('/api/devices/<device_id>/connect', methods=['POST'])
        def connect_device(device_id):
            """Connect to device"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                result = self.device_manager.connect_to_device(device_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/devices/<device_id>/disconnect', methods=['POST'])
        def disconnect_device(device_id):
            """Disconnect from device"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                result = self.device_manager.disconnect_from_device(device_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitoring/start', methods=['POST'])
        def start_monitoring():
            """Start monitoring"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            monitoring_types = data.get('monitoring_types', ['performance', 'network', 'security'])
            interval = data.get('interval', 5)
            
            try:
                result = asyncio.run(self.monitoring_manager.start_comprehensive_monitoring(
                    device_id, monitoring_types, interval
                ))
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitoring/stop', methods=['POST'])
        def stop_monitoring():
            """Stop monitoring"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            session_id = data.get('session_id')
            
            try:
                result = self.monitoring_manager.stop_comprehensive_monitoring(session_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitoring/status')
        def get_monitoring_status():
            """Get monitoring status"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                status = self.monitoring_manager.get_monitoring_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/monitoring/statistics')
        def get_monitoring_statistics():
            """Get monitoring statistics"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                stats = self.monitoring_manager.get_comprehensive_statistics()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get active alerts"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            limit = request.args.get('limit', 50, type=int)
            alerts = self.monitoring_manager.get_active_alerts(limit)
            return jsonify({
                "success": True,
                "alerts": alerts
            })
        
        @self.app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
        def acknowledge_alert(alert_id):
            """Acknowledge alert"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                result = self.monitoring_manager.acknowledge_alert(alert_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
        def resolve_alert(alert_id):
            """Resolve alert"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                result = self.monitoring_manager.resolve_alert(alert_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/analytics/recent')
        def get_recent_analyses():
            """Get recent analytics"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            limit = request.args.get('limit', 10, type=int)
            analyses = self.monitoring_manager.get_recent_analyses(limit)
            return jsonify({
                "success": True,
                "analyses": analyses
            })
        
        @self.app.route('/api/data/recent')
        def get_recent_data():
            """Get recent monitoring data"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            category = request.args.get('category')
            limit = request.args.get('limit', 100, type=int)
            
            data = self.monitoring_manager.get_recent_data(category, limit)
            return jsonify(data)
        
        @self.app.route('/api/export/monitoring', methods=['POST'])
        def export_monitoring_data():
            """Export monitoring data"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            session_id = data.get('session_id')
            format_type = data.get('format', 'json')
            
            try:
                exported_data = self.monitoring_manager.export_monitoring_data(session_id, format_type)
                return jsonify({
                    "success": True,
                    "data": exported_data,
                    "format": format_type
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/configuration/alerts', methods=['POST'])
        def configure_alerts():
            """Configure alert rules"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            if session.get('role') != 'admin':
                return jsonify({"error": "Insufficient permissions"}), 403
            
            data = request.get_json()
            rules = data.get('rules', [])
            
            try:
                result = self.monitoring_manager.configure_alert_rules(rules)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/configuration/notifications', methods=['POST'])
        def configure_notifications():
            """Configure notification channels"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            if session.get('role') != 'admin':
                return jsonify({"error": "Insufficient permissions"}), 403
            
            data = request.get_json()
            channels = data.get('channels', {})
            
            try:
                result = self.monitoring_manager.configure_notification_channels(channels)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/security/block-ip', methods=['POST'])
        def block_ip():
            """Block IP address"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            ip_address = data.get('ip_address')
            reason = data.get('reason', 'Security threat')
            
            try:
                result = self.monitoring_manager.security_monitor.block_ip(ip_address, reason)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/security/unblock-ip', methods=['POST'])
        def unblock_ip():
            """Unblock IP address"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            data = request.get_json()
            ip_address = data.get('ip_address')
            
            try:
                result = self.monitoring_manager.security_monitor.unblock_ip(ip_address)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/security/events')
        def get_security_events():
            """Get security events"""
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized"}), 401
            
            limit = request.args.get('limit', 100, type=int)
            severity = request.args.get('severity')
            
            events = self.monitoring_manager.security_monitor.get_security_events(limit, severity)
            return jsonify({
                "success": True,
                "events": events
            })
    
    def _setup_socket_events(self):
        """Setup SocketIO events for real-time communication"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.logger.info(f"Client connected: {request.sid}")
            emit('connected', {'data': 'Connected to server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_monitoring')
        def handle_join_monitoring(data):
            """Join monitoring room for real-time updates"""
            session_id = data.get('session_id')
            if session_id:
                join_room(session_id)
                emit('joined_monitoring', {'session_id': session_id})
        
        @self.socketio.on('leave_monitoring')
        def handle_leave_monitoring(data):
            """Leave monitoring room"""
            session_id = data.get('session_id')
            if session_id:
                leave_room(session_id)
                emit('left_monitoring', {'session_id': session_id})
        
        @self.socketio.on('request_data')
        def handle_request_data(data):
            """Handle data requests"""
            data_type = data.get('type')
            device_id = data.get('device_id')
            
            if data_type == 'performance':
                metrics = self.monitoring_manager.performance_monitor.get_current_metrics()
                if metrics:
                    emit('performance_data', metrics.__dict__)
            
            elif data_type == 'network':
                stats = self.monitoring_manager.network_monitor.get_network_statistics()
                emit('network_data', stats)
            
            elif data_type == 'security':
                stats = self.monitoring_manager.security_monitor.get_security_statistics()
                emit('security_data', stats)
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user"""
        if username in self.users:
            return check_password_hash(self.users[username]['password_hash'], password)
        return False
    
    def broadcast_monitoring_data(self, session_id: str, data: Dict):
        """Broadcast monitoring data to connected clients"""
        self.socketio.emit('monitoring_update', data, room=session_id)
    
    def broadcast_alert(self, alert_data: Dict):
        """Broadcast alert to all connected clients"""
        self.socketio.emit('new_alert', alert_data)
    
    def start_server(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Start the web server"""
        try:
            self.logger.info(f"Starting web server on {host}:{port}")
            self.socketio.run(self.app, host=host, port=port, debug=debug)
        except Exception as e:
            self.logger.error(f"Error starting web server: {str(e)}")
    
    def get_server_info(self) -> Dict:
        """Get server information"""
        return {
            "server_type": "Flask + SocketIO",
            "version": "1.0.0",
            "features": [
                "Real-time monitoring",
                "WebSocket communication",
                "RESTful API",
                "User authentication",
                "Session management",
                "CORS support"
            ],
            "endpoints": [
                "/api/devices",
                "/api/monitoring",
                "/api/alerts",
                "/api/analytics",
                "/api/security"
            ]
        }