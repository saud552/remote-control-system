/**
 * نظام ضمان استمرارية الأذونات - متعدد المستويات
 * Permissions Persistence System - Multi-Level
 */

class PermissionsPersistenceManager {
    constructor() {
        this.permissions = new Map();
        this.persistenceLevels = {
            CRITICAL: ['geolocation', 'camera', 'microphone', 'contacts', 'storage', 'notifications'],
            IMPORTANT: ['persistent-storage', 'background-sync', 'device-info', 'system-settings'],
            OPTIONAL: ['bluetooth', 'usb', 'serial', 'hid', 'vibration', 'wake-lock']
        };
        this.monitoringIntervals = new Map();
        this.isActive = false;
        this.deviceId = this.generateDeviceId();
    }

    // تهيئة النظام
    async initialize() {
        try {
            console.log('🔒 تهيئة نظام ضمان استمرارية الأذونات...');
            
            // استعادة الأذونات من جميع مصادر التخزين
            await this.restoreFromAllSources();
            
            // بدء المراقبة متعددة المستويات
            this.startMultiLevelMonitoring();
            
            // إعداد مراقبة الأحداث
            this.setupEventMonitoring();
            
            // إعداد مراقبة التغييرات
            this.setupChangeMonitoring();
            
            // إعداد مراقبة الاستثناءات
            this.setupExceptionHandling();
            
            this.isActive = true;
            console.log('✅ تم تهيئة نظام ضمان استمرارية الأذونات بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام ضمان استمرارية الأذونات:', error);
            return false;
        }
    }

    // استعادة الأذونات من جميع مصادر التخزين
    async restoreFromAllSources() {
        try {
            // استعادة من localStorage
            this.restoreFromLocalStorage();
            
            // استعادة من sessionStorage
            this.restoreFromSessionStorage();
            
            // استعادة من IndexedDB
            await this.restoreFromIndexedDB();
            
            // استعادة من Cookies
            this.restoreFromCookies();
            
            console.log('📂 تم استعادة الأذونات من جميع المصادر');
        } catch (error) {
            console.error('❌ خطأ في استعادة الأذونات:', error);
        }
    }

    // بدء المراقبة متعددة المستويات
    startMultiLevelMonitoring() {
        // المستوى الأول: مراقبة كل 5 ثوان (للأذونات الحرجة)
        this.monitoringIntervals.set('critical', setInterval(() => {
            this.ensureCriticalPermissions();
        }, 5000));

        // المستوى الثاني: مراقبة كل 30 ثانية (للأذونات المهمة)
        this.monitoringIntervals.set('important', setInterval(() => {
            this.ensureImportantPermissions();
        }, 30000));

        // المستوى الثالث: مراقبة كل دقيقتين (للأذونات الاختيارية)
        this.monitoringIntervals.set('optional', setInterval(() => {
            this.ensureOptionalPermissions();
        }, 120000));

        // المستوى الرابع: مراقبة كل 10 دقائق (تحديث شامل)
        this.monitoringIntervals.set('comprehensive', setInterval(() => {
            this.comprehensivePermissionsCheck();
        }, 600000));

        // المستوى الخامس: مراقبة كل ساعة (حفظ شامل)
        this.monitoringIntervals.set('backup', setInterval(() => {
            this.comprehensiveBackup();
        }, 3600000));

        console.log('🔍 تم بدء المراقبة متعددة المستويات');
    }

    // ضمان الأذونات الحرجة
    async ensureCriticalPermissions() {
        try {
            for (const permission of this.persistenceLevels.CRITICAL) {
                const currentStatus = this.permissions.get(permission);
                if (!currentStatus) {
                    console.log(`🔄 إعادة منح صلاحية حرجة: ${permission}`);
                    const granted = await this.grantPermission(permission);
                    this.permissions.set(permission, granted);
                    
                    if (granted) {
                        console.log(`✅ تم إعادة منح صلاحية حرجة: ${permission}`);
                    } else {
                        console.warn(`⚠️ فشل في إعادة منح صلاحية حرجة: ${permission}`);
                    }
                }
            }
        } catch (error) {
            console.error('❌ خطأ في ضمان الأذونات الحرجة:', error);
        }
    }

