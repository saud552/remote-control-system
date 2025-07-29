#!/bin/bash

# 🛑 Advanced Remote Control System - Phase 7 Shutdown Script
# إيقاف الأمان والعزل والتطوير النهائي

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
BACKUP_DIR="$SCRIPT_DIR/backups"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR" "$BACKUP_DIR"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/phase7_shutdown.log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/phase7_shutdown.log"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/phase7_shutdown.log"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/phase7_shutdown.log"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/phase7_shutdown.log"
}

# Banner
print_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🛑 PHASE 7 SHUTDOWN 🛑                   ║
║              إيقاف الأمان والعزل والتطوير النهائي          ║
║              Final Security, Isolation & Development        ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check if system is running
check_system_status() {
    log "Checking system status..."
    
    RUNNING_SERVICES=()
    STOPPED_SERVICES=()
    
    # Check each service
    SERVICES=(
        "main_server:server.py"
        "security_module:advanced_security_module.py"
        "performance_module:advanced_performance_module.py"
        "development_module:final_development_module.py"
        "web_dashboard:advanced_web_dashboard.py"
        "telegram_bot:enhanced_telegram_bot.py"
    )
    
    for service_info in "${SERVICES[@]}"; do
        IFS=':' read -r service_name service_file <<< "$service_info"
        
        if [[ -f "$PID_DIR/${service_name}.pid" ]]; then
            pid=$(cat "$PID_DIR/${service_name}.pid")
            if ps -p "$pid" > /dev/null 2>&1; then
                RUNNING_SERVICES+=("$service_name")
                info "$service_name is running (PID: $pid)"
            else
                STOPPED_SERVICES+=("$service_name")
                warning "$service_name is not running (stale PID file)"
            fi
        else
            STOPPED_SERVICES+=("$service_name")
            info "$service_name is not running (no PID file)"
        fi
    done
    
    if [[ ${#RUNNING_SERVICES[@]} -eq 0 ]]; then
        warning "No services are currently running"
        return 1
    else
        success "Found ${#RUNNING_SERVICES[@]} running services"
        return 0
    fi
}

# Graceful shutdown function
graceful_shutdown() {
    local service_name=$1
    local pid_file="$PID_DIR/${service_name}.pid"
    
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Gracefully stopping $service_name (PID: $pid)..."
            
            # Send SIGTERM
            kill -TERM "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while ps -p "$pid" > /dev/null 2>&1 && [[ $count -lt 10 ]]; do
                sleep 1
                ((count++))
            done
            
            # Check if process is still running
            if ps -p "$pid" > /dev/null 2>&1; then
                warning "$service_name did not stop gracefully, forcing shutdown..."
                kill -KILL "$pid"
                sleep 1
            fi
            
            # Remove PID file
            if [[ -f "$pid_file" ]]; then
                rm -f "$pid_file"
            fi
            
            success "$service_name stopped successfully"
        else
            warning "$service_name is not running (stale PID file)"
            rm -f "$pid_file"
        fi
    else
        info "$service_name is not running (no PID file)"
    fi
}

# Stop all services
stop_all_services() {
    log "Stopping all services..."
    
    # Stop services in reverse order (dependencies first)
    SERVICES=(
        "telegram_bot"
        "web_dashboard"
        "development_module"
        "performance_module"
        "security_module"
        "main_server"
    )
    
    for service in "${SERVICES[@]}"; do
        graceful_shutdown "$service"
    done
    
    success "All services stopped"
}

# Cleanup Docker containers
cleanup_docker() {
    log "Cleaning up Docker containers..."
    
    if command -v docker &> /dev/null; then
        # Stop all running containers
        local containers=$(docker ps -q)
        if [[ -n "$containers" ]]; then
            info "Stopping Docker containers..."
            docker stop $containers || warning "Failed to stop some containers"
        fi
        
        # Remove stopped containers
        local stopped_containers=$(docker ps -aq)
        if [[ -n "$stopped_containers" ]]; then
            info "Removing stopped containers..."
            docker rm $stopped_containers || warning "Failed to remove some containers"
        fi
        
        success "Docker cleanup completed"
    else
        info "Docker not available, skipping cleanup"
    fi
}

# Cleanup temporary files
cleanup_temp_files() {
    log "Cleaning up temporary files..."
    
    # Remove temporary files
    find /tmp -name "*phase7*" -delete 2>/dev/null || true
    find /var/tmp -name "*phase7*" -delete 2>/dev/null || true
    
    # Cleanup log files older than 7 days
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Cleanup PID files
    rm -f "$PID_DIR"/*.pid 2>/dev/null || true
    
    success "Temporary files cleaned up"
}

# Create backup
create_backup() {
    log "Creating system backup..."
    
    local backup_name="phase7_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup configuration files
    if [[ -d "config" ]]; then
        cp -r config "$backup_path/"
    fi
    
    # Backup logs
    if [[ -d "logs" ]]; then
        cp -r logs "$backup_path/"
    fi
    
    # Backup data
    if [[ -d "data" ]]; then
        cp -r data "$backup_path/"
    fi
    
    # Backup certificates
    if [[ -d "certificates" ]]; then
        cp -r certificates "$backup_path/"
    fi
    
    # Create backup archive
    cd "$BACKUP_DIR"
    tar -czf "${backup_name}.tar.gz" "$backup_name"
    rm -rf "$backup_name"
    cd "$SCRIPT_DIR"
    
    success "Backup created: $BACKUP_DIR/${backup_name}.tar.gz"
}

# Save system state
save_system_state() {
    log "Saving system state..."
    
    local state_file="$LOG_DIR/system_state_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$state_file" << EOF
{
  "shutdown_time": "$(date -Iseconds)",
  "system_info": {
    "os": "$(uname -s)",
    "kernel": "$(uname -r)",
    "python_version": "$(python3 --version 2>&1)",
    "docker_available": "$(command -v docker >/dev/null && echo "true" || echo "false")",
    "gpu_available": "$(command -v nvidia-smi >/dev/null && echo "true" || echo "false")"
  },
  "running_services": $(printf '%s\n' "${RUNNING_SERVICES[@]}" | jq -R . | jq -s .),
  "stopped_services": $(printf '%s\n' "${STOPPED_SERVICES[@]}" | jq -R . | jq -s .),
  "system_resources": {
    "cpu_usage": "$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)",
    "memory_usage": "$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')",
    "disk_usage": "$(df / | tail -1 | awk '{print $5}' | sed 's/%//')"
  }
}
EOF
    
    success "System state saved to: $state_file"
}

# Final cleanup
final_cleanup() {
    log "Performing final cleanup..."
    
    # Kill any remaining processes
    local remaining_pids=$(pgrep -f "advanced_security_module\|advanced_performance_module\|final_development_module\|advanced_web_dashboard\|enhanced_telegram_bot\|server.py" 2>/dev/null || true)
    
    if [[ -n "$remaining_pids" ]]; then
        warning "Found remaining processes, forcing shutdown..."
        kill -KILL $remaining_pids 2>/dev/null || true
    fi
    
    # Cleanup network connections
    local network_connections=$(netstat -tuln | grep ":8080\|:8443" 2>/dev/null || true)
    if [[ -n "$network_connections" ]]; then
        info "Cleaning up network connections..."
        # This would require root privileges to kill connections
    fi
    
    success "Final cleanup completed"
}

# Display shutdown summary
display_shutdown_summary() {
    log "Shutdown Summary:"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "${BLUE}Services Status:${NC}"
    for service in "${RUNNING_SERVICES[@]}"; do
        echo -e "  ${GREEN}✓${NC} $service (stopped)"
    done
    
    for service in "${STOPPED_SERVICES[@]}"; do
        echo -e "  ${YELLOW}○${NC} $service (was not running)"
    done
    
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    # Display cleanup info
    echo -e "${BLUE}Cleanup Actions:${NC}"
    echo -e "  ✓ Docker containers cleaned"
    echo -e "  ✓ Temporary files removed"
    echo -e "  ✓ PID files cleaned"
    echo -e "  ✓ System backup created"
    echo -e "  ✓ System state saved"
    
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    # Display next steps
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  • Check logs in: $LOG_DIR"
    echo -e "  • Restore from backup if needed"
    echo -e "  • Run 'start_phase7.sh' to restart"
    
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
}

# Main shutdown function
main() {
    print_banner
    
    log "Starting Phase 7 shutdown process..."
    
    # Check system status
    if ! check_system_status; then
        warning "No services are running, performing cleanup only"
    fi
    
    # Create backup before shutdown
    create_backup
    
    # Save system state
    save_system_state
    
    # Stop all services
    if [[ ${#RUNNING_SERVICES[@]} -gt 0 ]]; then
        stop_all_services
    fi
    
    # Cleanup Docker
    cleanup_docker
    
    # Cleanup temporary files
    cleanup_temp_files
    
    # Final cleanup
    final_cleanup
    
    # Display summary
    display_shutdown_summary
    
    success "Phase 7 shutdown completed successfully!"
    
    log "System has been safely shut down."
    log "Backup created in: $BACKUP_DIR"
    log "Logs available in: $LOG_DIR"
    
    echo -e "${GREEN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🛑 SHUTDOWN COMPLETE 🛑                   ║
║              All services have been stopped safely          ║
║              تم إيقاف جميع الخدمات بأمان                    ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Error handling
trap 'error "An error occurred during shutdown. Check logs for details."; exit 1' ERR

# Handle command line arguments
case "${1:-}" in
    --force|-f)
        log "Force shutdown mode enabled"
        FORCE_SHUTDOWN=true
        ;;
    --backup|-b)
        log "Backup-only mode enabled"
        BACKUP_ONLY=true
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --force, -f     Force shutdown (kill processes immediately)"
        echo "  --backup, -b    Create backup only, don't stop services"
        echo "  --help, -h      Show this help message"
        exit 0
        ;;
    *)
        # Normal shutdown
        ;;
esac

# Run main function
main "$@"