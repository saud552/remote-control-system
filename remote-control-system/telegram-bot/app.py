#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask wrapper for Telegram Bot to run as Web Service on Render
"""

import os
import threading
import time
import logging
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request
from bot import bot, logger as bot_logger, setup_authorized_users, device_manager, DB_FILE, SECURITY_CONFIG
from bot import command_executor as bot_command_executor

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعداد تسجيل خاص بـ Flask
flask_logger = logging.getLogger('flask_app')
flask_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
flask_logger.addHandler(handler)

# متغير لتتبع حالة البوت
bot_status = {
    "running": False,
    "start_time": None,
    "last_activity": None,
    "restart_count": 0,
    "active_devices": 0,
    "pending_commands": 0
}

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "status": "running",
        "service": "Telegram Bot",
        "version": "2.2.5",
        "bot_running": bot_status["running"],
        "uptime": time.time() - bot_status["start_time"] if bot_status["start_time"] else 0,
        "security": SECURITY_CONFIG,
        "restarts": bot_status["restart_count"],
        "active_devices": bot_status["active_devices"],
        "pending_commands": bot_status["pending_commands"]
    })

@app.route('/health')
def health():
    """فحص صحة الخدمة"""
    try:
        # فحص اتصال قاعدة البيانات
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        
        # فحص اتصال خادم الأوامر
        if not bot_command_executor.check_connection():
            return jsonify({"status": "warning", "message": "Command server not connected"}), 200
            
        return jsonify({
            "status": "healthy",
            "bot_running": bot_status["running"],
            "db_connection": "ok",
            "command_server": "connected"
        })
    except Exception as e:
        flask_logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/status')
def status():
    """حالة البوت"""
    try:
        # حساب الأجهزة النشطة
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM devices WHERE status = "active"')
        active_devices = cursor.fetchone()[0]
        
        # حساب الأوامر المعلقة
        cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "pending"')
        pending_commands = cursor.fetchone()[0]
        conn.close()
        
        bot_status["active_devices"] = active_devices
        bot_status["pending_commands"] = pending_commands
        
        return jsonify(bot_status)
    except Exception as e:
        flask_logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال webhook من Telegram"""
    try:
        update = request.get_json()
        if update:
            # معالجة التحديث في خيط منفصل
            threading.Thread(target=process_update, args=(update,)).start()
            return jsonify({"status": "ok"})
        return jsonify({"status": "no update"})
    except Exception as e:
        flask_logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

def process_update(update):
    """معالجة التحديث من Telegram"""
    try:
        bot.process_new_updates([update])
        bot_status["last_activity"] = datetime.now().isoformat()
    except Exception as e:
        flask_logger.error(f"Update processing error: {e}")

@app.route('/restart', methods=['POST'])
def restart_bot():
    """إعادة تشغيل البوت"""
    try:
        flask_logger.info("Restarting bot...")
        bot_status["restart_count"] += 1
        
        # إيقاف البوت الحالي
        bot.stop_polling()
        
        # إعادة تشغيل البوت
        threading.Thread(target=start_bot_safely).start()
        
        return jsonify({
            "status": "restarting",
            "message": "Bot restart initiated",
            "restart_count": bot_status["restart_count"]
        })
    except Exception as e:
        flask_logger.error(f"Restart error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def stats():
    """إحصائيات البوت"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # إحصائيات الأجهزة
        cursor.execute('SELECT COUNT(*) FROM devices')
        total_devices = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM devices WHERE status = "active"')
        active_devices = cursor.fetchone()[0]
        
        # إحصائيات الأوامر
        cursor.execute('SELECT COUNT(*) FROM commands')
        total_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "completed"')
        completed_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM commands WHERE status = "pending"')
        pending_commands = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "devices": {
                "total": total_devices,
                "active": active_devices,
                "inactive": total_devices - active_devices
            },
            "commands": {
                "total": total_commands,
                "completed": completed_commands,
                "pending": pending_commands,
                "failed": total_commands - completed_commands - pending_commands
            },
            "bot": bot_status
        })
    except Exception as e:
        flask_logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

def run_bot():
    """تشغيل البوت في خيط منفصل"""
    try:
        flask_logger.info("Starting bot...")
        bot_status["running"] = True
        bot_status["start_time"] = time.time()
        
        # إعداد المستخدمين المصرح لهم
        setup_authorized_users()
        
        # بدء البوت
        bot.polling(none_stop=True, timeout=60)
        
    except Exception as e:
        flask_logger.error(f"Bot error: {e}")
        bot_status["running"] = False
    finally:
        bot_status["running"] = False

def update_activity():
    """تحديث نشاط البوت"""
    while True:
        try:
            if bot_status["running"]:
                bot_status["last_activity"] = datetime.now().isoformat()
            time.sleep(60)  # تحديث كل دقيقة
        except Exception as e:
            flask_logger.error(f"Activity update error: {e}")

def start_bot_safely():
    """تشغيل البوت بشكل آمن"""
    try:
        run_bot()
    except Exception as e:
        flask_logger.error(f"Safe bot start error: {e}")
        bot_status["running"] = False

if __name__ == '__main__':
    # بدء خيط البوت
    bot_thread = threading.Thread(target=start_bot_safely, daemon=True)
    bot_thread.start()
    
    # بدء خيط تحديث النشاط
    activity_thread = threading.Thread(target=update_activity, daemon=True)
    activity_thread.start()
    
    # تشغيل Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)