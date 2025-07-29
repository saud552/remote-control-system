#!/bin/bash

# 🚀 Advanced Remote Control System - Phase 7 Startup Script
# الأمان والعزل والتطوير النهائي

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/pids"
CONFIG_DIR="$SCRIPT_DIR/config"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR" "$CONFIG_DIR"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/phase7_startup.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/phase7_startup.log"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/phase7_startup.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/phase7_startup.log"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/phase7_startup.log"
}

# Banner
print_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🚀 PHASE 7 STARTUP 🚀                    ║
║              الأمان والعزل والتطوير النهائي                ║
║              Final Security, Isolation & Development        ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
        error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    success "Python version: $PYTHON_VERSION"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        success "Docker is available"
        DOCKER_AVAILABLE=true
    else
        warning "Docker is not available - sandbox features will be limited"
        DOCKER_AVAILABLE=false
    fi
    
    # Check GPU
    if command -v nvidia-smi &> /dev/null; then
        success "NVIDIA GPU detected"
        GPU_AVAILABLE=true
    elif command -v lspci &> /dev/null && lspci | grep -i vga | grep -i amd &> /dev/null; then
        success "AMD GPU detected"
        GPU_AVAILABLE=true
    else
        warning "No GPU detected - performance may be limited"
        GPU_AVAILABLE=false
    fi
    
    # Check required packages
    REQUIRED_PACKAGES=("pip" "git" "wget" "curl")
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if command -v "$package" &> /dev/null; then
            success "$package is available"
        else
            error "$package is not installed"
            exit 1
        fi
    done
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        success "Python dependencies installed"
    else
        error "requirements.txt not found"
        exit 1
    fi
}

# Install system packages
install_system_packages() {
    log "Installing system packages..."
    
    # Update package list
    sudo apt update
    
    # Install required packages
    PACKAGES=(
        "docker.io"
        "nmap"
        "hashcat"
        "john"
        "aircrack-ng"
        "metasploit-framework"
        "wireshark"
        "tcpdump"
        "net-tools"
        "psutil"
    )
    
    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            info "Installing $package..."
            sudo apt install -y "$package" || warning "Failed to install $package"
        else
            success "$package is already installed"
        fi
    done
}

# Setup Docker
setup_docker() {
    if [[ "$DOCKER_AVAILABLE" == true ]]; then
        log "Setting up Docker..."
        
        # Start Docker service
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add user to docker group
        sudo usermod -aG docker "$USER"
        
        success "Docker setup completed"
    fi
}

# Clone hackingtool repository
setup_hackingtool() {
    log "Setting up hackingtool repository..."
    
    if [[ ! -d "hackingtool" ]]; then
        git clone https://github.com/Z4nzu/hackingtool.git
        success "Hackingtool repository cloned"
    else
        info "Hackingtool repository already exists"
    fi
    
    # Install hackingtool
    if [[ -f "hackingtool/install.sh" ]]; then
        cd hackingtool
        sudo bash install.sh
        cd ..
        success "Hackingtool installation completed"
    fi
}

# Generate SSL certificates
generate_certificates() {
    log "Generating SSL certificates..."
    
    mkdir -p certificates
    
    if [[ ! -f "certificates/server.crt" ]] || [[ ! -f "certificates/server.key" ]]; then
        openssl req -x509 -newkey rsa:4096 -keyout certificates/server.key -out certificates/server.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        success "SSL certificates generated"
    else
        info "SSL certificates already exist"
    fi
}

# Initialize configuration files
init_configuration() {
    log "Initializing configuration files..."
    
    # Create phase7 config if not exists
    if [[ ! -f "phase7_config.json" ]]; then
        error "phase7_config.json not found"
        exit 1
    fi
    
    # Create server config if not exists
    if [[ ! -f "server_config.json" ]]; then
        cat > server_config.json << EOF
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "ssl_enabled": true,
    "ssl_cert": "certificates/server.crt",
    "ssl_key": "certificates/server.key"
  },
  "security": {
    "encryption_enabled": true,
    "sandbox_enabled": true,
    "anti_detection": true
  },
  "performance": {
    "optimization_enabled": true,
    "gpu_acceleration": true,
    "multi_device": true
  }
}
EOF
        success "Server configuration created"
    fi
    
    success "Configuration files initialized"
}

# Start security module
start_security_module() {
    log "Starting Advanced Security Module..."
    
    if [[ -f "advanced_security_module.py" ]]; then
        python3 advanced_security_module.py &
        SECURITY_PID=$!
        echo $SECURITY_PID > "$PID_DIR/security_module.pid"
        success "Security module started (PID: $SECURITY_PID)"
    else
        error "advanced_security_module.py not found"
        return 1
    fi
}

# Start performance module
start_performance_module() {
    log "Starting Advanced Performance Module..."
    
    if [[ -f "advanced_performance_module.py" ]]; then
        python3 advanced_performance_module.py &
        PERFORMANCE_PID=$!
        echo $PERFORMANCE_PID > "$PID_DIR/performance_module.pid"
        success "Performance module started (PID: $PERFORMANCE_PID)"
    else
        error "advanced_performance_module.py not found"
        return 1
    fi
}

