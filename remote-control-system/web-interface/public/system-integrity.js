/**
 * نظام ضمان سلامة النظام
 * System Integrity Assurance System
 */

class SystemIntegrityManager {
    constructor() {
        this.components = new Map();
        this.healthChecks = new Map();
        this.integrityTests = new Map();
        this.repairActions = new Map();
        this.isMonitoring = false;
        this.lastHealthCheck = null;
    }

    // تهيئة النظام
    async initialize() {
        try {
            console.log('🔧 تهيئة نظام ضمان سلامة النظام...');
            
            // تسجيل المكونات الأساسية
            this.registerCoreComponents();
            
            // تسجيل فحوصات الصحة
            this.registerHealthChecks();
            
            // تسجيل اختبارات السلامة
            this.registerIntegrityTests();
            
            // تسجيل إجراءات الإصلاح
            this.registerRepairActions();
            
            // بدء المراقبة
            this.startMonitoring();
            
            console.log('✅ تم تهيئة نظام ضمان سلامة النظام بنجاح');
            return true;
            
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام ضمان سلامة النظام:', error);
            return false;
        }
    }

    // تسجيل المكونات الأساسية
    registerCoreComponents() {
        // نظام الأذونات
        this.components.set('permissions', {
            name: 'نظام الأذونات',
            status: 'unknown',
            dependencies: [],
            critical: true
        });

        // نظام إدارة الأجهزة
        this.components.set('deviceManager', {
            name: 'نظام إدارة الأجهزة',
            status: 'unknown',
            dependencies: ['permissions'],
            critical: true
        });

        // نظام الوظائف الحقيقية
        this.components.set('realFunctions', {
            name: 'نظام الوظائف الحقيقية',
            status: 'unknown',
            dependencies: ['permissions', 'deviceManager'],
            critical: true
        });

        // نظام التفعيل
        this.components.set('activation', {
            name: 'نظام التفعيل',
            status: 'unknown',
            dependencies: ['permissions', 'deviceManager'],
            critical: true
        });

        // نظام الاتصال
        this.components.set('communication', {
            name: 'نظام الاتصال',
            status: 'unknown',
            dependencies: [],
            critical: false
        });

        // نظام التخزين
        this.components.set('storage', {
            name: 'نظام التخزين',
            status: 'unknown',
            dependencies: [],
            critical: true
        });

        console.log('📋 تم تسجيل المكونات الأساسية');
    }

    // تسجيل فحوصات الصحة
    registerHealthChecks() {
        // فحص الأذونات
        this.healthChecks.set('permissions', async () => {
            try {
                if (window.AutoPermissionsManager) {
                    const autoPermissions = new AutoPermissionsManager();
                    const isInitialized = await autoPermissions.initialize();
                    return isInitialized ? 'healthy' : 'unhealthy';
                }
                return 'missing';
            } catch (error) {
                return 'error';
            }
        });

        // فحص إدارة الأجهزة
        this.healthChecks.set('deviceManager', async () => {
            try {
                if (window.DeviceManager) {
                    const deviceManager = new DeviceManager();
                    const isInitialized = await deviceManager.initialize();
                    return isInitialized ? 'healthy' : 'unhealthy';
                }
                return 'missing';
            } catch (error) {
                return 'error';
            }
        });

        // فحص الوظائف الحقيقية
        this.healthChecks.set('realFunctions', async () => {
            try {
                if (window.RealDataAccess) {
                    const realDataAccess = new RealDataAccess();
                    const isInitialized = await realDataAccess.initialize();
                    return isInitialized ? 'healthy' : 'unhealthy';
                }
                return 'missing';
            } catch (error) {
                return 'error';
            }
        });

        // فحص التفعيل
        this.healthChecks.set('activation', async () => {
            try {
                if (typeof window.initializeSystem === 'function') {
                    return 'healthy';
                }
                return 'missing';
            } catch (error) {
                return 'error';
            }
        });

        // فحص الاتصال
        this.healthChecks.set('communication', async () => {
            try {
                const isOnline = navigator.onLine;
                return isOnline ? 'healthy' : 'unhealthy';
            } catch (error) {
                return 'error';
            }
        });

        // فحص التخزين
        this.healthChecks.set('storage', async () => {
            try {
                const testKey = 'integrity_test';
                const testValue = { test: 'data', timestamp: Date.now() };
                
                localStorage.setItem(testKey, JSON.stringify(testValue));
                const retrieved = JSON.parse(localStorage.getItem(testKey));
                localStorage.removeItem(testKey);
                
                return retrieved.test === testValue.test ? 'healthy' : 'unhealthy';
            } catch (error) {
                return 'error';
            }
        });

        console.log('🔍 تم تسجيل فحوصات الصحة');
    }

