"""
Intelligent Alert System
Advanced alerting and notification system with machine learning capabilities
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class AlertRule:
    """Alert rule structure"""
    rule_id: str
    name: str
    description: str
    condition: str
    threshold: float
    severity: str
    enabled: bool
    notification_channels: List[str]
    cooldown_period: int  # seconds

@dataclass
class AlertEvent:
    """Alert event structure"""
    alert_id: str
    rule_id: str
    timestamp: float
    severity: str
    message: str
    data: Dict
    acknowledged: bool
    resolved: bool

class IntelligentAlertSystem:
    """Intelligent alert system with advanced features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_events: List[AlertEvent] = []
        self.notification_channels: Dict[str, Dict] = {}
        self.alert_history: List[Dict] = []
        self.ml_predictions: Dict[str, float] = {}
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
        # Initialize notification channels
        self._initialize_notification_channels()
        
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            {
                "rule_id": "high_cpu_usage",
                "name": "High CPU Usage",
                "description": "Alert when CPU usage exceeds threshold",
                "condition": "cpu_usage > threshold",
                "threshold": 80.0,
                "severity": "warning",
                "enabled": True,
                "notification_channels": ["email", "webhook"],
                "cooldown_period": 300
            },
            {
                "rule_id": "high_memory_usage",
                "name": "High Memory Usage",
                "description": "Alert when memory usage exceeds threshold",
                "condition": "memory_usage > threshold",
                "threshold": 85.0,
                "severity": "warning",
                "enabled": True,
                "notification_channels": ["email", "webhook"],
                "cooldown_period": 300
            },
            {
                "rule_id": "low_battery",
                "name": "Low Battery",
                "description": "Alert when battery level is low",
                "condition": "battery_level < threshold",
                "threshold": 20.0,
                "severity": "critical",
                "enabled": True,
                "notification_channels": ["email", "webhook", "sms"],
                "cooldown_period": 600
            },
            {
                "rule_id": "high_temperature",
                "name": "High Temperature",
                "description": "Alert when device temperature is high",
                "condition": "temperature > threshold",
                "threshold": 45.0,
                "severity": "critical",
                "enabled": True,
                "notification_channels": ["email", "webhook"],
                "cooldown_period": 300
            },
            {
                "rule_id": "network_anomaly",
                "name": "Network Anomaly",
                "description": "Alert when network activity is anomalous",
                "condition": "network_anomaly_score > threshold",
                "threshold": 0.8,
                "severity": "warning",
                "enabled": True,
                "notification_channels": ["email", "webhook"],
                "cooldown_period": 180
            },
            {
                "rule_id": "security_threat",
                "name": "Security Threat",
                "description": "Alert when security threat is detected",
                "condition": "security_threat_detected",
                "threshold": 0.0,
                "severity": "critical",
                "enabled": True,
                "notification_channels": ["email", "webhook", "sms"],
                "cooldown_period": 60
            }
        ]
        
        for rule_data in default_rules:
            rule = AlertRule(**rule_data)
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_notification_channels(self):
        """Initialize notification channels"""
        self.notification_channels = {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "headers": {},
                "timeout": 30
            },
            "sms": {
                "enabled": False,
                "provider": "",
                "api_key": "",
                "phone_numbers": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#alerts"
            },
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "username": "Alert Bot"
            }
        }
    
    async def evaluate_alert_rules(self, metrics: Dict) -> List[AlertEvent]:
        """Evaluate all alert rules against current metrics"""
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if self._is_in_cooldown(rule_id):
                continue
            
            # Evaluate rule condition
            if self._evaluate_condition(rule, metrics):
                alert_event = self._create_alert_event(rule, metrics)
                triggered_alerts.append(alert_event)
                
                # Send notifications
                await self._send_notifications(alert_event)
                
                # Update cooldown
                self._update_cooldown(rule_id)
        
        return triggered_alerts
    
    def _evaluate_condition(self, rule: AlertRule, metrics: Dict) -> bool:
        """Evaluate alert rule condition"""
        try:
            if rule.condition == "cpu_usage > threshold":
                return metrics.get("cpu_usage", 0) > rule.threshold
            elif rule.condition == "memory_usage > threshold":
                return metrics.get("memory_usage", 0) > rule.threshold
            elif rule.condition == "battery_level < threshold":
                return metrics.get("battery_level", 100) < rule.threshold
            elif rule.condition == "temperature > threshold":
                return metrics.get("temperature", 0) > rule.threshold
            elif rule.condition == "network_anomaly_score > threshold":
                return metrics.get("network_anomaly_score", 0) > rule.threshold
            elif rule.condition == "security_threat_detected":
                return metrics.get("security_threats", 0) > 0
            else:
                # Custom condition evaluation
                return self._evaluate_custom_condition(rule.condition, metrics)
                
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    def _evaluate_custom_condition(self, condition: str, metrics: Dict) -> bool:
        """Evaluate custom condition expressions"""
        try:
            # Simple expression evaluator
            # In production, use a proper expression evaluator
            condition = condition.replace("threshold", str(metrics.get("threshold", 0)))
            
            for key, value in metrics.items():
                condition = condition.replace(key, str(value))
            
            # Basic evaluation (simplified)
            return eval(condition)
            
        except Exception as e:
            self.logger.error(f"Error evaluating custom condition: {str(e)}")
            return False
    
    def _create_alert_event(self, rule: AlertRule, metrics: Dict) -> AlertEvent:
        """Create alert event"""
        alert_id = f"{rule.rule_id}_{int(time.time())}"
        
        alert_event = AlertEvent(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            timestamp=time.time(),
            severity=rule.severity,
            message=f"{rule.name}: {rule.description}",
            data=metrics,
            acknowledged=False,
            resolved=False
        )
        
        self.alert_events.append(alert_event)
        self.alert_history.append({
            "alert_id": alert_id,
            "rule_id": rule.rule_id,
            "timestamp": alert_event.timestamp,
            "severity": rule.severity,
            "message": alert_event.message,
            "data": metrics
        })
        
        return alert_event
    
    def _is_in_cooldown(self, rule_id: str) -> bool:
        """Check if rule is in cooldown period"""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        # Check last alert time
        recent_alerts = [
            event for event in self.alert_events
            if event.rule_id == rule_id and 
            time.time() - event.timestamp < rule.cooldown_period
        ]
        
        return len(recent_alerts) > 0
    
    def _update_cooldown(self, rule_id: str):
        """Update cooldown for rule"""
        # Cooldown is handled by checking recent alerts
        pass
    
    async def _send_notifications(self, alert_event: AlertEvent):
        """Send notifications for alert event"""
        rule = self.alert_rules.get(alert_event.rule_id)
        if not rule:
            return
        
        for channel in rule.notification_channels:
            if channel in self.notification_channels:
                channel_config = self.notification_channels[channel]
                if channel_config.get("enabled", False):
                    await self._send_notification(channel, alert_event, channel_config)
    
    async def _send_notification(self, channel: str, alert_event: AlertEvent, config: Dict):
        """Send notification to specific channel"""
        try:
            if channel == "email":
                await self._send_email_notification(alert_event, config)
            elif channel == "webhook":
                await self._send_webhook_notification(alert_event, config)
            elif channel == "sms":
                await self._send_sms_notification(alert_event, config)
            elif channel == "slack":
                await self._send_slack_notification(alert_event, config)
            elif channel == "discord":
                await self._send_discord_notification(alert_event, config)
                
        except Exception as e:
            self.logger.error(f"Error sending {channel} notification: {str(e)}")
    
    async def _send_email_notification(self, alert_event: AlertEvent, config: Dict):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = f"Alert: {alert_event.severity.upper()} - {alert_event.message}"
            
            body = f"""
            Alert Details:
            - Severity: {alert_event.severity}
            - Message: {alert_event.message}
            - Time: {datetime.fromtimestamp(alert_event.timestamp)}
            - Alert ID: {alert_event.alert_id}
            
            Data: {json.dumps(alert_event.data, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email notification sent for alert {alert_event.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")
    
    async def _send_webhook_notification(self, alert_event: AlertEvent, config: Dict):
        """Send webhook notification"""
        try:
            payload = {
                "alert_id": alert_event.alert_id,
                "severity": alert_event.severity,
                "message": alert_event.message,
                "timestamp": alert_event.timestamp,
                "data": alert_event.data
            }
            
            response = requests.post(
                config['url'],
                json=payload,
                headers=config.get('headers', {}),
                timeout=config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook notification sent for alert {alert_event.alert_id}")
            else:
                self.logger.error(f"Webhook notification failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {str(e)}")
    
    async def _send_sms_notification(self, alert_event: AlertEvent, config: Dict):
        """Send SMS notification"""
        try:
            # This would integrate with SMS service provider
            # For now, just log the attempt
            self.logger.info(f"SMS notification would be sent for alert {alert_event.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending SMS notification: {str(e)}")
    
    async def _send_slack_notification(self, alert_event: AlertEvent, config: Dict):
        """Send Slack notification"""
        try:
            payload = {
                "channel": config['channel'],
                "text": f"🚨 *{alert_event.severity.upper()} Alert*\n{alert_event.message}",
                "attachments": [
                    {
                        "fields": [
                            {
                                "title": "Alert ID",
                                "value": alert_event.alert_id,
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": alert_event.severity,
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": datetime.fromtimestamp(alert_event.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                config['webhook_url'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Slack notification sent for alert {alert_event.alert_id}")
            else:
                self.logger.error(f"Slack notification failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {str(e)}")
    
    async def _send_discord_notification(self, alert_event: AlertEvent, config: Dict):
        """Send Discord notification"""
        try:
            payload = {
                "username": config.get('username', 'Alert Bot'),
                "content": f"🚨 **{alert_event.severity.upper()} Alert**\n{alert_event.message}",
                "embeds": [
                    {
                        "title": "Alert Details",
                        "color": self._get_severity_color(alert_event.severity),
                        "fields": [
                            {
                                "name": "Alert ID",
                                "value": alert_event.alert_id,
                                "inline": True
                            },
                            {
                                "name": "Severity",
                                "value": alert_event.severity,
                                "inline": True
                            },
                            {
                                "name": "Time",
                                "value": datetime.fromtimestamp(alert_event.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                                "inline": True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                config['webhook_url'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Discord notification sent for alert {alert_event.alert_id}")
            else:
                self.logger.error(f"Discord notification failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending Discord notification: {str(e)}")
    
    def _get_severity_color(self, severity: str) -> int:
        """Get color code for severity level"""
        colors = {
            "low": 0x00ff00,      # Green
            "warning": 0xffff00,   # Yellow
            "critical": 0xff0000    # Red
        }
        return colors.get(severity, 0x808080)  # Gray default
    
    def add_alert_rule(self, rule_data: Dict) -> Dict:
        """Add new alert rule"""
        try:
            rule_id = rule_data.get("rule_id")
            if not rule_id:
                return {
                    "success": False,
                    "error": "Rule ID is required"
                }
            
            if rule_id in self.alert_rules:
                return {
                    "success": False,
                    "error": "Rule ID already exists"
                }
            
            rule = AlertRule(**rule_data)
            self.alert_rules[rule_id] = rule
            
            self.logger.info(f"Added alert rule: {rule_id}")
            return {
                "success": True,
                "rule_id": rule_id,
                "message": "Alert rule added successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error adding alert rule: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_alert_rule(self, rule_id: str, updates: Dict) -> Dict:
        """Update existing alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return {
                    "success": False,
                    "error": "Rule not found"
                }
            
            rule = self.alert_rules[rule_id]
            
            # Update rule attributes
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            self.logger.info(f"Updated alert rule: {rule_id}")
            return {
                "success": True,
                "rule_id": rule_id,
                "message": "Alert rule updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating alert rule: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_alert_rule(self, rule_id: str) -> Dict:
        """Delete alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return {
                    "success": False,
                    "error": "Rule not found"
                }
            
            del self.alert_rules[rule_id]
            
            self.logger.info(f"Deleted alert rule: {rule_id}")
            return {
                "success": True,
                "rule_id": rule_id,
                "message": "Alert rule deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting alert rule: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_notification_channel(self, channel: str, config: Dict) -> Dict:
        """Configure notification channel"""
        try:
            if channel not in self.notification_channels:
                return {
                    "success": False,
                    "error": "Channel not supported"
                }
            
            self.notification_channels[channel].update(config)
            
            self.logger.info(f"Configured notification channel: {channel}")
            return {
                "success": True,
                "channel": channel,
                "message": "Notification channel configured successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring notification channel: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_alert_statistics(self) -> Dict:
        """Get alert system statistics"""
        total_alerts = len(self.alert_events)
        active_alerts = len([a for a in self.alert_events if not a.resolved])
        acknowledged_alerts = len([a for a in self.alert_events if a.acknowledged])
        
        # Count by severity
        severity_counts = {}
        for event in self.alert_events:
            severity = event.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by rule
        rule_counts = {}
        for event in self.alert_events:
            rule_id = event.rule_id
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "alert_rules": len(self.alert_rules),
            "enabled_rules": len([r for r in self.alert_rules.values() if r.enabled]),
            "severity_distribution": severity_counts,
            "rule_distribution": rule_counts,
            "notification_channels": len([c for c in self.notification_channels.values() if c.get("enabled", False)])
        }
    
    def get_active_alerts(self, limit: int = 100) -> List[Dict]:
        """Get active alerts"""
        active_alerts = [a for a in self.alert_events if not a.resolved]
        
        alert_list = []
        for alert in active_alerts[-limit:]:
            alert_list.append({
                "alert_id": alert.alert_id,
                "rule_id": alert.rule_id,
                "timestamp": alert.timestamp,
                "severity": alert.severity,
                "message": alert.message,
                "acknowledged": alert.acknowledged,
                "data": alert.data
            })
        
        return alert_list
    
    def acknowledge_alert(self, alert_id: str) -> Dict:
        """Acknowledge an alert"""
        try:
            for alert in self.alert_events:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    
                    self.logger.info(f"Acknowledged alert: {alert_id}")
                    return {
                        "success": True,
                        "alert_id": alert_id,
                        "message": "Alert acknowledged successfully"
                    }
            
            return {
                "success": False,
                "error": "Alert not found"
            }
            
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resolve_alert(self, alert_id: str) -> Dict:
        """Resolve an alert"""
        try:
            for alert in self.alert_events:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    
                    self.logger.info(f"Resolved alert: {alert_id}")
                    return {
                        "success": True,
                        "alert_id": alert_id,
                        "message": "Alert resolved successfully"
                    }
            
            return {
                "success": False,
                "error": "Alert not found"
            }
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_resolved_alerts(self) -> Dict:
        """Clear resolved alerts"""
        try:
            original_count = len(self.alert_events)
            self.alert_events = [a for a in self.alert_events if not a.resolved]
            removed_count = original_count - len(self.alert_events)
            
            self.logger.info(f"Cleared {removed_count} resolved alerts")
            return {
                "success": True,
                "removed_count": removed_count,
                "message": f"Cleared {removed_count} resolved alerts"
            }
            
        except Exception as e:
            self.logger.error(f"Error clearing resolved alerts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_alert_data(self, format_type: str = "json") -> str:
        """Export alert data"""
        try:
            if format_type == "json":
                return json.dumps({
                    "alert_rules": [
                        {
                            "rule_id": rule.rule_id,
                            "name": rule.name,
                            "description": rule.description,
                            "condition": rule.condition,
                            "threshold": rule.threshold,
                            "severity": rule.severity,
                            "enabled": rule.enabled,
                            "notification_channels": rule.notification_channels,
                            "cooldown_period": rule.cooldown_period
                        }
                        for rule in self.alert_rules.values()
                    ],
                    "alert_events": [
                        {
                            "alert_id": event.alert_id,
                            "rule_id": event.rule_id,
                            "timestamp": event.timestamp,
                            "severity": event.severity,
                            "message": event.message,
                            "acknowledged": event.acknowledged,
                            "resolved": event.resolved,
                            "data": event.data
                        }
                        for event in self.alert_events
                    ],
                    "notification_channels": self.notification_channels,
                    "alert_history": self.alert_history
                }, indent=2)
            else:
                return "Unsupported format"
                
        except Exception as e:
            self.logger.error(f"Error exporting alert data: {str(e)}")
            return ""