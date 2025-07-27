const os = require('os');
const fs = require('fs');
const path = require('path');

class PerformanceOptimizer {
    constructor() {
        this.metrics = {
            startTime: Date.now(),
            requests: 0,
            errors: 0,
            responseTimes: [],
            memoryUsage: [],
            cpuUsage: [],
            connections: 0,
            maxConnections: 0
        };

        this.optimizationSettings = {
            maxResponseTime: 5000, // 5 ثوان
            maxMemoryUsage: 0.8, // 80% من الذاكرة المتاحة
            maxCPUUsage: 0.9, // 90% من المعالج
            cleanupInterval: 300000, // 5 دقائق
            logRetention: 24 * 60 * 60 * 1000 // 24 ساعة
        };

        this.setupPerformanceMonitoring();
    }

    // إعداد مراقبة الأداء
    setupPerformanceMonitoring() {
        // مراقبة الذاكرة والمعالج
        setInterval(() => {
            this.collectSystemMetrics();
        }, 30000); // كل 30 ثانية

        // تنظيف البيانات القديمة
        setInterval(() => {
            this.cleanupOldMetrics();
        }, this.optimizationSettings.cleanupInterval);

        // تحليل الأداء
        setInterval(() => {
            this.analyzePerformance();
        }, 60000); // كل دقيقة
    }

    // جمع مقاييس النظام
    collectSystemMetrics() {
        const memoryUsage = process.memoryUsage();
        const cpuUsage = os.loadavg()[0] / os.cpus().length;

        this.metrics.memoryUsage.push({
            timestamp: Date.now(),
            rss: memoryUsage.rss,
            heapTotal: memoryUsage.heapTotal,
            heapUsed: memoryUsage.heapUsed,
            external: memoryUsage.external,
            percentage: memoryUsage.heapUsed / memoryUsage.heapTotal
        });

        this.metrics.cpuUsage.push({
            timestamp: Date.now(),
            load: cpuUsage,
            percentage: cpuUsage
        });

        // الاحتفاظ بآخر 100 قياس فقط
        if (this.metrics.memoryUsage.length > 100) {
            this.metrics.memoryUsage = this.metrics.memoryUsage.slice(-100);
        }

        if (this.metrics.cpuUsage.length > 100) {
            this.metrics.cpuUsage = this.metrics.cpuUsage.slice(-100);
        }
    }

    // تسجيل طلب جديد
    recordRequest(responseTime) {
        this.metrics.requests++;
        this.metrics.responseTimes.push({
            timestamp: Date.now(),
            duration: responseTime
        });

        // الاحتفاظ بآخر 1000 قياس فقط
        if (this.metrics.responseTimes.length > 1000) {
            this.metrics.responseTimes = this.metrics.responseTimes.slice(-1000);
        }
    }

    // تسجيل خطأ
    recordError(error) {
        this.metrics.errors++;
        console.error('❌ خطأ في الأداء:', error);
    }

    // تسجيل اتصال جديد
    recordConnection() {
        this.metrics.connections++;
        if (this.metrics.connections > this.metrics.maxConnections) {
            this.metrics.maxConnections = this.metrics.connections;
        }
    }

    // تسجيل انقطاع اتصال
    recordDisconnection() {
        if (this.metrics.connections > 0) {
            this.metrics.connections--;
        }
    }

    // تحليل الأداء
    analyzePerformance() {
        const now = Date.now();
        const recentResponseTimes = this.metrics.responseTimes.filter(
            rt => now - rt.timestamp < 300000 // آخر 5 دقائق
        );

        if (recentResponseTimes.length === 0) return;

        const avgResponseTime = recentResponseTimes.reduce(
            (sum, rt) => sum + rt.duration, 0
        ) / recentResponseTimes.length;

        const maxResponseTime = Math.max(...recentResponseTimes.map(rt => rt.duration));
        const minResponseTime = Math.min(...recentResponseTimes.map(rt => rt.duration));

        // فحص الأداء
        if (avgResponseTime > this.optimizationSettings.maxResponseTime) {
            console.warn(`⚠️ متوسط وقت الاستجابة مرتفع: ${avgResponseTime.toFixed(2)}ms`);
        }

        // فحص الذاكرة
        const currentMemory = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1];
        if (currentMemory && currentMemory.percentage > this.optimizationSettings.maxMemoryUsage) {
            console.warn(`⚠️ استخدام الذاكرة مرتفع: ${(currentMemory.percentage * 100).toFixed(2)}%`);
            this.optimizeMemory();
        }

        // فحص المعالج
        const currentCPU = this.metrics.cpuUsage[this.metrics.cpuUsage.length - 1];
        if (currentCPU && currentCPU.percentage > this.optimizationSettings.maxCPUUsage) {
            console.warn(`⚠️ استخدام المعالج مرتفع: ${(currentCPU.percentage * 100).toFixed(2)}%`);
        }

