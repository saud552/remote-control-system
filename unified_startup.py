#!/usr/bin/env python3
"""
Unified Startup Script for Advanced Remote Control System
Phase 1: Fix Startup Mechanism
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional
try:
    import psutil
except ImportError:
    psutil = None

class UnifiedStartup:
    """Unified startup manager for all system components"""
    
    def __init__(self):
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.processes = {}
        self.running = False
        
        # Component ports (resolved conflicts)
        self.ports = {
            "command_server": 10001,  # Main command server
            "web_dashboard": 8081,    # Web dashboard
            "api_server": 8000,       # API server
            "telegram_bot": None      # Bot runs in background
        }
        
        # Component paths
        self.paths = {
            "command_server": "remote-control-system/command-server/server.js",
            "web_dashboard": "web_dashboard.py",
            "api_server": "remote-control-system/api/advanced_api_server.py",
            "telegram_bot": "remote-control-system/telegram-bot/bot.py"
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self) -> Dict:
        """Load system configuration"""
        try:
            with open("server_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            config = {
                "command_server": {
                    "port": 10001,
                    "host": "0.0.0.0",
                    "ssl_enabled": False
                },
                "web_dashboard": {
                    "port": 8081,
                    "host": "0.0.0.0",
                    "ssl_enabled": False
                },
                "api_server": {
                    "port": 8000,
                    "host": "0.0.0.0"
                },
                "telegram_bot": {
                    "enabled": True
                }
            }
            with open("server_config.json", "w") as f:
                json.dump(config, f, indent=4)
            return config
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/unified_startup.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def check_dependencies(self) -> bool:
        """Check if all dependencies are installed"""
        self.logger.info("Checking dependencies...")
        
        # Check Node.js
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            self.logger.info("✓ Node.js found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("✗ Node.js not found")
            return False
        
        # Check Python
        try:
            subprocess.run(["python3", "--version"], check=True, capture_output=True)
            self.logger.info("✓ Python3 found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("✗ Python3 not found")
            return False
        
        # Check npm
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            self.logger.info("✓ npm found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("✗ npm not found")
            return False
        
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.logger.info("Installing dependencies...")
        
        # Install Node.js dependencies
        if os.path.exists("remote-control-system/command-server/package.json"):
            self.logger.info("Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], cwd="remote-control-system/command-server", check=True)
        
        # Install Python dependencies
        if os.path.exists("requirements.txt"):
            self.logger.info("Installing Python dependencies...")
            subprocess.run(["pip3", "install", "-r", "requirements.txt"], check=True)
    
    def check_ports(self) -> bool:
        """Check if required ports are available"""
        self.logger.info("Checking port availability...")
        
        for component, port in self.ports.items():
            if port is None:
                continue
            
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    self.logger.warning(f"Port {port} ({component}) is already in use")
                    return False
                else:
                    self.logger.info(f"✓ Port {port} ({component}) is available")
            except Exception as e:
                self.logger.error(f"Error checking port {port}: {e}")
                return False
        
        return True
    
    def start_command_server(self):
        """Start the command server"""
        self.logger.info("Starting command server...")
        
        cmd = ["node", self.paths["command_server"]]
        env = os.environ.copy()
        env["PORT"] = str(self.ports["command_server"])
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd="remote-control-system/command-server",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["command_server"] = process
            self.logger.info(f"Command server started (PID: {process.pid})")
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.logger.info("✓ Command server is running")
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error(f"Command server failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting command server: {e}")
            return False
    
    def start_web_dashboard(self):
        """Start the web dashboard"""
        self.logger.info("Starting web dashboard...")
        
        cmd = ["python3", self.paths["web_dashboard"]]
        env = os.environ.copy()
        
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["web_dashboard"] = process
            self.logger.info(f"Web dashboard started (PID: {process.pid})")
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.logger.info("✓ Web dashboard is running")
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error(f"Web dashboard failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting web dashboard: {e}")
            return False
    
    def start_api_server(self):
        """Start the API server"""
        self.logger.info("Starting API server...")
        
        cmd = ["python3", self.paths["api_server"]]
        env = os.environ.copy()
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd="remote-control-system/api",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["api_server"] = process
            self.logger.info(f"API server started (PID: {process.pid})")
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.logger.info("✓ API server is running")
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error(f"API server failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting API server: {e}")
            return False
    
    def start_telegram_bot(self):
        """Start the Telegram bot"""
        self.logger.info("Starting Telegram bot...")
        
        cmd = ["python3", self.paths["telegram_bot"]]
        env = os.environ.copy()
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd="remote-control-system/telegram-bot",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["telegram_bot"] = process
            self.logger.info(f"Telegram bot started (PID: {process.pid})")
            
            # Wait a moment for bot to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                self.logger.info("✓ Telegram bot is running")
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error(f"Telegram bot failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Telegram bot: {e}")
            return False
    
    def start_all_components(self):
        """Start all system components"""
        self.logger.info("Starting all system components...")
        
        # Start components in order
        components = [
            ("command_server", self.start_command_server),
            ("web_dashboard", self.start_web_dashboard),
            ("api_server", self.start_api_server),
            ("telegram_bot", self.start_telegram_bot)
        ]
        
        failed_components = []
        
        for component_name, start_func in components:
            if not start_func():
                failed_components.append(component_name)
        
        if failed_components:
            self.logger.error(f"Failed to start components: {failed_components}")
            return False
        else:
            self.logger.info("✓ All components started successfully")
            return True
    
    def stop_all_components(self):
        """Stop all system components"""
        self.logger.info("Stopping all system components...")
        
        for component_name, process in self.processes.items():
            if process and process.poll() is None:
                self.logger.info(f"Stopping {component_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Force killing {component_name}")
                    process.kill()
        
        self.processes.clear()
        self.logger.info("✓ All components stopped")
    
    def monitor_components(self):
        """Monitor running components"""
        while self.running:
            for component_name, process in list(self.processes.items()):
                if process and process.poll() is not None:
                    self.logger.warning(f"Component {component_name} has stopped")
                    del self.processes[component_name]
            
            time.sleep(5)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all_components()
        sys.exit(0)
    
    def show_status(self):
        """Show status of all components"""
        self.logger.info("System Status:")
        
        for component_name, process in self.processes.items():
            if process and process.poll() is None:
                self.logger.info(f"  ✓ {component_name}: Running (PID: {process.pid})")
            else:
                self.logger.info(f"  ✗ {component_name}: Stopped")
        
        # Show port usage
        self.logger.info("Port Usage:")
        for component, port in self.ports.items():
            if port:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        self.logger.info(f"  ✓ Port {port} ({component}): In use")
                    else:
                        self.logger.info(f"  ✗ Port {port} ({component}): Available")
                except Exception:
                    self.logger.info(f"  ? Port {port} ({component}): Unknown")
    
    def run(self):
        """Main run method"""
        self.logger.info("🚀 Starting Advanced Remote Control System")
        self.logger.info("==========================================")
        
        # Check dependencies
        if not self.check_dependencies():
            self.logger.error("Dependencies check failed")
            return False
        
        # Install dependencies if needed
        self.install_dependencies()
        
        # Check ports
        if not self.check_ports():
            self.logger.error("Port check failed")
            return False
        
        # Start all components
        if not self.start_all_components():
            self.logger.error("Failed to start all components")
            return False
        
        self.running = True
        
        # Show status
        self.show_status()
        
        self.logger.info("✅ System is running!")
        self.logger.info("📊 Access URLs:")
        self.logger.info(f"  🔧 Command Server: http://localhost:{self.ports['command_server']}")
        self.logger.info(f"  🌐 Web Dashboard: http://localhost:{self.ports['web_dashboard']}")
        self.logger.info(f"  📡 API Server: http://localhost:{self.ports['api_server']}")
        self.logger.info("  🤖 Telegram Bot: Running in background")
        
        # Start monitoring
        try:
            self.monitor_components()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop_all_components()

def main():
    """Main entry point"""
    startup = UnifiedStartup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            startup.run()
        elif command == "stop":
            startup.stop_all_components()
        elif command == "status":
            startup.show_status()
        elif command == "check":
            startup.check_dependencies()
            startup.check_ports()
        else:
            print("Usage: python3 unified_startup.py [start|stop|status|check]")
    else:
        startup.run()

if __name__ == "__main__":
    main()