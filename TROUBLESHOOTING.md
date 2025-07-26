# دليل استكشاف الأخطاء - نظام التحكم عن بعد المتقدم

## 🔍 المشاكل الشائعة وحلولها

### 1. مشكلة الانتقال إلى `about:blank`

**المشكلة**: الصفحة تنتقل إلى `about:blank` بعد التفعيل

**الحل**: 
- ✅ تم إصلاح هذه المشكلة في الإصدار الحالي
- تم إزالة جميع الكود الذي يحاول إعادة التوجيه
- الصفحة تبقى مرئية بعد التفعيل

**التحقق من الإصلاح**:
```javascript
// في وحدة تحكم المتصفح
console.log('تم تفعيل الحماية من إعادة التوجيه');
```

### 2. مشاكل الاتصال بالخادم

**المشكلة**: رسائل "تم الاتصال بجهاز جديد" و "انقطع الاتصال"

**الحل**:
1. تأكد من تشغيل خادم الأوامر:
```bash
cd remote-control-system/command-server
npm start
```

2. تحقق من المنفذ الصحيح (10001):
```bash
netstat -tulpn | grep 10001
```

3. تحقق من إعدادات Firewall:
```bash
sudo ufw allow 10001
```

### 3. مشاكل التشفير

**المشكلة**: أخطاء في التشفير أو فك التشفير

**الحل**:
1. تأكد من إصدار Node.js:
```bash
node --version  # يجب أن يكون >= 16.0.0
```

2. إعادة تثبيت التبعيات:
```bash
cd remote-control-system/web-interface
rm -rf node_modules package-lock.json
npm install

cd ../command-server
rm -rf node_modules package-lock.json
npm install
```

### 4. مشاكل البوت

**المشكلة**: البوت لا يستجيب أو لا يعمل

**الحل**:
1. تأكد من تعيين Token البوت:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

2. تحقق من تشغيل البوت:
```bash
cd remote-control-system/telegram-bot
python3 bot.py
```

3. تحقق من السجلات:
```bash
tail -f logs/telegram-bot.log
```

### 5. مشاكل واجهة الويب

**المشكلة**: واجهة الويب لا تعمل أو تظهر أخطاء

**الحل**:
1. تأكد من تشغيل الخادم:
```bash
cd remote-control-system/web-interface
npm start
```

2. تحقق من المنفذ 3000:
```bash
netstat -tulpn | grep 3000
```

3. تحقق من السجلات:
```bash
tail -f logs/web-interface.log
```

### 6. مشاكل Service Worker

**المشكلة**: Service Worker لا يعمل أو لا يسجل

**الحل**:
1. تحقق من تسجيل Service Worker:
```javascript
// في وحدة تحكم المتصفح
navigator.serviceWorker.getRegistrations().then(registrations => {
    console.log('Service Workers:', registrations);
});
```

2. إعادة تسجيل Service Worker:
```javascript
navigator.serviceWorker.register('/sw.js').then(registration => {
    console.log('Service Worker registered:', registration);
});
```

### 7. مشاكل الصلاحيات

**المشكلة**: فشل في طلب الصلاحيات

**الحل**:
1. تأكد من استخدام HTTPS أو localhost
2. تحقق من إعدادات المتصفح للصلاحيات
3. أعد تحميل الصفحة وحاول مرة أخرى

### 8. مشاكل التخزين المحلي

**المشكلة**: فشل في حفظ البيانات محلياً

**الحل**:
1. تحقق من مساحة التخزين:
```javascript
// في وحدة تحكم المتصفح
console.log('LocalStorage available:', !!window.localStorage);
```

2. تنظيف التخزين المحلي:
```javascript
localStorage.clear();
```

### 9. مشاكل الأداء

**المشكلة**: النظام بطيء أو يستخدم موارد كثيرة

**الحل**:
1. تحقق من استخدام الذاكرة:
```bash
ps aux | grep node
```

2. إعادة تشغيل النظام:
```bash
./stop.sh
./start.sh
```

3. تنظيف السجلات القديمة:
```bash
find logs/ -name "*.log" -mtime +7 -delete
```

### 10. مشاكل الشبكة

**المشكلة**: مشاكل في الاتصال بالإنترنت

**الحل**:
1. تحقق من الاتصال:
```bash
ping google.com
```

2. تحقق من إعدادات Proxy
3. تحقق من إعدادات DNS

## 🔧 أوامر التشخيص

### فحص حالة النظام
```bash
# فحص العمليات
ps aux | grep -E "(node|python)" | grep -v grep

# فحص المنافذ
netstat -tulpn | grep -E "(3000|10001)"

# فحص السجلات
tail -f logs/*.log
```

### إعادة تشغيل النظام
```bash
# إيقاف النظام
./stop.sh

# انتظار قليل
sleep 5

# إعادة تشغيل النظام
./start.sh
```

### تنظيف النظام
```bash
# تنظيف node_modules
find . -name "node_modules" -type d -exec rm -rf {} +

# تنظيف السجلات القديمة
find logs/ -name "*.log" -mtime +7 -delete

# إعادة تثبيت التبعيات
cd remote-control-system/web-interface && npm install
cd ../command-server && npm install
cd ../telegram-bot && pip3 install -r requirements.txt
```

## 📊 مراقبة الأداء

### مراقبة الموارد
```bash
# مراقبة CPU و Memory
htop

# مراقبة الشبكة
iftop

# مراقبة القرص
iotop
```

### مراقبة السجلات
```bash
# مراقبة سجلات النظام
tail -f logs/command-server.log
tail -f logs/web-interface.log
tail -f logs/telegram-bot.log
```

## 🆘 الحصول على المساعدة

إذا لم تحل المشكلة:

1. **تحقق من السجلات**: اقرأ ملفات السجلات للحصول على تفاصيل الخطأ
2. **أعد تشغيل النظام**: استخدم `./stop.sh` ثم `./start.sh`
3. **تحقق من المتطلبات**: تأكد من تثبيت جميع المتطلبات
4. **راجع الوثائق**: اقرأ README.md للحصول على معلومات إضافية

## 📝 ملاحظات مهمة

- تأكد من استخدام إصدارات متوافقة من Node.js و Python
- تحقق من إعدادات Firewall والـ Proxy
- احتفظ بنسخة احتياطية من البيانات المهمة
- راقب استخدام الموارد بانتظام

---

**⚠️ تحذير**: هذا النظام مصمم للاستخدام التعليمي والاختباري فقط. يرجى الالتزام بالقوانين المحلية.