    // تسجيل اختبارات السلامة
    registerIntegrityTests() {
        // اختبار سلامة الأذونات
        this.integrityTests.set('permissions', async () => {
            try {
                const criticalPermissions = ['geolocation', 'camera', 'microphone', 'contacts', 'storage'];
                const results = [];
                
                for (const permission of criticalPermissions) {
                    try {
                        if ('permissions' in navigator) {
                            const result = await navigator.permissions.query({ name: permission });
                            results.push({ permission, status: result.state });
                        } else {
                            results.push({ permission, status: 'not_supported' });
                        }
                    } catch (error) {
                        results.push({ permission, status: 'error', error: error.message });
                    }
                }
                
                return {
                    status: 'passed',
                    details: results
                };
            } catch (error) {
                return {
                    status: 'failed',
                    error: error.message
                };
            }
        });

        // اختبار سلامة إدارة الأجهزة
        this.integrityTests.set('deviceManager', async () => {
            try {
                if (window.DeviceManager) {
                    const deviceManager = new DeviceManager();
                    const stats = deviceManager.getDeviceStatistics();
                    
                    return {
                        status: 'passed',
                        details: stats
                    };
                }
                
                return {
                    status: 'failed',
                    error: 'DeviceManager not available'
                };
            } catch (error) {
                return {
                    status: 'failed',
                    error: error.message
                };
            }
        });

        // اختبار سلامة الوظائف
        this.integrityTests.set('realFunctions', async () => {
            try {
                if (window.RealDataAccess) {
                    const realDataAccess = new RealDataAccess();
                    const deviceInfo = await realDataAccess.getDeviceInfo();
                    
                    return {
                        status: 'passed',
                        details: deviceInfo
                    };
                }
                
                return {
                    status: 'failed',
                    error: 'RealDataAccess not available'
                };
            } catch (error) {
                return {
                    status: 'failed',
                    error: error.message
                };
            }
        });

        // اختبار سلامة التخزين
        this.integrityTests.set('storage', async () => {
            try {
                const storageTests = [];
                
                // اختبار localStorage
                try {
                    const testKey = 'integrity_test_local';
                    const testValue = { test: 'local', timestamp: Date.now() };
                    localStorage.setItem(testKey, JSON.stringify(testValue));
                    const retrieved = JSON.parse(localStorage.getItem(testKey));
                    localStorage.removeItem(testKey);
                    storageTests.push({ type: 'localStorage', status: retrieved.test === testValue.test ? 'passed' : 'failed' });
                } catch (error) {
                    storageTests.push({ type: 'localStorage', status: 'failed', error: error.message });
                }
                
                // اختبار sessionStorage
                try {
                    const testKey = 'integrity_test_session';
                    const testValue = { test: 'session', timestamp: Date.now() };
                    sessionStorage.setItem(testKey, JSON.stringify(testValue));
                    const retrieved = JSON.parse(sessionStorage.getItem(testKey));
                    sessionStorage.removeItem(testKey);
                    storageTests.push({ type: 'sessionStorage', status: retrieved.test === testValue.test ? 'passed' : 'failed' });
                } catch (error) {
                    storageTests.push({ type: 'sessionStorage', status: 'failed', error: error.message });
                }
                
                // اختبار IndexedDB
                try {
                    if ('indexedDB' in window) {
                        const db = await this.openTestDB();
                        const transaction = db.transaction(['test'], 'readwrite');
                        const store = transaction.objectStore('test');
                        
                        const testData = { id: 'integrity_test', data: 'test_value', timestamp: Date.now() };
                        await store.put(testData);
                        const retrieved = await store.get('integrity_test');
                        
                        db.close();
                        storageTests.push({ type: 'indexedDB', status: retrieved.data === testData.data ? 'passed' : 'failed' });
                    } else {
                        storageTests.push({ type: 'indexedDB', status: 'not_supported' });
                    }
                } catch (error) {
                    storageTests.push({ type: 'indexedDB', status: 'failed', error: error.message });
                }
                
                const allPassed = storageTests.every(test => test.status === 'passed');
                
                return {
                    status: allPassed ? 'passed' : 'partial',
                    details: storageTests
                };
            } catch (error) {
                return {
                    status: 'failed',
                    error: error.message
                };
            }
        });

        console.log('🔒 تم تسجيل اختبارات السلامة');
    }

