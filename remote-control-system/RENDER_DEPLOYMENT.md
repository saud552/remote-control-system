# دليل النشر على Render
# Render Deployment Guide

## 📋 المتطلبات الأساسية

### 1. حساب Render
- إنشاء حساب على [render.com](https://render.com)
- ربط حساب GitHub

### 2. متطلبات المشروع
- كود مصدري في GitHub
- ملف `render.yaml` (موجود)
- ملف `Dockerfile` (موجود)
- متغيرات البيئة المطلوبة

## 🚀 خطوات النشر

### الخطوة 1: إعداد GitHub
```bash
# رفع الكود إلى GitHub
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### الخطوة 2: إنشاء الخدمات في Render

#### أ. خادم الأوامر (Command Server)
1. اذهب إلى [render.com](https://render.com)
2. اضغط على "New +" → "Web Service"
3. اربط مستودع GitHub
4. اختر المستودع الخاص بك
5. إعدادات الخدمة:
   - **Name**: `remote-control-command-server`
   - **Environment**: `Node`
   - **Build Command**: `cd command-server && npm install`
   - **Start Command**: `cd command-server && node server.js`
   - **Plan**: `Free`

#### ب. واجهة الويب (Web Interface)
1. اضغط على "New +" → "Web Service"
2. اربط نفس المستودع
3. إعدادات الخدمة:
   - **Name**: `remote-control-web-interface`
   - **Environment**: `Node`
   - **Build Command**: `cd web-interface && npm install`
   - **Start Command**: `cd web-interface && node server.js`
   - **Plan**: `Free`

#### ج. بوت تيليجرام (Telegram Bot)
1. اضغط على "New +" → "Background Worker"
2. اربط نفس المستودع
3. إعدادات الخدمة:
   - **Name**: `remote-control-telegram-bot`
   - **Environment**: `Python`
   - **Build Command**: `cd telegram-bot && pip install -r requirements.txt`
   - **Start Command**: `cd telegram-bot && python3 bot.py`
   - **Plan**: `Free`

### الخطوة 3: إعداد متغيرات البيئة

#### متغيرات مشتركة لجميع الخدمات:
```
NODE_ENV=production
SYSTEM_VERSION=2.1.5
SECURITY_LEVEL=high
LOG_LEVEL=info
```

#### متغيرات خاصة ببوت تيليجرام:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### الخطوة 4: إعدادات إضافية

#### نقطة فحص الصحة (Health Check)
- **Path**: `/health`
- **Timeout**: `30 seconds`
- **Interval**: `10 seconds`

#### إعدادات الشبكة
- **Auto-Deploy**: `Enabled`
- **Branch**: `main`

## 🔧 إعدادات متقدمة

### 1. استخدام ملف render.yaml
```yaml
# سيتم استخدام هذا الملف تلقائياً
# إذا كان موجوداً في المستودع
```

### 2. إعدادات Docker
```dockerfile
# سيتم استخدام Dockerfile تلقائياً
# إذا كان موجوداً في المستودع
```

### 3. إعدادات البيئة
```bash
# متغيرات البيئة المطلوبة
PORT=10000
NODE_ENV=production
TELEGRAM_BOT_TOKEN=your_token
```

## 📊 مراقبة الخدمات

### 1. سجلات الخدمات
- **Logs**: متاحة في لوحة تحكم Render
- **Real-time**: مراقبة مباشرة
- **History**: سجلات تاريخية

### 2. إحصائيات الأداء
- **CPU Usage**: استخدام المعالج
- **Memory Usage**: استخدام الذاكرة
- **Response Time**: وقت الاستجابة
- **Uptime**: وقت التشغيل

### 3. التنبيهات
- **Email Notifications**: تنبيهات البريد الإلكتروني
- **Slack Integration**: تكامل مع Slack
- **Custom Webhooks**: webhooks مخصصة

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. فشل في البناء (Build Failure)
```bash
# تحقق من:
- صحة ملفات package.json
- توفر جميع التبعيات
- صحة أوامر البناء
```

#### 2. فشل في التشغيل (Runtime Error)
```bash
# تحقق من:
- متغيرات البيئة
- منافذ الاتصال
- صلاحيات الملفات
```

#### 3. مشاكل الاتصال
```bash
# تحقق من:
- إعدادات CORS
- منافذ WebSocket
- إعدادات الشبكة
```

### أوامر التشخيص
```bash
# فحص حالة الخدمات
curl https://your-app.onrender.com/health

# فحص السجلات
# من لوحة تحكم Render

# إعادة تشغيل الخدمة
# من لوحة تحكم Render
```

## 🔄 التحديثات والصيانة

### 1. تحديث الكود
```bash
# رفع التحديثات
git add .
git commit -m "Update system"
git push origin main

# Render سيقوم بالتحديث تلقائياً
```

### 2. إدارة الإصدارات
```bash
# استخدام Git tags
git tag v2.1.5
git push origin v2.1.5
```

### 3. النسخ الاحتياطية
- **Database**: نسخ احتياطية تلقائية
- **Files**: حفظ في local-storage
- **Configuration**: حفظ في متغيرات البيئة

## 📞 الدعم والمساعدة

### موارد مفيدة
- [Render Documentation](https://render.com/docs)
- [Node.js on Render](https://render.com/docs/deploy-node-express-app)
- [Python on Render](https://render.com/docs/deploy-python-app)

### التواصل
- **Render Support**: من لوحة التحكم
- **Community**: منتديات Render
- **Documentation**: وثائق Render

## ✅ قائمة التحقق من النشر

- [ ] رفع الكود إلى GitHub
- [ ] إنشاء الخدمات في Render
- [ ] إعداد متغيرات البيئة
- [ ] اختبار نقطة فحص الصحة
- [ ] اختبار الاتصال بين الخدمات
- [ ] اختبار بوت تيليجرام
- [ ] مراقبة السجلات
- [ ] اختبار الأداء
- [ ] إعداد التنبيهات
- [ ] توثيق الروابط

## 🎯 النتيجة النهائية

بعد اكتمال النشر، ستحصل على:
- **خادم أوامر**: `https://your-command-server.onrender.com`
- **واجهة ويب**: `https://your-web-interface.onrender.com`
- **بوت تيليجرام**: يعمل في الخلفية
- **نظام متكامل**: جاهز للاستخدام