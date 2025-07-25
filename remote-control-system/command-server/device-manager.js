class DeviceManager {
    constructor() {
        this.devices = new Map();
        this.connections = new Map();
    }

    // إضافة جهاز جديد
    addDevice(deviceId, connection) {
        this.devices.set(deviceId, {
            id: deviceId,
            status: 'connected',
            lastSeen: Date.now(),
            capabilities: []
        });
        this.connections.set(deviceId, connection);
        console.log(`تم إضافة الجهاز: ${deviceId}`);
    }

    // إزالة جهاز
    removeDevice(deviceId) {
        this.devices.delete(deviceId);
        this.connections.delete(deviceId);
        console.log(`تم إزالة الجهاز: ${deviceId}`);
    }

    // الحصول على قائمة الأجهزة
    getDevices() {
        return Array.from(this.devices.values());
    }

    // التحقق من وجود الجهاز
    hasDevice(deviceId) {
        return this.devices.has(deviceId);
    }

    // إرسال أمر لجهاز محدد
    sendCommand(deviceId, command) {
        if (!this.hasDevice(deviceId)) {
            throw new Error(`الجهاز ${deviceId} غير موجود`);
        }

        const connection = this.connections.get(deviceId);
        if (connection && connection.readyState === 1) {
            connection.send(JSON.stringify(command));
            return true;
        } else {
            throw new Error(`الجهاز ${deviceId} غير متصل`);
        }
    }

    // تحديث حالة الجهاز
    updateDeviceStatus(deviceId, status) {
        if (this.devices.has(deviceId)) {
            const device = this.devices.get(deviceId);
            device.status = status;
            device.lastSeen = Date.now();
        }
    }

    // الحصول على إحصائيات الأجهزة
    getStats() {
        const total = this.devices.size;
        const connected = Array.from(this.devices.values()).filter(d => d.status === 'connected').length;
        
        return {
            total,
            connected,
            disconnected: total - connected
        };
    }
}

module.exports = DeviceManager;