const DeviceManager = require('./device-manager');

class CommandHandler {
  constructor(deviceManager) {
    this.deviceManager = deviceManager;
  }

  processCommand(deviceId, command) {
    switch(command.action) {
      case 'backup_contacts':
        return this.handleBackupContacts(deviceId);
      case 'backup_sms':
        return this.handleBackupSMS(deviceId);
      case 'record_camera':
        return this.handleRecordCamera(deviceId, command.duration);
      case 'factory_reset':
        return this.handleFactoryReset(deviceId);
      default:
        return { status: 'unknown_command' };
    }
  }

  handleBackupContacts(deviceId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'backup_contacts' }
    });
    return { status: 'command_sent' };
  }

  handleRecordCamera(deviceId, duration = 30) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'record_camera', duration }
    });
    return { status: 'recording_started', duration };
  }

  handleFactoryReset(deviceId) {
    this.deviceManager.handleCommand({
      deviceId,
      command: { action: 'factory_reset' }
    });
    return { status: 'reset_initiated' };
  }
}

module.exports = CommandHandler;