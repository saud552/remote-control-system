#!/bin/bash

# Remote Control Client Startup Script
# سكريبت تشغيل عميل التحكم عن بعد

echo "🔧 Remote Control Client - عميل التحكم عن بعد"
echo "=============================================="

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python3 أولاً."
    exit 1
fi

# التحقق من وجود الملفات المطلوبة
if [ ! -f "client.py" ]; then
    echo "❌ ملف client.py غير موجود."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ ملف requirements.txt غير موجود."
    exit 1
fi

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# طلب معلومات الاتصال
echo ""
echo "🌐 إعداد الاتصال:"
read -p "أدخل عنوان IP الخادم (مثال: 192.168.1.100): " SERVER_IP
read -p "أدخل معرف الجهاز (مثال: MY-PHONE-001): " DEVICE_ID

# التحقق من المدخلات
if [ -z "$SERVER_IP" ] || [ -z "$DEVICE_ID" ]; then
    echo "❌ يرجى إدخال جميع المعلومات المطلوبة."
    exit 1
fi

# تشغيل العميل
echo ""
echo "🚀 تشغيل العميل..."
echo "الخادم: $SERVER_IP"
echo "معرف الجهاز: $DEVICE_ID"
echo ""

python3 client.py "ws://$SERVER_IP:8080" "$DEVICE_ID"