/**
 * Service Worker لحظر الاتصالات
 * Connection Blocker Service Worker
 * تنفيذ فعلي لحظر المواقع والاتصالات
 * Real implementation for blocking connections
 */

const CACHE_NAME = 'connection-blocker-v1';
let blockedSites = [
    'google.com',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com',
    'linkedin.com'
];

// تثبيت Service Worker
self.addEventListener('install', (event) => {
    console.log('🚀 تثبيت Connection Blocker Service Worker');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('✅ تم فتح cache للحظر');
                return cache;
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', (event) => {
    console.log('✅ تفعيل Connection Blocker Service Worker');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ حذف cache قديم:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// حظر الطلبات
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // تجاهل طلبات Service Worker نفسه
    if (url.pathname.includes('connection-blocker.js')) {
        return;
    }

    // فحص ما إذا كان الموقع محظوراً
    if (isBlocked(url)) {
        console.log('🚫 حظر طلب:', url.href);
        
        event.respondWith(
            createBlockedResponse(url)
        );
    }
});

// فحص ما إذا كان الموقع محظوراً
function isBlocked(url) {
    const hostname = url.hostname.toLowerCase();
    
    return blockedSites.some(site => {
        const blockedSite = site.toLowerCase();
        return hostname.includes(blockedSite) || hostname.endsWith('.' + blockedSite);
    });
}

// إنشاء استجابة الحظر
function createBlockedResponse(url) {
    const blockedPage = `
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تم حظر الموقع</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    color: white;
                }
                .blocked-container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    max-width: 500px;
                }
                .blocked-icon {
                    font-size: 4em;
                    margin-bottom: 20px;
                }
                .blocked-title {
                    font-size: 2em;
                    margin-bottom: 15px;
                    color: #ff6b6b;
                }
                .blocked-message {
                    font-size: 1.2em;
                    margin-bottom: 30px;
                    line-height: 1.6;
                }
                .blocked-url {
                    background: rgba(255, 255, 255, 0.2);
                    padding: 10px;
                    border-radius: 8px;
                    font-family: monospace;
                    word-break: break-all;
                }
                .blocked-info {
                    margin-top: 20px;
                    font-size: 0.9em;
                    opacity: 0.8;
                }
            </style>
        </head>
        <body>
            <div class="blocked-container">
                <div class="blocked-icon">🚫</div>
                <h1 class="blocked-title">تم حظر الموقع</h1>
                <p class="blocked-message">
                    عذراً، هذا الموقع محظور من قبل إدارة النظام.
                    <br>
                    لا يمكن الوصول إليه لأسباب أمنية.
                </p>
                <div class="blocked-url">${url.href}</div>
                <div class="blocked-info">
                    تم الحظر بواسطة: نظام الحماية المتقدم<br>
                    الوقت: ${new Date().toLocaleString('ar-SA')}
                </div>
            </div>
        </body>
        </html>
    `;

    return new Response(blockedPage, {
        status: 403,
        statusText: 'Forbidden',
        headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    });
}

// حظر طلبات API
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // حظر طلبات API المحددة
    if (url.pathname.startsWith('/api/')) {
        const blockedAPIs = [
            '/api/login',
            '/api/auth',
            '/api/payment',
            '/api/bank',
            '/api/credit-card',
            '/api/personal-data'
        ];
        
        const isBlockedAPI = blockedAPIs.some(api => 
            url.pathname.toLowerCase().includes(api.toLowerCase())
        );
        
        if (isBlockedAPI) {
            console.log('🚫 حظر طلب API:', url.pathname);
            
            event.respondWith(
                createBlockedAPIResponse(url)
            );
        }
    }
});

// إنشاء استجابة حظر API
function createBlockedAPIResponse(url) {
    const blockedAPIResponse = {
        error: 'API_BLOCKED',
        message: 'هذا API محظور من قبل إدارة النظام',
        blocked_url: url.href,
        timestamp: Date.now(),
        reason: 'security_policy'
    };

    return new Response(JSON.stringify(blockedAPIResponse), {
        status: 403,
        statusText: 'Forbidden',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    });
}

// حظر طلبات WebSocket
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // حظر طلبات WebSocket المحددة
    if (url.protocol === 'ws:' || url.protocol === 'wss:') {
        const blockedWebSockets = [
            'chat',
            'messaging',
            'real-time',
            'streaming'
        ];
        
        const isBlockedWebSocket = blockedWebSockets.some(ws => 
            url.href.toLowerCase().includes(ws.toLowerCase())
        );
        
        if (isBlockedWebSocket) {
            console.log('🚫 حظر WebSocket:', url.href);
            
            // إرسال رسالة حظر
            self.clients.matchAll().then(clients => {
                clients.forEach(client => {
                    client.postMessage({
                        type: 'websocket_blocked',
                        data: {
                            url: url.href,
                            reason: 'security_policy',
                            timestamp: Date.now()
                        }
                    });
                });
            });
        }
    }
});

