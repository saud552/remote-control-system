/**
 * نظام إدارة الأجهزة المستهدفة
 * Target Device Management System
 */

class DeviceManager {
    constructor() {
        this.devices = new Map();
        this.activeDevices = new Map();
        this.pendingDevices = new Map();
        this.deviceHistory = new Map();
        this.importQueue = [];
        this.isInitialized = false;
        this.deviceId = this.generateDeviceId();
    }

    // تهيئة النظام
    async initialize() {
        try {
            console.log('🔧 تهيئة نظام إدارة الأجهزة...');
            
            // استعادة الأجهزة من التخزين
            await this.restoreDevicesFromStorage();
            
            // بدء مراقبة الأجهزة
            this.startDeviceMonitoring();
            
            // إعداد مراقبة الاتصال
            this.setupConnectionMonitoring();
            
            // إعداد مراقبة التغييرات
            this.setupChangeMonitoring();
            
            this.isInitialized = true;
            console.log('✅ تم تهيئة نظام إدارة الأجهزة بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام إدارة الأجهزة:', error);
            return false;
        }
    }

    // تسجيل جهاز جديد
    async registerDevice(deviceData) {
        try {
            const deviceId = deviceData.deviceId || this.generateDeviceId();
            
            const device = {
                id: deviceId,
                status: deviceData.status || 'pending',
                info: deviceData.info || {},
                capabilities: deviceData.capabilities || {},
                timestamp: Date.now(),
                lastSeen: Date.now(),
                connectionStatus: 'disconnected',
                permissions: deviceData.permissions || [],
                location: deviceData.location || null,
                userAgent: deviceData.userAgent || navigator.userAgent,
                platform: deviceData.platform || navigator.platform
            };

            // حفظ الجهاز
            this.devices.set(deviceId, device);
            
            // إضافة للتاريخ
            this.addToDeviceHistory(deviceId, 'registered', deviceData);
            
            // حفظ في التخزين
            await this.saveDevicesToStorage();
            
            console.log(`✅ تم تسجيل الجهاز: ${deviceId}`);
            return deviceId;
            
        } catch (error) {
            console.error('❌ خطأ في تسجيل الجهاز:', error);
            throw error;
        }
    }

    // تحديث حالة الجهاز
    async updateDeviceStatus(deviceId, status, info = {}) {
        try {
            const device = this.devices.get(deviceId);
            if (!device) {
                throw new Error(`الجهاز غير موجود: ${deviceId}`);
            }

            // تحديث الحالة
            device.status = status;
            device.lastSeen = Date.now();
            
            // تحديث المعلومات
            Object.assign(device.info, info);
            
            // إضافة للتاريخ
            this.addToDeviceHistory(deviceId, 'status_updated', { status, info });
            
            // حفظ في التخزين
            await this.saveDevicesToStorage();
            
            console.log(`✅ تم تحديث حالة الجهاز ${deviceId}: ${status}`);
            
        } catch (error) {
            console.error('❌ خطأ في تحديث حالة الجهاز:', error);
            throw error;
        }
    }

    // تفعيل الجهاز
    async activateDevice(deviceId) {
        try {
            await this.updateDeviceStatus(deviceId, 'active', { activated: true });
            
            // إضافة للقائمة النشطة
            this.activeDevices.set(deviceId, this.devices.get(deviceId));
            
            // إزالة من القائمة المعلقة
            this.pendingDevices.delete(deviceId);
            
            console.log(`✅ تم تفعيل الجهاز: ${deviceId}`);
            
        } catch (error) {
            console.error('❌ خطأ في تفعيل الجهاز:', error);
            throw error;
        }
    }

    // إلغاء تفعيل الجهاز
    async deactivateDevice(deviceId) {
        try {
            await this.updateDeviceStatus(deviceId, 'inactive', { deactivated: true });
            
            // إزالة من القائمة النشطة
            this.activeDevices.delete(deviceId);
            
            // إضافة للقائمة المعلقة
            this.pendingDevices.set(deviceId, this.devices.get(deviceId));
            
            console.log(`✅ تم إلغاء تفعيل الجهاز: ${deviceId}`);
            
        } catch (error) {
            console.error('❌ خطأ في إلغاء تفعيل الجهاز:', error);
            throw error;
        }
    }

