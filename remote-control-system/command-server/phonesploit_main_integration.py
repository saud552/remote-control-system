"""
PhoneSploit Main Integration
Main integration file for all PhoneSploit features
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional
from datetime import datetime

# Import all PhoneSploit modules
from enhanced_phonesploit_integration import PhoneSploitIntegration
from phonesploit_command_executor import PhoneSploitCommandExecutor
from enhanced_data_collection import EnhancedDataCollection
from enhanced_remote_control import EnhancedRemoteControl
from enhanced_hacking_system import EnhancedHackingSystem

class PhoneSploitMainIntegration:
    """Main integration class for all PhoneSploit features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all subsystems
        self.integration = PhoneSploitIntegration()
        self.command_executor = PhoneSploitCommandExecutor()
        self.data_collection = EnhancedDataCollection()
        self.remote_control = EnhancedRemoteControl()
        self.hacking_system = EnhancedHackingSystem()
        
        # Set current device for all subsystems
        self.current_device = None
        
        self.logger.info("PhoneSploit main integration initialized")
    
    def set_current_device(self, device_id: str):
        """Set current device for all subsystems"""
        self.current_device = device_id
        self.command_executor.current_device = device_id
        self.data_collection.current_device = device_id
        self.remote_control.current_device = device_id
        self.hacking_system.current_device = device_id
        
        self.logger.info(f"Current device set to: {device_id}")
    
    async def connect_to_device(self, ip_address: str, port: int = 5555) -> Dict:
        """Connect to device using PhoneSploit methods"""
        try:
            # Use command executor to connect
            result = await self.command_executor.connect_device(ip_address, port)
            
            if result["success"]:
                self.set_current_device(result["device"])
                
                # Mark connection features as implemented
                self.integration.mark_feature_implemented("connect")
                self.integration.mark_feature_implemented("list_devices")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error connecting to device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_screenshot(self, save_path: str = None) -> Dict:
        """Get device screenshot using PhoneSploit methods"""
        try:
            result = await self.command_executor.get_device_screenshot(save_path)
            
            if result["success"]:
                # Mark screenshot features as implemented
                self.integration.mark_feature_implemented("get_screenshot")
                self.integration.mark_feature_implemented("anonymous_screenshot")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting screenshot: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_device_screen(self, duration: int = 10, save_path: str = None) -> Dict:
        """Record device screen using PhoneSploit methods"""
        try:
            result = await self.command_executor.record_device_screen(duration, save_path)
            
            if result["success"]:
                # Mark screen recording features as implemented
                self.integration.mark_feature_implemented("screenrecord")
                self.integration.mark_feature_implemented("anonymous_screenrecord")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error recording screen: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def copy_whatsapp_data(self, save_path: str = None) -> Dict:
        """Copy WhatsApp data using PhoneSploit methods"""
        try:
            result = await self.data_collection.copy_whatsapp_data(save_path)
            
            if result["success"]:
                # Mark data collection features as implemented
                self.integration.mark_feature_implemented("copy_whatsapp")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error copying WhatsApp data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def dump_device_contacts(self, save_path: str = None) -> Dict:
        """Dump device contacts using PhoneSploit methods"""
        try:
            result = await self.data_collection.dump_device_contacts(save_path)
            
            if result["success"]:
                # Mark data collection features as implemented
                self.integration.mark_feature_implemented("dump_contacts")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error dumping contacts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def dump_sms_messages(self, save_path: str = None) -> Dict:
        """Dump SMS messages using PhoneSploit methods"""
        try:
            result = await self.data_collection.dump_sms_messages(save_path)
            
            if result["success"]:
                # Mark data collection features as implemented
                self.integration.mark_feature_implemented("dump_sms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error dumping SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_sms_message(self, phone_number: str, message: str) -> Dict:
        """Send SMS message using PhoneSploit methods"""
        try:
            result = await self.remote_control.send_sms_message(phone_number, message)
            
            if result["success"]:
                # Mark remote control features as implemented
                self.integration.mark_feature_implemented("send_sms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unlock_device_screen(self) -> Dict:
        """Unlock device screen using PhoneSploit methods"""
        try:
            result = await self.remote_control.unlock_device_screen()
            
            if result["success"]:
                # Mark remote control features as implemented
                self.integration.mark_feature_implemented("unlock_device")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error unlocking device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def lock_device_screen(self) -> Dict:
        """Lock device screen using PhoneSploit methods"""
        try:
            result = await self.remote_control.lock_device_screen()
            
            if result["success"]:
                # Mark remote control features as implemented
                self.integration.mark_feature_implemented("lock_device")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error locking device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def power_off_device(self) -> Dict:
        """Power off device using PhoneSploit methods"""
        try:
            result = await self.remote_control.power_off_device()
            
            if result["success"]:
                # Mark remote control features as implemented
                self.integration.mark_feature_implemented("power_off")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error powering off device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def install_apk_on_device(self, apk_path: str) -> Dict:
        """Install APK on device using PhoneSploit methods"""
        try:
            result = await self.command_executor.install_apk_on_device(apk_path)
            
            if result["success"]:
                # Mark app management features as implemented
                self.integration.mark_feature_implemented("install_app")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error installing APK: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def uninstall_app_from_device(self, package_name: str) -> Dict:
        """Uninstall app from device using PhoneSploit methods"""
        try:
            result = await self.command_executor.uninstall_app_from_device(package_name)
            
            if result["success"]:
                # Mark app management features as implemented
                self.integration.mark_feature_implemented("uninstall_app")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error uninstalling app: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def launch_app_on_device(self, package_name: str) -> Dict:
        """Launch app on device using PhoneSploit methods"""
        try:
            result = await self.command_executor.launch_app_on_device(package_name)
            
            if result["success"]:
                # Mark app management features as implemented
                self.integration.mark_feature_implemented("launch_app")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error launching app: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_installed_apps(self) -> Dict:
        """List installed apps using PhoneSploit methods"""
        try:
            result = await self.command_executor.list_installed_apps()
            
            if result["success"]:
                # Mark app management features as implemented
                self.integration.mark_feature_implemented("list_apps")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error listing apps: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_device_information(self) -> Dict:
        """Get device information using PhoneSploit methods"""
        try:
            result = await self.data_collection.get_device_information()
            
            if result["success"]:
                # Mark information features as implemented
                self.integration.mark_feature_implemented("get_device_info")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting device information: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def scan_network_devices(self, network_range: str = "192.168.1.0/24") -> Dict:
        """Scan network for devices using PhoneSploit methods"""
        try:
            result = await self.data_collection.scan_network_devices(network_range)
            
            if result["success"]:
                # Mark information features as implemented
                self.integration.mark_feature_implemented("scan_network")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error scanning network: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def hack_device_complete(self, target_ip: str, payload_type: str = "android/meterpreter/reverse_tcp") -> Dict:
        """Complete device hacking using PhoneSploit methods"""
        try:
            result = await self.hacking_system.hack_device_complete(target_ip, payload_type)
            
            if result["success"]:
                # Mark hacking features as implemented
                self.integration.mark_feature_implemented("hack")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error hacking device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def mirror_device_screen(self) -> Dict:
        """Mirror device screen using PhoneSploit methods"""
        try:
            result = await self.remote_control.mirror_device_screen()
            
            if result["success"]:
                # Mark media features as implemented
                self.integration.mark_feature_implemented("mirror")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error mirroring device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_device_audio(self, duration: int = 30, save_path: str = None) -> Dict:
        """Record device audio using PhoneSploit methods"""
        try:
            result = await self.remote_control.record_device_audio(duration, save_path)
            
            if result["success"]:
                # Mark media features as implemented
                self.integration.mark_feature_implemented("record_audio")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error recording audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reboot_device(self, mode: str = "system") -> Dict:
        """Reboot device using PhoneSploit methods"""
        try:
            result = await self.remote_control.reboot_device(mode)
            
            if result["success"]:
                # Mark reboot features as implemented
                self.integration.mark_feature_implemented("reboot")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error rebooting device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_integration_statistics(self) -> Dict:
        """Get comprehensive integration statistics"""
        feature_stats = self.integration.get_feature_statistics()
        command_stats = self.command_executor.get_execution_statistics()
        collection_stats = self.data_collection.get_collection_statistics()
        control_stats = self.remote_control.get_control_statistics()
        hacking_stats = self.hacking_system.get_hacking_statistics()
        system_requirements = self.hacking_system.get_system_requirements_status()
        
        return {
            "feature_statistics": feature_stats,
            "command_statistics": command_stats,
            "collection_statistics": collection_stats,
            "control_statistics": control_stats,
            "hacking_statistics": hacking_stats,
            "system_requirements": system_requirements,
            "current_device": self.current_device,
            "integration_status": "active"
        }
    
    def export_integration_report(self) -> Dict:
        """Export comprehensive integration report"""
        timestamp = datetime.now().isoformat()
        
        return {
            "timestamp": timestamp,
            "integration_version": "1.0.0",
            "statistics": self.get_integration_statistics(),
            "feature_list": self.integration.export_feature_list(),
            "system_status": {
                "adb_available": self.hacking_system._check_adb_availability(),
                "metasploit_available": self.hacking_system.metasploit_available,
                "nmap_available": self.hacking_system._check_nmap_availability(),
                "scrcpy_available": self.hacking_system._check_scrcpy_availability()
            },
            "subsystems": {
                "integration": "active",
                "command_executor": "active",
                "data_collection": "active",
                "remote_control": "active",
                "hacking_system": "active"
            }
        }
    
    def get_available_commands(self) -> List[Dict]:
        """Get list of available PhoneSploit commands"""
        commands = []
        
        for feature in self.integration.get_all_features():
            if feature.implemented:
                commands.append({
                    "name": feature.name,
                    "description": feature.description,
                    "function_name": feature.function_name,
                    "category": feature.category,
                    "priority": feature.priority
                })
        
        return commands
    
    def get_pending_commands(self) -> List[Dict]:
        """Get list of pending PhoneSploit commands"""
        commands = []
        
        for feature in self.integration.get_pending_features():
            commands.append({
                "name": feature.name,
                "description": feature.description,
                "function_name": feature.function_name,
                "category": feature.category,
                "priority": feature.priority
            })
        
        return commands