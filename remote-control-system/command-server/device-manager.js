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
    const { deviceId, command } = data;
    const deviceSocket = this.connectedDevices.get(deviceId);
    
    if (deviceSocket) {
      deviceSocket.send(JSON.stringify(command));
      console.log(`تم إرسال الأمر للجهاز ${deviceId}: ${command.action}`);
    } else {
      console.error(`الجهاز غير متصل: ${deviceId}`);
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