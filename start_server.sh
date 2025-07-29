#!/bin/bash

# ========================================
# Advanced Remote Control System
# Server Startup Script
# Phase 4: Advanced Jamming & Wireless Attack Tools
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_DIR/venv"
SERVER_SCRIPT="$PROJECT_DIR/command_server.py"
CONFIG_FILE="$PROJECT_DIR/server_config.json"
LOG_DIR="$PROJECT_DIR/logs"

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

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found. Please run install first."
        print_status "Run: ./install_and_run.sh install"
        exit 1
    fi
}

# Function to check if server script exists
check_server_script() {
    if [ ! -f "$SERVER_SCRIPT" ]; then
        print_error "Server script not found: $SERVER_SCRIPT"
        exit 1
    fi
}

# Function to check if config file exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_warning "Config file not found: $CONFIG_FILE"
        print_status "Creating default config..."
        # Create basic config if not exists
        cat > "$CONFIG_FILE" << EOF
{
    "host": "0.0.0.0",
    "port": 8080,
    "ssl_enabled": true,
    "ssl_cert": "certificates/server.crt",
    "ssl_key": "certificates/server.key",
    "max_clients": 100,
    "log_level": "INFO",
    "log_file": "logs/server.log"
}
EOF
    fi
}

# Function to create log directory
create_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        print_status "Creating log directory..."
        mkdir -p "$LOG_DIR"
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_header "Checking System Requirements"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python version: $python_version"
    else
        print_error "Python3 not found. Please install Python 3.9+"
        exit 1
    fi
    
    # Check if running as root (optional warning)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Some tools may require elevated privileges."
    fi
    
    # Check available memory
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_mem" -lt 2048 ]; then
        print_warning "Low memory detected: ${total_mem}MB. Recommended: 4GB+"
    else
        print_status "Memory: ${total_mem}MB ✓"
    fi
    
    # Check available disk space
    available_space=$(df -m . | awk 'NR==2{printf "%.0f", $4}')
    if [ "$available_space" -lt 1024 ]; then
        print_warning "Low disk space: ${available_space}MB. Recommended: 2GB+"
    else
        print_status "Disk space: ${available_space}MB ✓"
    fi
}

# Function to check network interfaces
check_network_interfaces() {
    print_header "Checking Network Interfaces"
    
    # Check for wireless interfaces
    wireless_interfaces=$(iwconfig 2>/dev/null | grep -o '^[[:alnum:]]*' || echo "")
    if [ -n "$wireless_interfaces" ]; then
        print_status "Wireless interfaces found: $wireless_interfaces"
    else
        print_warning "No wireless interfaces detected. WiFi attacks may not work."
    fi
    
    # Check for USB interfaces (for mobile attacks)
    usb_devices=$(lsusb 2>/dev/null | wc -l)
    print_status "USB devices detected: $usb_devices"
}

# Function to check required tools
check_required_tools() {
    print_header "Checking Required Tools"
    
    tools=(
        "wifijammer"
        "fluxion"
        "aircrack-ng"
        "hashcat"
        "john"
        "fcrackzip"
        "adb"
        "msfconsole"
        "apktool"
    )
    
    missing_tools=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_status "$tool: ✓"
        else
            print_warning "$tool: ✗"
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_warning "Missing tools: ${missing_tools[*]}"
        print_status "Run: ./install_and_run.sh install"
    fi
}

# Function to check SSL certificates
check_ssl_certificates() {
    print_header "Checking SSL Certificates"
    
    cert_file="$PROJECT_DIR/certificates/server.crt"
    key_file="$PROJECT_DIR/certificates/server.key"
    
    if [ -f "$cert_file" ] && [ -f "$key_file" ]; then
        print_status "SSL certificates: ✓"
        
        # Check certificate expiry
        expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" 2>/dev/null | cut -d= -f2)
        if [ -n "$expiry_date" ]; then
            print_status "Certificate expires: $expiry_date"
        fi
    else
        print_warning "SSL certificates not found. Generating self-signed certificates..."
        
        # Create certificates directory
        mkdir -p "$PROJECT_DIR/certificates"
        
        # Generate self-signed certificate
        openssl req -x509 -newkey rsa:2048 -keyout "$key_file" -out "$cert_file" -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" 2>/dev/null
        
        if [ -f "$cert_file" ] && [ -f "$key_file" ]; then
            print_status "SSL certificates generated successfully"
        else
            print_error "Failed to generate SSL certificates"
        fi
    fi
}

