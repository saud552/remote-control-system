#!/bin/bash

# ========================================
# Advanced Remote Control System
# Server Stop Script
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
PID_FILE="$PROJECT_DIR/server.pid"
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

# Function to stop server gracefully
stop_server_graceful() {
    local pid=$1
    local timeout=${2:-30}
    
    print_status "Sending SIGTERM to server (PID: $pid)..."
    kill -TERM $pid
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt $timeout ]; do
        if ! kill -0 $pid 2>/dev/null; then
            print_status "Server stopped gracefully"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    return 1
}

# Function to force kill server
force_kill_server() {
    local pid=$1
    
    print_warning "Force killing server (PID: $pid)..."
    kill -KILL $pid
    
    # Wait a moment
    sleep 2
    
    if ! kill -0 $pid 2>/dev/null; then
        print_status "Server force stopped"
        return 0
    else
        print_error "Failed to force kill server"
        return 1
    fi
}

# Function to stop all related processes
stop_related_processes() {
    print_status "Stopping related processes..."
    
    # Stop WiFi attack processes
    if pgrep -f "wifijammer" > /dev/null; then
        print_status "Stopping WiFiJammer processes..."
        pkill -f "wifijammer"
    fi
    
    if pgrep -f "fluxion" > /dev/null; then
        print_status "Stopping Fluxion processes..."
        pkill -f "fluxion"
    fi
    
    if pgrep -f "aircrack" > /dev/null; then
        print_status "Stopping Aircrack processes..."
        pkill -f "aircrack"
    fi
    
    # Stop mobile attack processes
    if pgrep -f "adb" > /dev/null; then
        print_status "Stopping ADB processes..."
        pkill -f "adb"
    fi
    
    if pgrep -f "msfconsole" > /dev/null; then
        print_status "Stopping Metasploit processes..."
        pkill -f "msfconsole"
    fi
    
    if pgrep -f "drozer" > /dev/null; then
        print_status "Stopping Drozer processes..."
        pkill -f "drozer"
    fi
    
    # Stop crypto cracking processes
    if pgrep -f "hashcat" > /dev/null; then
        print_status "Stopping Hashcat processes..."
        pkill -f "hashcat"
    fi
    
    if pgrep -f "john" > /dev/null; then
        print_status "Stopping John processes..."
        pkill -f "john"
    fi
    
    if pgrep -f "fcrackzip" > /dev/null; then
        print_status "Stopping fcrackzip processes..."
        pkill -f "fcrackzip"
    fi
    
    # Stop HashBuster processes
    if pgrep -f "hash.py" > /dev/null; then
        print_status "Stopping HashBuster processes..."
        pkill -f "hash.py"
    fi
}

# Function to clean up temporary files
cleanup_temp_files() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary files
    find "$PROJECT_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$PROJECT_DIR" -name "*.temp" -delete 2>/dev/null || true
    
    # Clean up log files if they're too large
    if [ -f "$LOG_DIR/server.log" ]; then
        local log_size=$(stat -c%s "$LOG_DIR/server.log" 2>/dev/null || echo "0")
        if [ "$log_size" -gt 104857600 ]; then  # 100MB
            print_status "Rotating large log file..."
            mv "$LOG_DIR/server.log" "$LOG_DIR/server.log.old"
            touch "$LOG_DIR/server.log"
        fi
    fi
    
    # Clean up old backup files
    find "$PROJECT_DIR/backups" -name "*.old" -mtime +7 -delete 2>/dev/null || true
}