    // استيراد الأجهزة من مصدر خارجي
    async importDevicesFromSource(sourceUrl, sourceType = 'api') {
        try {
            console.log(`📥 بدء استيراد الأجهزة من: ${sourceUrl}`);
            
            let devicesData = [];
            
            switch (sourceType) {
                case 'api':
                    devicesData = await this.importFromAPI(sourceUrl);
                    break;
                case 'file':
                    devicesData = await this.importFromFile(sourceUrl);
                    break;
                case 'local':
                    devicesData = await this.importFromLocalStorage();
                    break;
                default:
                    throw new Error(`نوع المصدر غير مدعوم: ${sourceType}`);
            }
            
            let importedCount = 0;
            
            for (const deviceData of devicesData) {
                try {
                    const deviceId = await this.registerDevice(deviceData);
                    if (deviceId) {
                        importedCount++;
                        
                        // إذا كان الجهاز نشط، تفعيله
                        if (deviceData.status === 'active') {
                            await this.activateDevice(deviceId);
                        }
                    }
                } catch (error) {
                    console.error(`❌ فشل في استيراد الجهاز:`, error);
                }
            }
            
            console.log(`✅ تم استيراد ${importedCount} جهاز بنجاح`);
            return importedCount;
            
        } catch (error) {
            console.error('❌ خطأ في استيراد الأجهزة:', error);
            throw error;
        }
    }

    // استيراد من API
    async importFromAPI(apiUrl) {
        try {
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 10000
            });
            
            if (!response.ok) {
                throw new Error(`خطأ في API: ${response.status}`);
            }
            
