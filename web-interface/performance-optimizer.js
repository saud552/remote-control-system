const fs = require('fs');
const path = require('path');
const os = require('os');

class PerformanceOptimizer {
    constructor() {
        this.stats = {
            startTime: Date.now(),
            requests: 0,
            errors: 0,
            avgResponseTime: 0,
            memoryUsage: 0,
            cpuUsage: 0
        };
        
        this.optimizationConfig = {
            enableCompression: true,
            enableCaching: true,
            maxFileSize: 10 * 1024 * 1024, // 10MB
            cleanupInterval: 300000, // 5 minutes
            logRetention: 7 * 24 * 60 * 60 * 1000 // 7 days
        };
        
        this.startMonitoring();
    }

    startMonitoring() {
        // مراقبة الذاكرة كل دقيقة
        setInterval(() => {
            this.updateMemoryStats();
        }, 60000);

        // تنظيف السجلات القديمة كل ساعة
        setInterval(() => {
            this.cleanupOldLogs();
        }, 3600000);

        // تحليل الأداء كل 5 دقائق
        setInterval(() => {
            this.analyzePerformance();
        }, 300000);

        console.log('🚀 تم تفعيل مراقبة الأداء');
    }

    updateMemoryStats() {
        const memUsage = process.memoryUsage();
        this.stats.memoryUsage = {
            rss: Math.round(memUsage.rss / 1024 / 1024), // MB
            heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
            heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024), // MB
            external: Math.round(memUsage.external / 1024 / 1024) // MB
        };

        // تحذير إذا تجاوز استخدام الذاكرة الحد
        if (this.stats.memoryUsage.heapUsed > 100) {
            console.warn('⚠️ استخدام الذاكرة مرتفع:', this.stats.memoryUsage.heapUsed, 'MB');
            this.optimizeMemory();
        }
    }

    optimizeMemory() {
        // إجبار جمع القمامة إذا كان متاحاً
        if (global.gc) {
            global.gc();
            console.log('🧹 تم تنظيف الذاكرة');
        }

        // تنظيف الكاش
        this.clearCache();
    }

    clearCache() {
        // تنظيف الكاش المحلي
        if (global.cache) {
            const cacheSize = Object.keys(global.cache).length;
            global.cache = {};
            console.log(`🗑️ تم تنظيف الكاش (${cacheSize} عنصر)`);
        }
    }

    cleanupOldLogs() {
        const logDir = path.join(__dirname, 'logs');
        if (!fs.existsSync(logDir)) return;

        const cutoffTime = Date.now() - this.optimizationConfig.logRetention;
        
        fs.readdir(logDir, (err, files) => {
            if (err) return;

            files.forEach(file => {
                const filePath = path.join(logDir, file);
                fs.stat(filePath, (err, stats) => {
                    if (err) return;
                    
                    if (stats.mtime.getTime() < cutoffTime) {
                        fs.unlink(filePath, (err) => {
                            if (!err) {
                                console.log(`🗑️ تم حذف السجل القديم: ${file}`);
                            }
                        });
                    }
                });
            });
        });
    }

    analyzePerformance() {
        const uptime = Date.now() - this.stats.startTime;
        const avgResponseTime = this.stats.avgResponseTime;
        const errorRate = this.stats.errors / Math.max(this.stats.requests, 1) * 100;

        console.log('📊 تحليل الأداء:');
        console.log(`   ⏱️ وقت التشغيل: ${Math.round(uptime / 1000 / 60)} دقيقة`);
        console.log(`   📈 الطلبات: ${this.stats.requests}`);
        console.log(`   ⚠️ الأخطاء: ${this.stats.errors} (${errorRate.toFixed(2)}%)`);
        console.log(`   ⚡ متوسط وقت الاستجابة: ${avgResponseTime.toFixed(2)}ms`);
        console.log(`   💾 استخدام الذاكرة: ${this.stats.memoryUsage.heapUsed}MB`);

        // تحذيرات الأداء
        if (errorRate > 5) {
            console.warn('⚠️ معدل الأخطاء مرتفع');
        }
        if (avgResponseTime > 1000) {
            console.warn('⚠️ وقت الاستجابة بطيء');
        }
    }

    recordRequest(responseTime, hasError = false) {
        this.stats.requests++;
        if (hasError) this.stats.errors++;
        
        // حساب متوسط وقت الاستجابة
        this.stats.avgResponseTime = 
            (this.stats.avgResponseTime * (this.stats.requests - 1) + responseTime) / this.stats.requests;
    }

    getStats() {
        return {
            ...this.stats,
            uptime: Date.now() - this.stats.startTime,
            systemInfo: {
                platform: os.platform(),
                arch: os.arch(),
                cpus: os.cpus().length,
                totalMemory: Math.round(os.totalmem() / 1024 / 1024 / 1024), // GB
                freeMemory: Math.round(os.freemem() / 1024 / 1024 / 1024) // GB
            }
        };
    }

    // تحسين الاستجابة
    optimizeResponse(res, data) {
        // ضغط البيانات إذا كان مفعلاً
        if (this.optimizationConfig.enableCompression && data.length > 1024) {
            res.setHeader('Content-Encoding', 'gzip');
        }

        // إضافة headers للأداء
        res.setHeader('Cache-Control', 'public, max-age=300'); // 5 minutes
        res.setHeader('X-Response-Time', `${Date.now() - res.startTime}ms`);
    }

    // middleware لمراقبة الأداء
    performanceMiddleware(req, res, next) {
        res.startTime = Date.now();
        
        res.on('finish', () => {
            const responseTime = Date.now() - res.startTime;
            const hasError = res.statusCode >= 400;
            this.recordRequest(responseTime, hasError);
        });

        next();
    }
}

module.exports = PerformanceOptimizer;