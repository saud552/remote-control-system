# 📱 تطبيق الموبايل - نظام التحكم عن بعد

## نظرة عامة

تطبيق الموبايل المتقدم لنظام التحكم عن بعد، مبني بـ React Native ويوفر واجهة مستخدم حديثة ومتجاوبة للتحكم في الأجهزة ومراقبتها.

## ✨ المميزات

### 🔐 الأمان والمصادقة
- تسجيل دخول آمن مع JWT
- مصادقة بيومترية (بصمة الإصبع، Face ID)
- تشفير البيانات المحلية
- إدارة الجلسات الآمنة

### 📊 لوحة التحكم
- إحصائيات فورية للأجهزة المتصلة
- مراقبة الأداء في الوقت الفعلي
- عرض التنبيهات النشطة
- مؤشرات حالة الأمان

### 📱 إدارة الأجهزة
- قائمة الأجهزة المتصلة
- تفاصيل شاملة لكل جهاز
- إجراءات التحكم السريعة
- فحص الأجهزة التلقائي

### 📈 المراقبة والتحليلات
- رسوم بيانية تفاعلية
- مراقبة الأداء والذاكرة
- تحليل حركة الشبكة
- تقارير مفصلة

### 🔔 نظام التنبيهات
- إشعارات فورية
- تصنيف التنبيهات حسب الأولوية
- إدارة التنبيهات
- إعدادات مخصصة

### ⚙️ الإعدادات المتقدمة
- تخصيص الواجهة
- إعدادات الأمان
- إدارة الحساب
- النسخ الاحتياطي

## 🚀 التثبيت والتشغيل

### المتطلبات الأساسية

```bash
# Node.js (الإصدار 16 أو أحدث)
node --version

# React Native CLI
npm install -g react-native-cli

# Android Studio (للتطوير على Android)
# Xcode (للتطوير على iOS)
```

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone https://github.com/remote-control-system/mobile-app.git
cd mobile-app
```

2. **تثبيت التبعيات**
```bash
npm install
# أو
yarn install
```

3. **إعداد iOS (للمطورين على macOS)**
```bash
cd ios
pod install
cd ..
```

4. **تشغيل التطبيق**

**لنظام Android:**
```bash
npx react-native run-android
```

**لنظام iOS:**
```bash
npx react-native run-ios
```

### إعدادات التطوير

1. **تكوين الخادم**
```javascript
// في src/services/ApiService.js
setBaseURL('http://your-server-ip:8000');
```

2. **إعداد الإشعارات**
```bash
# لنظام Android
npx react-native link react-native-push-notification

# لنظام iOS
cd ios && pod install
```

## 📁 هيكل المشروع

```
mobile-app/
├── android/                 # ملفات Android
├── ios/                    # ملفات iOS
├── src/
│   ├── components/         # المكونات القابلة لإعادة الاستخدام
│   │   ├── MetricCard.js
│   │   ├── DeviceCard.js
│   │   ├── AlertCard.js
│   │   └── ...
│   ├── screens/           # شاشات التطبيق
│   │   ├── DashboardScreen.js
│   │   ├── DevicesScreen.js
│   │   ├── MonitoringScreen.js
│   │   └── ...
│   ├── services/          # خدمات التطبيق
│   │   ├── ApiService.js
│   │   ├── StorageService.js
│   │   ├── NotificationService.js
│   │   └── ...
│   ├── navigation/        # إعدادات التنقل
│   ├── utils/            # أدوات مساعدة
│   ├── constants/        # الثوابت
│   └── assets/           # الصور والأيقونات
├── __tests__/            # اختبارات التطبيق
├── package.json
└── README.md
```

## 🔧 التكوين

### إعدادات البيئة

إنشاء ملف `.env`:
```env
API_BASE_URL=http://192.168.1.100:8000
ENVIRONMENT=development
DEBUG_MODE=true
```

### إعدادات الأمان

```javascript
// في src/services/SecurityService.js
const SECURITY_CONFIG = {
  encryptionKey: 'your-encryption-key',
  biometricEnabled: true,
  sessionTimeout: 3600, // ثانية
  maxLoginAttempts: 3,
};
```

## 📱 المميزات التقنية

### 🎨 واجهة المستخدم
- تصميم متجاوب لجميع أحجام الشاشات
- دعم الوضع المظلم والفاتح
- رسوم متحركة سلسة
- واجهة عربية كاملة

### 🔄 التحديثات الفورية
- WebSocket للبيانات المباشرة
- تحديث تلقائي للإحصائيات
- إشعارات فورية
- مزامنة البيانات

### 📊 الرسوم البيانية
- رسوم خطية للأداء
- رسوم دائرية للتوزيع
- رسوم شريطية للمقارنة
- رسوم تفاعلية

### 🔐 الأمان
- تشفير البيانات المحلية
- مصادقة آمنة
- حماية من التلاعب
- تسجيل الأحداث الأمنية

## 🧪 الاختبارات

### تشغيل الاختبارات
```bash
# جميع الاختبارات
npm test

# اختبارات محددة
npm test -- --testNamePattern="Dashboard"

# اختبارات مع تغطية
npm test -- --coverage
```

### أنواع الاختبارات
- **اختبارات الوحدة**: اختبار المكونات الفردية
- **اختبارات التكامل**: اختبار التفاعل بين المكونات
- **اختبارات E2E**: اختبار سيناريوهات المستخدم الكاملة

## 📦 البناء والإنتاج

### بناء تطبيق Android
```bash
# تنظيف المشروع
npm run clean

# بناء الإصدار الإنتاجي
npm run build:android
```

### بناء تطبيق iOS
```bash
# بناء الإصدار الإنتاجي
npm run build:ios
```

## 🚀 النشر

### متجر Google Play
1. إنشاء حساب مطور
2. تحضير ملف APK
3. رفع التطبيق
4. مراجعة الموافقة

### App Store
1. إنشاء حساب Apple Developer
2. تحضير ملف IPA
3. رفع التطبيق عبر Xcode
4. مراجعة الموافقة

## 🔧 استكشاف الأخطاء

### مشاكل شائعة

**مشكلة في الاتصال بالخادم:**
```bash
# التحقق من إعدادات الشبكة
npx react-native log-android
```

**مشكلة في الإشعارات:**
```bash
# إعادة تثبيت التبعيات
npm install
cd ios && pod install
```

**مشكلة في الأداء:**
```bash
# تنظيف الكاش
npm start -- --reset-cache
```

## 📚 الوثائق الإضافية

- [دليل المطور](docs/developer-guide.md)
- [دليل API](docs/api-guide.md)
- [دليل الأمان](docs/security-guide.md)
- [دليل النشر](docs/deployment-guide.md)

## 🤝 المساهمة

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة
3. Commit التغييرات
4. Push إلى الفرع
5. إنشاء Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 الدعم

- **البريد الإلكتروني**: support@remote-control-system.com
- **المسائل**: [GitHub Issues](https://github.com/remote-control-system/mobile-app/issues)
- **الوثائق**: [GitHub Wiki](https://github.com/remote-control-system/mobile-app/wiki)

## 🔄 الإصدارات

### الإصدار الحالي: 1.0.0

**التحديثات القادمة:**
- دعم الواقع المعزز (AR)
- تحسين الأداء
- ميزات أمان إضافية
- دعم المزيد من الأجهزة

---

**ملاحظة**: تأكد من تحديث إعدادات الخادم والـ API قبل تشغيل التطبيق.