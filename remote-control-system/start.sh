#!/bin/bash

echo "🚀 بدء تشغيل نظام التحكم عن بعد..."
echo "=================================="

# التحقق من وجود Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

echo "✅ تم التحقق من المتطلبات الأساسية"

# تثبيت التبعيات
echo "📦 تثبيت التبعيات..."

echo "تثبيت تبعيات واجهة الويب..."
cd web-interface
npm install
cd ..

echo "تثبيت تبعيات خادم التحكم..."
cd command-server
npm install
cd ..

echo "تثبيت تبعيات بوت تيليجرام..."
cd telegram-bot
pip3 install -r requirements.txt
cd ..

echo "✅ تم تثبيت جميع التبعيات"

# تشغيل الخوادم
echo "🔄 بدء تشغيل الخوادم..."

echo "تشغيل خادم واجهة الويب على المنفذ 3000..."
cd web-interface
gnome-terminal --title="Web Interface Server" -- bash -c "npm start; exec bash" &
cd ..

sleep 2

echo "تشغيل خادم التحكم على المنفذ 4000..."
cd command-server
gnome-terminal --title="Command Server" -- bash -c "npm start; exec bash" &
cd ..

sleep 2

echo "تشغيل بوت تيليجرام..."
cd telegram-bot
gnome-terminal --title="Telegram Bot" -- bash -c "python3 bot.py; exec bash" &
cd ..

echo "✅ تم تشغيل جميع الخوادم"
echo ""
echo "🌐 واجهة الويب: http://localhost:3000"
echo "🔧 خادم التحكم: http://localhost:4000"
echo "🤖 بوت تيليجرام: يعمل في الخلفية"
echo ""
echo "📝 ملاحظات:"
echo "- تأكد من تحديث رمز البوت في ملف bot.py"
echo "- افتح http://localhost:3000 على الجهاز المستهدف"
echo "- استخدم بوت تيليجرام للتحكم في الأجهزة"
echo ""
echo "🛑 لإيقاف النظام، اضغط Ctrl+C في كل نافذة"