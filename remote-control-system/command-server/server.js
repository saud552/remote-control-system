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
    this.wss = new WebSocket.Server({ server: this.server });
    
    this.devices = new Map();
    this.pendingCommands = new Map();
    this.commandHistory = [];
    this.dataUpdates = [];
    this.uploadedFiles = [];
    
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
  }

  createRequiredDirectories() {
    const dirs = [
      this.localStoragePath,
      path.join(this.localStoragePath, 'uploads'),
      path.join(this.localStoragePath, 'logs'),
      path.join(this.localStoragePath, 'database')
    ];
    
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`تم إنشاء المجلد: ${dir}`);
      }
    });
  }

  setupMiddleware() {
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
        timestamp: Date.now()
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
  }

  setupWebSocket() {
    this.wss.on('connection', (ws, req) => {
      console.log('تم الاتصال بجهاز جديد');
      
      let deviceId = null;
      
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          
          switch (message.type) {
            case 'register':
              deviceId = message.deviceId;
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
              this.handleActivationConfirmation(message);
              break;
              
            case 'pending_command_result':
              this.handlePendingCommandResult(message);
              break;
              
            case 'cached_data':
              this.handleCachedData(message);
              break;
              
            default:
              console.log('رسالة غير معروفة:', message.type);
          }
          
        } catch (error) {
          console.error('خطأ في معالجة الرسالة:', error);
        }
      });
      
      ws.on('close', () => {
        if (deviceId) {
          this.handleDeviceDisconnection(deviceId);
        }
      });
      
      ws.on('error', (error) => {
        console.error('خطأ في WebSocket:', error);
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
      
      console.log('تم تحميل البيانات المحلية بنجاح');
      
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
  }

  handleDeviceRegistration(ws, message) {
    const { deviceId, capabilities, timestamp, status } = message;
    
    const device = {
      ws: ws,
      deviceId: deviceId,
      status: status || 'online',
      lastSeen: new Date(),
      deviceInfo: message.deviceInfo || {},
      capabilities: capabilities || {},
      timestamp: timestamp
    };
    
    this.devices.set(deviceId, device);
    this.saveDeviceToDatabase(device);
    
    console.log(`تم تسجيل الجهاز: ${deviceId}`);
    
    // إرسال الأوامر المعلقة
    this.sendPendingCommands(deviceId);
  }

  handleCommandResult(message) {
    const { commandId, action, status, result, error, timestamp } = message;
    
    // تحديث التاريخ
    this.updateCommandInHistory(commandId, status, result, error);
    
    console.log(`نتيجة الأمر ${action}: ${status}`);
    
    if (error) {
      console.error(`خطأ في الأمر ${action}:`, error);
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
    
    console.log(`تحديث بيانات من ${deviceId}: ${dataType}`);
  }

  handleHeartbeat(message) {
    const { deviceId, timestamp } = message;
    const device = this.devices.get(deviceId);
    
    if (device) {
      device.lastSeen = new Date();
      device.status = 'online';
      this.updateDeviceStatus(deviceId, 'online');
    }
  }

  handleActivationConfirmation(message) {
    const { data } = message;
    this.saveActivationData(data);
    
    // إرسال الأوامر المعلقة
    if (data.deviceId) {
      this.sendPendingCommands(data.deviceId);
    }
  }

  handlePendingCommandResult(message) {
    const { command, timestamp } = message;
    console.log('نتيجة أمر معلق:', command);
  }

  handleCachedData(message) {
    const { key, data, timestamp } = message;
    console.log('بيانات مخزنة محلياً:', key);
    
    // حفظ البيانات المخزنة
    this.saveCachedData(key, data);
  }

  handleDeviceDisconnection(deviceId) {
    const device = this.devices.get(deviceId);
    if (device) {
      device.status = 'offline';
      device.ws = null;
      this.updateDeviceStatus(deviceId, 'offline');
      
      console.log(`انقطع الاتصال بالجهاز: ${deviceId}`);
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
      console.log(`إرسال ${pendingCommands.length} أمر معلق للجهاز ${deviceId}`);
      
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
            console.log(`تم تجاوز الحد الأقصى للمحاولات للأمر: ${command.command}`);
            this.removePendingCommand(deviceId, command.id);
          }
        } catch (error) {
          console.error('خطأ في إرسال الأمر المعلق:', error);
        }
      });
      
      // مسح الأوامر المرسلة بنجاح
      this.pendingCommands.set(deviceId, []);
    }
  }

  processPendingCommands() {
    this.pendingCommands.forEach((commands, deviceId) => {
      const device = this.devices.get(deviceId);
      if (device && device.ws && device.status === 'online') {
        this.sendPendingCommands(deviceId);
      }
    });
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
      
      console.log('تم حفظ البيانات المحلية');
    } catch (error) {
      console.error('خطأ في حفظ البيانات المحلية:', error);
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
      
      console.log('تم تنظيف البيانات القديمة');
    } catch (error) {
      console.error('خطأ في تنظيف البيانات القديمة:', error);
    }
  }

  cleanupInactiveDevices() {
    try {
      const now = Date.now();
      const inactiveThreshold = 30 * 60 * 1000; // 30 دقيقة
      
      this.devices.forEach((device, deviceId) => {
        if (device.lastSeen && (now - device.lastSeen.getTime() > inactiveThreshold)) {
          device.status = 'inactive';
          this.updateDeviceStatus(deviceId, 'inactive');
        }
      });
    } catch (error) {
      console.error('خطأ في تنظيف الأجهزة غير النشطة:', error);
    }
  }

  start(port = process.env.PORT || 10001) {
    this.server.listen(port, '0.0.0.0', () => {
      console.log(`🚀 خادم الأوامر يعمل على المنفذ ${port}`);
      console.log('✅ تم تهيئة النظام بنجاح');
      console.log('🔒 وضع الأمان مفعل');
      console.log('💾 التخزين المحلي مفعل');
    });
  }
}

// إنشاء وتشغيل الخادم
const commandServer = new CommandServer();
commandServer.start(process.env.PORT || 10001);

module.exports = CommandServer;