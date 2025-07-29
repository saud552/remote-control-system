#!/bin/bash

# ========================================
# Advanced Remote Control System
# Installation and Operation Script
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
PROJECT_NAME="AdvancedRemoteControlSystem"
PYTHON_VERSION="3.9"
REQUIRED_PACKAGES=(
    "python3"
    "python3-pip"
    "git"
    "wget"
    "curl"
    "build-essential"
    "libssl-dev"
    "libffi-dev"
    "python3-dev"
    "aircrack-ng"
    "hashcat"
    "john"
    "fcrackzip"
    "adb"
    "metasploit-framework"
    "apktool"
    "drozer"
    "wifijammer"
    "fluxion"
    "hashbuster"
)

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user is root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Some tools may require elevated privileges."
        return 0
    else
        print_warning "Not running as root. Some tools may not work properly."
        return 1
    fi
}

# Function to install system packages
install_system_packages() {
    print_header "Installing System Packages"
    
    # Update package list
    print_status "Updating package list..."
    sudo apt-get update
    
    # Install required packages
    print_status "Installing required packages..."
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_status "Installing $package..."
            sudo apt-get install -y "$package"
        else
            print_status "$package is already installed"
        fi
    done
    
    print_status "System packages installation completed"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python packages
    print_status "Installing Python packages..."
    pip install -r requirements.txt
    
    print_status "Python dependencies installation completed"
}

# Function to install WiFi tools
install_wifi_tools() {
    print_header "Installing WiFi Attack Tools"
    
    # Install WiFiJammer
    if ! command_exists wifijammer; then
        print_status "Installing WiFiJammer..."
        git clone https://github.com/DanMcInerney/wifijammer.git
        cd wifijammer
        sudo python3 setup.py install
        cd ..
    fi
    
    # Install Fluxion
    if [ ! -d "fluxion" ]; then
        print_status "Installing Fluxion..."
        git clone https://github.com/FluxionNetwork/fluxion.git
        cd fluxion
        chmod +x fluxion.sh
        cd ..
    fi
    
    # Install Aircrack-ng (if not already installed)
    if ! command_exists aircrack-ng; then
        print_status "Installing Aircrack-ng..."
        sudo apt-get install -y aircrack-ng
    fi
    
    print_status "WiFi tools installation completed"
}

# Function to install mobile attack tools
install_mobile_tools() {
    print_header "Installing Mobile Attack Tools"
    
    # Install ADB
    if ! command_exists adb; then
        print_status "Installing ADB..."
        sudo apt-get install -y android-tools-adb
    fi
    
    # Install Metasploit Framework
    if ! command_exists msfconsole; then
        print_status "Installing Metasploit Framework..."
        curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
        chmod +x msfinstall
        sudo ./msfinstall
        rm msfinstall
    fi
    
    # Install Apktool
    if ! command_exists apktool; then
        print_status "Installing Apktool..."
        wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.7.0.jar -O apktool.jar
        sudo mv apktool.jar /usr/local/bin/
        echo '#!/bin/bash' | sudo tee /usr/local/bin/apktool
        echo 'java -jar /usr/local/bin/apktool.jar "$@"' | sudo tee -a /usr/local/bin/apktool
        sudo chmod +x /usr/local/bin/apktool
    fi
    
    # Install Drozer
    if [ ! -d "drozer" ]; then
        print_status "Installing Drozer..."
        git clone https://github.com/FSecureLABS/drozer.git
        cd drozer
        sudo python3 setup.py install
        cd ..
    fi
    
    print_status "Mobile attack tools installation completed"
}

# Function to install crypto cracking tools
install_crypto_tools() {
    print_header "Installing Crypto Cracking Tools"
    
    # Install HashBuster
    if [ ! -d "HashBuster" ]; then
        print_status "Installing HashBuster..."
        git clone https://github.com/s0md3v/Hash-Buster.git HashBuster
        cd HashBuster
        chmod +x hash.py
        cd ..
    fi
    
    # Install John the Ripper (if not already installed)
    if ! command_exists john; then
        print_status "Installing John the Ripper..."
        sudo apt-get install -y john
    fi
    
    # Install Hashcat (if not already installed)
    if ! command_exists hashcat; then
        print_status "Installing Hashcat..."
        sudo apt-get install -y hashcat
    fi
    
    # Install fcrackzip (if not already installed)
    if ! command_exists fcrackzip; then
        print_status "Installing fcrackzip..."
        sudo apt-get install -y fcrackzip
    fi
    
    print_status "Crypto cracking tools installation completed"
}

