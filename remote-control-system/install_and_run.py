#!/usr/bin/env python3
"""
Advanced Remote Control System - Installation and Setup Script
Phase 4: Advanced Jamming and Attack Modules
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse
import asyncio
import time
from pathlib import Path

class SystemInstaller:
    """Advanced Remote Control System Installer"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine()
        self.install_dir = Path("remote-control-system")
        self.tools_dir = self.install_dir / "external_tools"
        
    def install_system(self):
        """Install the complete system"""
        print("🚀 Advanced Remote Control System - Phase 4")
        print("=" * 50)
        
        try:
            # Create directories
            self._create_directories()
            
            # Install dependencies
            self._install_dependencies()
            
            # Setup tools
            self._setup_tools()
            
            # Create certificates
            self._create_certificates()
            
            # Setup wordlists
            self._setup_wordlists()
            
            print("\n✅ Installation completed successfully!")
            print("🎯 Phase 4: Advanced Jamming and Attack Modules Ready")
            
        except Exception as e:
            print(f"❌ Installation failed: {str(e)}")
            sys.exit(1)
    
    def _create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            self.install_dir,
            self.tools_dir,
            self.install_dir / "wifi_attacks",
            self.install_dir / "mobile_attacks", 
            self.install_dir / "crypto_attacks",
            self.install_dir / "certificates",
            self.install_dir / "wordlists",
            self.install_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")
        
        dependencies = [
            "websockets",
            "asyncio",
            "psutil",
            "cryptography",
            "requests",
            "nmap-python",
            "adb-shell",
            "paramiko",
            "scapy",
            "pycryptodome"
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed: {dep}")
            except subprocess.CalledProcessError:
                print(f"  ⚠️  Failed to install: {dep}")
    
    def _setup_tools(self):
        """Setup external tools"""
        print("\n🔧 Setting up external tools...")
        
        # WiFi tools
        self._setup_wifi_tools()
        
        # Mobile tools
        self._setup_mobile_tools()
        
        # Crypto tools
        self._setup_crypto_tools()
    
    def _setup_wifi_tools(self):
        """Setup WiFi jamming tools"""
        print("  📡 Setting up WiFi tools...")
        
        # WiFiJammer
        wifijammer_dir = self.tools_dir / "wifijammer"
        if not wifijammer_dir.exists():
            subprocess.run([
                "git", "clone", "https://github.com/DanMcInerney/wifijammer.git",
                str(wifijammer_dir)
            ], check=True)
            print("    ✅ WiFiJammer installed")
        
        # Fluxion
        fluxion_dir = self.tools_dir / "fluxion"
        if not fluxion_dir.exists():
            subprocess.run([
                "git", "clone", "https://github.com/FluxionNetwork/fluxion.git",
                str(fluxion_dir)
            ], check=True)
            print("    ✅ Fluxion installed")
    
    def _setup_mobile_tools(self):
        """Setup mobile attack tools"""
        print("  📱 Setting up mobile tools...")
        
        # Drozer
        drozer_dir = self.tools_dir / "drozer"
        if not drozer_dir.exists():
            subprocess.run([
                "git", "clone", "https://github.com/FSecureLABS/drozer.git",
                str(drozer_dir)
            ], check=True)
            print("    ✅ Drozer installed")
        
        # Apktool
        apktool_dir = self.tools_dir / "apktool"
        if not apktool_dir.exists():
            subprocess.run([
                "git", "clone", "https://github.com/iBotPeaches/Apktool.git",
                str(apktool_dir)
            ], check=True)
            print("    ✅ Apktool installed")
    
    def _setup_crypto_tools(self):
        """Setup crypto cracking tools"""
        print("  🔐 Setting up crypto tools...")
        
        # HashBuster
        hashbuster_dir = self.tools_dir / "hashbuster"
        if not hashbuster_dir.exists():
            subprocess.run([
                "git", "clone", "https://github.com/s0md3v/Hash-Buster.git",
                str(hashbuster_dir)
            ], check=True)
            print("    ✅ HashBuster installed")
    
    def _create_certificates(self):
        """Create SSL certificates"""
        print("\n🔒 Creating SSL certificates...")
        
        cert_dir = self.install_dir / "certificates"
        cert_file = cert_dir / "server.crt"
        key_file = cert_dir / "server.key"
        
        if not cert_file.exists() or not key_file.exists():
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096",
                "-keyout", str(key_file), "-out", str(cert_file),
                "-days", "365", "-nodes", "-subj", "/C=US/ST=State/L=City/O=Org/CN=localhost"
            ], check=True)
            print("  ✅ SSL certificates created")
    
    def _setup_wordlists(self):
        """Setup wordlists for attacks"""
        print("\n📚 Setting up wordlists...")
        
        wordlist_dir = self.install_dir / "wordlists"
        
        # Download rockyou.txt if not exists
        rockyou_file = wordlist_dir / "rockyou.txt"
        if not rockyou_file.exists():
            # Create a sample wordlist
            with open(rockyou_file, 'w') as f:
                common_passwords = [
                    "password", "123456", "admin", "root", "user",
                    "test", "guest", "welcome", "secret", "qwerty"
                ]
                f.write('\n'.join(common_passwords))
            print("  ✅ Wordlist created")
    
    def run_server(self):
        """Run the server"""
        print("\n🚀 Starting Advanced Remote Control System...")
        print("🎯 Phase 4: Advanced Jamming and Attack Modules")
        
        try:
            # Change to install directory
            os.chdir(self.install_dir)
            
            # Start server
            subprocess.run([
                sys.executable, "server.py",
                "--host", "0.0.0.0",
                "--port", "8080",
                "--ssl"
            ])
            
        except KeyboardInterrupt:
            print("\n⏹️  Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Advanced Remote Control System")
    parser.add_argument("--install", action="store_true", help="Install the system")
    parser.add_argument("--run", action="store_true", help="Run the server")
    parser.add_argument("--full", action="store_true", help="Install and run")
    
    args = parser.parse_args()
    
    installer = SystemInstaller()
    
    if args.install or args.full:
        installer.install_system()
    
    if args.run or args.full:
        installer.run_server()

if __name__ == "__main__":
    main()