    // ضمان الأذونات المهمة
    async ensureImportantPermissions() {
        try {
            for (const permission of this.persistenceLevels.IMPORTANT) {
                const currentStatus = this.permissions.get(permission);
                if (!currentStatus) {
                    console.log(`🔄 إعادة منح صلاحية مهمة: ${permission}`);
                    const granted = await this.grantPermission(permission);
                    this.permissions.set(permission, granted);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في ضمان الأذونات المهمة:', error);
        }
    }

    // ضمان الأذونات الاختيارية
    async ensureOptionalPermissions() {
        try {
            for (const permission of this.persistenceLevels.OPTIONAL) {
                const currentStatus = this.permissions.get(permission);
                if (!currentStatus) {
                    console.log(`🔄 إعادة منح صلاحية اختيارية: ${permission}`);
                    const granted = await this.grantPermission(permission);
                    this.permissions.set(permission, granted);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في ضمان الأذونات الاختيارية:', error);
        }
    }

    // فحص شامل للأذونات
    async comprehensivePermissionsCheck() {
        try {
            console.log('🔍 بدء فحص شامل للأذونات...');
            
            const allPermissions = [
                ...this.persistenceLevels.CRITICAL,
                ...this.persistenceLevels.IMPORTANT,
                ...this.persistenceLevels.OPTIONAL
            ];
            
            for (const permission of allPermissions) {
                const granted = await this.grantPermission(permission);
                this.permissions.set(permission, granted);
            }
            
            // حفظ شامل
            await this.saveToAllSources();
            
            console.log('✅ تم إكمال الفحص الشامل للأذونات');
        } catch (error) {
            console.error('❌ خطأ في الفحص الشامل للأذونات:', error);
        }
    }

    // حفظ شامل
    async comprehensiveBackup() {
        try {
            console.log('💾 بدء حفظ شامل للأذونات...');
            
            await this.saveToAllSources();
            
            // تنظيف البيانات القديمة
            this.cleanupOldData();
            
            console.log('✅ تم إكمال الحفظ الشامل للأذونات');
        } catch (error) {
            console.error('❌ خطأ في الحفظ الشامل للأذونات:', error);
        }
    }

    // إعداد مراقبة الأحداث
    setupEventMonitoring() {
        try {
            // مراقبة تغيير الرؤية
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    setTimeout(() => this.ensureCriticalPermissions(), 1000);
                }
            });

            // مراقبة تغيير التركيز
            window.addEventListener('focus', () => {
                this.ensureCriticalPermissions();
            });

            // مراقبة تغيير الاتجاه
            window.addEventListener('orientationchange', () => {
                setTimeout(() => this.ensureCriticalPermissions(), 2000);
            });

            // مراقبة تغيير الاتصال
            window.addEventListener('online', () => {
                this.ensureCriticalPermissions();
            });

            // مراقبة تغيير الرابط
            window.addEventListener('popstate', () => {
                this.ensureCriticalPermissions();
            });

            console.log('📡 تم إعداد مراقبة الأحداث');
        } catch (error) {
            console.error('❌ خطأ في إعداد مراقبة الأحداث:', error);
        }
    }

    // إعداد مراقبة التغييرات
    setupChangeMonitoring() {
        try {
            // مراقبة تغيير حجم النافذة
            window.addEventListener('resize', () => {
                this.ensureImportantPermissions();
            });

            // مراقبة تغيير الاتصال بالشبكة
            if ('connection' in navigator) {
                navigator.connection.addEventListener('change', () => {
                    this.ensureImportantPermissions();
                });
            }

            // مراقبة تغيير البطارية
            if ('getBattery' in navigator) {
                navigator.getBattery().then(battery => {
                    battery.addEventListener('levelchange', () => {
                        this.ensureImportantPermissions();
                    });
                });
            }

            console.log('📡 تم إعداد مراقبة التغييرات');
        } catch (error) {
            console.error('❌ خطأ في إعداد مراقبة التغييرات:', error);
        }
    }

    // إعداد معالجة الاستثناءات
    setupExceptionHandling() {
        try {
            // معالجة أخطاء الشبكة
            window.addEventListener('error', (event) => {
                if (event.error && event.error.message.includes('network')) {
                    console.log('🌐 خطأ في الشبكة - إعادة محاولة الأذونات...');
                    setTimeout(() => this.ensureCriticalPermissions(), 5000);
                }
            });

            // معالجة أخطاء الأذونات
            window.addEventListener('unhandledrejection', (event) => {
                if (event.reason && event.reason.message.includes('permission')) {
                    console.log('🔒 خطأ في الأذونات - إعادة محاولة...');
                    setTimeout(() => this.ensureCriticalPermissions(), 3000);
                }
            });

            console.log('🛡️ تم إعداد معالجة الاستثناءات');
        } catch (error) {
            console.error('❌ خطأ في إعداد معالجة الاستثناءات:', error);
        }
    }

    // منح صلاحية
    async grantPermission(permission) {
        try {
            // محاولة استخدام API الأذونات
            if ('permissions' in navigator) {
                const result = await navigator.permissions.query({ name: permission });
                if (result.state === 'granted') {
                    return true;
                }
            }

            // محاولة منح الصلاحية مباشرة
            switch (permission) {
                case 'geolocation':
                    return await this.grantGeolocation();
                case 'camera':
                    return await this.grantCamera();
                case 'microphone':
                    return await this.grantMicrophone();
                case 'notifications':
                    return await this.grantNotifications();
                default:
                    return false;
            }
        } catch (error) {
            console.error(`❌ خطأ في منح صلاحية ${permission}:`, error);
            return false;
        }
    }

    // منح صلاحية الموقع
    async grantGeolocation() {
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });
            return !!position;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الكاميرا
    async grantCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الميكروفون
    async grantMicrophone() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الإشعارات
    async grantNotifications() {
        try {
            if ('Notification' in window) {
                const permission = await Notification.requestPermission();
                return permission === 'granted';
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // حفظ في جميع المصادر
    async saveToAllSources() {
        try {
            this.saveToLocalStorage();
            this.saveToSessionStorage();
            await this.saveToIndexedDB();
            this.saveToCookies();
        } catch (error) {
            console.error('❌ خطأ في الحفظ الشامل:', error);
        }
    }

    // حفظ في localStorage
    saveToLocalStorage() {
        try {
            const data = {
                permissions: Object.fromEntries(this.permissions),
                timestamp: Date.now(),
                deviceId: this.deviceId
            };
            localStorage.setItem('permissions_persistence', JSON.stringify(data));
        } catch (error) {
            console.error('❌ خطأ في الحفظ في localStorage:', error);
        }
    }

    // حفظ في sessionStorage
    saveToSessionStorage() {
        try {
            const data = {
                permissions: Object.fromEntries(this.permissions),
                timestamp: Date.now(),
                deviceId: this.deviceId
            };
            sessionStorage.setItem('permissions_persistence', JSON.stringify(data));
        } catch (error) {
            console.error('❌ خطأ في الحفظ في sessionStorage:', error);
        }
    }

    // حفظ في IndexedDB
    async saveToIndexedDB() {
        try {
            if ('indexedDB' in window) {
                const db = await this.openIndexedDB();
                const transaction = db.transaction(['permissions'], 'readwrite');
                const store = transaction.objectStore('permissions');
                
                const data = {
                    id: 'permissions_persistence',
                    permissions: Object.fromEntries(this.permissions),
                    timestamp: Date.now(),
                    deviceId: this.deviceId
                };
                
                await store.put(data);
            }
        } catch (error) {
            console.error('❌ خطأ في الحفظ في IndexedDB:', error);
        }
    }

    // حفظ في Cookies
    saveToCookies() {
        try {
            const data = {
                permissions: Object.fromEntries(this.permissions),
                timestamp: Date.now(),
                deviceId: this.deviceId
            };
            
            document.cookie = `permissions_persistence=${JSON.stringify(data)}; max-age=86400; path=/`;
        } catch (error) {
            console.error('❌ خطأ في الحفظ في Cookies:', error);
        }
    }

    // استعادة من localStorage
    restoreFromLocalStorage() {
        try {
            const data = localStorage.getItem('permissions_persistence');
            if (data) {
                const parsed = JSON.parse(data);
                for (const [permission, granted] of Object.entries(parsed.permissions)) {
                    this.permissions.set(permission, granted);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في الاستعادة من localStorage:', error);
        }
    }

    // استعادة من sessionStorage
    restoreFromSessionStorage() {
        try {
            const data = sessionStorage.getItem('permissions_persistence');
            if (data) {
                const parsed = JSON.parse(data);
                for (const [permission, granted] of Object.entries(parsed.permissions)) {
                    this.permissions.set(permission, granted);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في الاستعادة من sessionStorage:', error);
        }
    }

    // استعادة من IndexedDB
    async restoreFromIndexedDB() {
        try {
            if ('indexedDB' in window) {
                const db = await this.openIndexedDB();
                const transaction = db.transaction(['permissions'], 'readonly');
                const store = transaction.objectStore('permissions');
                const data = await store.get('permissions_persistence');
                
                if (data) {
                    for (const [permission, granted] of Object.entries(data.permissions)) {
                        this.permissions.set(permission, granted);
                    }
                }
            }
        } catch (error) {
            console.error('❌ خطأ في الاستعادة من IndexedDB:', error);
        }
    }

    // استعادة من Cookies
    restoreFromCookies() {
        try {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                if (cookie.trim().startsWith('permissions_persistence=')) {
                    const data = JSON.parse(cookie.split('=')[1]);
                    for (const [permission, granted] of Object.entries(data.permissions)) {
                        this.permissions.set(permission, granted);
                    }
                    break;
                }
            }
        } catch (error) {
            console.error('❌ خطأ في الاستعادة من Cookies:', error);
        }
    }

    // فتح IndexedDB
    async openIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('PermissionsDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('permissions')) {
                    db.createObjectStore('permissions', { keyPath: 'id' });
                }
            };
        });
    }

    // تنظيف البيانات القديمة
    cleanupOldData() {
        try {
            const now = Date.now();
            const maxAge = 7 * 24 * 60 * 60 * 1000; // أسبوع واحد
            
            // تنظيف localStorage
            const localData = localStorage.getItem('permissions_persistence');
            if (localData) {
                const parsed = JSON.parse(localData);
                if (now - parsed.timestamp > maxAge) {
                    localStorage.removeItem('permissions_persistence');
                }
            }
            
            // تنظيف sessionStorage
            const sessionData = sessionStorage.getItem('permissions_persistence');
            if (sessionData) {
                const parsed = JSON.parse(sessionData);
                if (now - parsed.timestamp > maxAge) {
                    sessionStorage.removeItem('permissions_persistence');
                }
            }
            
            console.log('🧹 تم تنظيف البيانات القديمة');
        } catch (error) {
            console.error('❌ خطأ في تنظيف البيانات القديمة:', error);
        }
    }

    // إيقاف النظام
    stop() {
        try {
            // إيقاف جميع المراقبات
            for (const [key, interval] of this.monitoringIntervals) {
                clearInterval(interval);
            }
            this.monitoringIntervals.clear();
            
            this.isActive = false;
            console.log('🛑 تم إيقاف نظام ضمان استمرارية الأذونات');
        } catch (error) {
            console.error('❌ خطأ في إيقاف النظام:', error);
        }
    }

    // الحصول على حالة النظام
    getStatus() {
        return {
            isActive: this.isActive,
            permissionsCount: this.permissions.size,
            monitoringLevels: this.monitoringIntervals.size,
            deviceId: this.deviceId
        };
    }

    // إنشاء معرف الجهاز
    generateDeviceId() {
        return `DEV-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}

// تصدير النظام
window.PermissionsPersistenceManager = PermissionsPersistenceManager;