# Function to create configuration files
create_config_files() {
    print_header "Creating Configuration Files"
    
    # Create server config
    cat > server_config.json << EOF
{
    "host": "0.0.0.0",
    "port": 8080,
    "ssl_enabled": true,
    "ssl_cert": "certificates/server.crt",
    "ssl_key": "certificates/server.key",
    "max_clients": 100,
    "log_level": "INFO",
    "log_file": "logs/server.log",
    "backup_enabled": true,
    "backup_interval": 3600,
    "security": {
        "rate_limit": 100,
        "max_connections": 50,
        "timeout": 300
    }
}
EOF
    
    # Create client config
    cat > client_config.json << EOF
{
    "server_host": "localhost",
    "server_port": 8080,
    "ssl_enabled": true,
    "ssl_verify": false,
    "reconnect_interval": 5,
    "log_level": "INFO",
    "log_file": "logs/client.log"
}
EOF
    
    print_status "Configuration files created"
}

# Function to create directories
create_directories() {
    print_header "Creating Project Directories"
    
    mkdir -p logs
    mkdir -p data
    mkdir -p certificates
    mkdir -p backups
    mkdir -p tools
    mkdir -p scripts
    mkdir -p reports
    
    print_status "Directories created successfully"
}

# Function to generate SSL certificates
generate_ssl_certificates() {
    print_header "Generating SSL Certificates"
    
    if [ ! -f "certificates/server.crt" ] || [ ! -f "certificates/server.key" ]; then
        print_status "Generating SSL certificates..."
        mkdir -p certificates
        
        # Generate private key
        openssl genrsa -out certificates/server.key 2048
        
        # Generate certificate signing request
        openssl req -new -key certificates/server.key -out certificates/server.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        # Generate self-signed certificate
        openssl x509 -req -days 365 -in certificates/server.csr -signkey certificates/server.key -out certificates/server.crt
        
        # Clean up CSR
        rm certificates/server.csr
        
        print_status "SSL certificates generated successfully"
    else
        print_status "SSL certificates already exist"
    fi
}

# Function to create startup scripts
create_startup_scripts() {
    print_header "Creating Startup Scripts"
    
    # Create server startup script
    cat > start_server.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start the server
python3 command_server.py --config server_config.json
EOF
    chmod +x start_server.sh
    
    # Create client startup script
    cat > start_client.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start the client
python3 client.py --config client_config.json
EOF
    chmod +x start_client.sh
    
    # Create systemd service file
    cat > advanced-remote-control.service << EOF
[Unit]
Description=Advanced Remote Control System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_server.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Startup scripts created"
}

# Function to create requirements.txt
create_requirements() {
    print_header "Creating Requirements File"
    
    cat > requirements.txt << EOF
# Core dependencies
asyncio==3.4.3
websockets==11.0.3
aiohttp==3.8.5
cryptography==41.0.7
psutil==5.9.5
dataclasses==0.6
typing-extensions==4.7.1

# Network and security
paramiko==3.3.1
scapy==2.5.0
netifaces==0.11.0
pycryptodome==3.19.0

# Database and storage
sqlite3
redis==4.6.0
pymongo==4.4.1

# Monitoring and logging
prometheus-client==0.17.1
structlog==23.1.0

# Web interface
flask==2.3.3
flask-socketio==5.3.6
jinja2==3.1.2

# Testing
pytest==7.4.2
pytest-asyncio==0.21.1

# Development
black==23.7.0
flake8==6.0.0
mypy==1.5.1
EOF
    
    print_status "Requirements file created"
}

# Function to run system checks
run_system_checks() {
    print_header "Running System Checks"
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python version: $python_version"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_status "Virtual environment: ✓"
    else
        print_warning "Virtual environment: ✗"
    fi
    
    # Check required tools
    tools=("wifijammer" "fluxion" "aircrack-ng" "hashcat" "john" "fcrackzip" "adb" "msfconsole" "apktool")
    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            print_status "$tool: ✓"
        else
            print_warning "$tool: ✗"
        fi
    done
    
    # Check SSL certificates
    if [ -f "certificates/server.crt" ] && [ -f "certificates/server.key" ]; then
        print_status "SSL certificates: ✓"
    else
        print_warning "SSL certificates: ✗"
    fi
    
    print_status "System checks completed"
}

