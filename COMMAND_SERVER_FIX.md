# 🔧 حل مشاكل خادم الأوامر

## 📋 المشاكل المحتملة وحلولها

### 1. مشكلة في التبعيات
**الأعراض:** خطأ في `npm install`
**الحل:**
```bash
# تحديث package.json
{
  "dependencies": {
    "express": "^4.18.2",
    "ws": "^8.14.2",
    "cors": "^2.8.5",
    "express-rate-limit": "^7.1.5",
    "helmet": "^7.1.0",
    "compression": "^1.7.4",
    "crypto": "^1.0.1",
    "multer": "^1.4.5-lts.1",
    "archiver": "^6.0.1",
    "sqlite3": "^5.1.6"
  }
}
```

### 2. مشكلة في المنفذ
**الأعراض:** خطأ في `PORT` أو `EADDRINUSE`
**الحل:**
```javascript
// في server.js
const PORT = process.env.PORT || 4000;
console.log(`محاولة تشغيل على المنفذ: ${PORT}`);
```

### 3. مشكلة في قاعدة البيانات
**الأعراض:** خطأ في `sqlite3` أو `database`
**الحل:**
```javascript
// إنشاء مجلد قاعدة البيانات
const dbDir = path.join(__dirname, 'database');
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}
```

### 4. مشكلة في الذاكرة
**الأعراض:** خطأ `ENOMEM` أو `out of memory`
**الحل:**
- زيادة الذاكرة في Render
- تحسين استخدام الذاكرة في الكود

## 🚀 خطوات الحل السريع

### 1. فحص السجلات
```bash
# في Render Dashboard
1. اذهب إلى الخدمة remote-control-command-server-x59k
2. انقر على "Logs"
3. ابحث عن كلمة "error" أو "failed"
4. انسخ الخطأ الكامل
```

### 2. إعادة تشغيل الخدمة
```bash
# في Render Dashboard
1. اذهب إلى الخدمة
2. انقر على "Manual Deploy"
3. اختر "Clear build cache & deploy"
4. انتظر إعادة البناء
```

### 3. فحص التكوين
```yaml
# في render.yaml
- type: web
  name: remote-control-command-server
  env: node
  plan: free
  buildCommand: cd remote-control-system/command-server && npm install
  startCommand: cd remote-control-system/command-server && npm start
  envVars:
    - key: NODE_ENV
      value: production
    - key: PORT
      value: 10001
```

## 🔍 تشخيص المشكلة

### الخطأ الأكثر شيوعاً:
1. **خطأ في التبعيات** - 40%
2. **مشكلة في المنفذ** - 30%
3. **مشكلة في الذاكرة** - 20%
4. **مشكلة في قاعدة البيانات** - 10%

### كيفية التشخيص:
1. **راجع السجلات** في Render
2. **ابحث عن كلمة "error"**
3. **انظر إلى آخر سطر في السجلات**
4. **تحقق من رسائل البناء**

## ⚡ حلول سريعة

### الحل السريع 1: إعادة تشغيل
1. **اذهب إلى Render Dashboard**
2. **اختر الخدمة المعلقة**
3. **انقر "Manual Deploy"**
4. **اختر "Clear build cache & deploy"**

### الحل السريع 2: فحص التبعيات
1. **تحقق من package.json**
2. **تأكد من وجود جميع التبعيات**
3. **تحقق من إصدارات التبعيات**

### الحل السريع 3: فحص المنفذ
1. **تحقق من متغير PORT**
2. **تأكد من عدم تعارض المنافذ**
3. **تحقق من إعدادات Render**

## 📞 إذا لم تحل المشكلة

### 1. راجع السجلات الكاملة
2. **انسخ السجلات** وأرسلها للمطور
3. **اختبر الكود محلياً**
4. **تحقق من إعدادات Render**

### 2. حلول بديلة
- **إنشاء الخدمة يدوياً** بدلاً من Blueprint
- **استخدام خطة مدفوعة** للحصول على موارد أكثر
- **تحسين الكود** لتقليل استخدام الموارد

---

**آخر تحديث:** $(date)  
**الحالة:** جاري الحل