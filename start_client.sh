#!/bin/bash

# ========================================
# Advanced Remote Control System
# Client Startup Script
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
CLIENT_SCRIPT="$PROJECT_DIR/client.py"
CONFIG_FILE="$PROJECT_DIR/client_config.json"
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

# Function to check if client script exists
check_client_script() {
    if [ ! -f "$CLIENT_SCRIPT" ]; then
        print_error "Client script not found: $CLIENT_SCRIPT"
        print_status "Creating basic client script..."
        create_basic_client_script
    fi
}

# Function to create basic client script if not exists
create_basic_client_script() {
    cat > "$CLIENT_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Advanced Remote Control System - Client
Phase 4: Advanced Jamming & Wireless Attack Tools
"""

import asyncio
import json
import logging
import ssl
import websockets
from typing import Dict, Any
import argparse
import sys
import os

class AdvancedRemoteControlClient:
    """Advanced remote control client with Phase 4 modules"""
    
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.logger = self.setup_logging()
        self.websocket = None
        self.connected = False
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load client configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_file}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file: {config_file}")
            sys.exit(1)
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(self.config.get('logging', {}).get('level', 'INFO'))
        
        # Create log directory if not exists
        log_dir = os.path.dirname(self.config.get('logging', {}).get('file', 'logs/client.log'))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        if 'file' in self.config.get('logging', {}):
            handler = logging.FileHandler(self.config['logging']['file'])
            handler.setFormatter(logging.Formatter(
                self.config['logging'].get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ))
            logger.addHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
        
        return logger
    
    async def connect(self) -> bool:
        """Connect to the remote control server"""
        try:
            connection_config = self.config.get('connection', {})
            host = connection_config.get('server_host', 'localhost')
            port = connection_config.get('server_port', 8080)
            ssl_enabled = connection_config.get('ssl_enabled', True)
            
            # Setup SSL context if enabled
            ssl_context = None
            if ssl_enabled:
                ssl_context = ssl.create_default_context()
                if not connection_config.get('ssl_verify', False):
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect to server
            uri = f"{'wss' if ssl_enabled else 'ws'}://{host}:{port}"
            self.logger.info(f"Connecting to server: {uri}")
            
            self.websocket = await websockets.connect(
                uri,
                ssl=ssl_context,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.connected = True
            self.logger.info("Connected to server successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            return False
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to server"""
        if not self.connected or not self.websocket:
            self.logger.error("Not connected to server")
            return False
        
        try:
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive message from server"""
        if not self.connected or not self.websocket:
            return {}
        
        try:
            message = await self.websocket.recv()
            return json.loads(message)
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return {}
    
    async def authenticate(self) -> bool:
        """Authenticate with server"""
        auth_config = self.config.get('authentication', {})
        if not auth_config.get('enabled', False):
            return True
        
        token = auth_config.get('token', '')
        if not token:
            self.logger.warning("No authentication token provided")
            return True
        
        auth_message = {
            "type": "authentication",
            "method": auth_config.get('method', 'token'),
            "token": token
        }
        
        return await self.send_message(auth_message)
    
    async def run(self):
        """Main client loop"""
        try:
            # Connect to server
            if not await self.connect():
                return
            
            # Authenticate
            if not await self.authenticate():
                self.logger.error("Authentication failed")
                return
            
            self.logger.info("Client started successfully")
            self.logger.info("Available commands:")
            self.logger.info("  wifi_start_attack - Start WiFi jamming attack")
            self.logger.info("  mobile_start_attack - Start mobile device attack")
            self.logger.info("  crypto_start_attack - Start crypto cracking attack")
            self.logger.info("  get_status - Get server status")
            self.logger.info("  quit - Exit client")
            
            # Main message loop
            while self.connected:
                try:
                    # Send keepalive
                    await self.send_message({"type": "keepalive"})
                    
                    # Receive messages
                    message = await self.receive_message()
                    if message:
                        await self.handle_message(message)
                    
                    await asyncio.sleep(5)
                    
                except websockets.exceptions.ConnectionClosed:
                    self.logger.warning("Connection to server lost")
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("Client interrupted by user")
        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            await self.disconnect()
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages from server"""
        msg_type = message.get('type', '')
        
        if msg_type == 'status':
            self.logger.info(f"Server status: {message.get('data', {})}")
        elif msg_type == 'attack_result':
            self.logger.info(f"Attack result: {message.get('data', {})}")
        elif msg_type == 'error':
            self.logger.error(f"Server error: {message.get('message', '')}")
        else:
            self.logger.info(f"Received message: {message}")
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        self.logger.info("Disconnected from server")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Advanced Remote Control Client')
    parser.add_argument('--config', default='client_config.json', help='Config file path')
    args = parser.parse_args()
    
    client = AdvancedRemoteControlClient(args.config)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    chmod +x "$CLIENT_SCRIPT"
    print_status "Basic client script created"
}