# Function to display usage information
display_usage() {
    print_header "Advanced Remote Control System - Usage"
    
    echo -e "${GREEN}Available Commands:${NC}"
    echo "  start_server    - Start the remote control server"
    echo "  start_client    - Start a client connection"
    echo "  install         - Install all dependencies and tools"
    echo "  check           - Run system checks"
    echo "  update          - Update all tools and dependencies"
    echo "  clean           - Clean up temporary files"
    echo "  help            - Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./install_and_run.sh install"
    echo "  ./install_and_run.sh start_server"
    echo "  ./install_and_run.sh check"
}

# Function to start the server
start_server() {
    print_header "Starting Advanced Remote Control Server"
    
    if [ ! -f "start_server.sh" ]; then
        print_error "Server startup script not found. Run install first."
        exit 1
    fi
    
    print_status "Starting server..."
    ./start_server.sh
}

# Function to start a client
start_client() {
    print_header "Starting Client Connection"
    
    if [ ! -f "start_client.sh" ]; then
        print_error "Client startup script not found. Run install first."
        exit 1
    fi
    
    print_status "Starting client..."
    ./start_client.sh
}

# Function to update tools
update_tools() {
    print_header "Updating Tools and Dependencies"
    
    # Update system packages
    print_status "Updating system packages..."
    sudo apt-get update && sudo apt-get upgrade -y
    
    # Update Python packages
    print_status "Updating Python packages..."
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
    
    # Update WiFi tools
    if [ -d "wifijammer" ]; then
        print_status "Updating WiFiJammer..."
        cd wifijammer && git pull && cd ..
    fi
    
    if [ -d "fluxion" ]; then
        print_status "Updating Fluxion..."
        cd fluxion && git pull && cd ..
    fi
    
    # Update mobile tools
    if [ -d "drozer" ]; then
        print_status "Updating Drozer..."
        cd drozer && git pull && cd ..
    fi
    
    # Update crypto tools
    if [ -d "HashBuster" ]; then
        print_status "Updating HashBuster..."
        cd HashBuster && git pull && cd ..
    fi
    
    print_status "Tools and dependencies updated"
}

# Function to clean up
clean_up() {
    print_header "Cleaning Up Temporary Files"
    
    # Remove temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +
    find . -name "*.log" -delete
    
    # Clean up build artifacts
    if [ -d "build" ]; then
        rm -rf build
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist
    fi
    
    print_status "Cleanup completed"
}

# Main installation function
install_system() {
    print_header "Advanced Remote Control System - Phase 4 Installation"
    
    # Check if running as root
    check_root
    
    # Create directories
    create_directories
    
    # Install system packages
    install_system_packages
    
    # Create requirements file
    create_requirements
    
    # Install Python dependencies
    install_python_dependencies
    
    # Install WiFi tools
    install_wifi_tools
    
    # Install mobile attack tools
    install_mobile_tools
    
    # Install crypto cracking tools
    install_crypto_tools
    
    # Generate SSL certificates
    generate_ssl_certificates
    
    # Create configuration files
    create_config_files
    
    # Create startup scripts
    create_startup_scripts
    
    # Run system checks
    run_system_checks
    
    print_header "Installation Completed Successfully!"
    echo -e "${GREEN}The Advanced Remote Control System has been installed successfully.${NC}"
    echo -e "${GREEN}You can now use the following commands:${NC}"
    echo "  ./install_and_run.sh start_server  - Start the server"
    echo "  ./install_and_run.sh start_client  - Start a client"
    echo "  ./install_and_run.sh check         - Run system checks"
}

# Main script logic
case "${1:-help}" in
    "install")
        install_system
        ;;
    "start_server")
        start_server
        ;;
    "start_client")
        start_client
        ;;
    "check")
        run_system_checks
        ;;
    "update")
        update_tools
        ;;
    "clean")
        clean_up
        ;;
    "help"|*)
        display_usage
        ;;
esac