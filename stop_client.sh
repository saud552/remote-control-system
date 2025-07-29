#!/bin/bash

# ========================================
# Advanced Remote Control System
# Client Stop Script
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
PID_FILE="$PROJECT_DIR/client.pid"
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

# Function to stop client gracefully
stop_client_graceful() {
    local pid=$1
    local timeout=${2:-15}
    
    print_status "Sending SIGTERM to client (PID: $pid)..."
    kill -TERM $pid
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt $timeout ]; do
        if ! kill -0 $pid 2>/dev/null; then
            print_status "Client stopped gracefully"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    return 1
}

# Function to force kill client
force_kill_client() {
    local pid=$1
    
    print_warning "Force killing client (PID: $pid)..."
    kill -KILL $pid
    
    # Wait a moment
    sleep 2
    
    if ! kill -0 $pid 2>/dev/null; then
        print_status "Client force stopped"
        return 0
    else
        print_error "Failed to force kill client"
        return 1
    fi
}

# Function to clean up temporary files
cleanup_temp_files() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary files
    find "$PROJECT_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$PROJECT_DIR" -name "*.temp" -delete 2>/dev/null || true
    
    # Clean up log files if they're too large
    if [ -f "$LOG_DIR/client.log" ]; then
        local log_size=$(stat -c%s "$LOG_DIR/client.log" 2>/dev/null || echo "0")
        if [ "$log_size" -gt 52428800 ]; then  # 50MB
            print_status "Rotating large log file..."
            mv "$LOG_DIR/client.log" "$LOG_DIR/client.log.old"
            touch "$LOG_DIR/client.log"
        fi
    fi
    
    # Clean up old backup files
    find "$PROJECT_DIR/backups" -name "*.old" -mtime +7 -delete 2>/dev/null || true
}

# Function to show client status
show_client_status() {
    print_header "Client Status Check"
    
    local client_running=false
    
    # Check main client process
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 $pid 2>/dev/null; then
            print_status "Main client is running (PID: $pid)"
            client_running=true
        else
            print_warning "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found"
    fi
    
    # Check for any client.py processes
    if pgrep -f "client.py" > /dev/null; then
        local pids=$(pgrep -f "client.py")
        print_warning "Found client.py processes: $pids"
        client_running=true
    fi
    
    if [ "$client_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to stop client using PID file
stop_client_by_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 $pid 2>/dev/null; then
            print_status "Found client process (PID: $pid)"
            
            # Try graceful shutdown first
            if stop_client_graceful $pid 15; then
                rm -f "$PID_FILE"
                return 0
            else
                # Force kill if graceful shutdown failed
                if force_kill_client $pid; then
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

# Function to stop client by process name
stop_client_by_name() {
    local pids=$(pgrep -f "client.py")
    
    if [ -n "$pids" ]; then
        print_status "Found client.py processes: $pids"
        
        for pid in $pids; do
            print_status "Stopping process $pid..."
            
            # Try graceful shutdown first
            if stop_client_graceful $pid 10; then
                continue
            else
                # Force kill if graceful shutdown failed
                force_kill_client $pid
            fi
        done
        
        return 0
    else
        print_warning "No client.py processes found"
        return 1
    fi
}

# Function to show help
show_help() {
    print_header "Client Stop Script - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  stop      - Stop the client gracefully"
    echo "  force     - Force stop the client"
    echo "  status    - Show client status"
    echo "  cleanup   - Clean up temporary files"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 stop"
    echo "  $0 force"
    echo "  $0 status"
}

# Main stop function
stop_client() {
    print_header "Stopping Advanced Remote Control Client"
    
    local force_stop=${1:-false}
    
    # Show current status
    show_client_status
    
    # Stop main client
    if ! stop_client_by_pid; then
        if ! stop_client_by_name; then
            print_warning "No client processes found to stop"
        fi
    fi
    
    # Force stop if requested
    if [ "$force_stop" = true ]; then
        print_warning "Force stopping all client processes..."
        pkill -f "client.py" 2>/dev/null || true
    fi
    
    # Clean up
    cleanup_temp_files
    
    # Final status check
    sleep 2
    if show_client_status; then
        print_warning "Some processes may still be running"
        return 1
    else
        print_status "All client processes stopped successfully"
        return 0
    fi
}

# Main script logic
case "${1:-stop}" in
    "stop")
        stop_client false
        ;;
    "force")
        stop_client true
        ;;
    "status")
        show_client_status
        ;;
    "cleanup")
        cleanup_temp_files
        ;;
    "help"|*)
        show_help
        ;;
esac