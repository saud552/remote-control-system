"""
Enhanced Remote Control System
Provides advanced remote control features from PhoneSploit
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Optional
from datetime import datetime

class EnhancedRemoteControl:
    """Enhanced remote control system for PhoneSploit features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adb_path = "adb"
        self.current_device = None
        self.control_history = []
        
    async def send_sms_message(self, phone_number: str, message: str) -> Dict:
        """Send SMS message from device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Send SMS using content provider
            sms_command = f"shell content insert --uri content://sms/sent --bind type:i:2 --bind address:s:{phone_number} --bind body:s:{message}"
            result = await self._execute_adb_command(sms_command)
            
            if "Success" in result or result.strip() == "":
                return {
                    "success": True,
                    "phone_number": phone_number,
                    "message": message,
                    "response": "SMS sent successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to send SMS",
                    "message": result
                }
                
        except Exception as e:
            self.logger.error(f"Error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unlock_device_screen(self) -> Dict:
        """Unlock device screen"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Wake up device
            await self._execute_adb_command("shell input keyevent 26")
            await asyncio.sleep(1)
            
            # Unlock screen (swipe up)
            await self._execute_adb_command("shell input swipe 540 1500 540 500")
            
            return {
                "success": True,
                "message": "Device unlocked successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error unlocking device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def lock_device_screen(self) -> Dict:
        """Lock device screen"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Lock screen
            await self._execute_adb_command("shell input keyevent 26")
            
            return {
                "success": True,
                "message": "Device locked successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error locking device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def power_off_device(self) -> Dict:
        """Power off device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Power off device
            await self._execute_adb_command("shell reboot -p")
            
            return {
                "success": True,
                "message": "Device powered off successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error powering off device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_keycodes(self, keycode: int) -> Dict:
        """Send keycodes to control device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Send keycode
            result = await self._execute_adb_command(f"shell input keyevent {keycode}")
            
            return {
                "success": True,
                "keycode": keycode,
                "message": "Keycode sent successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error sending keycode: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def open_link_on_device(self, url: str) -> Dict:
        """Open link on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Open link using intent
            intent_command = f"shell am start -a android.intent.action.VIEW -d {url}"
            result = await self._execute_adb_command(intent_command)
            
            return {
                "success": True,
                "url": url,
                "message": "Link opened successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error opening link: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def display_photo_on_device(self, photo_path: str) -> Dict:
        """Display photo on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not os.path.exists(photo_path):
                return {
                    "success": False,
                    "error": "Photo file does not exist"
                }
            
            # Push photo to device
            device_path = f"/sdcard/display_photo_{int(time.time())}.jpg"
            await self._execute_adb_command(f"push {photo_path} {device_path}")
            
            # Open photo with gallery app
            intent_command = f"shell am start -a android.intent.action.VIEW -d file://{device_path} -t image/*"
            result = await self._execute_adb_command(intent_command)
            
            return {
                "success": True,
                "photo_path": photo_path,
                "device_path": device_path,
                "message": "Photo displayed successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error displaying photo: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def play_audio_on_device(self, audio_path: str) -> Dict:
        """Play audio file on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not os.path.exists(audio_path):
                return {
                    "success": False,
                    "error": "Audio file does not exist"
                }
            
            # Push audio to device
            device_path = f"/sdcard/play_audio_{int(time.time())}.mp3"
            await self._execute_adb_command(f"push {audio_path} {device_path}")
            
            # Play audio with media player
            intent_command = f"shell am start -a android.intent.action.VIEW -d file://{device_path} -t audio/*"
            result = await self._execute_adb_command(intent_command)
            
            return {
                "success": True,
                "audio_path": audio_path,
                "device_path": device_path,
                "message": "Audio played successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error playing audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def play_video_on_device(self, video_path: str) -> Dict:
        """Play video file on device"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": "Video file does not exist"
                }
            
            # Push video to device
            device_path = f"/sdcard/play_video_{int(time.time())}.mp4"
            await self._execute_adb_command(f"push {video_path} {device_path}")
            
            # Play video with media player
            intent_command = f"shell am start -a android.intent.action.VIEW -d file://{device_path} -t video/*"
            result = await self._execute_adb_command(intent_command)
            
            return {
                "success": True,
                "video_path": video_path,
                "device_path": device_path,
                "message": "Video played successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error playing video: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def mirror_device_screen(self) -> Dict:
        """Mirror and control device screen using scrcpy"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Check if scrcpy is available
            scrcpy_check = subprocess.run(["which", "scrcpy"], capture_output=True, text=True)
            if scrcpy_check.returncode != 0:
                return {
                    "success": False,
                    "error": "Scrcpy not installed"
                }
            
            # Start scrcpy mirroring
            scrcpy_command = f"scrcpy -s {self.current_device}"
            
            # Run scrcpy in background
            process = subprocess.Popen(
                scrcpy_command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "device": self.current_device,
                "process_id": process.pid,
                "message": "Device mirroring started successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error mirroring device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_device_audio(self, duration: int = 30, save_path: str = None) -> Dict:
        """Record microphone or device audio"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_record_{timestamp}.mp3"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Record audio using device microphone
            record_command = f"shell am start -a android.media.action.RECORD_SOUND"
            await self._execute_adb_command(record_command)
            
            # Wait for recording duration
            await asyncio.sleep(duration)
            
            # Stop recording
            stop_command = "shell input keyevent 4"  # Back button to stop recording
            await self._execute_adb_command(stop_command)
            
            # Note: This is a simplified implementation
            # Real implementation would need to handle audio file retrieval
            
            return {
                "success": True,
                "duration": duration,
                "message": "Audio recording completed"
            }
                
        except Exception as e:
            self.logger.error(f"Error recording audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stream_device_audio(self) -> Dict:
        """Stream microphone or device audio"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            # Start audio streaming
            # This would require more complex implementation with audio streaming
            # For now, we'll return a placeholder response
            
            return {
                "success": True,
                "message": "Audio streaming started (placeholder implementation)"
            }
                
        except Exception as e:
            self.logger.error(f"Error streaming audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reboot_device(self, mode: str = "system") -> Dict:
        """Reboot device to system/recovery/bootloader/fastboot"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            valid_modes = ["system", "recovery", "bootloader", "fastboot"]
            if mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid reboot mode. Valid modes: {valid_modes}"
                }
            
            # Reboot device
            reboot_command = f"shell reboot {mode}"
            result = await self._execute_adb_command(reboot_command)
            
            return {
                "success": True,
                "mode": mode,
                "message": f"Device rebooted to {mode} successfully"
            }
                
        except Exception as e:
            self.logger.error(f"Error rebooting device: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def extract_apk_from_app(self, package_name: str, save_path: str = None) -> Dict:
        """Extract APK from installed app"""
        try:
            if not self.current_device:
                return {
                    "success": False,
                    "error": "No device connected"
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{package_name}_{timestamp}.apk"
            
            if save_path:
                filename = os.path.join(save_path, filename)
            
            # Get APK path
            path_command = f"shell pm path {package_name}"
            result = await self._execute_adb_command(path_command)
            
            if "package:" in result:
                apk_path = result.split("package:")[1].strip()
                
                # Pull APK from device
                pull_result = await self._execute_adb_command(f"pull {apk_path} {filename}")
                
                if os.path.exists(filename):
                    return {
                        "success": True,
                        "package_name": package_name,
                        "filename": filename,
                        "path": os.path.abspath(filename),
                        "message": "APK extracted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to extract APK"
                    }
            else:
                return {
                    "success": False,
                    "error": "Package not found"
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting APK: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_adb_command(self, command: str) -> str:
        """Execute ADB command"""
        try:
            full_command = f"{self.adb_path} {command}"
            self.logger.debug(f"Executing: {full_command}")
            
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Log control in history
            self.control_history.append({
                "command": full_command,
                "timestamp": datetime.now().isoformat(),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"ADB command failed: {result.stderr}")
                return result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {command}")
            return "Command timed out"
        except Exception as e:
            self.logger.error(f"Error executing ADB command: {str(e)}")
            return str(e)
    
    def get_control_history(self) -> List[Dict]:
        """Get remote control history"""
        return self.control_history
    
    def clear_control_history(self):
        """Clear control history"""
        self.control_history.clear()
        self.logger.info("Control history cleared")
    
    def get_control_statistics(self) -> Dict:
        """Get remote control statistics"""
        total_operations = len(self.control_history)
        successful_operations = len([op for op in self.control_history if op["return_code"] == 0])
        failed_operations = total_operations - successful_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0
        }