# Function to check if config file exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_warning "Config file not found: $CONFIG_FILE"
        print_status "Creating default config..."
        create_default_config
    fi
}

# Function to create default config
create_default_config() {
    cat > "$CONFIG_FILE" << EOF
{
    "connection": {
        "server_host": "localhost",
        "server_port": 8080,
        "ssl_enabled": true,
        "ssl_verify": false,
        "reconnect_interval": 5,
        "max_reconnect_attempts": 10,
        "timeout": 30,
        "keepalive": true,
        "keepalive_interval": 30
    },
    "authentication": {
        "enabled": true,
        "method": "token",
        "token": "",
        "auto_login": true,
        "save_credentials": false
    },
    "logging": {
        "level": "INFO",
        "file": "logs/client.log",
        "max_size": "50MB",
        "backup_count": 3,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "modules": {
        "wifi_jamming": {
            "enabled": true,
            "auto_connect": false,
            "default_interface": "wlan0",
            "save_captures": true,
            "capture_path": "data/wifi_captures/"
        },
        "mobile_attack": {
            "enabled": true,
            "auto_scan": false,
            "default_device": "",
            "save_extracted_data": true,
            "data_path": "data/mobile_data/"
        },
        "crypto_cracking": {
            "enabled": true,
            "auto_save_results": true,
            "results_path": "data/crypto_results/",
            "wordlist_path": "/usr/share/wordlists/rockyou.txt"
        }
    }
}
EOF
    
    print_status "Default config created"
}

# Function to create log directory
create_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        print_status "Creating log directory..."
        mkdir -p "$LOG_DIR"
    fi
}

