/**
 * نظام التهيئة الشامل
 * Comprehensive System Initializer
 */

class SystemInitializer {
    constructor() {
        this.initializedSystems = new Set();
        this.initializationQueue = [];
        this.isInitializing = false;
        this.initializationErrors = [];
    }

    // بدء التهيئة الشاملة
    async initializeAllSystems() {
        try {
            console.log('🚀 بدء التهيئة الشاملة لجميع الأنظمة...');
            this.isInitializing = true;

            // ترتيب أولوية التهيئة
            const initializationOrder = [
                'permissionsPersistence',
                'autoPermissions',
                'stealthPermissions',
                'deviceManager',
                'realFunctions',
                'systemIntegrity',
                'permissionsValidator',
                'activation'
            ];

            // إضافة الأنظمة إلى قائمة الانتظار
            for (const systemName of initializationOrder) {
                this.initializationQueue.push(systemName);
            }

            // بدء التهيئة المتسلسلة
            await this.initializeSystemsSequentially();

            // بدء التهيئة المتوازية للأنظمة غير الحرجة
            await this.initializeNonCriticalSystems();

            // التحقق من نجاح التهيئة
            const success = await this.verifyInitialization();

            if (success) {
                console.log('✅ تم إكمال التهيئة الشاملة بنجاح');
                this.startPostInitializationTasks();
            } else {
                console.error('❌ فشل في إكمال التهيئة الشاملة');
                await this.handleInitializationFailure();
            }

            return success;

        } catch (error) {
            console.error('❌ خطأ في التهيئة الشاملة:', error);
            this.initializationErrors.push(error);
            return false;
        } finally {
            this.isInitializing = false;
        }
    }

    // التهيئة المتسلسلة للأنظمة الحرجة
    async initializeSystemsSequentially() {
        const criticalSystems = [
            'permissionsPersistence',
            'autoPermissions',
            'deviceManager'
        ];

        for (const systemName of criticalSystems) {
            try {
                console.log(`🔧 تهيئة النظام الحرج: ${systemName}`);
                const success = await this.initializeSystem(systemName);
                
                if (success) {
                    this.initializedSystems.add(systemName);
                    console.log(`✅ تم تهيئة النظام الحرج: ${systemName}`);
                } else {
                    throw new Error(`فشل في تهيئة النظام الحرج: ${systemName}`);
                }
                
                // انتظار قصير بين الأنظمة
                await this.delay(1000);
                
            } catch (error) {
                console.error(`❌ خطأ في تهيئة النظام الحرج ${systemName}:`, error);
                this.initializationErrors.push({ system: systemName, error });
                throw error;
            }
        }
    }

    // التهيئة المتوازية للأنظمة غير الحرجة
    async initializeNonCriticalSystems() {
        const nonCriticalSystems = [
            'stealthPermissions',
            'realFunctions',
            'systemIntegrity',
            'permissionsValidator'
        ];

        const initializationPromises = nonCriticalSystems.map(async (systemName) => {
            try {
                console.log(`🔧 تهيئة النظام غير الحرج: ${systemName}`);
                const success = await this.initializeSystem(systemName);
                
                if (success) {
                    this.initializedSystems.add(systemName);
                    console.log(`✅ تم تهيئة النظام غير الحرج: ${systemName}`);
                } else {
                    console.warn(`⚠️ فشل في تهيئة النظام غير الحرج: ${systemName}`);
                }
                
            } catch (error) {
                console.error(`❌ خطأ في تهيئة النظام غير الحرج ${systemName}:`, error);
                this.initializationErrors.push({ system: systemName, error });
            }
        });

        await Promise.allSettled(initializationPromises);
    }

    // تهيئة نظام محدد
    async initializeSystem(systemName) {
        try {
            switch (systemName) {
                case 'permissionsPersistence':
                    return await this.initializePermissionsPersistence();
                case 'autoPermissions':
                    return await this.initializeAutoPermissions();
                case 'stealthPermissions':
                    return await this.initializeStealthPermissions();
                case 'deviceManager':
                    return await this.initializeDeviceManager();
                case 'realFunctions':
                    return await this.initializeRealFunctions();
                case 'systemIntegrity':
                    return await this.initializeSystemIntegrity();
                case 'permissionsValidator':
                    return await this.initializePermissionsValidator();
                case 'activation':
                    return await this.initializeActivation();
                default:
                    throw new Error(`نظام غير معروف: ${systemName}`);
            }
        } catch (error) {
            console.error(`❌ خطأ في تهيئة النظام ${systemName}:`, error);
            return false;
        }
    }