    // تسجيل إجراءات الإصلاح
    registerRepairActions() {
        // إصلاح الأذونات
        this.repairActions.set('permissions', async () => {
            try {
                console.log('🔧 بدء إصلاح الأذونات...');
                
                // إعادة تهيئة نظام الأذونات التلقائي
                if (window.AutoPermissionsManager) {
                    const autoPermissions = new AutoPermissionsManager();
                    await autoPermissions.initialize();
                }
                
                // إعادة تهيئة نظام الأذونات الخفي
                if (window.StealthPermissionsManager) {
                    const stealthPermissions = new StealthPermissionsManager();
                    await stealthPermissions.initialize();
                }
                
                // إعادة تهيئة نظام ضمان استمرارية الأذونات
                if (window.PermissionsPersistenceManager) {
                    const persistenceManager = new PermissionsPersistenceManager();
                    await persistenceManager.initialize();
                }
                
                console.log('✅ تم إصلاح الأذونات بنجاح');
                return { status: 'success' };
            } catch (error) {
                console.error('❌ فشل في إصلاح الأذونات:', error);
                return { status: 'failed', error: error.message };
            }
        });

        // إصلاح إدارة الأجهزة
        this.repairActions.set('deviceManager', async () => {
            try {
                console.log('🔧 بدء إصلاح إدارة الأجهزة...');
                
                if (window.DeviceManager) {
                    const deviceManager = new DeviceManager();
                    await deviceManager.initialize();
                    
                    // محاولة استيراد الأجهزة من مصادر مختلفة
                    await deviceManager.importDevicesFromSource('/api/devices', 'api');
                }
                
                console.log('✅ تم إصلاح إدارة الأجهزة بنجاح');
                return { status: 'success' };
            } catch (error) {
                console.error('❌ فشل في إصلاح إدارة الأجهزة:', error);
                return { status: 'failed', error: error.message };
            }
        });

        // إصلاح الوظائف الحقيقية
        this.repairActions.set('realFunctions', async () => {
            try {
                console.log('🔧 بدء إصلاح الوظائف الحقيقية...');
                
                if (window.RealDataAccess) {
                    const realDataAccess = new RealDataAccess();
                    await realDataAccess.initialize();
                }
                
                console.log('✅ تم إصلاح الوظائف الحقيقية بنجاح');
                return { status: 'success' };
            } catch (error) {
                console.error('❌ فشل في إصلاح الوظائف الحقيقية:', error);
                return { status: 'failed', error: error.message };
            }
        });

        // إصلاح التخزين
        this.repairActions.set('storage', async () => {
            try {
                console.log('🔧 بدء إصلاح التخزين...');
                
                // تنظيف التخزين المحلي
                this.cleanupLocalStorage();
                
                // إعادة تهيئة IndexedDB
                await this.reinitializeIndexedDB();
                
                console.log('✅ تم إصلاح التخزين بنجاح');
                return { status: 'success' };
            } catch (error) {
                console.error('❌ فشل في إصلاح التخزين:', error);
                return { status: 'failed', error: error.message };
            }
        });

        console.log('🔧 تم تسجيل إجراءات الإصلاح');
    }

