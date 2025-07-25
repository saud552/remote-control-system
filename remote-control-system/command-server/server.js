const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// تخزين الأجهزة المتصلة
const connectedDevices = new Map();

wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'register') {
                // تسجيل الجهاز
                connectedDevices.set(data.deviceId, ws);
                console.log(`تم تسجيل الجهاز: ${data.deviceId}`);
                ws.send(JSON.stringify({
                    type: 'status',
                    message: 'تم التسجيل بنجاح'
                }));
            }
        } catch (e) {
            console.error('خطأ في معالجة الرسالة:', e);
        }
    });
    
    ws.on('close', () => {
        // إزالة الجهاز عند انقطاع الاتصال
        for (const [deviceId, socket] of connectedDevices.entries()) {
            if (socket === ws) {
                connectedDevices.delete(deviceId);
                console.log(`انقطع اتصال الجهاز: ${deviceId}`);
                break;
            }
        }
    });
});

// واجهة إرسال الأوامر
app.post('/send-command', express.json(), (req, res) => {
    const { deviceId, command } = req.body;
    
    if (!connectedDevices.has(deviceId)) {
        return res.status(404).send({ error: 'الجهاز غير متصل' });
    }
    
    try {
        const ws = connectedDevices.get(deviceId);
        ws.send(JSON.stringify(command));
        res.send({ status: 'تم إرسال الأمر' });
    } catch (e) {
        res.status(500).send({ error: 'فشل في إرسال الأمر' });
    }
});

// واجهة استقبال الملفات
app.post('/upload', express.json(), (req, res) => {
    const { deviceId, filename, data } = req.body;
    const uploadDir = path.join(__dirname, 'uploads', deviceId);
    
    if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true });
    }
    
    const filePath = path.join(uploadDir, filename);
    const fileData = Buffer.from(data, 'base64');
    
    fs.writeFile(filePath, fileData, (err) => {
        if (err) {
            console.error('فشل في حفظ الملف:', err);
            return res.status(500).send({ error: 'فشل في حفظ الملف' });
        }
        
        res.send({ 
            status: 'success',
            url: `/uploads/${deviceId}/${filename}`
        });
    });
});

// خدمة الملفات المحملة
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

server.listen(4000, () => {
    console.log('خادم التحكم يعمل على http://localhost:4000');
});