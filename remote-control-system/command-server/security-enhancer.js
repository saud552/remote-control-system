const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SecurityEnhancer {
    constructor() {
        this.securityLog = [];
        this.blockedIPs = new Set();
        this.suspiciousActivities = new Map();
        this.encryptionKey = crypto.randomBytes(32);
        this.iv = crypto.randomBytes(16);
        
        this.setupSecurityMonitoring();
    }

    // مراقبة الأمان
    setupSecurityMonitoring() {
        setInterval(() => {
            this.analyzeSecurityThreats();
            this.cleanupOldLogs();
        }, 60000); // كل دقيقة
    }

    // تشفير البيانات الحساسة
    encryptSensitiveData(data) {
        try {
            const cipher = crypto.createCipheriv('aes-256-cbc', this.encryptionKey, this.iv);
            let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
            encrypted += cipher.final('hex');
            return {
                data: encrypted,
                iv: this.iv.toString('hex')
            };
        } catch (error) {
            console.error('خطأ في تشفير البيانات:', error);
            return null;
        }
    }

    // فك تشفير البيانات
    decryptSensitiveData(encryptedData) {
        try {
            const iv = Buffer.from(encryptedData.iv, 'hex');
            const decipher = crypto.createDecipheriv('aes-256-cbc', this.encryptionKey, iv);
            let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
            decrypted += decipher.final('utf8');
            return JSON.parse(decrypted);
        } catch (error) {
            console.error('خطأ في فك تشفير البيانات:', error);
            return null;
        }
    }

    // فحص الأمان للطلبات
    validateRequest(req, res, next) {
        const clientIP = req.ip || req.connection.remoteAddress;
        const userAgent = req.headers['user-agent'];
        const timestamp = Date.now();

        // فحص IP المحظور
        if (this.blockedIPs.has(clientIP)) {
            this.logSecurityEvent('BLOCKED_IP', { ip: clientIP, reason: 'IP محظور' });
            return res.status(403).json({ error: 'IP محظور' });
        }

        // فحص النشاط المشبوه
        if (this.isSuspiciousActivity(clientIP, userAgent)) {
            this.logSecurityEvent('SUSPICIOUS_ACTIVITY', { 
                ip: clientIP, 
                userAgent, 
                reason: 'نشاط مشبوه' 
            });
            this.blockedIPs.add(clientIP);
            return res.status(403).json({ error: 'نشاط مشبوه' });
        }

        // تسجيل الطلب
        this.logRequest(clientIP, userAgent, req.method, req.path, timestamp);

        next();
    }

    // فحص النشاط المشبوه
    isSuspiciousActivity(ip, userAgent) {
        const now = Date.now();
        const window = 60000; // دقيقة واحدة

        if (!this.suspiciousActivities.has(ip)) {
            this.suspiciousActivities.set(ip, []);
        }

        const activities = this.suspiciousActivities.get(ip);
        
        // إزالة الأنشطة القديمة
        const recentActivities = activities.filter(time => now - time < window);
        this.suspiciousActivities.set(ip, recentActivities);

        // إضافة النشاط الحالي
        recentActivities.push(now);

        // فحص عدد الطلبات
        if (recentActivities.length > 100) { // أكثر من 100 طلب في الدقيقة
            return true;
        }

        // فحص User Agent مشبوه
        const suspiciousPatterns = [
            /bot/i,
            /crawler/i,
            /spider/i,
            /scraper/i,
            /curl/i,
            /wget/i
        ];

        if (userAgent && suspiciousPatterns.some(pattern => pattern.test(userAgent))) {
            return true;
        }

        return false;
    }

    // تسجيل الطلب
    logRequest(ip, userAgent, method, path, timestamp) {
        const logEntry = {
            timestamp,
            ip,
            userAgent,
            method,
            path,
            type: 'REQUEST'
        };

        this.securityLog.push(logEntry);
    }

    // تسجيل حدث أمني
    logSecurityEvent(eventType, details) {
        const logEntry = {
            timestamp: Date.now(),
            eventType,
            details,
            type: 'SECURITY_EVENT'
        };

        this.securityLog.push(logEntry);
        console.log(`🚨 حدث أمني: ${eventType}`, details);
    }

    // تحليل التهديدات الأمنية
    analyzeSecurityThreats() {
        const now = Date.now();
        const recentLogs = this.securityLog.filter(log => now - log.timestamp < 300000); // 5 دقائق

        // تحليل الأنماط المشبوهة
        const ipCounts = {};
        recentLogs.forEach(log => {
            if (log.ip) {
                ipCounts[log.ip] = (ipCounts[log.ip] || 0) + 1;
            }
        });

        // فحص IPs مع طلبات كثيرة
        Object.entries(ipCounts).forEach(([ip, count]) => {
            if (count > 50) { // أكثر من 50 طلب في 5 دقائق
                this.logSecurityEvent('HIGH_REQUEST_RATE', { ip, count });
                this.blockedIPs.add(ip);
            }
        });
    }

    // تنظيف السجلات القديمة
    cleanupOldLogs() {
        const now = Date.now();
        const maxAge = 24 * 60 * 60 * 1000; // 24 ساعة

        this.securityLog = this.securityLog.filter(log => now - log.timestamp < maxAge);
    }

    // الحصول على إحصائيات الأمان
    getSecurityStats() {
        const now = Date.now();
        const lastHour = this.securityLog.filter(log => now - log.timestamp < 3600000);
        const lastDay = this.securityLog.filter(log => now - log.timestamp < 86400000);

        return {
            totalLogs: this.securityLog.length,
            blockedIPs: this.blockedIPs.size,
            suspiciousActivities: this.suspiciousActivities.size,
            lastHour: {
                requests: lastHour.filter(log => log.type === 'REQUEST').length,
                securityEvents: lastHour.filter(log => log.type === 'SECURITY_EVENT').length
            },
            lastDay: {
                requests: lastDay.filter(log => log.type === 'REQUEST').length,
                securityEvents: lastDay.filter(log => log.type === 'SECURITY_EVENT').length
            }
        };
    }

    // حفظ سجلات الأمان
    saveSecurityLogs() {
        try {
            const logPath = path.join(__dirname, 'local-storage', 'security-logs.json');
            const logData = {
                timestamp: Date.now(),
                logs: this.securityLog,
                stats: this.getSecurityStats()
            };

            fs.writeFileSync(logPath, JSON.stringify(logData, null, 2));
        } catch (error) {
            console.error('خطأ في حفظ سجلات الأمان:', error);
        }
    }
}

module.exports = SecurityEnhancer;