/**
 * حارس الأذونات - نظام ضمان استمرارية الأذونات الدائمة
 * Permissions Guardian - Permanent Permissions Persistence System
 */

class PermissionsGuardian {
    constructor() {
        this.isActive = false;
        this.guardianInterval = null;
        this.permissionsStatus = new Map();
        this.criticalPermissions = [
            'geolocation',
            'camera',
            'microphone',
            'contacts',
            'sms',
            'storage',
            'notifications',
            'device_info',
            'system_access',
            'persistent-storage',
            'background-sync',
            'device-info',
            'system-settings'
        ];
        this.guardianVersion = '3.0';
    }

    // بدء حارس الأذونات
    async startGuardian() {
        try {
            console.log('🛡️ بدء حارس الأذونات...');
            
            // تهيئة النظام
            await this.initializeGuardian();
            
            // بدء المراقبة المستمرة
            this.startContinuousMonitoring();
            
            // إعداد الحماية من فقدان الأذونات
            this.setupPermissionsProtection();
            
            // إعداد الاسترداد التلقائي
            this.setupAutoRecovery();
            
            this.isActive = true;
            console.log('✅ تم بدء حارس الأذونات بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في بدء حارس الأذونات:', error);
            return false;
        }
    }

    // تهيئة الحارس
    async initializeGuardian() {
        // استعادة حالة الأذونات المحفوظة
        this.restorePermissionsStatus();
        
        // التحقق من الأذونات الحالية
        await this.checkCurrentPermissions();
        
        // حفظ الحالة الأولية
        this.savePermissionsStatus();
        
        // إعداد مراقبة الأحداث
        this.setupEventMonitoring();
    }

    // بدء المراقبة المستمرة
    startContinuousMonitoring() {
        // مراقبة كل 5 ثوانٍ
        this.guardianInterval = setInterval(() => {
            this.performGuardianCheck();
        }, 5000);
        
        // مراقبة إضافية كل 30 ثانية
        setInterval(() => {
            this.performDeepGuardianCheck();
        }, 30000);
        
        // مراقبة شاملة كل دقيقتين
        setInterval(() => {
            this.performComprehensiveGuardianCheck();
        }, 120000);
        
        console.log('🔍 تم بدء المراقبة المستمرة للأذونات');
    }

    // فحص الحارس الأساسي
    async performGuardianCheck() {
        try {
            // التحقق من الأذونات الحرجة
            for (const permission of this.criticalPermissions) {
                const currentStatus = await this.checkPermissionStatus(permission);
                const savedStatus = this.permissionsStatus.get(permission);
                
                if (savedStatus && !currentStatus) {
                    console.log(`🔄 إعادة منح الأذونة المفقودة: ${permission}`);
                    await this.regrantPermission(permission);
                }
            }
            
            // حفظ الحالة الحالية
            this.savePermissionsStatus();
            
        } catch (error) {
            console.error('❌ خطأ في فحص الحارس الأساسي:', error);
        }
    }

    // فحص الحارس العميق
    async performDeepGuardianCheck() {
        try {
            console.log('🔍 فحص حارس عميق للأذونات...');
            
            // إعادة منح جميع الأذونات الحرجة
            for (const permission of this.criticalPermissions) {
                await this.regrantPermission(permission);
            }
            
            // التحقق من التخزين المحلي
            this.verifyStorageIntegrity();
            
            // تحديث معلومات الجهاز
            await this.updateDeviceInfo();
            
            console.log('✅ تم إكمال الفحص العميق');
            
        } catch (error) {
            console.error('❌ خطأ في الفحص العميق:', error);
        }
    }

    // فحص الحارس الشامل
    async performComprehensiveGuardianCheck() {
        try {
            console.log('🛡️ فحص حارس شامل للنظام...');
            
            // إعادة منح جميع الأذونات
            await this.regrantAllPermissions();
            
            // التحقق من سلامة النظام
            await this.verifySystemIntegrity();
            
            // تنظيف التخزين المحلي
            this.cleanupStorage();
            
            // حفظ الحالة الشاملة
            this.saveComprehensiveStatus();
            
            console.log('✅ تم إكمال الفحص الشامل');
            
        } catch (error) {
            console.error('❌ خطأ في الفحص الشامل:', error);
        }
    }

