const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SecurityManager {
    constructor() {
        this.securityConfig = {
            enableEncryption: true,
            enableRateLimit: true,
            enableLogging: true,
            maxRequestsPerMinute: 100,
            sessionTimeout: 30 * 60 * 1000, // 30 minutes
            encryptionKey: crypto.randomBytes(32).toString('hex'),
            blockedIPs: new Set(),
            suspiciousActivities: new Map()
        };
        
        this.securityLog = [];
        this.rateLimitMap = new Map();
        
        this.startSecurityMonitoring();
    }

    startSecurityMonitoring() {
        // تنظيف IPs المحظورة كل ساعة
        setInterval(() => {
            this.cleanupBlockedIPs();
        }, 3600000);

        // تنظيف السجلات الأمنية كل يوم
        setInterval(() => {
            this.cleanupSecurityLogs();
        }, 24 * 3600000);

        // تحليل النشاط المشبوه كل 5 دقائق
        setInterval(() => {
            this.analyzeSuspiciousActivity();
        }, 300000);

        console.log('🛡️ تم تفعيل مدير الأمان');
    }

    // تشفير البيانات
    encryptData(data) {
        try {
                const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(this.securityConfig.encryptionKey, 'hex'), iv);
            let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
            encrypted += cipher.final('hex');
            return iv.toString('hex') + ':' + encrypted;
        } catch (error) {
            console.error('خطأ في تشفير البيانات:', error);
            return null;
        }
    }

    // فك تشفير البيانات
    decryptData(encryptedData) {
        try {
            const [ivHex, encrypted] = encryptedData.split(':');
            const iv = Buffer.from(ivHex, 'hex');
            const decipher = crypto.createDecipheriv('aes-256-gcm', Buffer.from(this.securityConfig.encryptionKey, 'hex'), iv);
            let decrypted = decipher.update(encrypted, 'hex', 'utf8');
            decrypted += decipher.final('utf8');
            return JSON.parse(decrypted);
        } catch (error) {
            console.error('خطأ في فك تشفير البيانات:', error);
            return null;
        }
    }

    // فحص Rate Limit
    checkRateLimit(ip) {
        const now = Date.now();
        const minuteAgo = now - 60000;
        
        if (!this.rateLimitMap.has(ip)) {
            this.rateLimitMap.set(ip, []);
        }
        
        const requests = this.rateLimitMap.get(ip);
        
        // إزالة الطلبات القديمة
        const recentRequests = requests.filter(time => time > minuteAgo);
        this.rateLimitMap.set(ip, recentRequests);
        
        // إضافة الطلب الحالي
        recentRequests.push(now);
        
        // فحص الحد الأقصى
        if (recentRequests.length > this.securityConfig.maxRequestsPerMinute) {
            this.blockIP(ip, 'Rate limit exceeded');
            return false;
        }
        
        return true;
    }

    // حظر IP
    blockIP(ip, reason) {
        this.securityConfig.blockedIPs.add(ip);
        this.logSecurityEvent('IP_BLOCKED', { ip, reason });
        console.log(`🚫 تم حظر IP: ${ip} - السبب: ${reason}`);
    }

    // فحص IP محظور
    isIPBlocked(ip) {
        return this.securityConfig.blockedIPs.has(ip);
    }

    // تنظيف IPs المحظورة
    cleanupBlockedIPs() {
        // إزالة الحظر بعد ساعة
        const oneHourAgo = Date.now() - 3600000;
        this.securityLog.forEach(log => {
            if (log.type === 'IP_BLOCKED' && log.timestamp < oneHourAgo) {
                this.securityConfig.blockedIPs.delete(log.data.ip);
            }
        });
    }

    // تسجيل الأحداث الأمنية
    logSecurityEvent(type, data) {
        const event = {
            type,
            data,
            timestamp: Date.now(),
            ip: data.ip || 'unknown'
        };
        
        this.securityLog.push(event);
        
        // حفظ في الملف
        this.saveSecurityLog(event);
    }

    // حفظ السجل الأمني
    saveSecurityLog(event) {
        const logDir = path.join(__dirname, 'security-logs');
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        const logFile = path.join(logDir, `security-${new Date().toISOString().split('T')[0]}.json`);
        
        try {
            let logs = [];
            if (fs.existsSync(logFile)) {
                logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
            }
            
            logs.push(event);
            fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
        } catch (error) {
            console.error('خطأ في حفظ السجل الأمني:', error);
        }
    }

    // تنظيف السجلات الأمنية
    cleanupSecurityLogs() {
        const logDir = path.join(__dirname, 'security-logs');
        if (!fs.existsSync(logDir)) return;

        const oneWeekAgo = Date.now() - 7 * 24 * 3600000;
        
        fs.readdir(logDir, (err, files) => {
            if (err) return;

            files.forEach(file => {
                const filePath = path.join(logDir, file);
                fs.stat(filePath, (err, stats) => {
                    if (err) return;
                    
                    if (stats.mtime.getTime() < oneWeekAgo) {
                        fs.unlink(filePath, (err) => {
                            if (!err) {
                                console.log(`🗑️ تم حذف السجل الأمني القديم: ${file}`);
                            }
                        });
                    }
                });
            });
        });
    }

    // تحليل النشاط المشبوه
    analyzeSuspiciousActivity() {
        const now = Date.now();
        const fiveMinutesAgo = now - 300000;
        
        // تجميع النشاط حسب IP
        const activityByIP = new Map();
        
        this.securityLog
            .filter(log => log.timestamp > fiveMinutesAgo)
            .forEach(log => {
                if (!activityByIP.has(log.ip)) {
                    activityByIP.set(log.ip, []);
                }
                activityByIP.get(log.ip).push(log);
            });
        
        // فحص النشاط المشبوه
        activityByIP.forEach((activities, ip) => {
            const errorCount = activities.filter(a => a.type === 'ERROR').length;
            const failedAuthCount = activities.filter(a => a.type === 'AUTH_FAILED').length;
            
            if (errorCount > 10 || failedAuthCount > 5) {
                this.blockIP(ip, 'Suspicious activity detected');
            }
        });
    }

    // فحص الأمان للطلب
    securityMiddleware(req, res, next) {
        const clientIP = req.ip || req.connection.remoteAddress;
        
        // فحص IP محظور
        if (this.isIPBlocked(clientIP)) {
            this.logSecurityEvent('BLOCKED_REQUEST', { ip: clientIP, path: req.path });
            return res.status(403).json({ error: 'Access denied' });
        }
        
        // فحص Rate Limit
        if (!this.checkRateLimit(clientIP)) {
            return res.status(429).json({ error: 'Too many requests' });
        }
        
        // فحص User Agent مشبوه
        const userAgent = req.get('User-Agent');
        if (this.isSuspiciousUserAgent(userAgent)) {
            this.logSecurityEvent('SUSPICIOUS_UA', { ip: clientIP, userAgent });
        }
        
        // فحص Referer مشبوه
        const referer = req.get('Referer');
        if (referer && this.isSuspiciousReferer(referer)) {
            this.logSecurityEvent('SUSPICIOUS_REFERER', { ip: clientIP, referer });
        }
        
        next();
    }

    // فحص User Agent مشبوه
    isSuspiciousUserAgent(userAgent) {
        if (!userAgent) return true;
        
        const suspiciousPatterns = [
            /bot/i,
            /crawler/i,
            /spider/i,
            /scraper/i,
            /curl/i,
            /wget/i
        ];
        
        return suspiciousPatterns.some(pattern => pattern.test(userAgent));
    }

    // فحص Referer مشبوه
    isSuspiciousReferer(referer) {
        const suspiciousDomains = [
            'malicious-site.com',
            'spam-site.com',
            'fake-site.com'
        ];
        
        return suspiciousDomains.some(domain => referer.includes(domain));
    }

    // الحصول على إحصائيات الأمان
    getSecurityStats() {
        const now = Date.now();
        const oneHourAgo = now - 3600000;
        const oneDayAgo = now - 24 * 3600000;
        
        const recentLogs = this.securityLog.filter(log => log.timestamp > oneHourAgo);
        const dailyLogs = this.securityLog.filter(log => log.timestamp > oneDayAgo);
        
        return {
            blockedIPs: this.securityConfig.blockedIPs.size,
            recentEvents: recentLogs.length,
            dailyEvents: dailyLogs.length,
            rateLimitMap: this.rateLimitMap.size,
            securityLogSize: this.securityLog.length
        };
    }
}

module.exports = SecurityManager;