# Function to show server status
show_server_status() {
    print_header "Server Status Check"
    
    local server_running=false
    local related_processes=0
    
    # Check main server process
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 $pid 2>/dev/null; then
            print_status "Main server is running (PID: $pid)"
            server_running=true
        else
            print_warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found"
    fi
    
    # Check for any command_server.py processes
    if pgrep -f "command_server.py" > /dev/null; then
        local pids=$(pgrep -f "command_server.py")
        print_warning "Found command_server.py processes: $pids"
        server_running=true
    fi
    
    # Count related processes
    related_processes=$(pgrep -f "wifijammer\|fluxion\|aircrack\|adb\|msfconsole\|drozer\|hashcat\|john\|fcrackzip\|hash.py" | wc -l)
    
    if [ "$related_processes" -gt 0 ]; then
        print_warning "Found $related_processes related processes running"
    fi
    
    if [ "$server_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to stop server using PID file
stop_server_by_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 $pid 2>/dev/null; then
            print_status "Found server process (PID: $pid)"
            
            # Try graceful shutdown first
            if stop_server_graceful $pid 30; then
                rm -f "$PID_FILE"
                return 0
            else
                # Force kill if graceful shutdown failed
                if force_kill_server $pid; then
                    rm -f "$PID_FILE"
                    return 0
                else
                    return 1
                fi
            fi
        else
            print_warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
            return 0
        fi
    else
        print_warning "No PID file found"
        return 1
    fi
}

# Function to stop server by process name
stop_server_by_name() {
    local pids=$(pgrep -f "command_server.py")
    
    if [ -n "$pids" ]; then
        print_status "Found command_server.py processes: $pids"
        
        for pid in $pids; do
            print_status "Stopping process $pid..."
            
            # Try graceful shutdown first
            if stop_server_graceful $pid 15; then
                continue
            else
                # Force kill if graceful shutdown failed
                force_kill_server $pid
            fi
        done
        
        return 0
    else
        print_warning "No command_server.py processes found"
        return 1
    fi
}

# Function to stop all attack modules
stop_attack_modules() {
    print_header "Stopping Attack Modules"
    
    # Stop WiFi jamming module
    if pgrep -f "wifi_jamming" > /dev/null; then
        print_status "Stopping WiFi jamming module..."
        pkill -f "wifi_jamming"
    fi
    
    # Stop mobile attack module
    if pgrep -f "mobile_attack" > /dev/null; then
        print_status "Stopping mobile attack module..."
        pkill -f "mobile_attack"
    fi
    
    # Stop crypto cracking module
    if pgrep -f "crypto_cracking" > /dev/null; then
        print_status "Stopping crypto cracking module..."
        pkill -f "crypto_cracking"
    fi
    
    # Stop any remaining Python processes related to the project
    local python_pids=$(pgrep -f "python.*command_server\|python.*wifi_jamming\|python.*mobile_attack\|python.*crypto_cracking")
    if [ -n "$python_pids" ]; then
        print_status "Stopping related Python processes: $python_pids"
        echo "$python_pids" | xargs kill -TERM 2>/dev/null || true
    fi
}

# Function to show help
show_help() {
    print_header "Server Stop Script - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  stop      - Stop the server gracefully"
    echo "  force     - Force stop the server"
    echo "  all       - Stop server and all related processes"
    echo "  status    - Show server status"
    echo "  cleanup   - Clean up temporary files"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 stop"
    echo "  $0 force"
    echo "  $0 all"
    echo "  $0 status"
}

# Main stop function
stop_server() {
    print_header "Stopping Advanced Remote Control Server"
    
    local force_stop=${1:-false}
    local stop_all=${2:-false}
    
    # Show current status
    show_server_status
    
    # Stop main server
    if ! stop_server_by_pid; then
        if ! stop_server_by_name; then
            print_warning "No server processes found to stop"
        fi
    fi
    
    # Stop related processes if requested
    if [ "$stop_all" = true ]; then
        stop_related_processes
        stop_attack_modules
    fi
    
    # Force stop if requested
    if [ "$force_stop" = true ]; then
        print_warning "Force stopping all related processes..."
        pkill -f "command_server\|wifijammer\|fluxion\|aircrack\|adb\|msfconsole\|drozer\|hashcat\|john\|fcrackzip\|hash.py" 2>/dev/null || true
    fi
    
    # Clean up
    cleanup_temp_files
    
    # Final status check
    sleep 2
    if show_server_status; then
        print_warning "Some processes may still be running"
        return 1
    else
        print_status "All server processes stopped successfully"
        return 0
    fi
}

# Main script logic
case "${1:-stop}" in
    "stop")
        stop_server false false
        ;;
    "force")
        stop_server true false
        ;;
    "all")
        stop_server false true
        ;;
    "status")
        show_server_status
        ;;
    "cleanup")
        cleanup_temp_files
        ;;
    "help"|*)
        show_help
        ;;
esac