# Function to check server connectivity
check_server_connectivity() {
    print_header "Checking Server Connectivity"
    
    connection_config=$(python3 -c "
import json
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = json.load(f)
    conn = config.get('connection', {})
    print(f\"{conn.get('server_host', 'localhost')}:{conn.get('server_port', 8080)}\")
except:
    print('localhost:8080')
" 2>/dev/null)
    
    host=$(echo "$connection_config" | cut -d: -f1)
    port=$(echo "$connection_config" | cut -d: -f2)
    
    print_status "Checking connection to $host:$port..."
    
    # Check if port is open
    if command -v nc &> /dev/null; then
        if nc -z "$host" "$port" 2>/dev/null; then
            print_status "Server is reachable ✓"
            return 0
        else
            print_warning "Server is not reachable ✗"
            print_status "Make sure the server is running: ./start_server.sh"
            return 1
        fi
    else
        print_warning "netcat not available, skipping connectivity check"
        return 0
    fi
}

# Function to start the client
start_client() {
    print_header "Starting Advanced Remote Control Client"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    export PYTHONUNBUFFERED=1
    
    # Check if client is already running
    if pgrep -f "client.py" > /dev/null; then
        print_warning "Client is already running. Stopping existing process..."
        pkill -f "client.py"
        sleep 2
    fi
    
    # Start the client
    print_status "Starting client with config: $CONFIG_FILE"
    print_status "Log file: $LOG_DIR/client.log"
    
    # Start client in foreground for interactive use
    print_status "Starting client in interactive mode..."
    print_status "Press Ctrl+C to stop the client"
    
    python3 "$CLIENT_SCRIPT" --config "$CONFIG_FILE"
}

# Function to start client in background
start_client_background() {
    print_header "Starting Advanced Remote Control Client (Background)"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    export PYTHONUNBUFFERED=1
    
    # Check if client is already running
    if pgrep -f "client.py" > /dev/null; then
        print_warning "Client is already running. Stopping existing process..."
        pkill -f "client.py"
        sleep 2
    fi
    
    # Start the client in background
    print_status "Starting client in background..."
    nohup python3 "$CLIENT_SCRIPT" --config "$CONFIG_FILE" > "$LOG_DIR/client.log" 2>&1 &
    CLIENT_PID=$!
    
    # Wait a moment for client to start
    sleep 2
    
    # Check if client started successfully
    if kill -0 $CLIENT_PID 2>/dev/null; then
        print_status "Client started successfully with PID: $CLIENT_PID"
        echo "$CLIENT_PID" > "$PROJECT_DIR/client.pid"
        
        # Show client status
        print_status "Client status:"
        echo "  - PID: $CLIENT_PID"
        echo "  - Config: $CONFIG_FILE"
        echo "  - Log: $LOG_DIR/client.log"
        echo "  - Stop command: ./stop_client.sh"
        
    else
        print_error "Failed to start client"
        print_status "Check logs: tail -f $LOG_DIR/client.log"
        exit 1
    fi
}

# Function to show client status
show_status() {
    print_header "Client Status"
    
    if [ -f "$PROJECT_DIR/client.pid" ]; then
        PID=$(cat "$PROJECT_DIR/client.pid")
        if kill -0 $PID 2>/dev/null; then
            print_status "Client is running (PID: $PID)"
            
            # Show process info
            ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
            
        else
            print_warning "Client PID file exists but process is not running")
            rm -f "$PROJECT_DIR/client.pid"
        fi
    else
        print_warning "Client is not running"
    fi
}

# Function to show help
show_help() {
    print_header "Client Startup Script - Help"
    
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     - Start the client interactively"
    echo "  background - Start the client in background"
    echo "  stop      - Stop the client"
    echo "  status    - Show client status"
    echo "  check     - Check server connectivity"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 background"
    echo "  $0 status"
    echo "  $0 check"
}

# Function to stop the client
stop_client() {
    print_header "Stopping Advanced Remote Control Client"
    
    if [ -f "$PROJECT_DIR/client.pid" ]; then
        PID=$(cat "$PROJECT_DIR/client.pid")
        if kill -0 $PID 2>/dev/null; then
            print_status "Stopping client (PID: $PID)..."
            kill $PID
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 $PID 2>/dev/null; then
                    print_status "Client stopped successfully"
                    rm -f "$PROJECT_DIR/client.pid"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            print_warning "Force killing client..."
            kill -9 $PID
            rm -f "$PROJECT_DIR/client.pid"
            print_status "Client force stopped"
        else
            print_warning "Client is not running")
            rm -f "$PROJECT_DIR/client.pid"
        fi
    else
        print_warning "No client PID file found")
        
        # Try to kill by process name
        if pgrep -f "client.py" > /dev/null; then
            print_status "Killing client by process name..."
            pkill -f "client.py"
            print_status "Client stopped"
        else
            print_warning "No client process found")
        fi
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        check_venv
        check_client_script
        check_config
        create_log_dir
        check_server_connectivity
        start_client
        ;;
    "background")
        check_venv
        check_client_script
        check_config
        create_log_dir
        check_server_connectivity
        start_client_background
        ;;
    "stop")
        stop_client
        ;;
    "status")
        show_status
        ;;
    "check")
        check_server_connectivity
        ;;
    "help"|*)
        show_help
        ;;
esac