# Start development module
start_development_module() {
    log "Starting Final Development Module..."
    
    if [[ -f "final_development_module.py" ]]; then
        python3 final_development_module.py &
        DEVELOPMENT_PID=$!
        echo $DEVELOPMENT_PID > "$PID_DIR/development_module.pid"
        success "Development module started (PID: $DEVELOPMENT_PID)"
    else
        error "final_development_module.py not found"
        return 1
    fi
}

# Start web dashboard
start_web_dashboard() {
    log "Starting Advanced Web Dashboard..."
    
    if [[ -f "advanced_web_dashboard.py" ]]; then
        python3 advanced_web_dashboard.py &
        DASHBOARD_PID=$!
        echo $DASHBOARD_PID > "$PID_DIR/web_dashboard.pid"
        success "Web dashboard started (PID: $DASHBOARD_PID)"
    else
        warning "advanced_web_dashboard.py not found"
    fi
}

# Start Telegram bot
start_telegram_bot() {
    log "Starting Enhanced Telegram Bot..."
    
    if [[ -f "enhanced_telegram_bot.py" ]]; then
        python3 enhanced_telegram_bot.py &
        TELEGRAM_PID=$!
        echo $TELEGRAM_PID > "$PID_DIR/telegram_bot.pid"
        success "Telegram bot started (PID: $TELEGRAM_PID)"
    else
        warning "enhanced_telegram_bot.py not found"
    fi
}

# Start main server
start_main_server() {
    log "Starting Main Server..."
    
    if [[ -f "server.py" ]]; then
        python3 server.py &
        SERVER_PID=$!
        echo $SERVER_PID > "$PID_DIR/main_server.pid"
        success "Main server started (PID: $SERVER_PID)"
    else
        error "server.py not found"
        return 1
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check if all PIDs are running
    for pid_file in "$PID_DIR"/*.pid; do
        if [[ -f "$pid_file" ]]; then
            pid=$(cat "$pid_file")
            if ps -p "$pid" > /dev/null 2>&1; then
                service_name=$(basename "$pid_file" .pid)
                success "$service_name is running (PID: $pid)"
            else
                error "$(basename "$pid_file" .pid) is not running"
                return 1
            fi
        fi
    done
    
    # Check system resources
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    
    info "CPU Usage: ${CPU_USAGE}%"
    info "Memory Usage: ${MEMORY_USAGE}%"
    
    if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
        warning "High CPU usage detected"
    fi
    
    if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
        warning "High memory usage detected"
    fi
    
    success "Health check completed"
}

# Display status
display_status() {
    log "System Status:"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    # Display running services
    for pid_file in "$PID_DIR"/*.pid; do
        if [[ -f "$pid_file" ]]; then
            pid=$(cat "$pid_file")
            service_name=$(basename "$pid_file" .pid)
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} $service_name (PID: $pid)"
            else
                echo -e "${RED}✗${NC} $service_name (not running)"
            fi
        fi
    done
    
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    # Display system info
    echo -e "${BLUE}System Information:${NC}"
    echo -e "  OS: $(uname -s) $(uname -r)"
    echo -e "  Python: $(python3 --version)"
    echo -e "  Docker: $([[ "$DOCKER_AVAILABLE" == true ]] && echo "Available" || echo "Not available")"
    echo -e "  GPU: $([[ "$GPU_AVAILABLE" == true ]] && echo "Available" || echo "Not available")"
    
    # Display URLs
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  Web Dashboard: https://localhost:8080"
    echo -e "  API Endpoint: https://localhost:8080/api"
    echo -e "  Health Check: https://localhost:8080/health"
    
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
}

# Main function
main() {
    print_banner
    
    log "Starting Phase 7 initialization..."
    
    # Check requirements
    check_requirements
    
    # Install dependencies
    install_dependencies
    
    # Install system packages
    install_system_packages
    
    # Setup Docker
    setup_docker
    
    # Setup hackingtool
    setup_hackingtool
    
    # Generate certificates
    generate_certificates
    
    # Initialize configuration
    init_configuration
    
    # Start modules
    log "Starting all modules..."
    
    start_security_module
    start_performance_module
    start_development_module
    start_web_dashboard
    start_telegram_bot
    start_main_server
    
    # Wait a moment for services to start
    sleep 3
    
    # Health check
    health_check
    
    # Display status
    display_status
    
    success "Phase 7 startup completed successfully!"
    
    log "System is ready for use."
    log "Check logs in: $LOG_DIR"
    log "PID files in: $PID_DIR"
    
    echo -e "${GREEN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SYSTEM READY 🎉                       ║
║              All modules are running successfully           ║
║              جميع الوحدات تعمل بنجاح                        ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Error handling
trap 'error "An error occurred. Check logs for details."; exit 1' ERR

# Run main function
main "$@"