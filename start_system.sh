#!/bin/bash

# ========================================
# Advanced Remote Control System
# Unified Startup Script
# Phase 1: Fixed Startup Mechanism
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if Python3 is available
check_python() {
    if command -v python3 &> /dev/null; then
        print_status "Python3 found: $(python3 --version)"
        return 0
    else
        print_error "Python3 not found. Please install Python 3.9+"
        return 1
    fi
}

# Function to check if Node.js is available
check_node() {
    if command -v node &> /dev/null; then
        print_status "Node.js found: $(node --version)"
        return 0
    else
        print_error "Node.js not found. Please install Node.js"
        return 1
    fi
}

# Function to check if npm is available
check_npm() {
    if command -v npm &> /dev/null; then
        print_status "npm found: $(npm --version)"
        return 0
    else
        print_error "npm not found. Please install npm"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_status "Python dependencies installed successfully"
    else
        print_warning "requirements.txt not found"
    fi
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    if [ -f "remote-control-system/command-server/package.json" ]; then
        cd remote-control-system/command-server
        npm install
        cd ../..
        print_status "Node.js dependencies installed successfully"
    else
        print_warning "package.json not found"
    fi
}

# Function to start the system
start_system() {
    print_header "Starting Advanced Remote Control System"
    
    # Check dependencies
    print_status "Checking system dependencies..."
    
    if ! check_python; then
        exit 1
    fi
    
    if ! check_node; then
        exit 1
    fi
    
    if ! check_npm; then
        exit 1
    fi
    
    # Install dependencies
    print_status "Installing dependencies..."
    install_python_deps
    install_node_deps
    
    # Start the unified startup script
    print_status "Starting system components..."
    python3 unified_startup.py start
}

# Function to stop the system
stop_system() {
    print_header "Stopping Advanced Remote Control System"
    
    # Stop using the unified startup script
    python3 unified_startup.py stop
    
    # Kill any remaining processes
    pkill -f "unified_startup.py" 2>/dev/null || true
    pkill -f "web_dashboard.py" 2>/dev/null || true
    pkill -f "server.js" 2>/dev/null || true
    pkill -f "bot.py" 2>/dev/null || true
    
    print_status "System stopped successfully"
}

# Function to show system status
show_status() {
    print_header "System Status"
    
    if [ -f "unified_startup.py" ]; then
        python3 unified_startup.py status
    else
        print_error "Unified startup script not found"
    fi
}

# Function to check system
check_system() {
    print_header "System Check"
    
    if [ -f "unified_startup.py" ]; then
        python3 unified_startup.py check
    else
        print_error "Unified startup script not found"
    fi
}

# Function to show help
show_help() {
    print_header "Advanced Remote Control System - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     - Start the system"
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
    echo "  📡 API Server: http://localhost:8000"
    echo "  🤖 Telegram Bot: Running in background"
}

# Function to restart the system
restart_system() {
    print_header "Restarting Advanced Remote Control System"
    stop_system
    sleep 2
    start_system
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
        show_status
        ;;
    "check")
        check_system
        ;;
    "help"|*)
        show_help
        ;;
esac