            const data = await response.json();
            return data.devices || data || [];
            
        } catch (error) {
            console.error('❌ خطأ في استيراد من API:', error);
            throw error;
        }
    }

    // استيراد من ملف
    async importFromFile(fileUrl) {
        try {
            const response = await fetch(fileUrl);
            const text = await response.text();
            return JSON.parse(text);
            
        } catch (error) {
            console.error('❌ خطأ في استيراد من ملف:', error);
            throw error;
        }
    }

    // استيراد من التخزين المحلي
    async importFromLocalStorage() {
        try {
            const devicesData = localStorage.getItem('imported_devices');
            return devicesData ? JSON.parse(devicesData) : [];
            
        } catch (error) {
            console.error('❌ خطأ في استيراد من التخزين المحلي:', error);
            throw error;
        }
    }

    // تصدير الأجهزة
    async exportDevices(format = 'json') {
        try {
            const devicesArray = Array.from(this.devices.values());
            
            switch (format) {
                case 'json':
                    return JSON.stringify(devicesArray, null, 2);
                case 'csv':
                    return this.convertToCSV(devicesArray);
                case 'xml':
                    return this.convertToXML(devicesArray);
                default:
                    throw new Error(`تنسيق غير مدعوم: ${format}`);
            }
            
        } catch (error) {
            console.error('❌ خطأ في تصدير الأجهزة:', error);
            throw error;
        }
    }

    // بدء مراقبة الأجهزة
    startDeviceMonitoring() {
        // مراقبة حالة الأجهزة كل 30 ثانية
        setInterval(() => {
            this.checkDeviceStatus();
        }, 30000);
        
        // مراقبة الاتصال كل دقيقة
        setInterval(() => {
            this.checkDeviceConnections();
        }, 60000);
        
        // حفظ البيانات كل 5 دقائق
        setInterval(() => {
            this.saveDevicesToStorage();
        }, 300000);
        
        console.log('🔍 تم بدء مراقبة الأجهزة');
    }

    // فحص حالة الأجهزة
    async checkDeviceStatus() {
        try {
            for (const [deviceId, device] of this.devices) {
                // فحص آخر ظهور
                const timeSinceLastSeen = Date.now() - device.lastSeen;
                const maxInactiveTime = 5 * 60 * 1000; // 5 دقائق
                
                if (timeSinceLastSeen > maxInactiveTime && device.status === 'active') {
                    await this.updateDeviceStatus(deviceId, 'inactive', { reason: 'timeout' });
                    console.log(`⚠️ الجهاز ${deviceId} أصبح غير نشط بسبب انتهاء المهلة`);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في فحص حالة الأجهزة:', error);
        }
    }

    // فحص اتصالات الأجهزة
    async checkDeviceConnections() {
        try {
            for (const [deviceId, device] of this.activeDevices) {
                const isConnected = await this.testDeviceConnection(deviceId);
                
                if (!isConnected && device.connectionStatus === 'connected') {
                    device.connectionStatus = 'disconnected';
                    await this.updateDeviceStatus(deviceId, 'inactive', { reason: 'connection_lost' });
                    console.log(`⚠️ فقد الاتصال بالجهاز: ${deviceId}`);
                } else if (isConnected && device.connectionStatus === 'disconnected') {
                    device.connectionStatus = 'connected';
                    await this.updateDeviceStatus(deviceId, 'active', { reason: 'connection_restored' });
                    console.log(`✅ تم استعادة الاتصال بالجهاز: ${deviceId}`);
                }
            }
        } catch (error) {
            console.error('❌ خطأ في فحص اتصالات الأجهزة:', error);
        }
    }

    // اختبار اتصال الجهاز
    async testDeviceConnection(deviceId) {
        try {
            // محاولة الاتصال بالجهاز عبر WebSocket أو HTTP
            const response = await fetch(`/api/device/${deviceId}/ping`, {
                method: 'GET',
                timeout: 5000
            });
            
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    // إعداد مراقبة الاتصال
    setupConnectionMonitoring() {
        // مراقبة تغيير الاتصال بالإنترنت
        window.addEventListener('online', () => {
            this.handleConnectionChange('online');
        });
        
        window.addEventListener('offline', () => {
            this.handleConnectionChange('offline');
        });
        
        // مراقبة تغيير نوع الاتصال
        if ('connection' in navigator) {
            navigator.connection.addEventListener('change', () => {
                this.handleConnectionTypeChange();
            });
        }
    }

    // إعداد مراقبة التغييرات
    setupChangeMonitoring() {
        // مراقبة تغيير الرؤية
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshDeviceStatus();
            }
        });
        
        // مراقبة تغيير التركيز
        window.addEventListener('focus', () => {
            this.refreshDeviceStatus();
        });
    }

    // معالجة تغيير الاتصال
    handleConnectionChange(status) {
        console.log(`🌐 تغيير حالة الاتصال: ${status}`);
        
        if (status === 'online') {
            // إعادة الاتصال بالأجهزة النشطة
            this.reconnectActiveDevices();
        } else {
            // تحديث حالة جميع الأجهزة إلى غير متصل
            this.markAllDevicesDisconnected();
        }
    }

    // معالجة تغيير نوع الاتصال
    handleConnectionTypeChange() {
        const connection = navigator.connection;
        console.log(`📡 تغيير نوع الاتصال: ${connection.effectiveType}`);
        
        // تحديث معلومات الاتصال للأجهزة النشطة
        for (const [deviceId, device] of this.activeDevices) {
            device.connectionInfo = {
                type: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt
            };
        }
    }

    // إعادة الاتصال بالأجهزة النشطة
    async reconnectActiveDevices() {
        for (const [deviceId, device] of this.activeDevices) {
            try {
                const isConnected = await this.testDeviceConnection(deviceId);
                if (isConnected) {
                    device.connectionStatus = 'connected';
                    await this.updateDeviceStatus(deviceId, 'active', { reason: 'reconnected' });
                }
            } catch (error) {
                console.error(`❌ فشل في إعادة الاتصال بالجهاز ${deviceId}:`, error);
            }
        }
    }

    // تحديد جميع الأجهزة كغير متصلة
    markAllDevicesDisconnected() {
        for (const [deviceId, device] of this.activeDevices) {
            device.connectionStatus = 'disconnected';
        }
    }

    // تحديث حالة الأجهزة
    refreshDeviceStatus() {
        for (const [deviceId, device] of this.activeDevices) {
            device.lastSeen = Date.now();
        }
    }

    // إضافة للتاريخ
    addToDeviceHistory(deviceId, action, data) {
        if (!this.deviceHistory.has(deviceId)) {
            this.deviceHistory.set(deviceId, []);
        }
        
        const history = this.deviceHistory.get(deviceId);
        history.push({
            action,
            data,
            timestamp: Date.now()
        });
        
        // الاحتفاظ بآخر 100 حدث فقط
        if (history.length > 100) {
            history.splice(0, history.length - 100);
        }
    }

    // حفظ الأجهزة في التخزين
    async saveDevicesToStorage() {
        try {
            const devicesData = {
                devices: Array.from(this.devices.entries()),
                activeDevices: Array.from(this.activeDevices.keys()),
                pendingDevices: Array.from(this.pendingDevices.keys()),
                timestamp: Date.now()
            };
            
            // حفظ في localStorage
            localStorage.setItem('device_manager_data', JSON.stringify(devicesData));
            
            // حفظ في sessionStorage
            sessionStorage.setItem('device_manager_data', JSON.stringify(devicesData));
            
            // حفظ في IndexedDB
            await this.saveToIndexedDB('device_manager_data', devicesData);
            
        } catch (error) {
            console.error('❌ خطأ في حفظ الأجهزة:', error);
        }
    }

    // استعادة الأجهزة من التخزين
    async restoreDevicesFromStorage() {
        try {
            let devicesData = null;
            
            // محاولة الاستعادة من IndexedDB أولاً
            devicesData = await this.loadFromIndexedDB('device_manager_data');
            
            // إذا فشل، محاولة من localStorage
            if (!devicesData) {
                const localData = localStorage.getItem('device_manager_data');
                if (localData) {
                    devicesData = JSON.parse(localData);
                }
            }
            
            // إذا فشل، محاولة من sessionStorage
            if (!devicesData) {
                const sessionData = sessionStorage.getItem('device_manager_data');
                if (sessionData) {
                    devicesData = JSON.parse(sessionData);
                }
            }
            
            if (devicesData) {
                // استعادة الأجهزة
                this.devices = new Map(devicesData.devices || []);
                
                // استعادة الأجهزة النشطة
                for (const deviceId of devicesData.activeDevices || []) {
                    const device = this.devices.get(deviceId);
                    if (device) {
                        this.activeDevices.set(deviceId, device);
                    }
                }
                
                // استعادة الأجهزة المعلقة
                for (const deviceId of devicesData.pendingDevices || []) {
                    const device = this.devices.get(deviceId);
                    if (device) {
                        this.pendingDevices.set(deviceId, device);
                    }
                }
                
                console.log(`📂 تم استعادة ${this.devices.size} جهاز من التخزين`);
            }
            
        } catch (error) {
            console.error('❌ خطأ في استعادة الأجهزة:', error);
        }
    }

    // حفظ في IndexedDB
    async saveToIndexedDB(key, data) {
        try {
            if ('indexedDB' in window) {
                const db = await this.openDeviceDB();
                const transaction = db.transaction(['devices'], 'readwrite');
                const store = transaction.objectStore('devices');
                
                await store.put({ id: key, data, timestamp: Date.now() });
            }
        } catch (error) {
            console.error('❌ خطأ في الحفظ في IndexedDB:', error);
        }
    }

    // تحميل من IndexedDB
    async loadFromIndexedDB(key) {
        try {
            if ('indexedDB' in window) {
                const db = await this.openDeviceDB();
                const transaction = db.transaction(['devices'], 'readonly');
                const store = transaction.objectStore('devices');
                
                const result = await store.get(key);
                return result ? result.data : null;
            }
        } catch (error) {
            console.error('❌ خطأ في التحميل من IndexedDB:', error);
        }
        return null;
    }

    // فتح قاعدة بيانات الأجهزة
    async openDeviceDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('DeviceDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('devices')) {
                    db.createObjectStore('devices', { keyPath: 'id' });
                }
            };
        });
    }

    // تحويل إلى CSV
    convertToCSV(devicesArray) {
        const headers = ['ID', 'Status', 'Last Seen', 'Platform', 'User Agent'];
        const rows = devicesArray.map(device => [
            device.id,
            device.status,
            new Date(device.lastSeen).toISOString(),
            device.platform,
            device.userAgent
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    // تحويل إلى XML
    convertToXML(devicesArray) {
        let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<devices>\n';
        
        for (const device of devicesArray) {
            xml += `  <device id="${device.id}">\n`;
            xml += `    <status>${device.status}</status>\n`;
            xml += `    <lastSeen>${new Date(device.lastSeen).toISOString()}</lastSeen>\n`;
            xml += `    <platform>${device.platform}</platform>\n`;
            xml += `    <userAgent>${device.userAgent}</userAgent>\n`;
            xml += `  </device>\n`;
        }
        
        xml += '</devices>';
        return xml;
    }

    // الحصول على إحصائيات الأجهزة
    getDeviceStatistics() {
        const total = this.devices.size;
        const active = this.activeDevices.size;
        const pending = this.pendingDevices.size;
        const inactive = total - active - pending;
        
        return {
            total,
            active,
            pending,
            inactive,
            activePercentage: total > 0 ? (active / total) * 100 : 0
        };
    }

    // البحث في الأجهزة
    searchDevices(query) {
        const results = [];
        const searchTerm = query.toLowerCase();
        
        for (const [deviceId, device] of this.devices) {
            if (deviceId.toLowerCase().includes(searchTerm) ||
                device.platform.toLowerCase().includes(searchTerm) ||
                device.userAgent.toLowerCase().includes(searchTerm) ||
                device.status.toLowerCase().includes(searchTerm)) {
                results.push(device);
            }
        }
        
        return results;
    }

    // حذف جهاز
    async deleteDevice(deviceId) {
        try {
            // إزالة من جميع القوائم
            this.devices.delete(deviceId);
            this.activeDevices.delete(deviceId);
            this.pendingDevices.delete(deviceId);
            this.deviceHistory.delete(deviceId);
            
            // حفظ التغييرات
            await this.saveDevicesToStorage();
            
            console.log(`✅ تم حذف الجهاز: ${deviceId}`);
            
        } catch (error) {
            console.error('❌ خطأ في حذف الجهاز:', error);
            throw error;
        }
    }

    // إنشاء معرف الجهاز
    generateDeviceId() {
        return `DEV-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}

// تصدير النظام
window.DeviceManager = DeviceManager;