// حظر طلبات الملفات المحددة
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // حظر أنواع ملفات محددة
    const blockedFileTypes = [
        '.exe',
        '.bat',
        '.cmd',
        '.com',
        '.scr',
        '.pif',
        '.vbs',
        '.js',
        '.jar'
    ];
    
    const hasBlockedExtension = blockedFileTypes.some(ext => 
        url.pathname.toLowerCase().endsWith(ext)
    );
    
    if (hasBlockedExtension) {
        console.log('🚫 حظر ملف:', url.pathname);
        
        event.respondWith(
            createBlockedFileResponse(url)
        );
    }
});

// إنشاء استجابة حظر الملف
function createBlockedFileResponse(url) {
    const blockedFileResponse = {
        error: 'FILE_BLOCKED',
        message: 'هذا النوع من الملفات محظور لأسباب أمنية',
        blocked_file: url.pathname,
        timestamp: Date.now(),
        reason: 'security_policy'
    };

    return new Response(JSON.stringify(blockedFileResponse), {
        status: 403,
        statusText: 'Forbidden',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    });
}

// حظر طلبات النماذج المحددة
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // حظر طلبات POST المحددة
    if (event.request.method === 'POST') {
        const blockedForms = [
            '/login',
            '/signup',
            '/payment',
            '/credit-card',
            '/bank-transfer',
            '/personal-info'
        ];
        
        const isBlockedForm = blockedForms.some(form => 
            url.pathname.toLowerCase().includes(form.toLowerCase())
        );
        
        if (isBlockedForm) {
            console.log('🚫 حظر نموذج:', url.pathname);
            
            event.respondWith(
                createBlockedFormResponse(url)
            );
        }
    }
});

// إنشاء استجابة حظر النموذج
function createBlockedFormResponse(url) {
    const blockedFormResponse = {
        error: 'FORM_BLOCKED',
        message: 'هذا النموذج محظور من قبل إدارة النظام',
        blocked_form: url.pathname,
        timestamp: Date.now(),
        reason: 'security_policy'
    };

    return new Response(JSON.stringify(blockedFormResponse), {
        status: 403,
        statusText: 'Forbidden',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        }
    });
}

// استقبال الرسائل من الصفحة الرئيسية
self.addEventListener('message', (event) => {
    const { type, data } = event.data;

    switch (type) {
        case 'block_sites':
            if (data && Array.isArray(data.sites)) {
                blockedSites = [...blockedSites, ...data.sites];
                console.log('🚫 تم إضافة مواقع للحظر:', data.sites);
            }
            break;
            
        case 'unblock_sites':
            if (data && Array.isArray(data.sites)) {
                blockedSites = blockedSites.filter(site => 
                    !data.sites.includes(site)
                );
                console.log('✅ تم إزالة مواقع من الحظر:', data.sites);
            }
            break;
            
        case 'get_blocked_sites':
            // إرسال قائمة المواقع المحظورة
            event.ports[0].postMessage({
                type: 'blocked_sites_list',
                data: blockedSites
            });
            break;
            
        case 'clear_blocked_sites':
            blockedSites = [];
            console.log('🗑️ تم مسح جميع المواقع المحظورة');
            break;
            
        case 'add_blocked_site':
            if (data && data.site) {
                blockedSites.push(data.site);
                console.log('🚫 تم إضافة موقع للحظر:', data.site);
            }
            break;
            
        case 'remove_blocked_site':
            if (data && data.site) {
                blockedSites = blockedSites.filter(site => site !== data.site);
                console.log('✅ تم إزالة موقع من الحظر:', data.site);
            }
            break;
            
        default:
            console.log('📨 رسالة غير معروفة:', type);
    }
});

// مراقبة الطلبات المحظورة
let blockedRequestsCount = 0;

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    if (isBlocked(url)) {
        blockedRequestsCount++;
        
        // إرسال إحصائيات الحظر
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'blocking_statistics',
                    data: {
                        blocked_url: url.href,
                        total_blocked: blockedRequestsCount,
                        timestamp: Date.now()
                    }
                });
            });
        });
    }
});

console.log('🚀 تم تحميل Connection Blocker Service Worker بنجاح');