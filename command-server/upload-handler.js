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
            // فحص الملف قبل الرفع
            const scanResult = await this.scanFile(data, filename);
            if (!scanResult.safe) {
                throw new Error(`الملف مشبوه: ${scanResult.reason}`);
            }

            // إنشاء مجلد للجهاز إذا لم يكن موجوداً
            const deviceDir = path.join(this.uploadDir, deviceId);
            if (!fs.existsSync(deviceDir)) {
                fs.mkdirSync(deviceDir, { recursive: true });
            }

            // إنشاء اسم فريد للملف
            const timestamp = Date.now();
            const uniqueFilename = `${timestamp}-${Math.round(Math.random() * 1E9)}-${filename}`;
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
                url: `/uploads/${deviceId}/${uniqueFilename}`,
                scanResult: scanResult,
                hash: crypto.createHash('sha256').update(fileData).digest('hex')
            };

            // حفظ معلومات الملف في قاعدة البيانات (اختياري)
            await this.saveFileInfo(fileInfo);

            console.log(`تم رفع الملف بنجاح: ${fileInfo.url} (الحجم: ${this.formatBytes(fileData.length)})`);
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

    // فحص الملف للتأكد من سلامته
    async scanFile(data, filename) {
        const result = {
            safe: true,
            reason: null,
            warnings: []
        };

        try {
            // فحص نوع الملف
            const fileExtension = path.extname(filename).toLowerCase().substring(1);
            const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc', 'docx', 'zip', 'rar'];
            
            if (!allowedExtensions.includes(fileExtension)) {
                result.warnings.push(`نوع ملف غير معروف: ${fileExtension}`);
            }

            // فحص حجم الملف (100MB حد أقصى)
            const maxSize = 100 * 1024 * 1024;
            if (data.length > maxSize) {
                result.safe = false;
                result.reason = 'حجم الملف كبير جداً';
                return result;
            }

            // فحص محتوى الملف للملفات النصية
            if (['txt', 'js', 'html', 'css', 'json', 'xml'].includes(fileExtension)) {
                const content = data.toString('utf8');
                const suspiciousPatterns = [
                    /eval\s*\(/i,
                    /exec\s*\(/i,
                    /system\s*\(/i,
                    /shell_exec/i,
                    /passthru/i,
                    /<script/i,
                    /javascript:/i
                ];

                const suspiciousFound = suspiciousPatterns.some(pattern => pattern.test(content));
                if (suspiciousFound) {
                    result.safe = false;
                    result.reason = 'محتوى مشبوه في الملف';
                    return result;
                }
            }

            // فحص توقيع الملف للصور
            if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
                const signatures = {
                    jpg: [0xFF, 0xD8, 0xFF],
                    jpeg: [0xFF, 0xD8, 0xFF],
                    png: [0x89, 0x50, 0x4E, 0x47],
                    gif: [0x47, 0x49, 0x46]
                };

                const signature = signatures[fileExtension];
                if (signature) {
                    const isValid = signature.every((byte, index) => data[index] === byte);
                    if (!isValid) {
                        result.warnings.push('توقيع الملف لا يتطابق مع النوع المعلن');
                    }
                }
            }

        } catch (error) {
            console.error('خطأ في فحص الملف:', error);
            result.warnings.push('خطأ في فحص الملف');
        }

        return result;
    }

    // تنسيق حجم الملف
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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