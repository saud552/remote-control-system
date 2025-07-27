#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مراقب الأداء المتقدم لبوت تيليجرام
Advanced Performance Monitor for Telegram Bot
"""

import os
import time
import psutil
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'requests': defaultdict(int),
            'response_times': defaultdict(list),
            'errors': defaultdict(int),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'disk_usage': deque(maxlen=50),
            'network_io': deque(maxlen=50),
            'bot_commands': defaultdict(int),
            'user_activities': defaultdict(int),
            'device_operations': defaultdict(int)
        }
        
        self.alerts = []
        self.thresholds = {
            'memory_usage': 80.0,  # 80%
            'cpu_usage': 90.0,     # 90%
            'disk_usage': 85.0,    # 85%
            'response_time': 5.0,  # 5 seconds
            'error_rate': 10.0     # 10%
        }
        
        # إعداد التسجيل
        self.logger = logging.getLogger(__name__)
        
        # بدء المراقبة
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """حلقة المراقبة الرئيسية"""
        while self.monitoring_active:
            try:
                # جمع مقاييس النظام
                self._collect_system_metrics()
                
                # فحص التنبيهات
                self._check_alerts()
                
                # تنظيف البيانات القديمة
                self._cleanup_old_data()
                
                # انتظار قبل الجولة التالية
                time.sleep(30)  # كل 30 ثانية
                
            except Exception as e:
                self.logger.error(f"خطأ في حلقة المراقبة: {e}")
                time.sleep(60)  # انتظار أطول في حالة الخطأ
    
    def _collect_system_metrics(self):
        """جمع مقاييس النظام"""
        try:
            # استخدام الذاكرة
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append({
                'timestamp': time.time(),
                'percent': memory.percent,
                'used': memory.used,
                'available': memory.available,
                'total': memory.total
            })
            
            # استخدام المعالج
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append({
                'timestamp': time.time(),
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            })
            
            # استخدام القرص
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'].append({
                'timestamp': time.time(),
                'percent': (disk.used / disk.total) * 100,
                'used': disk.used,
                'free': disk.free,
                'total': disk.total
            })
            
            # إحصائيات الشبكة
            network = psutil.net_io_counters()
            self.metrics['network_io'].append({
                'timestamp': time.time(),
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            })
            
        except Exception as e:
            self.logger.error(f"خطأ في جمع مقاييس النظام: {e}")
    
    def record_request(self, endpoint: str, method: str = "GET", response_time: float = 0.0):
        """تسجيل طلب جديد"""
        key = f"{method}_{endpoint}"
        self.metrics['requests'][key] += 1
        
        if response_time > 0:
            self.metrics['response_times'][key].append(response_time)
            
            # الاحتفاظ بآخر 100 قياس فقط
            if len(self.metrics['response_times'][key]) > 100:
                self.metrics['response_times'][key] = self.metrics['response_times'][key][-100:]
    
    def record_error(self, error_type: str, error_message: str = ""):
        """تسجيل خطأ جديد"""
        self.metrics['errors'][error_type] += 1
        
        # تسجيل في السجل
        self.logger.error(f"خطأ مسجل: {error_type} - {error_message}")
    
    def record_bot_command(self, command: str, user_id: int = None):
        """تسجيل أمر بوت جديد"""
        self.metrics['bot_commands'][command] += 1
        
        if user_id:
            self.metrics['user_activities'][user_id] += 1
    
    def record_device_operation(self, operation: str, device_id: str = None):
        """تسجيل عملية جهاز جديدة"""
        self.metrics['device_operations'][operation] += 1
    
    def _check_alerts(self):
        """فحص التنبيهات"""
        current_time = time.time()
        
        # فحص استخدام الذاكرة
        if self.metrics['memory_usage']:
            latest_memory = self.metrics['memory_usage'][-1]
            if latest_memory['percent'] > self.thresholds['memory_usage']:
                self._create_alert('HIGH_MEMORY_USAGE', {
                    'current': latest_memory['percent'],
                    'threshold': self.thresholds['memory_usage'],
                    'timestamp': current_time
                })
        
        # فحص استخدام المعالج
        if self.metrics['cpu_usage']:
            latest_cpu = self.metrics['cpu_usage'][-1]
            if latest_cpu['percent'] > self.thresholds['cpu_usage']:
                self._create_alert('HIGH_CPU_USAGE', {
                    'current': latest_cpu['percent'],
                    'threshold': self.thresholds['cpu_usage'],
                    'timestamp': current_time
                })
        
        # فحص استخدام القرص
        if self.metrics['disk_usage']:
            latest_disk = self.metrics['disk_usage'][-1]
            if latest_disk['percent'] > self.thresholds['disk_usage']:
                self._create_alert('HIGH_DISK_USAGE', {
                    'current': latest_disk['percent'],
                    'threshold': self.thresholds['disk_usage'],
                    'timestamp': current_time
                })
        
        # فحص وقت الاستجابة
        for endpoint, times in self.metrics['response_times'].items():
            if times:
                avg_response_time = sum(times) / len(times)
                if avg_response_time > self.thresholds['response_time']:
                    self._create_alert('SLOW_RESPONSE_TIME', {
                        'endpoint': endpoint,
                        'avg_time': avg_response_time,
                        'threshold': self.thresholds['response_time'],
                        'timestamp': current_time
                    })
        
        # فحص معدل الأخطاء
        total_requests = sum(self.metrics['requests'].values())
        total_errors = sum(self.metrics['errors'].values())
        
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            if error_rate > self.thresholds['error_rate']:
                self._create_alert('HIGH_ERROR_RATE', {
                    'error_rate': error_rate,
                    'threshold': self.thresholds['error_rate'],
                    'total_requests': total_requests,
                    'total_errors': total_errors,
                    'timestamp': current_time
                })
    
    def _create_alert(self, alert_type: str, details: dict):
        """إنشاء تنبيه جديد"""
        alert = {
            'type': alert_type,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'severity': self._get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        
        # الاحتفاظ بآخر 100 تنبيه فقط
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # تسجيل التنبيه
        self.logger.warning(f"تنبيه أداء: {alert_type} - {details}")
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """تحديد شدة التنبيه"""
        high_severity = ['HIGH_MEMORY_USAGE', 'HIGH_CPU_USAGE', 'HIGH_ERROR_RATE']
        medium_severity = ['HIGH_DISK_USAGE', 'SLOW_RESPONSE_TIME']
        
        if alert_type in high_severity:
            return 'HIGH'
        elif alert_type in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _cleanup_old_data(self):
        """تنظيف البيانات القديمة"""
        current_time = time.time()
        cutoff_time = current_time - 86400  # يوم واحد
        
        # تنظيف مقاييس الذاكرة والمعالج والقرص
        for metric_name in ['memory_usage', 'cpu_usage', 'disk_usage', 'network_io']:
            if self.metrics[metric_name]:
                self.metrics[metric_name] = deque([
                    item for item in self.metrics[metric_name]
                    if item['timestamp'] > cutoff_time
                ], maxlen=self.metrics[metric_name].maxlen)
    
    def get_performance_stats(self) -> dict:
        """الحصول على إحصائيات الأداء"""
        uptime = time.time() - self.start_time
        
        # إحصائيات الطلبات
        total_requests = sum(self.metrics['requests'].values())
        total_errors = sum(self.metrics['errors'].values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # متوسط وقت الاستجابة
        avg_response_times = {}
        for endpoint, times in self.metrics['response_times'].items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        # إحصائيات النظام الحالية
        current_memory = self.metrics['memory_usage'][-1] if self.metrics['memory_usage'] else None
        current_cpu = self.metrics['cpu_usage'][-1] if self.metrics['cpu_usage'] else None
        current_disk = self.metrics['disk_usage'][-1] if self.metrics['disk_usage'] else None
        
        # أكثر الأوامر استخداماً
        top_commands = sorted(
            self.metrics['bot_commands'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # أكثر المستخدمين نشاطاً
        top_users = sorted(
            self.metrics['user_activities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'uptime': uptime,
            'requests': {
                'total': total_requests,
                'errors': total_errors,
                'error_rate': error_rate,
                'by_endpoint': dict(self.metrics['requests'])
            },
            'response_times': avg_response_times,
            'system': {
                'memory': current_memory,
                'cpu': current_cpu,
                'disk': current_disk
            },
            'bot_activity': {
                'total_commands': sum(self.metrics['bot_commands'].values()),
                'top_commands': top_commands,
                'top_users': top_users
            },
            'device_operations': dict(self.metrics['device_operations']),
            'alerts': {
                'total': len(self.alerts),
                'recent': len([a for a in self.alerts if time.time() - datetime.fromisoformat(a['timestamp']).timestamp() < 3600])
            }
        }
    
    def get_system_health(self) -> dict:
        """الحصول على صحة النظام"""
        health_status = 'HEALTHY'
        issues = []
        
        # فحص الذاكرة
        if self.metrics['memory_usage']:
            memory_percent = self.metrics['memory_usage'][-1]['percent']
            if memory_percent > self.thresholds['memory_usage']:
                health_status = 'WARNING'
                issues.append(f"استخدام الذاكرة مرتفع: {memory_percent:.1f}%")
        
        # فحص المعالج
        if self.metrics['cpu_usage']:
            cpu_percent = self.metrics['cpu_usage'][-1]['percent']
            if cpu_percent > self.thresholds['cpu_usage']:
                health_status = 'WARNING'
                issues.append(f"استخدام المعالج مرتفع: {cpu_percent:.1f}%")
        
        # فحص القرص
        if self.metrics['disk_usage']:
            disk_percent = self.metrics['disk_usage'][-1]['percent']
            if disk_percent > self.thresholds['disk_usage']:
                health_status = 'WARNING'
                issues.append(f"استخدام القرص مرتفع: {disk_percent:.1f}%")
        
        # فحص معدل الأخطاء
        total_requests = sum(self.metrics['requests'].values())
        total_errors = sum(self.metrics['errors'].values())
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            if error_rate > self.thresholds['error_rate']:
                health_status = 'CRITICAL'
                issues.append(f"معدل الأخطاء مرتفع: {error_rate:.1f}%")
        
        return {
            'status': health_status,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_metrics(self) -> dict:
        """تصدير جميع المقاييس"""
        return {
            'metrics': dict(self.metrics),
            'alerts': self.alerts,
            'thresholds': self.thresholds,
            'export_time': datetime.now().isoformat()
        }
    
    def import_metrics(self, data: dict):
        """استيراد المقاييس"""
        if 'metrics' in data:
            for key, value in data['metrics'].items():
                if key in self.metrics:
                    if isinstance(value, list):
                        self.metrics[key] = deque(value, maxlen=self.metrics[key].maxlen)
                    else:
                        self.metrics[key].update(value)
        
        if 'alerts' in data:
            self.alerts.extend(data['alerts'])
    
    def reset_metrics(self):
        """إعادة تعيين جميع المقاييس"""
        for key in self.metrics:
            if isinstance(self.metrics[key], defaultdict):
                self.metrics[key].clear()
            elif isinstance(self.metrics[key], deque):
                self.metrics[key].clear()
            else:
                self.metrics[key] = defaultdict(int)
        
        self.alerts.clear()
        self.start_time = time.time()
    
    def stop_monitoring(self):
        """إيقاف المراقبة"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)