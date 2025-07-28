"""
Advanced Tool Manager System
Manages external hacking tools with automatic installation, updates, and execution
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import shutil
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib
import zipfile
import tarfile

class ToolType(Enum):
    """Tool type enumeration"""
    RAT = "rat"
    PHISHING = "phishing"
    PAYLOAD = "payload"
    WIFI_JAMMING = "wifi_jamming"
    HASH_CRACKING = "hash_cracking"
    RECONNAISSANCE = "reconnaissance"
    EXPLOIT = "exploit"
    STEGANOGRAPHY = "steganography"

@dataclass
class ToolInfo:
    """Tool information structure"""
    name: str
    tool_type: ToolType
    github_url: str
    description: str
    version: str
    dependencies: List[str]
    install_commands: List[str]
    run_commands: List[str]
    is_installed: bool = False
    is_updated: bool = False
    last_updated: Optional[float] = None
    status: str = "unknown"

class AdvancedToolManager:
    """Advanced tool manager for external hacking tools"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools_directory = "external_tools"
        self.tools_config_file = "tools_config.json"
        self.installed_tools: Dict[str, ToolInfo] = {}
        self.tool_processes: Dict[str, Any] = {}
        
        # Create tools directory
        os.makedirs(self.tools_directory, exist_ok=True)
        
        # Initialize tools database
        self._initialize_tools_database()
        
        # Load existing tools
        self._load_tools_config()
        
    def _initialize_tools_database(self):
        """Initialize database of available tools"""
        self.available_tools = {
            # RAT Tools
            "stitch": ToolInfo(
                name="Stitch",
                tool_type=ToolType.RAT,
                github_url="https://github.com/nathanlopez/Stitch",
                description="Cross-platform Python RAT framework",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/nathanlopez/Stitch.git",
                    "cd Stitch && pip install -r lnx_requirements.txt"
                ],
                run_commands=["cd Stitch && python main.py"]
            ),
            
            "pyshell": ToolInfo(
                name="Pyshell",
                tool_type=ToolType.RAT,
                github_url="https://github.com/knassar702/pyshell",
                description="Advanced Python RAT with file transfer",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/knassar702/pyshell.git",
                    "cd pyshell && pip install pyscreenshot python-nmap requests"
                ],
                run_commands=["cd pyshell && python pyshell.py"]
            ),
            
            "thefatrat": ToolInfo(
                name="TheFatRat",
                tool_type=ToolType.PAYLOAD,
                github_url="https://github.com/Screetsec/TheFatRat",
                description="Advanced payload generator with anti-detection",
                version="latest",
                dependencies=["git", "java"],
                install_commands=[
                    "git clone https://github.com/Screetsec/TheFatRat.git",
                    "cd TheFatRat && chmod +x setup.sh"
                ],
                run_commands=["cd TheFatRat && bash setup.sh"]
            ),
            
            # Phishing Tools
            "hiddeneye": ToolInfo(
                name="HiddenEye",
                tool_type=ToolType.PHISHING,
                github_url="https://github.com/DarkSecDevelopers/HiddenEye",
                description="Modern phishing tool with advanced features",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/DarkSecDevelopers/HiddenEye.git",
                    "cd HiddenEye && pip install -r requirements.txt"
                ],
                run_commands=["cd HiddenEye && python3 HiddenEye.py"]
            ),
            
            "evilginx2": ToolInfo(
                name="Evilginx2",
                tool_type=ToolType.PHISHING,
                github_url="https://github.com/kgretzky/evilginx2",
                description="Advanced man-in-the-middle attack framework",
                version="latest",
                dependencies=["go", "git"],
                install_commands=[
                    "go get -u github.com/kgretzky/evilginx2",
                    "cd $GOPATH/src/github.com/kgretzky/evilginx2 && make"
                ],
                run_commands=["evilginx"]
            ),
            
            # WiFi Jamming Tools
            "wifijammer": ToolInfo(
                name="WiFiJammer",
                tool_type=ToolType.WIFI_JAMMING,
                github_url="https://github.com/MisterBianco/wifijammer-ng",
                description="Advanced WiFi jamming and deauthentication",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/MisterBianco/wifijammer-ng.git",
                    "cd wifijammer-ng && pip install -r requirements.txt"
                ],
                run_commands=["cd wifijammer-ng && python wifijammer.py"]
            ),
            
            "fluxion": ToolInfo(
                name="Fluxion",
                tool_type=ToolType.WIFI_JAMMING,
                github_url="https://github.com/FluxionNetwork/fluxion",
                description="Advanced WiFi attack framework",
                version="latest",
                dependencies=["git"],
                install_commands=[
                    "git clone https://github.com/FluxionNetwork/fluxion.git",
                    "cd fluxion && chmod +x fluxion.sh"
                ],
                run_commands=["cd fluxion && bash fluxion.sh"]
            ),
            
            # Hash Cracking Tools
            "hashbuster": ToolInfo(
                name="HashBuster",
                tool_type=ToolType.HASH_CRACKING,
                github_url="https://github.com/s0md3v/Hash-Buster",
                description="Advanced hash cracking and identification",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/s0md3v/Hash-Buster.git",
                    "cd Hash-Buster && make install"
                ],
                run_commands=["buster -h"]
            ),
            
            # Reconnaissance Tools
            "reconspider": ToolInfo(
                name="ReconSpider",
                tool_type=ToolType.RECONNAISSANCE,
                github_url="https://github.com/bhavsec/reconspider",
                description="Advanced OSINT reconnaissance framework",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/bhavsec/reconspider.git",
                    "cd reconspider && python3 setup.py install"
                ],
                run_commands=["cd reconspider && python3 reconspider.py"]
            ),
            
            "sherlock": ToolInfo(
                name="Sherlock",
                tool_type=ToolType.RECONNAISSANCE,
                github_url="https://github.com/sherlock-project/sherlock",
                description="Hunt down social media accounts by username",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/sherlock-project/sherlock.git",
                    "cd sherlock && pip install -r requirements.txt"
                ],
                run_commands=["cd sherlock && python3 sherlock"]
            ),
            
            # Exploit Tools
            "metasploit": ToolInfo(
                name="Metasploit",
                tool_type=ToolType.EXPLOIT,
                github_url="https://github.com/rapid7/metasploit-framework",
                description="Advanced penetration testing framework",
                version="latest",
                dependencies=["curl"],
                install_commands=[
                    "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall",
                    "chmod +x msfinstall && ./msfinstall"
                ],
                run_commands=["msfconsole"]
            ),
            
            # Steganography Tools
            "stegcracker": ToolInfo(
                name="StegCracker",
                tool_type=ToolType.STEGANOGRAPHY,
                github_url="https://github.com/Paradoxis/StegCracker",
                description="Advanced steganography tool",
                version="latest",
                dependencies=["python3", "git"],
                install_commands=[
                    "git clone https://github.com/Paradoxis/StegCracker.git",
                    "cd StegCracker && pip install -r requirements.txt"
                ],
                run_commands=["cd StegCracker && python3 stegcracker.py"]
            )
        }
    
    def _load_tools_config(self):
        """Load tools configuration from file"""
        try:
            if os.path.exists(self.tools_config_file):
                with open(self.tools_config_file, 'r') as f:
                    config = json.load(f)
                    for tool_name, tool_data in config.items():
                        if tool_name in self.available_tools:
                            tool = self.available_tools[tool_name]
                            tool.is_installed = tool_data.get("is_installed", False)
                            tool.is_updated = tool_data.get("is_updated", False)
                            tool.last_updated = tool_data.get("last_updated")
                            tool.status = tool_data.get("status", "unknown")
                            self.installed_tools[tool_name] = tool
        except Exception as e:
            self.logger.error(f"Error loading tools config: {str(e)}")
    
    def _save_tools_config(self):
        """Save tools configuration to file"""
        try:
            config = {}
            for tool_name, tool in self.installed_tools.items():
                config[tool_name] = {
                    "is_installed": tool.is_installed,
                    "is_updated": tool.is_updated,
                    "last_updated": tool.last_updated,
                    "status": tool.status
                }
            
            with open(self.tools_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving tools config: {str(e)}")
    
    async def install_tool(self, tool_name: str, force_reinstall: bool = False) -> Dict:
        """Install a tool"""
        try:
            if tool_name not in self.available_tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found"
                }
            
            tool = self.available_tools[tool_name]
            
            # Check if already installed
            if tool.is_installed and not force_reinstall:
                return {
                    "success": True,
                    "message": f"Tool {tool_name} is already installed"
                }
            
            self.logger.info(f"Installing tool: {tool_name}")
            
            # Create tool directory
            tool_dir = os.path.join(self.tools_directory, tool_name)
            os.makedirs(tool_dir, exist_ok=True)
            
            # Change to tool directory
            original_dir = os.getcwd()
            os.chdir(tool_dir)
            
            # Execute install commands
            for command in tool.install_commands:
                self.logger.info(f"Executing: {command}")
                
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    subprocess.run,
                    command.split(),
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE,
                    timeout=300
                )
                
                if result.returncode != 0:
                    os.chdir(original_dir)
                    return {
                        "success": False,
                        "error": f"Installation failed for {tool_name}",
                        "stderr": result.stderr.decode()
                    }
            
            # Update tool status
            tool.is_installed = True
            tool.is_updated = True
            tool.last_updated = time.time()
            tool.status = "installed"
            
            self.installed_tools[tool_name] = tool
            self._save_tools_config()
            
            os.chdir(original_dir)
            
            return {
                "success": True,
                "message": f"Tool {tool_name} installed successfully",
                "tool_info": asdict(tool)
            }
            
        except Exception as e:
            self.logger.error(f"Error installing tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_tool(self, tool_name: str) -> Dict:
        """Update a tool"""
        try:
            if tool_name not in self.installed_tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is not installed"
                }
            
            tool = self.installed_tools[tool_name]
            tool_dir = os.path.join(self.tools_directory, tool_name)
            
            if not os.path.exists(tool_dir):
                return {
                    "success": False,
                    "error": f"Tool directory not found for {tool_name}"
                }
            
            self.logger.info(f"Updating tool: {tool_name}")
            
            # Change to tool directory
            original_dir = os.getcwd()
            os.chdir(tool_dir)
            
            # Update using git pull
            if os.path.exists(".git"):
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    subprocess.run,
                    ["git", "pull"],
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.PIPE,
                    timeout=60
                )
                
                if result.returncode == 0:
                    tool.is_updated = True
                    tool.last_updated = time.time()
                    tool.status = "updated"
                    self._save_tools_config()
                    
                    os.chdir(original_dir)
                    return {
                        "success": True,
                        "message": f"Tool {tool_name} updated successfully"
                    }
                else:
                    os.chdir(original_dir)
                    return {
                        "success": False,
                        "error": f"Update failed for {tool_name}",
                        "stderr": result.stderr.decode()
                    }
            else:
                os.chdir(original_dir)
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is not a git repository"
                }
                
        except Exception as e:
            self.logger.error(f"Error updating tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_tool(self, tool_name: str, parameters: Dict = None) -> Dict:
        """Run a tool"""
        try:
            if tool_name not in self.installed_tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is not installed"
                }
            
            tool = self.installed_tools[tool_name]
            tool_dir = os.path.join(self.tools_directory, tool_name)
            
            if not os.path.exists(tool_dir):
                return {
                    "success": False,
                    "error": f"Tool directory not found for {tool_name}"
                }
            
            self.logger.info(f"Running tool: {tool_name}")
            
            # Change to tool directory
            original_dir = os.getcwd()
            os.chdir(tool_dir)
            
            # Execute run commands
            for command in tool.run_commands:
                self.logger.info(f"Executing: {command}")
                
                # Add parameters if provided
                if parameters:
                    for key, value in parameters.items():
                        command = command.replace(f"{{{key}}}", str(value))
                
                process = await asyncio.create_subprocess_exec(
                    *command.split(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                self.tool_processes[tool_name] = process
                
                return {
                    "success": True,
                    "message": f"Tool {tool_name} started successfully",
                    "process_id": process.pid,
                    "command": command
                }
            
            os.chdir(original_dir)
            
        except Exception as e:
            self.logger.error(f"Error running tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_tool(self, tool_name: str) -> Dict:
        """Stop a running tool"""
        try:
            if tool_name in self.tool_processes:
                process = self.tool_processes[tool_name]
                process.terminate()
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                
                del self.tool_processes[tool_name]
                
                return {
                    "success": True,
                    "message": f"Tool {tool_name} stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is not running"
                }
                
        except Exception as e:
            self.logger.error(f"Error stopping tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of available tools"""
        return [asdict(tool) for tool in self.available_tools.values()]
    
    def get_installed_tools(self) -> List[Dict]:
        """Get list of installed tools"""
        return [asdict(tool) for tool in self.installed_tools.values()]
    
    def get_tool_status(self, tool_name: str) -> Dict:
        """Get status of a specific tool"""
        if tool_name in self.available_tools:
            tool = self.available_tools[tool_name]
            return {
                "name": tool.name,
                "is_installed": tool.is_installed,
                "is_updated": tool.is_updated,
                "status": tool.status,
                "last_updated": tool.last_updated,
                "is_running": tool_name in self.tool_processes
            }
        else:
            return {
                "error": f"Tool {tool_name} not found"
            }
    
    async def uninstall_tool(self, tool_name: str) -> Dict:
        """Uninstall a tool"""
        try:
            if tool_name not in self.installed_tools:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} is not installed"
                }
            
            # Stop tool if running
            if tool_name in self.tool_processes:
                await self.stop_tool(tool_name)
            
            # Remove tool directory
            tool_dir = os.path.join(self.tools_directory, tool_name)
            if os.path.exists(tool_dir):
                shutil.rmtree(tool_dir)
            
            # Update tool status
            tool = self.installed_tools[tool_name]
            tool.is_installed = False
            tool.is_updated = False
            tool.status = "uninstalled"
            
            del self.installed_tools[tool_name]
            self._save_tools_config()
            
            return {
                "success": True,
                "message": f"Tool {tool_name} uninstalled successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error uninstalling tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tool_statistics(self) -> Dict:
        """Get tool manager statistics"""
        total_tools = len(self.available_tools)
        installed_tools = len(self.installed_tools)
        running_tools = len(self.tool_processes)
        
        return {
            "total_tools": total_tools,
            "installed_tools": installed_tools,
            "running_tools": running_tools,
            "installation_rate": (installed_tools / total_tools * 100) if total_tools > 0 else 0
        }