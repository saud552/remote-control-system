#!/bin/bash

# نظام التحكم في الأجهزة - سكريبت الإيقاف
# إيقاف جميع الخوادم والخدمات

# ألوان للعرض
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# مسارات النظام
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$PROJECT_DIR/logs"

echo -e "${BLUE}🛑 إيقاف نظام التحكم في الأجهزة...${NC}"
echo "=================================="

# إيقاف خادم واجهة الويب
if [ -f "$LOGS_DIR/web-interface.pid" ]; then
    WEB_PID=$(cat "$LOGS_DIR/web-interface.pid")
    if ps -p $WEB_PID > /dev/null 2>&1; then
        echo -e "${CYAN}إيقاف خادم واجهة الويب (PID: $WEB_PID)...${NC}"
        kill $WEB_PID 2>/dev/null
        sleep 2
        if ps -p $WEB_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}إجبار إيقاف خادم واجهة الويب...${NC}"
            kill -9 $WEB_PID 2>/dev/null
        fi
        echo -e "${GREEN}✅ تم إيقاف خادم واجهة الويب${NC}"
    else
        echo -e "${YELLOW}⚠️ خادم واجهة الويب غير متاح${NC}"
    fi
    rm -f "$LOGS_DIR/web-interface.pid"
else
    echo -e "${YELLOW}⚠️ ملف PID خادم واجهة الويب غير موجود${NC}"
fi

# إيقاف خادم التحكم
if [ -f "$LOGS_DIR/command-server.pid" ]; then
    COMMAND_PID=$(cat "$LOGS_DIR/command-server.pid")
    if ps -p $COMMAND_PID > /dev/null 2>&1; then
        echo -e "${CYAN}إيقاف خادم التحكم (PID: $COMMAND_PID)...${NC}"
        kill $COMMAND_PID 2>/dev/null
        sleep 2
        if ps -p $COMMAND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}إجبار إيقاف خادم التحكم...${NC}"
            kill -9 $COMMAND_PID 2>/dev/null
        fi
        echo -e "${GREEN}✅ تم إيقاف خادم التحكم${NC}"
    else
        echo -e "${YELLOW}⚠️ خادم التحكم غير متاح${NC}"
    fi
    rm -f "$LOGS_DIR/command-server.pid"
else
    echo -e "${YELLOW}⚠️ ملف PID خادم التحكم غير موجود${NC}"
fi

# إيقاف بوت تيليجرام
if [ -f "$LOGS_DIR/telegram-bot.pid" ]; then
    BOT_PID=$(cat "$LOGS_DIR/telegram-bot.pid")
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo -e "${CYAN}إيقاف بوت تيليجرام (PID: $BOT_PID)...${NC}"
        kill $BOT_PID 2>/dev/null
        sleep 2
        if ps -p $BOT_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}إجبار إيقاف بوت تيليجرام...${NC}"
            kill -9 $BOT_PID 2>/dev/null
        fi
        echo -e "${GREEN}✅ تم إيقاف بوت تيليجرام${NC}"
    else
        echo -e "${YELLOW}⚠️ بوت تيليجرام غير متاح${NC}"
    fi
    rm -f "$LOGS_DIR/telegram-bot.pid"
else
    echo -e "${YELLOW}⚠️ ملف PID بوت تيليجرام غير موجود${NC}"
fi

# إيقاف أي عمليات Node.js متبقية
echo -e "${CYAN}البحث عن عمليات Node.js متبقية...${NC}"
NODE_PROCESSES=$(pgrep -f "node.*server.js" 2>/dev/null)
if [ ! -z "$NODE_PROCESSES" ]; then
    echo -e "${YELLOW}إيقاف عمليات Node.js متبقية...${NC}"
    echo "$NODE_PROCESSES" | xargs kill 2>/dev/null
    sleep 2
    echo "$NODE_PROCESSES" | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ تم إيقاف جميع عمليات Node.js${NC}"
else
    echo -e "${GREEN}✅ لا توجد عمليات Node.js متبقية${NC}"
fi

# إيقاف أي عمليات Python متبقية
echo -e "${CYAN}البحث عن عمليات Python متبقية...${NC}"
PYTHON_PROCESSES=$(pgrep -f "python.*bot.py" 2>/dev/null)
if [ ! -z "$PYTHON_PROCESSES" ]; then
    echo -e "${YELLOW}إيقاف عمليات Python متبقية...${NC}"
    echo "$PYTHON_PROCESSES" | xargs kill 2>/dev/null
    sleep 2
    echo "$PYTHON_PROCESSES" | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ تم إيقاف جميع عمليات Python${NC}"
else
    echo -e "${GREEN}✅ لا توجد عمليات Python متبقية${NC}"
fi

# تنظيف الملفات المؤقتة
echo -e "${CYAN}تنظيف الملفات المؤقتة...${NC}"
find "$PROJECT_DIR" -name "*.tmp" -delete 2>/dev/null
find "$PROJECT_DIR" -name "*.log.tmp" -delete 2>/dev/null
echo -e "${GREEN}✅ تم تنظيف الملفات المؤقتة${NC}"

# التحقق من حالة الخوادم
echo -e "${BLUE}🔍 التحقق من حالة الخوادم...${NC}"

# التحقق من خادم واجهة الويب
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ خادم واجهة الويب لا يزال يعمل${NC}"
else
    echo -e "${GREEN}✅ خادم واجهة الويب متوقف${NC}"
fi

# التحقق من خادم التحكم
if curl -s http://localhost:4000 > /dev/null 2>&1; then
    echo -e "${RED}❌ خادم التحكم لا يزال يعمل${NC}"
else
    echo -e "${GREEN}✅ خادم التحكم متوقف${NC}"
fi

echo ""
echo -e "${GREEN}🎉 تم إيقاف النظام بنجاح!${NC}"
echo -e "${YELLOW}💡 لإعادة التشغيل، استخدم: ./start.sh${NC}"