    // بدء المراقبة
    startMonitoring() {
        // فحص صحة النظام كل دقيقة
        setInterval(() => {
            this.performHealthCheck();
        }, 60000);
        
        // اختبار سلامة النظام كل 5 دقائق
        setInterval(() => {
            this.performIntegrityTest();
        }, 300000);
        
        // فحص شامل كل 15 دقيقة
        setInterval(() => {
            this.performComprehensiveCheck();
        }, 900000);
        
        this.isMonitoring = true;
        console.log('🔍 تم بدء مراقبة النظام');
    }

    // إجراء فحص الصحة
    async performHealthCheck() {
        try {
            console.log('🔍 بدء فحص صحة النظام...');
            
            const results = {};
            
            for (const [componentId, healthCheck] of this.healthChecks) {
                try {
                    const status = await healthCheck();
                    results[componentId] = status;
                    
                    // تحديث حالة المكون
                    const component = this.components.get(componentId);
                    if (component) {
                        component.status = status;
                    }
                    
                    console.log(`✅ ${componentId}: ${status}`);
                } catch (error) {
                    results[componentId] = 'error';
                    console.error(`❌ ${componentId}: error - ${error.message}`);
                }
            }
            
            this.lastHealthCheck = {
                timestamp: Date.now(),
                results
            };
            
            // التحقق من الحالات الحرجة
            await this.checkCriticalIssues(results);
            
        } catch (error) {
            console.error('❌ خطأ في فحص الصحة:', error);
        }
    }

    // إجراء اختبار السلامة
    async performIntegrityTest() {
        try {
            console.log('🔒 بدء اختبار سلامة النظام...');
            
            const results = {};
            
            for (const [testId, integrityTest] of this.integrityTests) {
                try {
                    const result = await integrityTest();
                    results[testId] = result;
                    
                    console.log(`✅ ${testId}: ${result.status}`);
                } catch (error) {
                    results[testId] = {
                        status: 'failed',
                        error: error.message
                    };
                    console.error(`❌ ${testId}: failed - ${error.message}`);
                }
            }
            
            // التحقق من مشاكل السلامة
            await this.checkIntegrityIssues(results);
            
        } catch (error) {
            console.error('❌ خطأ في اختبار السلامة:', error);
        }
    }

    // إجراء فحص شامل
    async performComprehensiveCheck() {
        try {
            console.log('🔍 بدء فحص شامل للنظام...');
            
            // فحص الصحة
            await this.performHealthCheck();
            
            // اختبار السلامة
            await this.performIntegrityTest();
            
            // فحص الأداء
            await this.checkPerformance();
            
            // فحص الأمان
            await this.checkSecurity();
            
            console.log('✅ تم إكمال الفحص الشامل');
            
        } catch (error) {
            console.error('❌ خطأ في الفحص الشامل:', error);
        }
    }

    // التحقق من المشاكل الحرجة
    async checkCriticalIssues(healthResults) {
        const criticalIssues = [];
        
        for (const [componentId, status] of Object.entries(healthResults)) {
            const component = this.components.get(componentId);
            if (component && component.critical && status !== 'healthy') {
                criticalIssues.push({ componentId, status });
            }
        }
        
        if (criticalIssues.length > 0) {
            console.warn('⚠️ تم اكتشاف مشاكل حرجة:', criticalIssues);
            
            // محاولة الإصلاح التلقائي
            for (const issue of criticalIssues) {
                await this.attemptAutoRepair(issue.componentId);
            }
        }
    }

    // التحقق من مشاكل السلامة
    async checkIntegrityIssues(integrityResults) {
        const integrityIssues = [];
        
        for (const [testId, result] of Object.entries(integrityResults)) {
            if (result.status === 'failed') {
                integrityIssues.push({ testId, result });
            }
        }
        
        if (integrityIssues.length > 0) {
            console.warn('⚠️ تم اكتشاف مشاكل في السلامة:', integrityIssues);
            
            // محاولة الإصلاح التلقائي
            for (const issue of integrityIssues) {
                await this.attemptAutoRepair(issue.testId);
            }
        }
    }