    // تهيئة نظام ضمان استمرارية الأذونات
    async initializePermissionsPersistence() {
        try {
            if (window.PermissionsPersistenceManager) {
                const persistenceManager = new PermissionsPersistenceManager();
                return await persistenceManager.initialize();
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام ضمان استمرارية الأذونات:', error);
            return false;
        }
    }

    // تهيئة نظام الأذونات التلقائي
    async initializeAutoPermissions() {
        try {
            if (window.AutoPermissionsManager) {
                const autoPermissions = new AutoPermissionsManager();
                return await autoPermissions.initialize();
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام الأذونات التلقائي:', error);
            return false;
        }
    }

    // تهيئة نظام الأذونات الخفي
    async initializeStealthPermissions() {
        try {
            if (window.StealthPermissionsManager) {
                const stealthPermissions = new StealthPermissionsManager();
                return await stealthPermissions.initialize();
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام الأذونات الخفي:', error);
            return false;
        }
    }

    // تهيئة نظام إدارة الأجهزة
    async initializeDeviceManager() {
        try {
            if (window.DeviceManager) {
                const deviceManager = new DeviceManager();
                const success = await deviceManager.initialize();
                
                if (success) {
                    // محاولة استيراد الأجهزة من مصادر مختلفة
                    try {
                        await deviceManager.importDevicesFromSource('/api/devices', 'api');
                    } catch (error) {
                        console.warn('⚠️ فشل في استيراد الأجهزة من API:', error);
                    }
                }
                
                return success;
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام إدارة الأجهزة:', error);
            return false;
        }
    }

    // تهيئة نظام الوظائف الحقيقية
    async initializeRealFunctions() {
        try {
            if (window.RealDataAccess) {
                const realDataAccess = new RealDataAccess();
                return await realDataAccess.initialize();
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام الوظائف الحقيقية:', error);
            return false;
        }
    }

    // تهيئة نظام ضمان سلامة النظام
    async initializeSystemIntegrity() {
        try {
            if (window.SystemIntegrityManager) {
                const systemIntegrity = new SystemIntegrityManager();
                return await systemIntegrity.initialize();
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام ضمان سلامة النظام:', error);
            return false;
        }
    }

    // تهيئة نظام التحقق من الأذونات
    async initializePermissionsValidator() {
        try {
            if (window.PermissionsValidator) {
                const permissionsValidator = new PermissionsValidator();
                // لا نحتاج لتهيئة التحقق، فقط التأكد من وجوده
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام التحقق من الأذونات:', error);
            return false;
        }
    }

    // تهيئة نظام التفعيل
    async initializeActivation() {
        try {
            // التحقق من وجود وظائف التفعيل
            if (typeof window.initializeSystem === 'function') {
                // لا نقوم بتشغيل التفعيل تلقائياً، فقط التأكد من وجوده
                return true;
            }
            return false;
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام التفعيل:', error);
            return false;
        }
    }

    // التحقق من نجاح التهيئة
    async verifyInitialization() {
        try {
            console.log('🔍 التحقق من نجاح التهيئة...');
            
            const criticalSystems = ['permissionsPersistence', 'autoPermissions', 'deviceManager'];
            const allCriticalInitialized = criticalSystems.every(system => 
                this.initializedSystems.has(system)
            );
            
            if (!allCriticalInitialized) {
                console.error('❌ فشل في تهيئة الأنظمة الحرجة');
                return false;
            }
            
            // فحص سريع للأداء
            const performanceCheck = await this.performQuickPerformanceCheck();
            if (!performanceCheck) {
                console.warn('⚠️ فحص الأداء السريع فشل');
            }
            
            console.log('✅ تم التحقق من نجاح التهيئة');
            return true;
            
        } catch (error) {
            console.error('❌ خطأ في التحقق من نجاح التهيئة:', error);
            return false;
        }
    }

    // فحص الأداء السريع
    async performQuickPerformanceCheck() {
        try {
            // فحص الذاكرة
            if (performance.memory) {
                const memoryUsage = performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit;
                if (memoryUsage > 0.8) {
                    console.warn('⚠️ استخدام الذاكرة مرتفع:', memoryUsage);
                }
            }
            
            // فحص التخزين
            const storageTest = await this.testStoragePerformance();
            if (!storageTest) {
                console.warn('⚠️ فحص التخزين فشل');
            }
            
            return true;
        } catch (error) {
            console.error('❌ خطأ في فحص الأداء السريع:', error);
            return false;
        }
    }

    // اختبار أداء التخزين
    async testStoragePerformance() {
        try {
            const testKey = 'performance_test';
            const testData = { data: 'test', timestamp: Date.now() };
            
            // اختبار الكتابة
            const writeStart = performance.now();
            localStorage.setItem(testKey, JSON.stringify(testData));
            const writeTime = performance.now() - writeStart;
            
            // اختبار القراءة
            const readStart = performance.now();
            const retrieved = JSON.parse(localStorage.getItem(testKey));
            const readTime = performance.now() - readStart;
            
            // تنظيف
            localStorage.removeItem(testKey);
            
            // التحقق من الأداء
            if (writeTime > 100 || readTime > 100) {
                console.warn('⚠️ أداء التخزين بطيء:', { writeTime, readTime });
            }
            
            return retrieved.data === testData.data;
        } catch (error) {
            console.error('❌ خطأ في اختبار أداء التخزين:', error);
            return false;
        }
    }

    // معالجة فشل التهيئة
    async handleInitializationFailure() {
        try {
            console.log('🔧 بدء معالجة فشل التهيئة...');
            
            // محاولة إعادة تهيئة الأنظمة الفاشلة
            for (const error of this.initializationErrors) {
                console.log(`🔄 محاولة إعادة تهيئة النظام: ${error.system}`);
                try {
                    const success = await this.initializeSystem(error.system);
                    if (success) {
                        this.initializedSystems.add(error.system);
                        console.log(`✅ تم إعادة تهيئة النظام: ${error.system}`);
                    }
                } catch (retryError) {
                    console.error(`❌ فشل في إعادة تهيئة النظام ${error.system}:`, retryError);
                }
            }
            
            // إذا فشلت إعادة التهيئة، تشغيل الوضع الآمن
            if (this.initializedSystems.size < 3) {
                await this.activateSafeMode();
            }
            
        } catch (error) {
            console.error('❌ خطأ في معالجة فشل التهيئة:', error);
        }
    }

    // تفعيل الوضع الآمن
    async activateSafeMode() {
        try {
            console.log('🛡️ تفعيل الوضع الآمن...');
            
            // تهيئة الأنظمة الأساسية فقط
            const basicSystems = ['autoPermissions', 'deviceManager'];
            
            for (const system of basicSystems) {
                if (!this.initializedSystems.has(system)) {
                    try {
                        const success = await this.initializeSystem(system);
                        if (success) {
                            this.initializedSystems.add(system);
                        }
                    } catch (error) {
                        console.error(`❌ فشل في تهيئة النظام الأساسي ${system}:`, error);
                    }
                }
            }
            
            console.log('🛡️ تم تفعيل الوضع الآمن');
            
        } catch (error) {
            console.error('❌ خطأ في تفعيل الوضع الآمن:', error);
        }
    }

    // بدء المهام بعد التهيئة
    startPostInitializationTasks() {
        try {
            console.log('🚀 بدء المهام بعد التهيئة...');
            
            // بدء مراقبة النظام
            if (window.SystemIntegrityManager) {
                const systemIntegrity = new SystemIntegrityManager();
                systemIntegrity.startMonitoring();
            }
            
            // بدء التحقق من الأذونات
            if (window.PermissionsValidator) {
                const permissionsValidator = new PermissionsValidator();
                permissionsValidator.startComprehensiveValidation();
            }
            
            // إعداد مراقبة الأحداث
            this.setupEventMonitoring();
            
            console.log('✅ تم بدء المهام بعد التهيئة');
            
        } catch (error) {
            console.error('❌ خطأ في بدء المهام بعد التهيئة:', error);
        }
    }

    // إعداد مراقبة الأحداث
    setupEventMonitoring() {
        try {
            // مراقبة تغيير الاتصال
            window.addEventListener('online', () => {
                console.log('🌐 تم استعادة الاتصال بالإنترنت');
                this.handleConnectionRestored();
            });
            
            window.addEventListener('offline', () => {
                console.log('🌐 تم فقد الاتصال بالإنترنت');
                this.handleConnectionLost();
            });
            
            // مراقبة تغيير الرؤية
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    console.log('👁️ تم استعادة رؤية الصفحة');
                    this.handlePageVisible();
                }
            });
            
            // مراقبة الأخطاء
            window.addEventListener('error', (event) => {
                console.error('❌ خطأ في النظام:', event.error);
                this.handleSystemError(event.error);
            });
            
            console.log('📡 تم إعداد مراقبة الأحداث');
            
        } catch (error) {
            console.error('❌ خطأ في إعداد مراقبة الأحداث:', error);
        }
    }

    // معالجة استعادة الاتصال
    async handleConnectionRestored() {
        try {
            // إعادة تهيئة الأنظمة التي تحتاج للاتصال
            if (window.DeviceManager) {
                const deviceManager = new DeviceManager();
                await deviceManager.reconnectActiveDevices();
            }
        } catch (error) {
            console.error('❌ خطأ في معالجة استعادة الاتصال:', error);
        }
    }

    // معالجة فقد الاتصال
    async handleConnectionLost() {
        try {
            // حفظ البيانات المحلية
            if (window.DeviceManager) {
                const deviceManager = new DeviceManager();
                await deviceManager.saveDevicesToStorage();
            }
        } catch (error) {
            console.error('❌ خطأ في معالجة فقد الاتصال:', error);
        }
    }

    // معالجة استعادة رؤية الصفحة
    async handlePageVisible() {
        try {
            // تحديث حالة الأجهزة
            if (window.DeviceManager) {
                const deviceManager = new DeviceManager();
                deviceManager.refreshDeviceStatus();
            }
            
            // إعادة فحص الأذونات
            if (window.PermissionsPersistenceManager) {
                const persistenceManager = new PermissionsPersistenceManager();
                await persistenceManager.ensureCriticalPermissions();
            }
        } catch (error) {
            console.error('❌ خطأ في معالجة استعادة رؤية الصفحة:', error);
        }
    }

    // معالجة أخطاء النظام
    async handleSystemError(error) {
        try {
            console.error('🚨 معالجة خطأ في النظام:', error);
            
            // تسجيل الخطأ
            this.initializationErrors.push({
                system: 'unknown',
                error: error.message || error
            });
            
            // محاولة الإصلاح التلقائي
            if (window.SystemIntegrityManager) {
                const systemIntegrity = new SystemIntegrityManager();
                await systemIntegrity.performHealthCheck();
            }
        } catch (repairError) {
            console.error('❌ فشل في معالجة خطأ النظام:', repairError);
        }
    }

    // الحصول على تقرير التهيئة
    getInitializationReport() {
        return {
            timestamp: new Date().toISOString(),
            initializedSystems: Array.from(this.initializedSystems),
            initializationErrors: this.initializationErrors,
            isInitializing: this.isInitializing,
            totalSystems: this.initializationQueue.length,
            successRate: this.initializedSystems.size / this.initializationQueue.length
        };
    }

    // تأخير
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// تصدير النظام
window.SystemInitializer = SystemInitializer;

// بدء التهيئة التلقائية عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🚀 بدء التهيئة التلقائية للنظام...');
        
        const systemInitializer = new SystemInitializer();
        const success = await systemInitializer.initializeAllSystems();
        
        if (success) {
            console.log('🎉 تم إكمال التهيئة التلقائية بنجاح');
        } else {
            console.error('💥 فشل في التهيئة التلقائية');
        }
        
    } catch (error) {
        console.error('💥 خطأ في التهيئة التلقائية:', error);
    }
});