        // حفظ الإحصائيات
        this.savePerformanceStats({
            timestamp: now,
            avgResponseTime,
            maxResponseTime,
            minResponseTime,
            requests: recentResponseTimes.length,
            errors: this.metrics.errors,
            connections: this.metrics.connections,
            memoryUsage: currentMemory,
            cpuUsage: currentCPU
        });
    }

    // تحسين الذاكرة
    optimizeMemory() {
        // تشغيل garbage collection إذا كان متاحاً
        if (global.gc) {
            global.gc();
            console.log('🧹 تم تشغيل garbage collection');
        }

        // تنظيف البيانات المؤقتة
        this.metrics.responseTimes = this.metrics.responseTimes.slice(-500);
        this.metrics.memoryUsage = this.metrics.memoryUsage.slice(-50);
        this.metrics.cpuUsage = this.metrics.cpuUsage.slice(-50);
    }

    // تنظيف المقاييس القديمة
    cleanupOldMetrics() {
        const now = Date.now();
        const cutoff = now - this.optimizationSettings.logRetention;

        this.metrics.responseTimes = this.metrics.responseTimes.filter(
            rt => rt.timestamp > cutoff
        );

        this.metrics.memoryUsage = this.metrics.memoryUsage.filter(
            mu => mu.timestamp > cutoff
        );

        this.metrics.cpuUsage = this.metrics.cpuUsage.filter(
            cu => cu.timestamp > cutoff
        );
    }

    // الحصول على إحصائيات الأداء
    getPerformanceStats() {
        const now = Date.now();
        const uptime = now - this.metrics.startTime;

        const recentResponseTimes = this.metrics.responseTimes.filter(
            rt => now - rt.timestamp < 300000 // آخر 5 دقائق
        );

        const avgResponseTime = recentResponseTimes.length > 0 
            ? recentResponseTimes.reduce((sum, rt) => sum + rt.duration, 0) / recentResponseTimes.length
            : 0;

        const currentMemory = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1];
        const currentCPU = this.metrics.cpuUsage[this.metrics.cpuUsage.length - 1];

        return {
            uptime,
            requests: {
                total: this.metrics.requests,
                recent: recentResponseTimes.length,
                errors: this.metrics.errors,
                errorRate: this.metrics.requests > 0 ? (this.metrics.errors / this.metrics.requests * 100).toFixed(2) : 0
            },
            responseTime: {
                average: avgResponseTime.toFixed(2),
                min: recentResponseTimes.length > 0 ? Math.min(...recentResponseTimes.map(rt => rt.duration)) : 0,
                max: recentResponseTimes.length > 0 ? Math.max(...recentResponseTimes.map(rt => rt.duration)) : 0
            },
            connections: {
                current: this.metrics.connections,
                max: this.metrics.maxConnections
            },
            system: {
                memory: currentMemory ? {
                    rss: this.formatBytes(currentMemory.rss),
                    heapUsed: this.formatBytes(currentMemory.heapUsed),
                    heapTotal: this.formatBytes(currentMemory.heapTotal),
                    percentage: (currentMemory.percentage * 100).toFixed(2)
                } : null,
                cpu: currentCPU ? {
                    load: currentCPU.load.toFixed(2),
                    percentage: (currentCPU.percentage * 100).toFixed(2)
                } : null,
                platform: os.platform(),
                arch: os.arch(),
                cpus: os.cpus().length,
                totalMemory: this.formatBytes(os.totalmem()),
                freeMemory: this.formatBytes(os.freemem())
            }
        };
    }

    // تنسيق البايت
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // حفظ إحصائيات الأداء
    savePerformanceStats(stats) {
        try {
            const statsPath = path.join(__dirname, 'local-storage', 'performance-stats.json');
            const existingStats = fs.existsSync(statsPath) 
                ? JSON.parse(fs.readFileSync(statsPath, 'utf8'))
                : { history: [] };

            existingStats.history.push(stats);
            existingStats.lastUpdate = Date.now();

            // الاحتفاظ بآخر 1000 إحصائية فقط
            if (existingStats.history.length > 1000) {
                existingStats.history = existingStats.history.slice(-1000);
            }

            fs.writeFileSync(statsPath, JSON.stringify(existingStats, null, 2));
        } catch (error) {
            console.error('خطأ في حفظ إحصائيات الأداء:', error);
        }
    }

    // middleware لقياس الأداء
    performanceMiddleware() {
        return (req, res, next) => {
            const startTime = Date.now();
            
            res.on('finish', () => {
                const responseTime = Date.now() - startTime;
                this.recordRequest(responseTime);
            });

            next();
        };
    }
}

module.exports = PerformanceOptimizer;