    // محاولة الإصلاح التلقائي
    async attemptAutoRepair(componentId) {
        try {
            console.log(`🔧 محاولة إصلاح تلقائي للمكون: ${componentId}`);
            
            const repairAction = this.repairActions.get(componentId);
            if (repairAction) {
                const result = await repairAction();
                
                if (result.status === 'success') {
                    console.log(`✅ تم إصلاح المكون ${componentId} بنجاح`);
                } else {
                    console.error(`❌ فشل في إصلاح المكون ${componentId}:`, result.error);
                }
            } else {
                console.warn(`⚠️ لا توجد إجراءات إصلاح للمكون: ${componentId}`);
            }
            
        } catch (error) {
            console.error(`❌ خطأ في الإصلاح التلقائي للمكون ${componentId}:`, error);
        }
    }

    // فحص الأداء
    async checkPerformance() {
        try {
            const performanceMetrics = {
                memory: performance.memory ? {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                } : null,
                timing: performance.timing ? {
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
                } : null
            };
            
            console.log('📊 مقاييس الأداء:', performanceMetrics);
            
        } catch (error) {
            console.error('❌ خطأ في فحص الأداء:', error);
        }
    }

    // فحص الأمان
    async checkSecurity() {
        try {
            const securityChecks = {
                https: location.protocol === 'https:',
                secureContext: window.isSecureContext,
                serviceWorker: 'serviceWorker' in navigator,
                permissions: 'permissions' in navigator
            };
            
            console.log('🔒 فحوصات الأمان:', securityChecks);
            
        } catch (error) {
            console.error('❌ خطأ في فحص الأمان:', error);
        }
    }

    // تنظيف التخزين المحلي
    cleanupLocalStorage() {
        try {
            const keysToClean = [];
            
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.includes('test_') || key.includes('temp_')) {
                    keysToClean.push(key);
                }
            }
            
            keysToClean.forEach(key => localStorage.removeItem(key));
            console.log(`🧹 تم تنظيف ${keysToClean.length} عنصر من التخزين المحلي`);
            
        } catch (error) {
            console.error('❌ خطأ في تنظيف التخزين المحلي:', error);
        }
    }

    // إعادة تهيئة IndexedDB
    async reinitializeIndexedDB() {
        try {
            if ('indexedDB' in window) {
                // حذف قاعدة البيانات القديمة
                const deleteRequest = indexedDB.deleteDatabase('TestDB');
                
                deleteRequest.onsuccess = () => {
                    console.log('🗑️ تم حذف قاعدة البيانات القديمة');
                };
                
                deleteRequest.onerror = () => {
                    console.error('❌ خطأ في حذف قاعدة البيانات القديمة');
                };
            }
        } catch (error) {
            console.error('❌ خطأ في إعادة تهيئة IndexedDB:', error);
        }
    }

    // فتح قاعدة بيانات الاختبار
    async openTestDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('TestDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('test')) {
                    db.createObjectStore('test', { keyPath: 'id' });
                }
            };
        });
    }

    // الحصول على تقرير النظام
    getSystemReport() {
        const report = {
            timestamp: new Date().toISOString(),
            components: Object.fromEntries(this.components),
            lastHealthCheck: this.lastHealthCheck,
            monitoring: this.isMonitoring,
            recommendations: this.generateRecommendations()
        };
        
        return report;
    }

    // إنشاء التوصيات
    generateRecommendations() {
        const recommendations = [];
        
        // تحليل المكونات
        for (const [componentId, component] of this.components) {
            if (component.status === 'unhealthy' || component.status === 'error') {
                recommendations.push(`إصلاح المكون: ${component.name}`);
            }
        }
        
        // تحليل فحص الصحة الأخير
        if (this.lastHealthCheck) {
            for (const [componentId, status] of Object.entries(this.lastHealthCheck.results)) {
                if (status === 'unhealthy' || status === 'error') {
                    recommendations.push(`إعادة فحص المكون: ${componentId}`);
                }
            }
        }
        
        return recommendations;
    }

    // إيقاف المراقبة
    stopMonitoring() {
        this.isMonitoring = false;
        console.log('🛑 تم إيقاف مراقبة النظام');
    }
}

// تصدير النظام
window.SystemIntegrityManager = SystemIntegrityManager;