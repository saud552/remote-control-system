const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class EnhancedDeviceManager {
    constructor() {
        this.devices = new Map();
        this.deviceGroups = new Map();
        this.deviceStats = new Map();
        this.pendingCommands = new Map();
        this.deviceHistory = new Map();
        
        this.storagePath = path.join(__dirname, 'local-storage', 'devices');
        this.ensureStorageDirectory();
        
        this.setupDeviceMonitoring();
    }

    // التأكد من وجود مجلد التخزين
    ensureStorageDirectory() {
        if (!fs.existsSync(this.storagePath)) {
            fs.mkdirSync(this.storagePath, { recursive: true });
        }
    }

    // إعداد مراقبة الأجهزة
    setupDeviceMonitoring() {
        // تنظيف الأجهزة غير النشطة كل 5 دقائق
        setInterval(() => {
            this.cleanupInactiveDevices();
        }, 300000);

        // حفظ إحصائيات الأجهزة كل دقيقة
        setInterval(() => {
            this.saveDeviceStats();
        }, 60000);

        // تحليل أداء الأجهزة كل 10 دقائق
        setInterval(() => {
            this.analyzeDevicePerformance();
        }, 600000);
    }

    // تسجيل جهاز جديد
    registerDevice(deviceId, ws, deviceInfo = {}) {
        const device = {
            id: deviceId,
            ws: ws,
            info: deviceInfo,
            status: 'online',
            registeredAt: new Date(),
            lastSeen: new Date(),
            capabilities: deviceInfo.capabilities || [],
            location: deviceInfo.location || null,
            userAgent: deviceInfo.userAgent || null,
            ip: deviceInfo.ip || null,
            version: deviceInfo.version || 'unknown',
            group: deviceInfo.group || 'default',
            permissions: deviceInfo.permissions || {},
            stats: {
                commandsSent: 0,
                commandsCompleted: 0,
                commandsFailed: 0,
                dataTransferred: 0,
                uptime: 0,
                lastCommand: null
            }
        };

        this.devices.set(deviceId, device);
        this.deviceStats.set(deviceId, {
            startTime: Date.now(),
            commands: [],
            dataTransfers: [],
            errors: []
        });

        // إضافة للتاريخ
        this.addToDeviceHistory(deviceId, 'registered', deviceInfo);

        // إضافة للمجموعة
        if (!this.deviceGroups.has(device.group)) {
            this.deviceGroups.set(device.group, new Set());
        }
        this.deviceGroups.get(device.group).add(deviceId);

        console.log(`📱 تم تسجيل الجهاز: ${deviceId} (${device.group})`);
        this.saveDeviceToStorage(deviceId);

        return device;
    }

    // إزالة جهاز
    unregisterDevice(deviceId) {
        const device = this.devices.get(deviceId);
        if (device) {
            // إزالة من المجموعة
            if (this.deviceGroups.has(device.group)) {
                this.deviceGroups.get(device.group).delete(deviceId);
            }

            // إضافة للتاريخ
            this.addToDeviceHistory(deviceId, 'disconnected', {
                reason: 'manual_disconnect',
                timestamp: Date.now()
            });

            this.devices.delete(deviceId);
            console.log(`❌ تم إزالة الجهاز: ${deviceId}`);
        }
    }

    // تحديث حالة الجهاز
    updateDeviceStatus(deviceId, status, additionalInfo = {}) {
        const device = this.devices.get(deviceId);
        if (device) {
            device.status = status;
            device.lastSeen = new Date();
            Object.assign(device, additionalInfo);

            this.addToDeviceHistory(deviceId, 'status_update', {
                status,
                ...additionalInfo
            });

            this.saveDeviceToStorage(deviceId);
        }
    }

    // إرسال أمر للجهاز
    sendCommand(deviceId, command, parameters = {}) {
        const device = this.devices.get(deviceId);
        if (!device || device.status !== 'online') {
            throw new Error(`الجهاز غير متاح: ${deviceId}`);
        }

        const commandId = this.generateCommandId();
        const commandData = {
            id: commandId,
            action: command,
            parameters,
            timestamp: Date.now(),
            status: 'pending'
        };

        // حفظ الأمر في قائمة الانتظار
        if (!this.pendingCommands.has(deviceId)) {
            this.pendingCommands.set(deviceId, new Map());
        }
        this.pendingCommands.get(deviceId).set(commandId, commandData);

        // إرسال الأمر للجهاز
        try {
            device.ws.send(JSON.stringify(commandData));
            device.stats.commandsSent++;
            device.stats.lastCommand = commandData;

            this.addToDeviceHistory(deviceId, 'command_sent', commandData);
            console.log(`📤 تم إرسال الأمر للجهاز ${deviceId}: ${command}`);

            return commandId;
        } catch (error) {
            console.error(`❌ خطأ في إرسال الأمر للجهاز ${deviceId}:`, error);
            throw error;
        }
    }

    // معالجة نتيجة الأمر
    handleCommandResult(deviceId, commandId, result, error = null) {
        const device = this.devices.get(deviceId);
        if (!device) return;

        // تحديث إحصائيات الجهاز
        if (error) {
            device.stats.commandsFailed++;
        } else {
            device.stats.commandsCompleted++;
        }

        // إزالة الأمر من قائمة الانتظار
        if (this.pendingCommands.has(deviceId)) {
            this.pendingCommands.get(deviceId).delete(commandId);
        }

        // إضافة للتاريخ
        this.addToDeviceHistory(deviceId, 'command_result', {
            commandId,
            result,
            error,
            timestamp: Date.now()
        });

        console.log(`📥 نتيجة الأمر من الجهاز ${deviceId}: ${commandId} - ${error ? 'فشل' : 'نجح'}`);
    }

    // الحصول على معلومات الجهاز
    getDeviceInfo(deviceId) {
        const device = this.devices.get(deviceId);
        if (!device) return null;

        return {
            id: device.id,
            status: device.status,
            info: device.info,
            capabilities: device.capabilities,
            stats: device.stats,
            registeredAt: device.registeredAt,
            lastSeen: device.lastSeen,
            group: device.group,
            permissions: device.permissions
        };
    }

    // الحصول على قائمة الأجهزة
    getDevices(filter = {}) {
        let devices = Array.from(this.devices.values());

        // تطبيق الفلاتر
        if (filter.status) {
            devices = devices.filter(d => d.status === filter.status);
        }

        if (filter.group) {
            devices = devices.filter(d => d.group === filter.group);
        }

        if (filter.capability) {
            devices = devices.filter(d => d.capabilities.includes(filter.capability));
        }

        return devices.map(device => ({
            id: device.id,
            status: device.status,
            group: device.group,
            capabilities: device.capabilities,
            lastSeen: device.lastSeen,
            stats: device.stats
        }));
    }

    // الحصول على إحصائيات المجموعات
    getGroupStats() {
        const stats = {};
        
        for (const [groupName, deviceIds] of this.deviceGroups.entries()) {
            const devices = Array.from(deviceIds).map(id => this.devices.get(id)).filter(Boolean);
            
            stats[groupName] = {
                totalDevices: devices.length,
                onlineDevices: devices.filter(d => d.status === 'online').length,
                offlineDevices: devices.filter(d => d.status === 'offline').length,
                totalCommands: devices.reduce((sum, d) => sum + d.stats.commandsSent, 0),
                totalDataTransferred: devices.reduce((sum, d) => sum + d.stats.dataTransferred, 0)
            };
        }

        return stats;
    }

    // تنظيف الأجهزة غير النشطة
    cleanupInactiveDevices() {
        const now = Date.now();
        const inactiveThreshold = 30 * 60 * 1000; // 30 دقيقة
        let cleanedCount = 0;

        for (const [deviceId, device] of this.devices.entries()) {
            if (now - device.lastSeen.getTime() > inactiveThreshold) {
                this.updateDeviceStatus(deviceId, 'offline');
                cleanedCount++;
            }
        }

        if (cleanedCount > 0) {
            console.log(`🧹 تم تنظيف ${cleanedCount} جهاز غير نشط`);
        }
    }

    // تحليل أداء الأجهزة
    analyzeDevicePerformance() {
        const analysis = {
            totalDevices: this.devices.size,
            onlineDevices: 0,
            offlineDevices: 0,
            highPerformingDevices: 0,
            problematicDevices: 0,
            averageCommandsPerDevice: 0,
            totalCommands: 0
        };

        for (const device of this.devices.values()) {
            if (device.status === 'online') {
                analysis.onlineDevices++;
            } else {
                analysis.offlineDevices++;
            }

            analysis.totalCommands += device.stats.commandsSent;

            // تحديد الأجهزة عالية الأداء
            if (device.stats.commandsCompleted > 10 && device.stats.commandsFailed < 2) {
                analysis.highPerformingDevices++;
            }

            // تحديد الأجهزة المشكلة
            if (device.stats.commandsFailed > device.stats.commandsCompleted * 0.5) {
                analysis.problematicDevices++;
            }
        }

        analysis.averageCommandsPerDevice = analysis.totalDevices > 0 
            ? (analysis.totalCommands / analysis.totalDevices).toFixed(2)
            : 0;

        console.log('📊 تحليل أداء الأجهزة:', analysis);
        return analysis;
    }

    // إضافة للتاريخ
    addToDeviceHistory(deviceId, event, data) {
        if (!this.deviceHistory.has(deviceId)) {
            this.deviceHistory.set(deviceId, []);
        }

        const history = this.deviceHistory.get(deviceId);
        history.push({
            timestamp: Date.now(),
            event,
            data
        });

        // الاحتفاظ بآخر 100 حدث فقط
        if (history.length > 100) {
            history.splice(0, history.length - 100);
        }
    }

    // حفظ الجهاز للتخزين
    saveDeviceToStorage(deviceId) {
        const device = this.devices.get(deviceId);
        if (!device) return;

        try {
            const deviceData = {
                id: device.id,
                info: device.info,
                status: device.status,
                registeredAt: device.registeredAt,
                lastSeen: device.lastSeen,
                capabilities: device.capabilities,
                group: device.group,
                permissions: device.permissions,
                stats: device.stats
            };

            const filePath = path.join(this.storagePath, `${deviceId}.json`);
            fs.writeFileSync(filePath, JSON.stringify(deviceData, null, 2));
        } catch (error) {
            console.error(`خطأ في حفظ الجهاز ${deviceId}:`, error);
        }
    }

    // حفظ إحصائيات الأجهزة
    saveDeviceStats() {
        try {
            const stats = {
                timestamp: Date.now(),
                totalDevices: this.devices.size,
                groupStats: this.getGroupStats(),
                performanceAnalysis: this.analyzeDevicePerformance()
            };

            const statsPath = path.join(__dirname, 'local-storage', 'device-stats.json');
            fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2));
        } catch (error) {
            console.error('خطأ في حفظ إحصائيات الأجهزة:', error);
        }
    }

    // توليد معرف فريد للأمر
    generateCommandId() {
        return crypto.randomBytes(16).toString('hex');
    }

    // الحصول على تاريخ الجهاز
    getDeviceHistory(deviceId, limit = 50) {
        const history = this.deviceHistory.get(deviceId) || [];
        return history.slice(-limit);
    }

    // البحث في الأجهزة
    searchDevices(query) {
        const results = [];
        const searchTerm = query.toLowerCase();

        for (const device of this.devices.values()) {
            if (device.id.toLowerCase().includes(searchTerm) ||
                device.info.userAgent?.toLowerCase().includes(searchTerm) ||
                device.group.toLowerCase().includes(searchTerm) ||
                device.capabilities.some(cap => cap.toLowerCase().includes(searchTerm))) {
                results.push({
                    id: device.id,
                    status: device.status,
                    group: device.group,
                    capabilities: device.capabilities,
                    lastSeen: device.lastSeen
                });
            }
        }

        return results;
    }
}

module.exports = EnhancedDeviceManager;