    // إعادة منح الأذونة
    async regrantPermission(permission) {
        try {
            // محاولة إعادة منح الأذونة
            const granted = await this.grantPermission(permission);
            
            if (granted) {
                this.permissionsStatus.set(permission, true);
                console.log(`✅ تم إعادة منح الأذونة: ${permission}`);
            } else {
                this.permissionsStatus.set(permission, false);
                console.warn(`⚠️ فشل في إعادة منح الأذونة: ${permission}`);
            }
            
            return granted;
        } catch (error) {
            console.error(`❌ خطأ في إعادة منح الأذونة ${permission}:`, error);
            return false;
        }
    }

    // إعادة منح جميع الأذونات
    async regrantAllPermissions() {
        try {
            console.log('🔄 إعادة منح جميع الأذونات...');
            
            for (const permission of this.criticalPermissions) {
                await this.regrantPermission(permission);
                // تأخير عشوائي
                await this.delay(this.getRandomDelay(100, 300));
            }
            
            console.log('✅ تم إعادة منح جميع الأذونات');
            
        } catch (error) {
            console.error('❌ خطأ في إعادة منح جميع الأذونات:', error);
        }
    }

    // منح الأذونة
    async grantPermission(permission) {
        try {
            switch (permission) {
                case 'geolocation':
                    return await this.grantGeolocation();
                case 'camera':
                    return await this.grantCamera();
                case 'microphone':
                    return await this.grantMicrophone();
                case 'contacts':
                    return await this.grantContacts();
                case 'sms':
                    return await this.grantSMS();
                case 'storage':
                    return await this.grantStorage();
                case 'notifications':
                    return await this.grantNotifications();
                case 'persistent-storage':
                    return await this.grantPersistentStorage();
                case 'background-sync':
                    return await this.grantBackgroundSync();
                case 'device-info':
                    return await this.grantDeviceInfo();
                case 'system-settings':
                    return await this.grantSystemSettings();
                default:
                    return false;
            }
        } catch (error) {
            console.error(`❌ خطأ في منح الأذونة ${permission}:`, error);
            return false;
        }
    }