# Function to start the server
start_server() {
    print_header "Starting Advanced Remote Control Server"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    export PYTHONUNBUFFERED=1
    
    # Check if server is already running
    if pgrep -f "command_server.py" > /dev/null; then
        print_warning "Server is already running. Stopping existing process..."
        pkill -f "command_server.py"
        sleep 2
    fi
    
    # Start the server
    print_status "Starting server with config: $CONFIG_FILE"
    print_status "Log file: $LOG_DIR/server.log"
    print_status "Server will be available at: https://localhost:8080"
    
    # Start server in background
    nohup python3 "$SERVER_SCRIPT" --config "$CONFIG_FILE" > "$LOG_DIR/server.log" 2>&1 &
    SERVER_PID=$!
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server started successfully
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_status "Server started successfully with PID: $SERVER_PID"
        echo "$SERVER_PID" > "$PROJECT_DIR/server.pid"
        
        # Show server status
        print_status "Server status:"
        echo "  - PID: $SERVER_PID"
        echo "  - Config: $CONFIG_FILE"
        echo "  - Log: $LOG_DIR/server.log"
        echo "  - URL: https://localhost:8080"
        echo "  - Stop command: ./stop_server.sh"
        
    else
        print_error "Failed to start server"
        print_status "Check logs: tail -f $LOG_DIR/server.log"
        exit 1
    fi
}

# Function to show server status
show_status() {
    print_header "Server Status"
    
    if [ -f "$PROJECT_DIR/server.pid" ]; then
        PID=$(cat "$PROJECT_DIR/server.pid")
        if kill -0 $PID 2>/dev/null; then
            print_status "Server is running (PID: $PID)"
            
            # Show process info
            ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
            
            # Show port usage
            if command -v netstat &> /dev/null; then
                print_status "Port usage:"
                netstat -tlnp 2>/dev/null | grep :8080 || echo "  Port 8080 not in use"
            fi
            
        else
            print_warning "Server PID file exists but process is not running"
            rm -f "$PROJECT_DIR/server.pid"
        fi
    else
        print_warning "Server is not running"
    fi
}

# Function to show help
show_help() {
    print_header "Server Startup Script - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     - Start the server"
    echo "  stop      - Stop the server"
    echo "  restart   - Restart the server"
    echo "  status    - Show server status"
    echo "  check     - Check system requirements"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 check"
}

# Function to stop the server
stop_server() {
    print_header "Stopping Advanced Remote Control Server"
    
    if [ -f "$PROJECT_DIR/server.pid" ]; then
        PID=$(cat "$PROJECT_DIR/server.pid")
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping server (PID: $PID)..."
            kill $PID
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 $PID 2>/dev/null; then
                    print_status "Server stopped successfully"
                    rm -f "$PROJECT_DIR/server.pid"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            print_warning "Force killing server..."
            kill -9 $PID
            rm -f "$PROJECT_DIR/server.pid"
            print_status "Server force stopped"
        else
            print_warning "Server is not running"
            rm -f "$PROJECT_DIR/server.pid"
        fi
    else
        print_warning "No server PID file found"
        
        # Try to kill by process name
        if pgrep -f "command_server.py" > /dev/null; then
            print_status "Killing server by process name..."
            pkill -f "command_server.py"
            print_status "Server stopped"
        else
            print_warning "No server process found"
        fi
    fi
}

# Function to restart the server
restart_server() {
    print_header "Restarting Advanced Remote Control Server"
    stop_server
    sleep 2
    start_server
}

# Main script logic
case "${1:-start}" in
    "start")
        check_venv
        check_server_script
        check_config
        create_log_dir
        check_system_requirements
        check_network_interfaces
        check_required_tools
        check_ssl_certificates
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        restart_server
        ;;
    "status")
        show_status
        ;;
    "check")
        check_system_requirements
        check_network_interfaces
        check_required_tools
        check_ssl_certificates
        ;;
    "help"|*)
        show_help
        ;;
esac