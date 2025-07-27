#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير الأمان المتقدم لبوت تيليجرام
Advanced Security Manager for Telegram Bot
"""

import os
import hashlib
import hmac
import base64
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AdvancedSecurityManager:
    def __init__(self):
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.blocked_users = set()
        self.suspicious_activities = {}
        self.rate_limits = {}
        self.security_log = []
        self.max_attempts = 5
        self.block_duration = 3600  # ساعة واحدة
        self.session_timeout = 1800  # 30 دقيقة
        
        # إعداد التسجيل
        self.logger = logging.getLogger(__name__)
        
    def _generate_encryption_key(self) -> bytes:
        """توليد مفتاح تشفير آمن"""
        try:
            # محاولة استعادة المفتاح من المتغيرات البيئية
            env_key = os.environ.get('ENCRYPTION_KEY')
            if env_key:
                return base64.urlsafe_b64decode(env_key)
            
            # توليد مفتاح جديد
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
            return key
            
        except Exception as e:
            self.logger.error(f"خطأ في توليد مفتاح التشفير: {e}")
            # مفتاح احتياطي
            return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> str:
        """تشفير البيانات"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"خطأ في تشفير البيانات: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"خطأ في فك تشفير البيانات: {e}")
            return encrypted_data
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """تشفير كلمة المرور"""
        if not salt:
            salt = os.urandom(16).hex()
        
        # استخدام PBKDF2 مع SHA256
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key).decode(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """التحقق من كلمة المرور"""
        try:
            new_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(hashed_password, new_hash)
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من كلمة المرور: {e}")
            return False
    
    def check_rate_limit(self, user_id: int, action: str = "general") -> bool:
        """فحص حد المعدل للمستخدم"""
        current_time = time.time()
        key = f"{user_id}_{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # إزالة الطلبات القديمة
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key]
            if current_time - req_time < 60  # دقيقة واحدة
        ]
        
        # فحص عدد الطلبات
        if len(self.rate_limits[key]) >= self.max_attempts:
            self.log_security_event("RATE_LIMIT_EXCEEDED", {
                "user_id": user_id,
                "action": action,
                "attempts": len(self.rate_limits[key])
            })
            return False
        
        # إضافة الطلب الحالي
        self.rate_limits[key].append(current_time)
        return True
    
    def is_user_blocked(self, user_id: int) -> bool:
        """فحص ما إذا كان المستخدم محظور"""
        if user_id in self.blocked_users:
            # فحص مدة الحظر
            block_info = self.suspicious_activities.get(user_id, {})
            block_time = block_info.get('block_time', 0)
            
            if time.time() - block_time < self.block_duration:
                return True
            else:
                # إزالة الحظر
                self.blocked_users.discard(user_id)
                if user_id in self.suspicious_activities:
                    del self.suspicious_activities[user_id]
        
        return False
    
    def block_user(self, user_id: int, reason: str = "Suspicious activity"):
        """حظر المستخدم"""
        self.blocked_users.add(user_id)
        self.suspicious_activities[user_id] = {
            'block_time': time.time(),
            'reason': reason,
            'attempts': self.suspicious_activities.get(user_id, {}).get('attempts', 0) + 1
        }
        
        self.log_security_event("USER_BLOCKED", {
            "user_id": user_id,
            "reason": reason,
            "block_time": datetime.now().isoformat()
        })
    
    def check_suspicious_activity(self, user_id: int, action: str, data: dict = None) -> bool:
        """فحص النشاط المشبوه"""
        current_time = time.time()
        
        if user_id not in self.suspicious_activities:
            self.suspicious_activities[user_id] = {
                'activities': [],
                'attempts': 0,
                'last_activity': current_time
            }
        
        user_activities = self.suspicious_activities[user_id]
        
        # إضافة النشاط الحالي
        activity = {
            'action': action,
            'timestamp': current_time,
            'data': data
        }
        user_activities['activities'].append(activity)
        
        # إزالة الأنشطة القديمة (أكثر من ساعة)
        user_activities['activities'] = [
            act for act in user_activities['activities']
            if current_time - act['timestamp'] < 3600
        ]
        
        # فحص الأنماط المشبوهة
        suspicious_patterns = self._detect_suspicious_patterns(user_activities['activities'])
        
        if suspicious_patterns:
            user_activities['attempts'] += 1
            self.log_security_event("SUSPICIOUS_ACTIVITY_DETECTED", {
                "user_id": user_id,
                "patterns": suspicious_patterns,
                "attempts": user_activities['attempts']
            })
            
            # حظر المستخدم إذا تجاوز الحد
            if user_activities['attempts'] >= 3:
                self.block_user(user_id, f"Multiple suspicious activities: {suspicious_patterns}")
                return True
        
        return False
    
    def _detect_suspicious_patterns(self, activities: List[dict]) -> List[str]:
        """اكتشاف الأنماط المشبوهة"""
        patterns = []
        
        if len(activities) > 50:  # أكثر من 50 نشاط في الساعة
            patterns.append("HIGH_ACTIVITY_RATE")
        
        # فحص تكرار الأوامر
        command_counts = {}
        for activity in activities:
            action = activity['action']
            command_counts[action] = command_counts.get(action, 0) + 1
        
        for command, count in command_counts.items():
            if count > 10:  # أكثر من 10 أوامر من نفس النوع
                patterns.append(f"REPEATED_COMMAND_{command}")
        
        # فحص الأوامر الحساسة
        sensitive_commands = ['reset', 'delete', 'format', 'wipe']
        for activity in activities:
            if activity['action'] in sensitive_commands:
                patterns.append(f"SENSITIVE_COMMAND_{activity['action']}")
        
        return patterns
    
    def validate_session(self, user_id: int, session_token: str) -> bool:
        """التحقق من صحة الجلسة"""
        try:
            # فك تشفير token الجلسة
            decrypted_token = self.decrypt_data(session_token)
            token_data = json.loads(decrypted_token)
            
            # فحص انتهاء صلاحية الجلسة
            session_time = token_data.get('timestamp', 0)
            if time.time() - session_time > self.session_timeout:
                return False
            
            # فحص معرف المستخدم
            if token_data.get('user_id') != user_id:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الجلسة: {e}")
            return False
    
    def create_session_token(self, user_id: int) -> str:
        """إنشاء token جلسة جديد"""
        session_data = {
            'user_id': user_id,
            'timestamp': time.time(),
            'random': os.urandom(16).hex()
        }
        
        session_json = json.dumps(session_data)
        return self.encrypt_data(session_json)
    
    def log_security_event(self, event_type: str, details: dict):
        """تسجيل حدث أمني"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        self.security_log.append(event)
        
        # الاحتفاظ بآخر 1000 حدث فقط
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
        
        # تسجيل في السجل
        self.logger.warning(f"حدث أمني: {event_type} - {details}")
    
    def get_security_stats(self) -> dict:
        """الحصول على إحصائيات الأمان"""
        current_time = time.time()
        
        # إحصائيات الحظر
        active_blocks = len([
            user_id for user_id in self.blocked_users
            if current_time - self.suspicious_activities.get(user_id, {}).get('block_time', 0) < self.block_duration
        ])
        
        # إحصائيات النشاط المشبوه
        suspicious_users = len([
            user_id for user_id, data in self.suspicious_activities.items()
            if data.get('attempts', 0) > 0
        ])
        
        # إحصائيات حد المعدل
        rate_limited_users = len([
            key for key, requests in self.rate_limits.items()
            if len(requests) >= self.max_attempts
        ])
        
        return {
            'blocked_users': active_blocks,
            'suspicious_users': suspicious_users,
            'rate_limited_users': rate_limited_users,
            'total_security_events': len(self.security_log),
            'recent_events': len([
                event for event in self.security_log
                if current_time - datetime.fromisoformat(event['timestamp']).timestamp() < 3600
            ])
        }
    
    def cleanup_old_data(self):
        """تنظيف البيانات القديمة"""
        current_time = time.time()
        
        # تنظيف حد المعدل
        for key in list(self.rate_limits.keys()):
            self.rate_limits[key] = [
                req_time for req_time in self.rate_limits[key]
                if current_time - req_time < 3600  # ساعة واحدة
            ]
            if not self.rate_limits[key]:
                del self.rate_limits[key]
        
        # تنظيف الأنشطة المشبوهة
        for user_id in list(self.suspicious_activities.keys()):
            user_data = self.suspicious_activities[user_id]
            user_data['activities'] = [
                act for act in user_data['activities']
                if current_time - act['timestamp'] < 86400  # يوم واحد
            ]
            
            # إزالة المستخدمين الذين لم يعد لديهم أنشطة
            if not user_data['activities'] and user_data.get('attempts', 0) == 0:
                del self.suspicious_activities[user_id]
    
    def export_security_log(self) -> List[dict]:
        """تصدير سجل الأمان"""
        return self.security_log.copy()
    
    def import_security_log(self, log_data: List[dict]):
        """استيراد سجل الأمان"""
        self.security_log.extend(log_data)
        
        # الاحتفاظ بآخر 1000 حدث فقط
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]