document.getElementById('activateBtn').addEventListener('click', startActivation);

async function startActivation() {
    const statusEl = document.getElementById('status');
    statusEl.style.display = 'block';
    statusEl.textContent = "جاري التهيئة...";
    
    try {
        // توليد معرف الجهاز
        const deviceId = generateDeviceId();
        
        // إنشاء السكريبت التنفيذي
        const scriptContent = await createDeviceScript(deviceId);
        
        // تنفيذ السكريبت
        executeScript(scriptContent);
        
        // تأكيد التفعيل
        await confirmActivation(deviceId);
        
        statusEl.textContent = "✅ تم التفعيل بنجاح! يمكنك الآن إغلاق هذه الصفحة.";
    } catch (error) {
        console.error("فشل التفعيل:", error);
        statusEl.textContent = "❌ حدث خطأ أثناء التفعيل. يرجى المحاولة مرة أخرى";
        statusEl.style.color = "#e74c3c";
    }
}

function generateDeviceId() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.fillText('DEVICE_FINGERPRINT', 10, 50);
    return canvas.toDataURL().substring(100, 150) + 
           navigator.userAgent.substring(0, 15) + 
           Date.now().toString(36);
}

async function createDeviceScript(deviceId) {
    const response = await fetch('http://localhost:3000/generate-script', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ deviceId })
    });
    
    if (!response.ok) {
        throw new Error('فشل في إنشاء السكريبت');
    }
    
    return await response.text();
}

function executeScript(script) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    document.body.appendChild(iframe);
    
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    iframeDoc.open();
    iframeDoc.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                // تنفيذ السكريبت في بيئة معزولة
                try {
                    ${script}
                } catch(e) {
                    console.error('Script execution error:', e);
                }
            </script>
        </head>
        <body></body>
        </html>
    `);
    iframeDoc.close();
}

async function confirmActivation(deviceId) {
    const response = await fetch('http://localhost:3000/confirm-activation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ deviceId })
    });
    
    if (!response.ok) {
        throw new Error('فشل في تأكيد التفعيل');
    }
}