/**
 * نظام التشفير المتقدم
 * Advanced Encryption System
 */

class EncryptionManager {
    constructor() {
        this.algorithm = 'AES-GCM';
        this.keyLength = 256;
        this.ivLength = 12;
        this.tagLength = 16;
        this.encryptionKey = null;
        this.isInitialized = false;
    }

    // تهيئة نظام التشفير
    async initialize() {
        try {
            console.log('🔐 تهيئة نظام التشفير...');
            
            // توليد مفتاح التشفير
            this.encryptionKey = await this.generateKey();
            
            // اختبار التشفير
            await this.testEncryption();
            
            this.isInitialized = true;
            console.log('✅ تم تهيئة نظام التشفير بنجاح');
            
            return true;
        } catch (error) {
            console.error('❌ فشل في تهيئة نظام التشفير:', error);
            return false;
        }
    }

    // توليد مفتاح التشفير
    async generateKey() {
        try {
            const key = await window.crypto.subtle.generateKey(
                {
                    name: this.algorithm,
                    length: this.keyLength
                },
                true,
                ['encrypt', 'decrypt']
            );
            
            console.log('🔑 تم توليد مفتاح التشفير');
            return key;
        } catch (error) {
            console.error('❌ فشل في توليد مفتاح التشفير:', error);
            throw error;
        }
    }

    // تشفير البيانات
    async encrypt(data) {
        try {
            if (!this.isInitialized) {
                throw new Error('نظام التشفير غير مهيأ');
            }

            // تحويل البيانات إلى نص
            const textEncoder = new TextEncoder();
            const encodedData = textEncoder.encode(JSON.stringify(data));

            // توليد IV
            const iv = window.crypto.getRandomValues(new Uint8Array(this.ivLength));

            // تشفير البيانات
            const encryptedData = await window.crypto.subtle.encrypt(
                {
                    name: this.algorithm,
                    iv: iv
                },
                this.encryptionKey,
                encodedData
            );

            // دمج IV والبيانات المشفرة
            const combined = new Uint8Array(iv.length + encryptedData.byteLength);
            combined.set(iv);
            combined.set(new Uint8Array(encryptedData), iv.length);

            // تحويل إلى Base64
            const base64 = btoa(String.fromCharCode(...combined));
            
            console.log('🔐 تم تشفير البيانات بنجاح');
            return base64;
        } catch (error) {
            console.error('❌ فشل في تشفير البيانات:', error);
            throw error;
        }
    }

    // فك تشفير البيانات
    async decrypt(encryptedData) {
        try {
            if (!this.isInitialized) {
                throw new Error('نظام التشفير غير مهيأ');
            }

            // تحويل من Base64
            const combined = new Uint8Array(
                atob(encryptedData).split('').map(char => char.charCodeAt(0))
            );

            // فصل IV والبيانات المشفرة
            const iv = combined.slice(0, this.ivLength);
            const data = combined.slice(this.ivLength);

            // فك تشفير البيانات
            const decryptedData = await window.crypto.subtle.decrypt(
                {
                    name: this.algorithm,
                    iv: iv
                },
                this.encryptionKey,
                data
            );

            // تحويل البيانات إلى نص
            const textDecoder = new TextDecoder();
            const decodedData = textDecoder.decode(decryptedData);
            
            console.log('🔓 تم فك تشفير البيانات بنجاح');
            return JSON.parse(decodedData);
        } catch (error) {
            console.error('❌ فشل في فك تشفير البيانات:', error);
            throw error;
        }
    }

    // تشفير النص
    async encryptText(text) {
        try {
            const data = { text: text, timestamp: Date.now() };
            return await this.encrypt(data);
        } catch (error) {
            console.error('❌ فشل في تشفير النص:', error);
            throw error;
        }
    }

    // فك تشفير النص
    async decryptText(encryptedText) {
        try {
            const data = await this.decrypt(encryptedText);
            return data.text;
        } catch (error) {
            console.error('❌ فشل في فك تشفير النص:', error);
            throw error;
        }
    }

    // تشفير الملف
    async encryptFile(file) {
        try {
            const arrayBuffer = await file.arrayBuffer();
            const data = { 
                file: Array.from(new Uint8Array(arrayBuffer)),
                name: file.name,
                type: file.type,
                size: file.size,
                timestamp: Date.now()
            };
            return await this.encrypt(data);
        } catch (error) {
            console.error('❌ فشل في تشفير الملف:', error);
            throw error;
        }
    }

    // فك تشفير الملف
    async decryptFile(encryptedFile) {
        try {
            const data = await this.decrypt(encryptedFile);
            const arrayBuffer = new Uint8Array(data.file).buffer;
            return new Blob([arrayBuffer], { type: data.type });
        } catch (error) {
            console.error('❌ فشل في فك تشفير الملف:', error);
            throw error;
        }
    }

    // تشفير الاتصالات
    async encryptCommunication(data) {
        try {
            const communicationData = {
                data: data,
                timestamp: Date.now(),
                sessionId: this.generateSessionId()
            };
            return await this.encrypt(communicationData);
        } catch (error) {
            console.error('❌ فشل في تشفير الاتصالات:', error);
            throw error;
        }
    }

    // فك تشفير الاتصالات
    async decryptCommunication(encryptedCommunication) {
        try {
            const data = await this.decrypt(encryptedCommunication);
            return data.data;
        } catch (error) {
            console.error('❌ فشل في فك تشفير الاتصالات:', error);
            throw error;
        }
    }

    // توليد معرف الجلسة
    generateSessionId() {
        const array = new Uint8Array(16);
        window.crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }

    // اختبار التشفير
    async testEncryption() {
        try {
            const testData = { message: 'Test encryption', number: 123 };
            
            // تشفير البيانات
            const encrypted = await this.encrypt(testData);
            
            // فك تشفير البيانات
            const decrypted = await this.decrypt(encrypted);
            
            // التحقق من النتيجة
            if (JSON.stringify(testData) === JSON.stringify(decrypted)) {
                console.log('✅ اختبار التشفير ناجح');
                return true;
            } else {
                throw new Error('فشل في اختبار التشفير');
            }
        } catch (error) {
            console.error('❌ فشل في اختبار التشفير:', error);
            throw error;
        }
    }

    // الحصول على حالة النظام
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            algorithm: this.algorithm,
            keyLength: this.keyLength,
            hasKey: this.encryptionKey !== null
        };
    }

    // تصدير المفتاح (للاستخدام في المكونات الأخرى)
    exportKey() {
        if (!this.encryptionKey) {
            throw new Error('لا يوجد مفتاح تشفير');
        }
        return this.encryptionKey;
    }

    // استيراد مفتاح
    async importKey(keyData) {
        try {
            this.encryptionKey = await window.crypto.subtle.importKey(
                'raw',
                keyData,
                {
                    name: this.algorithm,
                    length: this.keyLength
                },
                true,
                ['encrypt', 'decrypt']
            );
            
            console.log('🔑 تم استيراد مفتاح التشفير');
            return true;
        } catch (error) {
            console.error('❌ فشل في استيراد مفتاح التشفير:', error);
            throw error;
        }
    }
}

// إنشاء مثيل مدير التشفير
const encryptionManager = new EncryptionManager();

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    encryptionManager.initialize();
});

// تصدير النظام للاستخدام العام
window.EncryptionManager = EncryptionManager;
window.encryptionManager = encryptionManager;

console.log('🔐 تم تحميل نظام التشفير المتقدم');