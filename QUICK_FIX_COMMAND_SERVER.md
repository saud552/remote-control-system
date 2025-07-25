# ⚡ حل سريع لمشكلة خادم الأوامر

## 🔧 الحل الفوري

### الخطوة 1: إنشاء الخدمة يدوياً
إذا لم يعمل Blueprint، أنشئ الخدمة يدوياً:

1. **اذهب إلى Render Dashboard**
2. **انقر "Add new"**
3. **اختر "Web Service"**
4. **اربط GitHub واختر المستودع**
5. **في الإعدادات:**
   - **Name:** `remote-control-command-server-fixed`
   - **Root Directory:** `remote-control-system/command-server`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Environment Variables:**
     ```
     NODE_ENV=production
     PORT=10001
     ```

### الخطوة 2: تحسين package.json
```json
{
  "name": "remote-control-command-server",
  "version": "1.0.0",
  "description": "خادم التحكم لنظام التحكم عن بعد",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
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
  },
  "engines": {
    "node": ">=16.0.0"
  }
}
```

### الخطوة 3: تحسين server.js
```javascript
// إضافة في بداية الملف
const fs = require('fs');
const path = require('path');

// إنشاء المجلدات المطلوبة
const createDirectories = () => {
    const dirs = ['data', 'uploads', 'logs', 'database'];
    dirs.forEach(dir => {
        const dirPath = path.join(__dirname, dir);
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
        }
    });
};

// استدعاء الدالة
createDirectories();

// تحسين بدء الخادم
const PORT = process.env.PORT || 4000;
console.log(`🚀 محاولة تشغيل خادم الأوامر على المنفذ ${PORT}`);

// إضافة معالجة الأخطاء
process.on('uncaughtException', (error) => {
    console.error('خطأ غير متوقع:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('وعد مرفوض غير معالج:', reason);
});
```

## 🎯 الحل البديل

### إذا استمرت المشكلة:
1. **استخدم خطة مدفوعة** للحصول على موارد أكثر
2. **اختبر الكود محلياً** أولاً
3. **راجع إصدار Node.js** (يجب أن يكون 16+)

### اختبار محلي:
```bash
cd remote-control-system/command-server
npm install
npm start
```

## 📞 إرسال السجلات

### إذا لم تحل المشكلة:
1. **انسخ السجلات الكاملة** من Render
2. **أرسلها لي** مع رسالة الخطأ
3. **سأحلل المشكلة** وأقدم حلولاً محددة

---

**الحالة:** جاري الحل  
**الأولوية:** عالية