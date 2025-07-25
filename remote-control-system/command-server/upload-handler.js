const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class UploadHandler {
    constructor(uploadDir = 'uploads') {
        this.uploadDir = uploadDir;
        this.ensureUploadDirectory();
    }

    // التأكد من وجود مجلد الرفع
    ensureUploadDirectory() {
        if (!fs.existsSync(this.uploadDir)) {
            fs.mkdirSync(this.uploadDir, { recursive: true });
        }
    }

    // معالجة رفع ملف
    async handleUpload(deviceId, filename, data, fileType = 'binary') {
        try {
            // إنشاء مجلد للجهاز إذا لم يكن موجوداً
            const deviceDir = path.join(this.uploadDir, deviceId);
            if (!fs.existsSync(deviceDir)) {
                fs.mkdirSync(deviceDir, { recursive: true });
            }

            // إنشاء اسم فريد للملف
            const timestamp = Date.now();
            const uniqueFilename = `${timestamp}-${filename}`;
            const filePath = path.join(deviceDir, uniqueFilename);

            // حفظ الملف
            let fileData;
            if (fileType === 'base64') {
                fileData = Buffer.from(data, 'base64');
            } else {
                fileData = Buffer.from(data);
            }

            await this.saveFile(filePath, fileData);

            // إنشاء معلومات الملف
            const fileInfo = {
                originalName: filename,
                savedName: uniqueFilename,
                path: filePath,
                size: fileData.length,
                uploadedAt: new Date().toISOString(),
                deviceId: deviceId,
                url: `/uploads/${deviceId}/${uniqueFilename}`
            };

            // حفظ معلومات الملف في قاعدة البيانات (اختياري)
            await this.saveFileInfo(fileInfo);

            console.log(`تم رفع الملف بنجاح: ${fileInfo.url}`);
            return fileInfo;

        } catch (error) {
            console.error('خطأ في رفع الملف:', error);
            throw error;
        }
    }

    // حفظ الملف على القرص
    async saveFile(filePath, data) {
        return new Promise((resolve, reject) => {
            fs.writeFile(filePath, data, (err) => {
                if (err) {
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    // حفظ معلومات الملف
    async saveFileInfo(fileInfo) {
        const infoPath = path.join(this.uploadDir, 'file_info.json');
        let fileInfos = [];

        try {
            if (fs.existsSync(infoPath)) {
                const data = fs.readFileSync(infoPath, 'utf8');
                fileInfos = JSON.parse(data);
            }
        } catch (error) {
            console.warn('خطأ في قراءة معلومات الملفات:', error);
        }

        fileInfos.push(fileInfo);

        try {
            fs.writeFileSync(infoPath, JSON.stringify(fileInfos, null, 2));
        } catch (error) {
            console.warn('خطأ في حفظ معلومات الملف:', error);
        }
    }

    // الحصول على قائمة ملفات الجهاز
    getDeviceFiles(deviceId) {
        const deviceDir = path.join(this.uploadDir, deviceId);
        
        if (!fs.existsSync(deviceDir)) {
            return [];
        }

        try {
            const files = fs.readdirSync(deviceDir);
            return files.map(filename => ({
                name: filename,
                path: path.join(deviceDir, filename),
                url: `/uploads/${deviceId}/${filename}`,
                size: fs.statSync(path.join(deviceDir, filename)).size
            }));
        } catch (error) {
            console.error('خطأ في قراءة ملفات الجهاز:', error);
            return [];
        }
    }

    // حذف ملف
    deleteFile(deviceId, filename) {
        const filePath = path.join(this.uploadDir, deviceId, filename);
        
        if (fs.existsSync(filePath)) {
            try {
                fs.unlinkSync(filePath);
                console.log(`تم حذف الملف: ${filePath}`);
                return true;
            } catch (error) {
                console.error('خطأ في حذف الملف:', error);
                return false;
            }
        }
        
        return false;
    }

    // الحصول على حجم مجلد الجهاز
    getDeviceStorageSize(deviceId) {
        const deviceDir = path.join(this.uploadDir, deviceId);
        
        if (!fs.existsSync(deviceDir)) {
            return 0;
        }

        try {
            const files = fs.readdirSync(deviceDir);
            let totalSize = 0;
            
            files.forEach(filename => {
                const filePath = path.join(deviceDir, filename);
                const stats = fs.statSync(filePath);
                totalSize += stats.size;
            });
            
            return totalSize;
        } catch (error) {
            console.error('خطأ في حساب حجم التخزين:', error);
            return 0;
        }
    }

    // تنظيف الملفات القديمة
    cleanupOldFiles(maxAge = 7 * 24 * 60 * 60 * 1000) { // 7 أيام افتراضياً
        const cutoffTime = Date.now() - maxAge;
        
        try {
            const devices = fs.readdirSync(this.uploadDir);
            
            devices.forEach(deviceId => {
                if (deviceId === 'file_info.json') return;
                
                const deviceDir = path.join(this.uploadDir, deviceId);
                const files = fs.readdirSync(deviceDir);
                
                files.forEach(filename => {
                    const filePath = path.join(deviceDir, filename);
                    const stats = fs.statSync(filePath);
                    
                    if (stats.mtime.getTime() < cutoffTime) {
                        try {
                            fs.unlinkSync(filePath);
                            console.log(`تم حذف الملف القديم: ${filePath}`);
                        } catch (error) {
                            console.error('خطأ في حذف الملف القديم:', error);
                        }
                    }
                });
            });
        } catch (error) {
            console.error('خطأ في تنظيف الملفات القديمة:', error);
        }
    }
}

module.exports = UploadHandler;