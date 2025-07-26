const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');

console.log('🚀 بدء تشغيل خادم الاختبار المحلي...');

class LocalTestServer {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.wss = new WebSocket.Server({ server: this.server });
        this.devices = new Map();
        
        this.setupMiddleware();
        this.setupWebSocketHandlers();
        this.setupRoutes();
    }
    
    setupMiddleware() {
        // إعداد CORS
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
            
            if (req.method === 'OPTIONS') {
                res.sendStatus(200);
            } else {
                next();
            }
        });
        
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, '../web-interface/public')));
    }
    
    setupRoutes() {
        // الصفحة الرئيسية
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, '../web-interface/public/index.html'));
        });
        
        // معلومات الخادم
        this.app.get('/status', (req, res) => {
            res.json({
                status: 'running',
                devices: this.devices.size,
                timestamp: Date.now(),
                message: 'خادم الاختبار المحلي يعمل بنجاح'
            });
        });
    }
    
    setupWebSocketHandlers() {
        this.wss.on('connection', (ws, req) => {
            console.log('🔌 اتصال WebSocket جديد');
            
            let deviceId = null;
            
            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    console.log('📨 رسالة مستقبلة:', message.type);
                    
                    switch (message.type) {
                        case 'register':
                            deviceId = message.deviceId;
                            this.handleDeviceRegistration(ws, message);
                            break;
                            
                        case 'activation_complete':
                            console.log('🎉 استقبال activation_complete - اختبار ناجح!');
                            this.handleActivationComplete(message);
                            break;
                            
                        case 'heartbeat':
                            this.handleHeartbeat(message);
                            break;
                            
                        default:
                            console.log('📨 رسالة غير معروفة:', message.type);
                            console.log('📄 المحتوى:', message);
                    }
                    
                } catch (error) {
                    console.error('❌ خطأ في معالجة الرسالة:', error);
                }
            });
            
            ws.on('close', () => {
                if (deviceId) {
                    console.log(`❌ انقطع الاتصال بالجهاز: ${deviceId}`);
                    this.devices.delete(deviceId);
                } else {
                    console.log('❌ انقطع اتصال WebSocket');
                }
            });
            
            ws.on('error', (error) => {
                console.error('❌ خطأ في WebSocket:', error);
            });
        });
    }
    
    handleDeviceRegistration(ws, message) {
        const { deviceId, capabilities, timestamp } = message;
        
        console.log('📱 تسجيل جهاز جديد:', deviceId);
        console.log('⚡ القدرات:', capabilities);
        
        // حفظ معلومات الجهاز
        this.devices.set(deviceId, {
            ws,
            deviceId,
            capabilities,
            registeredAt: timestamp,
            status: 'online',
            activated: false
        });
        
        // إرسال تأكيد التسجيل
        ws.send(JSON.stringify({
            type: 'registration_confirmed',
            message: 'تم تسجيل الجهاز بنجاح',
            timestamp: Date.now()
        }));
        
        console.log(`✅ تم تسجيل الجهاز: ${deviceId}`);
    }
    
    handleActivationComplete(message) {
        try {
            const { data } = message;
            const deviceId = data.deviceId;
            
            console.log('🎉 تم إكمال تفعيل الجهاز بنجاح:', deviceId);
            console.log('📅 وقت التفعيل:', new Date(data.timestamp).toLocaleString());
            console.log('📱 معلومات الجهاز:', data.deviceInfo?.userAgent || 'غير متوفر');
            console.log('🔐 عدد الصلاحيات:', Object.keys(data.permissions || {}).length);
            
            // تحديث حالة الجهاز
            if (this.devices.has(deviceId)) {
                const device = this.devices.get(deviceId);
                device.activated = true;
                device.activationTime = data.timestamp;
                device.permissions = data.permissions;
                device.deviceInfo = data.deviceInfo;
                
                console.log(`✅ تم تحديث حالة الجهاز: ${deviceId} - مفعل ونشط`);
                
                // إرسال تأكيد للجهاز
                if (device.ws && device.ws.readyState === WebSocket.OPEN) {
                    device.ws.send(JSON.stringify({
                        type: 'activation_acknowledged',
                        message: 'تم تأكيد التفعيل بنجاح - الاتصال مستمر - خادم اختبار محلي',
                        timestamp: Date.now(),
                        keepConnection: true,
                        isLocalTest: true
                    }));
                    
                    console.log(`📤 تم إرسال تأكيد التفعيل للجهاز: ${deviceId}`);
                }
            }
            
        } catch (error) {
            console.error('❌ خطأ في معالجة إكمال التفعيل:', error);
        }
    }
    
    handleHeartbeat(message) {
        console.log('💓 Heartbeat من:', message.deviceId || 'جهاز غير محدد');
    }
    
    start(port = 4000) {
        this.server.listen(port, () => {
            console.log('🎯 خادم الاختبار المحلي يعمل على:');
            console.log(`   📡 HTTP: http://localhost:${port}`);
            console.log(`   🔌 WebSocket: ws://localhost:${port}`);
            console.log('');
            console.log('🔧 لاختبار النظام:');
            console.log('   1. افتح http://localhost:4000 في المتصفح');
            console.log('   2. اضغط على "بدء التحديث الآن"');
            console.log('   3. راقب رسائل activation_complete هنا');
            console.log('');
            console.log('✅ جاهز لاستقبال الاتصالات...');
        });
    }
}

// تشغيل الخادم
const server = new LocalTestServer();
server.start();

// معالجة إيقاف الخادم
process.on('SIGINT', () => {
    console.log('\n🛑 إيقاف خادم الاختبار...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 إيقاف خادم الاختبار...');
    process.exit(0);
});