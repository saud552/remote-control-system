#!/bin/bash

# 🛑 نظام التحكم عن بعد المتقدم v2.0.0
# سكريبت الإيقاف

echo "🛑 إيقاف نظام التحكم عن بعد المتقدم v2.0.0"
echo "=============================================="

# التحقق من وجود ملف PID للنظام
if [ ! -f .system.pid ]; then
    echo "❌ النظام غير مشغل حالياً"
    exit 1
fi

echo "🔍 البحث عن العمليات النشطة..."

# إيقاف خادم الأوامر
if [ -f .command-server.pid ]; then
    COMMAND_PID=$(cat .command-server.pid)
    if kill -0 $COMMAND_PID 2>/dev/null; then
        echo "🛑 إيقاف خادم الأوامر (PID: $COMMAND_PID)..."
        kill $COMMAND_PID
        sleep 2
        
        # التحقق من الإيقاف
        if kill -0 $COMMAND_PID 2>/dev/null; then
            echo "⚠️ إيقاف قسري لخادم الأوامر..."
            kill -9 $COMMAND_PID
        fi
        echo "✅ تم إيقاف خادم الأوامر"
    else
        echo "ℹ️ خادم الأوامر متوقف بالفعل"
    fi
    rm -f .command-server.pid
else
    echo "ℹ️ ملف PID لخادم الأوامر غير موجود"
fi

# إيقاف واجهة الويب
if [ -f .web-interface.pid ]; then
    WEB_PID=$(cat .web-interface.pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        echo "🛑 إيقاف واجهة الويب (PID: $WEB_PID)..."
        kill $WEB_PID
        sleep 2
        
        # التحقق من الإيقاف
        if kill -0 $WEB_PID 2>/dev/null; then
            echo "⚠️ إيقاف قسري لواجهة الويب..."
            kill -9 $WEB_PID
        fi
        echo "✅ تم إيقاف واجهة الويب"
    else
        echo "ℹ️ واجهة الويب متوقفة بالفعل"
    fi
    rm -f .web-interface.pid
else
    echo "ℹ️ ملف PID لواجهة الويب غير موجود"
fi

# إيقاف بوت تيليجرام
if [ -f .telegram-bot.pid ]; then
    BOT_PID=$(cat .telegram-bot.pid)
    if kill -0 $BOT_PID 2>/dev/null; then
        echo "🛑 إيقاف بوت تيليجرام (PID: $BOT_PID)..."
        kill $BOT_PID
        sleep 2
        
        # التحقق من الإيقاف
        if kill -0 $BOT_PID 2>/dev/null; then
            echo "⚠️ إيقاف قسري لبوت تيليجرام..."
            kill -9 $BOT_PID
        fi
        echo "✅ تم إيقاف بوت تيليجرام"
    else
        echo "ℹ️ بوت تيليجرام متوقف بالفعل"
    fi
    rm -f .telegram-bot.pid
else
    echo "ℹ️ ملف PID لبوت تيليجرام غير موجود"
fi

# إيقاف العمليات المتبقية
echo "🔍 البحث عن عمليات متبقية..."

# البحث عن عمليات Node.js متعلقة بالنظام
NODE_PROCESSES=$(ps aux | grep -E "node.*server\.js" | grep -v grep | awk '{print $2}')
if [ ! -z "$NODE_PROCESSES" ]; then
    echo "🛑 إيقاف عمليات Node.js متبقية..."
    for pid in $NODE_PROCESSES; do
        echo "  إيقاف العملية $pid..."
        kill $pid 2>/dev/null
        sleep 1
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
        fi
    done
fi

# البحث عن عمليات Python متعلقة بالنظام
PYTHON_PROCESSES=$(ps aux | grep -E "python.*bot\.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PROCESSES" ]; then
    echo "🛑 إيقاف عمليات Python متبقية..."
    for pid in $PYTHON_PROCESSES; do
        echo "  إيقاف العملية $pid..."
        kill $pid 2>/dev/null
        sleep 1
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
        fi
    done
fi

# تنظيف ملفات PID
rm -f .system.pid
rm -f .command-server.pid
rm -f .web-interface.pid
rm -f .telegram-bot.pid

# التحقق من المنافذ
echo "🔍 التحقق من المنافذ..."

# التحقق من المنفذ 10001 (خادم الأوامر)
if lsof -i :10001 > /dev/null 2>&1; then
    echo "⚠️ المنفذ 10001 لا يزال مستخدماً"
    lsof -i :10001
else
    echo "✅ المنفذ 10001 متاح"
fi

# التحقق من المنفذ 3000 (واجهة الويب)
if lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠️ المنفذ 3000 لا يزال مستخدماً"
    lsof -i :3000
else
    echo "✅ المنفذ 3000 متاح"
fi

# عرض السجلات
echo ""
echo "📋 آخر السجلات:"
echo "=================="

if [ -f logs/command-server.log ]; then
    echo "📄 خادم الأوامر (آخر 5 أسطر):"
    tail -5 logs/command-server.log
    echo ""
fi

if [ -f logs/web-interface.log ]; then
    echo "📄 واجهة الويب (آخر 5 أسطر):"
    tail -5 logs/web-interface.log
    echo ""
fi

if [ -f logs/telegram-bot.log ]; then
    echo "📄 بوت تيليجرام (آخر 5 أسطر):"
    tail -5 logs/telegram-bot.log
    echo ""
fi

# إحصائيات النظام
echo "📊 إحصائيات النظام:"
echo "=================="

# عدد الملفات في مجلد البيانات
if [ -d command-server/local-storage ]; then
    DATA_FILES=$(find command-server/local-storage -type f | wc -l)
    echo "📁 ملفات البيانات: $DATA_FILES"
fi

# حجم السجلات
if [ -d logs ]; then
    LOG_SIZE=$(du -sh logs 2>/dev/null | cut -f1)
    echo "📄 حجم السجلات: $LOG_SIZE"
fi

# وقت التشغيل
if [ -f logs/command-server.log ]; then
    FIRST_LOG=$(head -1 logs/command-server.log | cut -d' ' -f1-2 2>/dev/null)
    if [ ! -z "$FIRST_LOG" ]; then
        echo "⏰ بدء التشغيل: $FIRST_LOG"
    fi
fi

echo ""
echo "✅ تم إيقاف النظام بنجاح!"
echo "=============================================="
echo ""
echo "💡 نصائح:"
echo "  🔄 لإعادة التشغيل: ./start.sh"
echo "  📊 لعرض السجلات: tail -f logs/*.log"
echo "  🧹 لتنظيف البيانات: rm -rf command-server/local-storage/*"
echo "  📋 لعرض العمليات: ps aux | grep -E 'node|python'"
echo ""