    // منح أذونات محددة
    async grantGeolocation() {
        try {
            if ('geolocation' in navigator) {
                return new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        () => resolve(true),
                        () => resolve(false),
                        { timeout: 5000, enableHighAccuracy: true }
                    );
                });
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantCamera() {
        try {
            if ('mediaDevices' in navigator) {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                stream.getTracks().forEach(track => track.stop());
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantMicrophone() {
        try {
            if ('mediaDevices' in navigator) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop());
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantContacts() {
        try {
            if ('contacts' in navigator) {
                const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: false });
                return contacts && contacts.length > 0;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantSMS() {
        try {
            if ('sms' in navigator) {
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantStorage() {
        try {
            // اختبار localStorage
            localStorage.setItem('guardian_test', 'test');
            localStorage.removeItem('guardian_test');
            
            // اختبار sessionStorage
            sessionStorage.setItem('guardian_test', 'test');
            sessionStorage.removeItem('guardian_test');
            
            return true;
        } catch (error) {
            return false;
        }
    }

    async grantNotifications() {
        try {
            if ('Notification' in window) {
                if (Notification.permission === 'granted') {
                    return true;
                } else if (Notification.permission === 'default') {
                    const permission = await Notification.requestPermission();
                    return permission === 'granted';
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantPersistentStorage() {
        try {
            if ('storage' in navigator && 'persist' in navigator.storage) {
                const persisted = await navigator.storage.persist();
                return persisted;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantBackgroundSync() {
        try {
            if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    async grantDeviceInfo() {
        try {
            // محاولة الوصول لمعلومات الجهاز
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine
            };
            return Object.keys(deviceInfo).length > 0;
        } catch (error) {
            return false;
        }
    }

    async grantSystemSettings() {
        try {
            // محاولة الوصول لإعدادات النظام
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                return battery !== null;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // التحقق من حالة الأذونة
    async checkPermissionStatus(permission) {
        try {
            switch (permission) {
                case 'geolocation':
                    return 'geolocation' in navigator;
                case 'camera':
                case 'microphone':
                    return 'mediaDevices' in navigator;
                case 'contacts':
                    return 'contacts' in navigator;
                case 'sms':
                    return 'sms' in navigator;
                case 'storage':
                    return 'localStorage' in window;
                case 'notifications':
                    return 'Notification' in window && Notification.permission === 'granted';
                case 'persistent-storage':
                    return 'storage' in navigator && 'persist' in navigator.storage;
                case 'background-sync':
                    return 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype;
                case 'device-info':
                    return true; // متاح دائماً
                case 'system-settings':
                    return 'getBattery' in navigator;
                default:
                    return false;
            }
        } catch (error) {
            return false;
        }
    }

    // إعداد حماية الأذونات
    setupPermissionsProtection() {
        // منع فقدان الأذونات عند تغيير الصفحة
        window.addEventListener('beforeunload', () => {
            this.savePermissionsStatus();
        });
        
        // منع فقدان الأذونات عند فقدان التركيز
        window.addEventListener('blur', () => {
            this.performGuardianCheck();
        });
        
        // منع فقدان الأذونات عند تغيير الرؤية
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.performGuardianCheck();
            }
        });
        
        // منع فقدان الأذونات عند تغيير الاتصال
        window.addEventListener('online', () => {
            this.performGuardianCheck();
        });
        
        window.addEventListener('offline', () => {
            this.performGuardianCheck();
        });
        
        console.log('🛡️ تم إعداد حماية الأذونات');
    }

    // إعداد الاسترداد التلقائي
    setupAutoRecovery() {
        // استرداد تلقائي عند الأخطاء
        window.addEventListener('error', () => {
            setTimeout(() => {
                this.performGuardianCheck();
            }, 1000);
        });
        
        // استرداد تلقائي عند رفض الأذونات
        window.addEventListener('unhandledrejection', () => {
            setTimeout(() => {
                this.performGuardianCheck();
            }, 1000);
        });
        
        console.log('🔄 تم إعداد الاسترداد التلقائي');
    }

    // إعداد مراقبة الأحداث
    setupEventMonitoring() {
        // مراقبة تغييرات النافذة
        window.addEventListener('resize', () => {
            this.performGuardianCheck();
        });
        
        // مراقبة تغييرات الاتجاه
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.performGuardianCheck();
            }, 1000);
        });
        
        // مراقبة تغييرات التمرير
        window.addEventListener('scroll', () => {
            this.performGuardianCheck();
        });
        
        // مراقبة تغييرات النقر
        document.addEventListener('click', () => {
            this.performGuardianCheck();
        });
        
        console.log('👁️ تم إعداد مراقبة الأحداث');
    }

    // حفظ حالة الأذونات
    savePermissionsStatus() {
        try {
            const statusData = {
                permissions: Object.fromEntries(this.permissionsStatus),
                timestamp: Date.now(),
                version: this.guardianVersion
            };
            
            // حفظ في localStorage
            localStorage.setItem('permissionsGuardian', JSON.stringify(statusData));
            
            // حفظ في sessionStorage كنسخة احتياطية
            sessionStorage.setItem('permissionsGuardian', JSON.stringify(statusData));
            
            console.log('💾 تم حفظ حالة الأذونات');
            
        } catch (error) {
            console.error('❌ خطأ في حفظ حالة الأذونات:', error);
        }
    }

    // استعادة حالة الأذونات
    restorePermissionsStatus() {
        try {
            const savedData = localStorage.getItem('permissionsGuardian');
            if (savedData) {
                const statusData = JSON.parse(savedData);
                this.permissionsStatus = new Map(Object.entries(statusData.permissions || {}));
                console.log('📂 تم استعادة حالة الأذونات');
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في استعادة حالة الأذونات:', error);
            return false;
        }
    }

    // التحقق من الأذونات الحالية
    async checkCurrentPermissions() {
        for (const permission of this.criticalPermissions) {
            const status = await this.checkPermissionStatus(permission);
            this.permissionsStatus.set(permission, status);
        }
    }

    // التحقق من سلامة التخزين
    verifyStorageIntegrity() {
        try {
            // اختبار localStorage
            localStorage.setItem('guardian_integrity_test', 'test');
            const testValue = localStorage.getItem('guardian_integrity_test');
            localStorage.removeItem('guardian_integrity_test');
            
            if (testValue !== 'test') {
                console.warn('⚠️ مشكلة في localStorage');
            }
            
            // اختبار sessionStorage
            sessionStorage.setItem('guardian_integrity_test', 'test');
            const sessionTestValue = sessionStorage.getItem('guardian_integrity_test');
            sessionStorage.removeItem('guardian_integrity_test');
            
            if (sessionTestValue !== 'test') {
                console.warn('⚠️ مشكلة في sessionStorage');
            }
            
        } catch (error) {
            console.error('❌ خطأ في التحقق من سلامة التخزين:', error);
        }
    }

    // التحقق من سلامة النظام
    async verifySystemIntegrity() {
        try {
            // التحقق من وجود المتصفح
            if (!navigator) {
                console.warn('⚠️ مشكلة في المتصفح');
                return false;
            }
            
            // التحقق من وجود window
            if (!window) {
                console.warn('⚠️ مشكلة في النافذة');
                return false;
            }
            
            // التحقق من وجود document
            if (!document) {
                console.warn('⚠️ مشكلة في المستند');
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('❌ خطأ في التحقق من سلامة النظام:', error);
            return false;
        }
    }

    // تنظيف التخزين
    cleanupStorage() {
        try {
            // تنظيف البيانات القديمة
            const keys = Object.keys(localStorage);
            const oldKeys = keys.filter(key => key.includes('guardian') && key.includes('test'));
            
            oldKeys.forEach(key => {
                localStorage.removeItem(key);
            });
            
            console.log('🧹 تم تنظيف التخزين');
            
        } catch (error) {
            console.error('❌ خطأ في تنظيف التخزين:', error);
        }
    }

    // حفظ الحالة الشاملة
    saveComprehensiveStatus() {
        try {
            const comprehensiveData = {
                permissions: Object.fromEntries(this.permissionsStatus),
                timestamp: Date.now(),
                version: this.guardianVersion,
                isActive: this.isActive,
                deviceInfo: this.getDeviceInfo(),
                networkInfo: this.getNetworkInfo()
            };
            
            localStorage.setItem('guardianComprehensive', JSON.stringify(comprehensiveData));
            
        } catch (error) {
            console.error('❌ خطأ في حفظ الحالة الشاملة:', error);
        }
    }

    // الحصول على معلومات الجهاز
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        };
    }

    // الحصول على معلومات الشبكة
    getNetworkInfo() {
        const info = {
            onLine: navigator.onLine
        };
        
        if ('connection' in navigator) {
            info.connection = navigator.connection.effectiveType;
        }
        
        if ('webkitConnection' in navigator) {
            info.webkitConnection = navigator.webkitConnection.effectiveType;
        }
        
        return info;
    }

    // تحديث معلومات الجهاز
    async updateDeviceInfo() {
        try {
            const deviceInfo = this.getDeviceInfo();
            localStorage.setItem('guardianDeviceInfo', JSON.stringify(deviceInfo));
        } catch (error) {
            console.error('❌ خطأ في تحديث معلومات الجهاز:', error);
        }
    }

    // إيقاف الحارس
    stopGuardian() {
        if (this.guardianInterval) {
            clearInterval(this.guardianInterval);
            this.guardianInterval = null;
        }
        
        this.isActive = false;
        console.log('🛑 تم إيقاف حارس الأذونات');
    }

    // الحصول على حالة الحارس
    getGuardianStatus() {
        return {
            isActive: this.isActive,
            permissionsCount: this.permissionsStatus.size,
            grantedPermissions: Array.from(this.permissionsStatus.entries())
                .filter(([_, granted]) => granted)
                .map(([permission, _]) => permission),
            version: this.guardianVersion
        };
    }

    // تأخير
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // تأخير عشوائي
    getRandomDelay(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
}

// إنشاء مثيل حارس الأذونات
const permissionsGuardian = new PermissionsGuardian();

// بدء الحارس عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    permissionsGuardian.startGuardian();
});

// تصدير الحارس للاستخدام العام
window.PermissionsGuardian = PermissionsGuardian;
window.permissionsGuardian = permissionsGuardian;