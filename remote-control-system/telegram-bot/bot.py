import telebot
import requests
import sqlite3
import uuid
import time

bot = telebot.TeleBot("YOUR_BOT_TOKEN")
DB_FILE = 'devices.db'

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            user_id INTEGER,
            device_id TEXT,
            activation_code TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# إضافة جهاز جديد
def add_device(user_id, device_id, activation_code):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO devices (user_id, device_id, activation_code, status)
        VALUES (?, ?, ?, ?)
    ''', (user_id, device_id, activation_code, 'pending'))
    conn.commit()
    conn.close()

# الحصول على أجهزة المستخدم
def get_user_devices(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT device_id, status FROM devices WHERE user_id = ?', (user_id,))
    devices = cursor.fetchall()
    conn.close()
    return devices

# توليد كود التفعيل
def generate_activation_code():
    return str(uuid.uuid4())[:8].upper()

# إرسال الأوامر للجهاز
def send_command(device_id, command):
    try:
        response = requests.post(
            'http://localhost:4000/send-command',
            json={
                'deviceId': device_id,
                'command': command
            }
        )
        return response.json()
    except Exception as e:
        print(f"Error sending command: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحبًا! أنا بوت التحكم في الأجهزة. استخدم /link لربط جهازك")

@bot.message_handler(commands=['link'])
def link_device(message):
    user_id = message.chat.id
    activation_code = generate_activation_code()
    device_id = f"DEV-{user_id}-{int(time.time())}"
    
    add_device(user_id, device_id, activation_code)
    
    bot.send_message(
        user_id,
        f"لربط جهازك:\n"
        f"1. افتح هذا الرابط على الجهاز:\n"
        f"http://localhost:3000\n"
        f"2. أدخل هذا الكود عند الطلب: {activation_code}\n\n"
        f"معرف الجهاز: {device_id}"
    )

@bot.message_handler(commands=['devices'])
def list_devices(message):
    user_id = message.chat.id
    devices = get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "ليس لديك أجهزة مرتبطة. استخدم /link لربط جهاز جديد")
        return
    
    response = "الأجهزة المرتبطة لديك:\n\n"
    for device in devices:
        status_icon = "🟢" if device[1] == 'active' else "🔴"
        response += f"{status_icon} {device[0]}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['contacts'])
def backup_contacts(message):
    user_id = message.chat.id
    devices = get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "ليس لديك أجهزة مرتبطة. استخدم /link لربط جهاز جديد")
        return
    
    # نستخدم الجهاز الأول النشط
    device_id = devices[0][0]
    
    result = send_command(device_id, {'action': 'backup_contacts'})
    
    if result and 'status' in result and result['status'] == 'تم إرسال الأمر':
        bot.reply_to(message, "جارٍ إنشاء نسخة احتياطية من جهات الاتصال...")
    else:
        bot.reply_to(message, "فشل في إرسال الأمر. تأكد من اتصال الجهاز")

@bot.message_handler(commands=['sms'])
def backup_sms(message):
    user_id = message.chat.id
    devices = get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "ليس لديك أجهزة مرتبطة. استخدم /link لربط جهاز جديد")
        return
    
    device_id = devices[0][0]
    result = send_command(device_id, {'action': 'backup_sms'})
    
    if result and 'status' in result and result['status'] == 'تم إرسال الأمر':
        bot.reply_to(message, "جارٍ إنشاء نسخة احتياطية من الرسائل النصية...")
    else:
        bot.reply_to(message, "فشل في إرسال الأمر. تأكد من اتصال الجهاز")

@bot.message_handler(commands=['record'])
def record_camera(message):
    user_id = message.chat.id
    devices = get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "ليس لديك أجهزة مرتبطة. استخدم /link لربط جهاز جديد")
        return
    
    device_id = devices[0][0]
    result = send_command(device_id, {'action': 'record_camera', 'duration': 30})
    
    if result and 'status' in result and result['status'] == 'تم إرسال الأمر':
        bot.reply_to(message, "جارٍ تسجيل الفيديو من الكاميرا الأمامية...")
    else:
        bot.reply_to(message, "فشل في إرسال الأمر. تأكد من اتصال الجهاز")

@bot.message_handler(commands=['reset'])
def factory_reset(message):
    user_id = message.chat.id
    devices = get_user_devices(user_id)
    
    if not devices:
        bot.reply_to(message, "ليس لديك أجهزة مرتبطة. استخدم /link لربط جهاز جديد")
        return
    
    device_id = devices[0][0]
    result = send_command(device_id, {'action': 'factory_reset'})
    
    if result and 'status' in result and result['status'] == 'تم إرسال الأمر':
        bot.reply_to(message, "جارٍ إعادة ضبط الجهاز إلى إعدادات المصنع...")
    else:
        bot.reply_to(message, "فشل في إرسال الأمر. تأكد من اتصال الجهاز")

if __name__ == '__main__':
    init_db()
    print("تم بدء بوت تيليجرام...")
    bot.polling()