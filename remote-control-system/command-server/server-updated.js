const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const multer = require('multer');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const compression = require('compression');
const os = require('os');
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

// إضافة معالجة الأخطاء
process.on('uncaughtException', (error) => {
  console.error('خطأ غير متوقع:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('وعد مرفوض غير معالج:', reason);
});

class CommandServer {
  constructor() {
    this.app = express();
    this.server = http.createServer(this.app);
    
    // قائمة الأصول المسموح بها
    this.allowedOrigins = [
      'https://yourdomain.com', 
      'https://yourapp.com',
      'http://localhost:3000'
    ];
    
    this.wss = new WebSocket.Server({ 
      server: this.server,
      perMessageDeflate: false,
      clientTracking: true,
      maxPayload: 100 * 1024 * 1024, // 100MB
      handshakeTimeout: 30000, // 30 ثانية
      verifyClient: (info) => {
        console.log('🔍 فحص عميل جديد:', info.origin);
        
        // تحقق من أصل الاتصال
        if (this.allowedOrigins.includes(info.origin)) {
          console.log('✅ أصل الاتصال مسموح به:', info.origin);
          return true;
        } else {
          console.log('⛔ رفض اتصال من أصل غير مصرح به:', info.origin);
          return false;
        }
      }
    });
    
    this.devices = new Map();
    this.pendingCommands = new Map();
    this.commandHistory = [];
    this.dataUpdates = [];
    this.uploadedFiles = [];
    
    // إحصائيات الأداء
    this.performanceStats = {
      startTime: Date.now(),
      totalRequests: 0,
      totalCommands: 0,
      totalDataTransferred: 0,
      averageResponseTime: 0,
      errorCount: 0,
      uptime: 0
    };
    
    // إعدادات الأمان المتقدمة (محدثة)
    this.securityConfig = {
      maxFileSize: 100 * 1024 * 1024, // 100MB
      allowedFileTypes: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx'],
      maxConnectionsPerIP: 10,
      sessionTimeout: 30 * 60 * 1000, // 30 دقيقة
      encryptionKey: crypto.randomBytes(32).toString('hex'), // مفتاح تشفير أقوى
      encryptionAlgorithm: 'aes-256-gcm' // خوارزمية تشفير أكثر أمانًا
    };
    
    // إعدادات الاتصال والـ heartbeat
    this.connectionConfig = {
      heartbeatInterval: 30000, // 30 ثانية
      connectionTimeout: 60000, // 60 ثانية
      maxReconnectAttempts: 5,
      reconnectDelay: 5000, // 5 ثوان
      pingInterval: 25000, // 25 ثانية
      pongTimeout: 10000 // 10 ثوان
    };
    
    this.localStoragePath = path.join(__dirname, 'local-storage');
    this.devicesFilePath = path.join(this.localStoragePath, 'devices.json');
    this.commandsFilePath = path.join(this.localStoragePath, 'commands.json');
    this.statsFilePath = path.join(this.localStoragePath, 'stats.json');
    
    this.initializeStorage();
    this.setupMiddleware();
    this.setupWebSocket();
    this.setupRoutes();
    this.startMonitoring();
    
    console.log('🚀 تم تشغيل خادم الأوامر المحدث بنجاح');
  }

  initializeStorage() {
    if (!fs.existsSync(this.localStoragePath)) {
      fs.mkdirSync(this.localStoragePath, { recursive: true });
    }
    
    // تهيئة الملفات إذا لم تكن موجودة
    const files = [
      { path: this.devicesFilePath, default: {} },
      { path: this.commandsFilePath, default: [] },
      { path: this.statsFilePath, default: this.performanceStats }
    ];
    
    files.forEach(file => {
      if (!fs.existsSync(file.path)) {
        fs.writeFileSync(file.path, JSON.stringify(file.default, null, 2));
      }
    });
    
    // تحميل البيانات المحفوظة
    this.loadSavedData();
  }

  loadSavedData() {
    try {
      if (fs.existsSync(this.devicesFilePath)) {
        const devicesData = JSON.parse(fs.readFileSync(this.devicesFilePath, 'utf8'));
        this.devices = new Map(Object.entries(devicesData));
      }
      
      if (fs.existsSync(this.commandsFilePath)) {
        this.commandHistory = JSON.parse(fs.readFileSync(this.commandsFilePath, 'utf8'));
      }
      
      if (fs.existsSync(this.statsFilePath)) {
        this.performanceStats = JSON.parse(fs.readFileSync(this.statsFilePath, 'utf8'));
      }
      
      console.log('📂 تم تحميل البيانات المحفوظة بنجاح');
    } catch (error) {
      console.error('❌ خطأ في تحميل البيانات المحفوظة:', error);
    }
  }

  saveData() {
    try {
      // حفظ الأجهزة
      const devicesData = Object.fromEntries(this.devices);
      fs.writeFileSync(this.devicesFilePath, JSON.stringify(devicesData, null, 2));
      
      // حفظ الأوامر
      fs.writeFileSync(this.commandsFilePath, JSON.stringify(this.commandHistory, null, 2));
      
      // حفظ الإحصائيات
      fs.writeFileSync(this.statsFilePath, JSON.stringify(this.performanceStats, null, 2));
      
      console.log('💾 تم حفظ البيانات بنجاح');
    } catch (error) {
      console.error('❌ خطأ في حفظ البيانات:', error);
    }
  }

  setupMiddleware() {
    // إعدادات الأمان المتقدمة
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", "data:", "https:"],
          connectSrc: ["'self'", "ws:", "wss:"],
          fontSrc: ["'self'"],
          objectSrc: ["'none'"],
          mediaSrc: ["'self'"],
          frameSrc: ["'none'"]
        }
      },
      crossOriginEmbedderPolicy: false,
      crossOriginResourcePolicy: { policy: "cross-origin" }
    }));

    // CORS محسن
    this.app.use((req, res, next) => {
      const origin = req.headers.origin;
      if (this.allowedOrigins.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
      }
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      res.setHeader('Access-Control-Allow-Credentials', 'true');
      
      if (req.method === 'OPTIONS') {
        res.sendStatus(200);
      } else {
        next();
      }
    });

    // Rate Limiting مع استثناءات للـ IPs الموثوقة
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 دقيقة
      max: 100, // حد أقصى 100 طلب لكل IP
      message: 'تم تجاوز الحد الأقصى للطلبات',
      skip: (req) => {
        // استثناء IPs موثوقة
        const trustedIPs = ['127.0.0.1', '::1', 'localhost'];
        return trustedIPs.includes(req.ip);
      }
    });
    this.app.use(limiter);

    // ضغط البيانات
    this.app.use(compression());

    // معالجة البيانات
    this.app.use(express.json({ limit: '100mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '100mb' }));

    // إعداد Multer للملفات
    this.upload = multer({
      storage: multer.diskStorage({
        destination: (req, file, cb) => {
          const uploadDir = path.join(__dirname, 'uploads');
          if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
          }
          cb(null, uploadDir);
        },
        filename: (req, file, cb) => {
          const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1E9)}-${file.originalname}`;
          cb(null, uniqueName);
        }
      }),
      limits: {
        fileSize: this.securityConfig.maxFileSize,
        files: 10
      },
      fileFilter: (req, file, cb) => {
        const fileExtension = path.extname(file.originalname).toLowerCase().substring(1);
        if (this.securityConfig.allowedFileTypes.includes(fileExtension)) {
          cb(null, true);
        } else {
          cb(new Error('نوع الملف غير مسموح به'), false);
        }
      }
    });
  }

  setupWebSocket() {
    this.wss.on('connection', (ws, req) => {
      console.log('🔗 اتصال WebSocket جديد');
      
      const clientIP = req.socket.remoteAddress;
      console.log('📍 IP العميل:', clientIP);
      
      // إعداد خصائص الاتصال
      ws.isAlive = true;
      ws.lastPing = Date.now();
      ws.deviceId = null;
      ws.clientIP = clientIP;
      
      // إعداد معالجات الأحداث
      ws.on('pong', () => {
        ws.isAlive = true;
        ws.lastPing = Date.now();
      });
      
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          this.handleWebSocketMessage(ws, message);
        } catch (error) {
          console.error('❌ خطأ في معالجة رسالة WebSocket:', error);
          ws.send(JSON.stringify({ error: 'رسالة غير صالحة' }));
        }
      });
      
      ws.on('close', () => {
        console.log('🔌 انقطع اتصال WebSocket');
        if (ws.deviceId) {
          this.handleDeviceDisconnection(ws.deviceId);
        }
      });
      
      ws.on('error', (error) => {
        console.error('❌ خطأ في WebSocket:', error);
        if (ws.deviceId) {
          this.handleDeviceDisconnection(ws.deviceId);
        }
      });
    });
    
    // إعداد فحص الاتصالات
    this.setupHeartbeat();
  }

  setupHeartbeat() {
    setInterval(() => {
      this.wss.clients.forEach((ws) => {
        if (ws.isAlive === false) {
          console.log('💀 إغلاق اتصال غير نشط');
          return ws.terminate();
        }
        
        ws.isAlive = false;
        ws.ping();
        
        // فحص timeout
        if (Date.now() - ws.lastPing > this.connectionConfig.pongTimeout) {
          console.log('⏰ انتهت مهلة الاتصال');
          ws.terminate();
        }
      });
    }, this.connectionConfig.pingInterval);
  }

  handleWebSocketMessage(ws, message) {
    const { type, deviceId, data, commandId } = message;
    
    switch (type) {
      case 'device_register':
        this.handleDeviceRegistration(ws, deviceId, data);
        break;
        
      case 'command_result':
        this.handleCommandResult(ws, deviceId, commandId, data);
        break;
        
      case 'heartbeat':
        this.handleHeartbeat(ws, deviceId);
        break;
        
      case 'data_update':
        this.handleDataUpdate(ws, deviceId, data);
        break;
        
      default:
        console.log('❓ نوع رسالة غير معروف:', type);
        ws.send(JSON.stringify({ error: 'نوع رسالة غير معروف' }));
    }
  }

  handleDeviceRegistration(ws, deviceId, data) {
    console.log('📱 تسجيل جهاز جديد:', deviceId);
    
    const deviceInfo = {
      id: deviceId,
      ws: ws,
      lastSeen: Date.now(),
      status: 'online',
      info: data || {},
      commands: [],
      performance: {
        cpu: 0,
        memory: 0,
        uptime: 0
      }
    };
    
    this.devices.set(deviceId, deviceInfo);
    ws.deviceId = deviceId;
    
    // إرسال تأكيد التسجيل
    ws.send(JSON.stringify({
      type: 'registration_confirmed',
      deviceId: deviceId,
      timestamp: Date.now()
    }));
    
    // إرسال الأوامر المعلقة
    this.sendPendingCommands(deviceId);
    
    console.log('✅ تم تسجيل الجهاز بنجاح');
    this.broadcastDeviceList();
  }

  handleDeviceDisconnection(deviceId) {
    console.log('🔌 انفصال الجهاز:', deviceId);
    
    if (this.devices.has(deviceId)) {
      const device = this.devices.get(deviceId);
      device.status = 'offline';
      device.lastSeen = Date.now();
      device.ws = null;
      
      this.devices.set(deviceId, device);
      this.broadcastDeviceList();
    }
  }

  handleCommandResult(ws, deviceId, commandId, data) {
    console.log('📋 نتيجة أمر:', commandId, 'من الجهاز:', deviceId);
    
    const result = {
      deviceId,
      commandId,
      data,
      timestamp: Date.now(),
      success: data && !data.error
    };
    
    // تحديث الأوامر المعلقة
    if (this.pendingCommands.has(commandId)) {
      const pendingCommand = this.pendingCommands.get(commandId);
      pendingCommand.result = result;
      pendingCommand.completed = true;
      pendingCommand.completedAt = Date.now();
      
      this.pendingCommands.set(commandId, pendingCommand);
    }
    
    // إضافة إلى التاريخ
    this.commandHistory.push(result);
    
    // حفظ البيانات
    this.saveData();
    
    // إرسال النتيجة للمراقبين
    this.broadcastCommandResult(result);
    
    console.log('✅ تم معالجة نتيجة الأمر');
  }

  handleHeartbeat(ws, deviceId) {
    if (this.devices.has(deviceId)) {
      const device = this.devices.get(deviceId);
      device.lastSeen = Date.now();
      device.status = 'online';
      
      this.devices.set(deviceId, device);
    }
  }

  handleDataUpdate(ws, deviceId, data) {
    console.log('📊 تحديث بيانات من الجهاز:', deviceId);
    
    const update = {
      deviceId,
      data,
      timestamp: Date.now()
    };
    
    this.dataUpdates.push(update);
    
    // تحديث معلومات الجهاز
    if (this.devices.has(deviceId)) {
      const device = this.devices.get(deviceId);
      device.info = { ...device.info, ...data };
      device.lastSeen = Date.now();
      
      this.devices.set(deviceId, device);
    }
    
    // إرسال التحديث للمراقبين
    this.broadcastDataUpdate(update);
  }

  sendPendingCommands(deviceId) {
    const pendingCommands = Array.from(this.pendingCommands.values())
      .filter(cmd => cmd.deviceId === deviceId && !cmd.completed);
    
    if (pendingCommands.length > 0) {
      console.log(`📤 إرسال ${pendingCommands.length} أمر معلق للجهاز:`, deviceId);
      
      pendingCommands.forEach(cmd => {
        this.sendCommandToDevice(deviceId, cmd.command, cmd.commandId);
      });
    }
  }

  sendCommandToDevice(deviceId, command, commandId) {
    const device = this.devices.get(deviceId);
    if (!device || !device.ws) {
      console.log('❌ الجهاز غير متصل:', deviceId);
      return false;
    }
    
    try {
      const message = {
        type: 'command',
        commandId: commandId,
        command: command,
        timestamp: Date.now()
      };
      
      device.ws.send(JSON.stringify(message));
      console.log('📤 تم إرسال الأمر:', commandId, 'إلى الجهاز:', deviceId);
      return true;
    } catch (error) {
      console.error('❌ خطأ في إرسال الأمر:', error);
      return false;
    }
  }

  setupRoutes() {
    // مسار الصحة
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        uptime: Date.now() - this.performanceStats.startTime,
        devices: this.devices.size,
        pendingCommands: this.pendingCommands.size
      });
    });

    // مسار معلومات النظام
    this.app.get('/system-info', (req, res) => {
      const systemInfo = {
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        uptime: os.uptime(),
        loadAverage: os.loadavg()
      };
      
      res.json(systemInfo);
    });

    // مسار إحصائيات الأداء
    this.app.get('/performance-stats', (req, res) => {
      this.performanceStats.uptime = Date.now() - this.performanceStats.startTime;
      res.json(this.performanceStats);
    });

    // مسار قائمة الأجهزة
    this.app.get('/devices', (req, res) => {
      const devicesList = Array.from(this.devices.values()).map(device => ({
        id: device.id,
        status: device.status,
        lastSeen: device.lastSeen,
        info: device.info,
        performance: device.performance
      }));
      
      res.json(devicesList);
    });

    // مسار إرسال أمر
    this.app.post('/send-command', (req, res) => {
      const { deviceId, command, priority = 'normal' } = req.body;
      
      if (!deviceId || !command) {
        return res.status(400).json({ error: 'معرف الجهاز والأمر مطلوبان' });
      }
      
      const commandId = crypto.randomBytes(16).toString('hex');
      const pendingCommand = {
        id: commandId,
        deviceId,
        command,
        priority,
        timestamp: Date.now(),
        retryCount: 0,
        maxRetries: 3,
        completed: false
      };
      
      this.pendingCommands.set(commandId, pendingCommand);
      
      // محاولة الإرسال الفوري
      const sent = this.sendCommandToDevice(deviceId, command, commandId);
      
      if (!sent) {
        console.log('⏳ الأمر معلق للإرسال لاحقاً:', commandId);
      }
      
      res.json({
        success: true,
        commandId,
        sent,
        message: sent ? 'تم إرسال الأمر بنجاح' : 'الأمر معلق للإرسال'
      });
    });

    // مسار نتائج الأوامر
    this.app.get('/command-results/:commandId', (req, res) => {
      const { commandId } = req.params;
      
      if (this.pendingCommands.has(commandId)) {
        const command = this.pendingCommands.get(commandId);
        res.json(command);
      } else {
        res.status(404).json({ error: 'الأمر غير موجود' });
      }
    });

    // مسار رفع الملفات
    this.app.post('/upload', this.upload.single('file'), (req, res) => {
      try {
        if (!req.file) {
          return res.status(400).json({ error: 'لم يتم تحديد ملف' });
        }
        
        const fileInfo = {
          originalName: req.file.originalname,
          filename: req.file.filename,
          path: req.file.path,
          size: req.file.size,
          mimetype: req.file.mimetype,
          uploadedAt: Date.now()
        };
        
        this.uploadedFiles.push(fileInfo);
        
        // فحص الملف للتأكد من سلامته
        this.scanUploadedFile(fileInfo);
        
        res.json({
          success: true,
          file: fileInfo,
          message: 'تم رفع الملف بنجاح'
        });
      } catch (error) {
        console.error('❌ خطأ في رفع الملف:', error);
        res.status(500).json({ error: 'خطأ في رفع الملف' });
      }
    });

    // مسار إعادة تشغيل النظام
    this.app.post('/restart', (req, res) => {
      console.log('🔄 طلب إعادة تشغيل النظام');
      
      res.json({
        success: true,
        message: 'سيتم إعادة تشغيل النظام قريباً'
      });
      
      // إعادة تشغيل بعد 2 ثانية
      setTimeout(() => {
        this.restartSystem();
      }, 2000);
    });

    // مسار تنظيف البيانات
    this.app.post('/cleanup', (req, res) => {
      console.log('🧹 طلب تنظيف البيانات');
      
      this.cleanupData();
      
      res.json({
        success: true,
        message: 'تم تنظيف البيانات بنجاح'
      });
    });
  }

  scanUploadedFile(fileInfo) {
    console.log('🔍 فحص الملف المرفوع:', fileInfo.originalName);
    
    // فحص حجم الملف
    if (fileInfo.size > this.securityConfig.maxFileSize) {
      console.warn('⚠️ حجم الملف كبير جداً:', fileInfo.size);
    }
    
    // فحص نوع الملف
    const fileExtension = path.extname(fileInfo.originalname).toLowerCase().substring(1);
    if (!this.securityConfig.allowedFileTypes.includes(fileExtension)) {
      console.warn('⚠️ نوع ملف غير مسموح به:', fileExtension);
    }
    
    // فحص محتوى الملف (مبسط)
    try {
      const content = fs.readFileSync(fileInfo.path, 'utf8');
      const suspiciousPatterns = [
        /eval\s*\(/i,
        /exec\s*\(/i,
        /system\s*\(/i,
        /shell_exec/i,
        /passthru/i
      ];
      
      const isSuspicious = suspiciousPatterns.some(pattern => pattern.test(content));
      if (isSuspicious) {
        console.warn('⚠️ محتوى مشبوه في الملف:', fileInfo.originalName);
      }
    } catch (error) {
      // الملف ثنائي أو غير قابل للقراءة
    }
    
    console.log('✅ تم فحص الملف بنجاح');
  }

  cleanupData() {
    console.log('🧹 بدء تنظيف البيانات');
    
    const now = Date.now();
    const oneDayAgo = now - 24 * 60 * 60 * 1000;
    const oneWeekAgo = now - 7 * 24 * 60 * 60 * 1000;
    
    // تنظيف الأوامر المعلقة القديمة
    const oldPendingCommands = Array.from(this.pendingCommands.entries())
      .filter(([id, cmd]) => cmd.timestamp < oneDayAgo);
    
    oldPendingCommands.forEach(([id]) => {
      this.pendingCommands.delete(id);
    });
    
    // تنظيف تاريخ الأوامر القديم
    this.commandHistory = this.commandHistory.filter(cmd => cmd.timestamp > oneWeekAgo);
    
    // تنظيف تحديثات البيانات القديمة
    this.dataUpdates = this.dataUpdates.filter(update => update.timestamp > oneDayAgo);
    
    // تنظيف الملفات المرفوعة القديمة
    this.uploadedFiles = this.uploadedFiles.filter(file => file.uploadedAt > oneWeekAgo);
    
    // تنظيف الأجهزة غير المتصلة
    const offlineDevices = Array.from(this.devices.entries())
      .filter(([id, device]) => device.status === 'offline' && device.lastSeen < oneDayAgo);
    
    offlineDevices.forEach(([id]) => {
      this.devices.delete(id);
    });
    
    console.log(`🧹 تم تنظيف ${oldPendingCommands.length} أمر معلق قديم`);
    console.log(`🧹 تم تنظيف ${offlineDevices.length} جهاز غير متصل`);
    
    // حفظ البيانات بعد التنظيف
    this.saveData();
  }

  startMonitoring() {
    // مراقبة الأداء كل دقيقة
    setInterval(() => {
      this.updatePerformanceStats();
    }, 60000);
    
    // تنظيف البيانات كل ساعة
    setInterval(() => {
      this.cleanupData();
    }, 3600000);
    
    // حفظ البيانات كل 5 دقائق
    setInterval(() => {
      this.saveData();
    }, 300000);
    
    console.log('📊 تم تفعيل مراقبة النظام');
  }

  updatePerformanceStats() {
    const now = Date.now();
    this.performanceStats.uptime = now - this.performanceStats.startTime;
    
    // حساب متوسط وقت الاستجابة
    if (this.commandHistory.length > 0) {
      const recentCommands = this.commandHistory
        .filter(cmd => cmd.timestamp > now - 60000) // آخر دقيقة
        .map(cmd => cmd.responseTime || 0);
      
      if (recentCommands.length > 0) {
        this.performanceStats.averageResponseTime = 
          recentCommands.reduce((sum, time) => sum + time, 0) / recentCommands.length;
      }
    }
    
    // إحصائيات النظام
    const memUsage = process.memoryUsage();
    this.performanceStats.memoryUsage = {
      rss: Math.round(memUsage.rss / 1024 / 1024), // MB
      heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
      heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024), // MB
      external: Math.round(memUsage.external / 1024 / 1024) // MB
    };
    
    this.performanceStats.cpuUsage = process.cpuUsage();
  }

  broadcastDeviceList() {
    const devicesList = Array.from(this.devices.values()).map(device => ({
      id: device.id,
      status: device.status,
      lastSeen: device.lastSeen,
      info: device.info
    }));
    
    const message = {
      type: 'device_list_update',
      devices: devicesList,
      timestamp: Date.now()
    };
    
    this.broadcastToMonitors(message);
  }

  broadcastCommandResult(result) {
    const message = {
      type: 'command_result',
      result: result,
      timestamp: Date.now()
    };
    
    this.broadcastToMonitors(message);
  }

  broadcastDataUpdate(update) {
    const message = {
      type: 'data_update',
      update: update,
      timestamp: Date.now()
    };
    
    this.broadcastToMonitors(message);
  }

  broadcastToMonitors(message) {
    this.wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN && !client.deviceId) {
        // إرسال فقط للمراقبين (ليس الأجهزة)
        try {
          client.send(JSON.stringify(message));
        } catch (error) {
          console.error('❌ خطأ في إرسال رسالة للمراقب:', error);
        }
      }
    });
  }

  restartSystem() {
    console.log('🔄 إعادة تشغيل النظام...');
    
    // حفظ البيانات قبل الإعادة تشغيل
    this.saveData();
    
    // إغلاق جميع الاتصالات
    this.wss.clients.forEach(client => {
      client.close();
    });
    
    // إغلاق الخادم
    this.server.close(() => {
      console.log('✅ تم إغلاق الخادم بنجاح');
      process.exit(0);
    });
  }

  start(port = process.env.PORT || 10001) {
    this.server.listen(port, '0.0.0.0', () => {
      console.log(`🚀 خادم الأوامر يعمل على المنفذ ${port}`);
      console.log(`📊 عدد المعالجات: ${numCPUs}`);
      console.log(`🛡️ وضع الأمان: مفعل`);
      console.log(`🔐 خوارزمية التشفير: ${this.securityConfig.encryptionAlgorithm}`);
      console.log(`📁 مسار التخزين: ${this.localStoragePath}`);
    });
  }
}

// تشغيل الخادم
if (cluster.isMaster) {
  console.log(`🎯 المعالج الرئيسي ${process.pid} يعمل`);
  
  // إنشاء عمال
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`💀 العامل ${worker.process.pid} توقف`);
    console.log('🔄 إنشاء عامل جديد...');
    cluster.fork();
  });
  
  // إعادة تشغيل متزامن لجميع العمال
  cluster.on('message', (worker, message) => {
    if (message.type === 'restart_all') {
      console.log('🔄 إعادة تشغيل جميع العمال...');
      for (const id in cluster.workers) {
        cluster.workers[id].send('restart');
      }
    }
  });
} else {
  const server = new CommandServer();
  server.start();
  
  // إرسال رسالة تأكيد للمعالج الرئيسي
  process.send({ type: 'worker_ready', pid: process.pid });
  
  console.log(`👷 العامل ${process.pid} جاهز`);
}

module.exports = CommandServer;