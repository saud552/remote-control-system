# نظام التحكم في أجهزة Android عن بعد

## المتطلبات
- Node.js 18+
- Python 3.8+
- متصفح ويب حديث

## خطوات التنصيب

1. **تثبيت التبعيات:**
```bash
# لواجهة الويب وخادم التحكم
cd web-interface
npm install express

cd ../command-server
npm install express ws

# لبوت تيليجرام
cd ../telegram-bot
pip install -r requirements.txt
