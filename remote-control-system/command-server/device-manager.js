const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

class DeviceManager {
  constructor() {
    this.connectedDevices = new Map();
    this.wss = new WebSocket.Server({ port: 10001 });
    
    this.init();
  }

  init() {
    this.wss.on('connection', (ws) => {
      ws.on('message', (message) => {
        const data = JSON.parse(message);
        
        if (data.type === 'register') {
          this.registerDevice(data.deviceId, ws);
        } else if (data.type === 'command') {
          this.handleCommand(data);
        }
      });
      
      ws.on('close', () => {
        this.unregisterDevice(ws);
      });
    });
  }

  registerDevice(deviceId, ws) {
    this.connectedDevices.set(deviceId, ws);
    console.log(`تم تسجيل الجهاز: ${deviceId}`);
    
    // حفظ حالة الجهاز
    this.saveDeviceState(deviceId, 'connected');
  }

  unregisterDevice(ws) {
    for (const [deviceId, socket] of this.connectedDevices.entries()) {
      if (socket === ws) {
        this.connectedDevices.delete(deviceId);
        console.log(`انقطع اتصال الجهاز: ${deviceId}`);
        
        // تحديث حالة الجهاز
        this.saveDeviceState(deviceId, 'disconnected');
        break;
      }
    }
  }

  handleCommand(data) {
    const { deviceId, command, commandId } = data;
    const deviceSocket = this.connectedDevices.get(deviceId);
    
    if (deviceSocket) {
      const message = {
        type: 'command',
        commandId: commandId || require('crypto').randomBytes(16).toString('hex'),
        command: command,
        timestamp: Date.now()
      };
      
      deviceSocket.send(JSON.stringify(message));
      console.log(`تم إرسال الأمر للجهاز ${deviceId}: ${command.action} (ID: ${message.commandId})`);
      
      // حفظ الأمر في قائمة الأوامر المعلقة
      this.pendingCommands = this.pendingCommands || new Map();
      this.pendingCommands.set(message.commandId, {
        deviceId,
        command,
        timestamp: Date.now(),
        status: 'sent'
      });
    } else {
      console.error(`الجهاز غير متصل: ${deviceId}`);
      return { error: 'device_not_connected', deviceId };
    }
  }

  saveDeviceState(deviceId, state) {
    const deviceData = {
      deviceId,
      status: state,
      lastSeen: new Date().toISOString()
    };
    
    const filePath = path.join(__dirname, 'devices', `${deviceId}.json`);
    fs.writeFileSync(filePath, JSON.stringify(deviceData));
  }
}

module.exports = DeviceManager;