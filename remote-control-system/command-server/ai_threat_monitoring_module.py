"""
AI Threat Monitoring Module - Phase 5
Advanced AI-powered threat detection and monitoring system
"""

import asyncio
import json
import logging
import os
import time
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import re
import pickle
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import layers
import joblib

@dataclass
class ThreatEvent:
    """Threat event data structure"""
    threat_id: str
    threat_type: str
    severity: str
    source: str
    target: str
    timestamp: float
    description: str
    indicators: List[str]
    confidence: float
    status: str

@dataclass
class VulnerabilityAlert:
    """Vulnerability alert structure"""
    alert_id: str
    vuln_type: str
    severity: str
    affected_systems: List[str]
    detection_time: float
    description: str
    remediation: str
    status: str
    risk_score: float

@dataclass
class DefenseRecommendation:
    """Defense recommendation structure"""
    recommendation_id: str
    threat_type: str
    priority: str
    description: str
    implementation_steps: List[str]
    expected_effectiveness: float
    cost: str
    time_to_implement: str

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    intel_id: str
    threat_family: str
    indicators: List[str]
    tactics: List[str]
    techniques: List[str]
    targets: List[str]
    confidence: float
    last_seen: float
    source: str

class AIThreatMonitoringModule:
    """Advanced AI-powered threat monitoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.threat_events: List[ThreatEvent] = []
        self.vulnerability_alerts: List[VulnerabilityAlert] = []
        self.defense_recommendations: List[DefenseRecommendation] = []
        self.threat_intelligence: List[ThreatIntelligence] = []
        
        # AI Models
        self.threat_detector = None
        self.vulnerability_analyzer = None
        self.anomaly_detector = None
        self.defense_optimizer = None
        
        # Data storage
        self.threat_cache = {}
        self.monitoring_history = {}
        self.alert_queue = []
        
        # Initialize AI models
        self._initialize_ai_models()
        self._load_threat_intelligence()
    
    def _initialize_ai_models(self):
        """Initialize AI models for threat monitoring"""
        try:
            # Threat detection model
            self.threat_detector = self._create_threat_detector()
            
            # Vulnerability analysis model
            self.vulnerability_analyzer = self._create_vulnerability_analyzer()
            
            # Anomaly detection model
            self.anomaly_detector = self._create_anomaly_detector()
            
            # Defense optimization model
            self.defense_optimizer = self._create_defense_optimizer()
            
            self.logger.info("AI threat monitoring models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AI threat monitoring models: {str(e)}")
    
    def _create_threat_detector(self):
        """Create threat detection model"""
        # model = keras.Sequential([
        #     layers.Dense(256, activation='relu', input_shape=(100,)),
        #     layers.Dropout(0.4),
        #     layers.Dense(128, activation='relu'),
        #     layers.Dropout(0.3),
        #     layers.Dense(64, activation='relu'),
        #     layers.Dense(10, activation='softmax')  # 10 threat categories
        # ])
        # 
        # model.compile(
        #     optimizer='adam',
        #     loss='categorical_crossentropy',
        #     metrics=['accuracy']
        # )
        model = None  # Placeholder for compatibility
        
        return model
    
    def _create_vulnerability_analyzer(self):
        """Create vulnerability analysis model"""
        # Placeholder for compatibility
        return None
    
    def _create_anomaly_detector(self):
        """Create anomaly detection model"""
        # Placeholder for compatibility
        return None
    
    def _create_defense_optimizer(self):
        """Create defense optimization model"""
        # Placeholder for compatibility
        return None
    
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        try:
            # Default threat intelligence
            default_intel = [
                ThreatIntelligence(
                    intel_id="apt_29",
                    threat_family="APT29",
                    indicators=["malware_signature_1", "network_pattern_1", "domain_1"],
                    tactics=["initial_access", "persistence", "privilege_escalation"],
                    techniques=["spear_phishing", "credential_dumping", "lateral_movement"],
                    targets=["government", "energy", "financial"],
                    confidence=0.9,
                    last_seen=time.time() - 86400,
                    source="threat_intel_feed"
                ),
                ThreatIntelligence(
                    intel_id="lazarus_group",
                    threat_family="Lazarus Group",
                    indicators=["malware_signature_2", "network_pattern_2", "domain_2"],
                    tactics=["initial_access", "execution", "data_exfiltration"],
                    techniques=["supply_chain_attack", "fileless_execution", "data_staging"],
                    targets=["financial", "healthcare", "technology"],
                    confidence=0.85,
                    last_seen=time.time() - 172800,
                    source="threat_intel_feed"
                ),
                ThreatIntelligence(
                    intel_id="ransomware_family",
                    threat_family="Ransomware",
                    indicators=["encryption_pattern", "ransom_note", "bitcoin_address"],
                    tactics=["initial_access", "execution", "impact"],
                    techniques=["phishing", "exploit_public_application", "data_encryption"],
                    targets=["all_sectors"],
                    confidence=0.95,
                    last_seen=time.time() - 3600,
                    source="threat_intel_feed"
                )
            ]
            
            self.threat_intelligence.extend(default_intel)
            self.logger.info("Threat intelligence loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading threat intelligence: {str(e)}")
    
    async def detect_new_threats(self, system_data: Dict) -> Dict:
        """Detect new threats using AI"""
        try:
            # Extract threat features
            threat_features = self._extract_threat_features(system_data)
            
            # Use threat detector model
            threat_predictions = self.threat_detector.predict(threat_features.reshape(1, -1))
            
            # Analyze predictions
            detected_threats = self._analyze_threat_predictions(threat_predictions[0], system_data)
            
            # Generate threat events
            threat_events = []
            for threat in detected_threats:
                event = self._create_threat_event(threat, system_data)
                threat_events.append(event)
                self.threat_events.append(event)
            
            return {
                "success": True,
                "detected_threats": detected_threats,
                "threat_events": [asdict(event) for event in threat_events],
                "total_threats": len(self.threat_events)
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting threats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_threat_features(self, system_data: Dict) -> np.ndarray:
        """Extract features for threat detection"""
        features = []
        
        # Network activity features
        features.extend([
            system_data.get("network_connections", 0),
            system_data.get("suspicious_connections", 0),
            system_data.get("data_transfer_volume", 0.0),
            system_data.get("unusual_ports", 0)
        ])
        
        # System activity features
        features.extend([
            system_data.get("cpu_usage", 0.0),
            system_data.get("memory_usage", 0.0),
            system_data.get("disk_activity", 0.0),
            system_data.get("process_count", 0)
        ])
        
        # Security events features
        features.extend([
            system_data.get("failed_logins", 0),
            system_data.get("suspicious_processes", 0),
            system_data.get("file_modifications", 0),
            system_data.get("registry_changes", 0)
        ])
        
        # Threat indicators
        indicators = system_data.get("threat_indicators", [])
        indicator_types = ["malware", "phishing", "exploit", "data_exfiltration", "privilege_escalation"]
        features.extend([1 if indicator in indicators else 0 for indicator in indicator_types])
        
        # Pad to required size
        while len(features) < 100:
            features.append(0.0)
        
        return np.array(features[:100])
    
    def _analyze_threat_predictions(self, predictions: np.ndarray, system_data: Dict) -> List[Dict]:
        """Analyze threat predictions"""
        threat_categories = [
            "malware", "phishing", "exploit", "data_exfiltration", "privilege_escalation",
            "lateral_movement", "persistence", "defense_evasion", "command_control", "impact"
        ]
        
        detected_threats = []
        threshold = 0.5
        
        for i, confidence in enumerate(predictions):
            if confidence > threshold:
                threat = {
                    "threat_type": threat_categories[i],
                    "confidence": float(confidence),
                    "severity": self._assess_threat_severity(confidence),
                    "indicators": self._get_threat_indicators(threat_categories[i]),
                    "recommendations": self._get_threat_recommendations(threat_categories[i])
                }
                detected_threats.append(threat)
        
        return detected_threats
    
    def _assess_threat_severity(self, confidence: float) -> str:
        """Assess threat severity based on confidence"""
        if confidence > 0.9:
            return "CRITICAL"
        elif confidence > 0.7:
            return "HIGH"
        elif confidence > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_threat_indicators(self, threat_type: str) -> List[str]:
        """Get indicators for threat type"""
        indicators = {
            "malware": ["suspicious_processes", "file_modifications", "network_connections"],
            "phishing": ["suspicious_emails", "fake_websites", "credential_theft"],
            "exploit": ["vulnerability_scanning", "exploit_attempts", "system_compromise"],
            "data_exfiltration": ["large_data_transfers", "encrypted_communications", "data_staging"],
            "privilege_escalation": ["admin_privileges", "service_manipulation", "token_theft"]
        }
        
        return indicators.get(threat_type, [])
    
    def _get_threat_recommendations(self, threat_type: str) -> List[str]:
        """Get recommendations for threat type"""
        recommendations = {
            "malware": [
                "Implement advanced malware detection",
                "Use sandboxing for suspicious files",
                "Update antivirus signatures"
            ],
            "phishing": [
                "Implement email filtering",
                "Train users on phishing awareness",
                "Use multi-factor authentication"
            ],
            "exploit": [
                "Patch vulnerabilities immediately",
                "Implement exploit prevention",
                "Use intrusion detection systems"
            ],
            "data_exfiltration": [
                "Monitor data transfers",
                "Implement data loss prevention",
                "Use encryption for sensitive data"
            ],
            "privilege_escalation": [
                "Implement least privilege access",
                "Monitor privilege changes",
                "Use privilege access management"
            ]
        }
        
        return recommendations.get(threat_type, ["Implement general security measures"])
    
    def _create_threat_event(self, threat: Dict, system_data: Dict) -> ThreatEvent:
        """Create threat event from detection"""
        return ThreatEvent(
            threat_id=f"threat_{int(time.time())}_{hash(threat['threat_type'])}",
            threat_type=threat["threat_type"],
            severity=threat["severity"],
            source=system_data.get("source", "unknown"),
            target=system_data.get("target", "unknown"),
            timestamp=time.time(),
            description=f"Detected {threat['threat_type']} threat with {threat['confidence']:.1%} confidence",
            indicators=threat["indicators"],
            confidence=threat["confidence"],
            status="active"
        )
    
    async def analyze_vulnerabilities(self, system_scan_data: Dict) -> Dict:
        """Analyze vulnerabilities using AI"""
        try:
            # Extract vulnerability features
            vuln_features = self._extract_vulnerability_features(system_scan_data)
            
            # Use vulnerability analyzer model
            vuln_predictions = self.vulnerability_analyzer.predict(vuln_features.reshape(1, -1))
            
            # Analyze vulnerabilities
            detected_vulns = self._analyze_vulnerability_predictions(vuln_predictions[0], system_scan_data)
            
            # Generate vulnerability alerts
            vuln_alerts = []
            for vuln in detected_vulns:
                alert = self._create_vulnerability_alert(vuln, system_scan_data)
                vuln_alerts.append(alert)
                self.vulnerability_alerts.append(alert)
            
            return {
                "success": True,
                "detected_vulnerabilities": detected_vulns,
                "vulnerability_alerts": [asdict(alert) for alert in vuln_alerts],
                "total_vulnerabilities": len(self.vulnerability_alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing vulnerabilities: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_vulnerability_features(self, scan_data: Dict) -> np.ndarray:
        """Extract features for vulnerability analysis"""
        features = []
        
        # System vulnerabilities
        features.extend([
            len(scan_data.get("open_ports", [])),
            len(scan_data.get("outdated_software", [])),
            len(scan_data.get("weak_passwords", [])),
            len(scan_data.get("misconfigurations", []))
        ])
        
        # Network vulnerabilities
        features.extend([
            len(scan_data.get("unencrypted_services", [])),
            len(scan_data.get("default_credentials", [])),
            len(scan_data.get("unpatched_systems", [])),
            len(scan_data.get("exposed_services", []))
        ])
        
        # Application vulnerabilities
        features.extend([
            len(scan_data.get("sql_injection_vulns", [])),
            len(scan_data.get("xss_vulns", [])),
            len(scan_data.get("csrf_vulns", [])),
            len(scan_data.get("file_upload_vulns", []))
        ])
        
        # Risk factors
        features.extend([
            scan_data.get("risk_score", 0.0),
            scan_data.get("exposure_level", 0.0),
            scan_data.get("attack_surface", 0.0),
            scan_data.get("compliance_violations", 0)
        ])
        
        # Pad to required size
        while len(features) < 50:
            features.append(0.0)
        
        return np.array(features[:50])
    
    def _analyze_vulnerability_predictions(self, predictions: np.ndarray, scan_data: Dict) -> List[Dict]:
        """Analyze vulnerability predictions"""
        detected_vulns = []
        threshold = 0.6
        
        if predictions[0] > threshold:
            vuln = {
                "vuln_type": "system_vulnerability",
                "severity": self._assess_vuln_severity(predictions[0]),
                "affected_systems": scan_data.get("affected_systems", []),
                "description": "System-level vulnerabilities detected",
                "remediation": "Apply security patches and updates",
                "risk_score": float(predictions[0])
            }
            detected_vulns.append(vuln)
        
        return detected_vulns
    
    def _assess_vuln_severity(self, risk_score: float) -> str:
        """Assess vulnerability severity"""
        if risk_score > 0.9:
            return "CRITICAL"
        elif risk_score > 0.7:
            return "HIGH"
        elif risk_score > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _create_vulnerability_alert(self, vuln: Dict, scan_data: Dict) -> VulnerabilityAlert:
        """Create vulnerability alert"""
        return VulnerabilityAlert(
            alert_id=f"vuln_alert_{int(time.time())}_{hash(vuln['vuln_type'])}",
            vuln_type=vuln["vuln_type"],
            severity=vuln["severity"],
            affected_systems=vuln["affected_systems"],
            detection_time=time.time(),
            description=vuln["description"],
            remediation=vuln["remediation"],
            status="active",
            risk_score=vuln["risk_score"]
        )
    
    async def detect_anomalies(self, system_metrics: Dict) -> Dict:
        """Detect anomalies using AI"""
        try:
            # Extract anomaly features
            anomaly_features = self._extract_anomaly_features(system_metrics)
            
            # Use anomaly detector model
            anomaly_scores = self.anomaly_detector.predict(anomaly_features.reshape(1, -1))
            
            # Analyze anomalies
            detected_anomalies = self._analyze_anomaly_scores(anomaly_scores[0], system_metrics)
            
            return {
                "success": True,
                "detected_anomalies": detected_anomalies,
                "anomaly_score": float(anomaly_scores[0]),
                "total_anomalies": len(detected_anomalies)
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_anomaly_features(self, metrics: Dict) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = []
        
        # Performance metrics
        features.extend([
            metrics.get("cpu_usage", 0.0),
            metrics.get("memory_usage", 0.0),
            metrics.get("disk_usage", 0.0),
            metrics.get("network_usage", 0.0)
        ])
        
        # Activity metrics
        features.extend([
            metrics.get("process_count", 0),
            metrics.get("network_connections", 0),
            metrics.get("file_operations", 0),
            metrics.get("user_sessions", 0)
        ])
        
        # Security metrics
        features.extend([
            metrics.get("failed_logins", 0),
            metrics.get("suspicious_activities", 0),
            metrics.get("security_events", 0),
            metrics.get("threat_indicators", 0)
        ])
        
        # Pad to required size
        while len(features) < 75:
            features.append(0.0)
        
        return np.array(features[:75])
    
    def _analyze_anomaly_scores(self, anomaly_score: float, metrics: Dict) -> List[Dict]:
        """Analyze anomaly scores"""
        anomalies = []
        threshold = 0.7
        
        if anomaly_score > threshold:
            anomaly = {
                "anomaly_type": "system_anomaly",
                "severity": self._assess_anomaly_severity(anomaly_score),
                "description": f"System anomaly detected with {anomaly_score:.1%} confidence",
                "affected_metrics": self._get_affected_metrics(metrics),
                "recommendations": self._get_anomaly_recommendations(anomaly_score)
            }
            anomalies.append(anomaly)
        
        return anomalies
    
    def _assess_anomaly_severity(self, anomaly_score: float) -> str:
        """Assess anomaly severity"""
        if anomaly_score > 0.9:
            return "CRITICAL"
        elif anomaly_score > 0.7:
            return "HIGH"
        elif anomaly_score > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_affected_metrics(self, metrics: Dict) -> List[str]:
        """Get affected metrics"""
        affected = []
        
        if metrics.get("cpu_usage", 0.0) > 0.8:
            affected.append("high_cpu_usage")
        if metrics.get("memory_usage", 0.0) > 0.8:
            affected.append("high_memory_usage")
        if metrics.get("network_usage", 0.0) > 0.8:
            affected.append("high_network_usage")
        if metrics.get("failed_logins", 0) > 10:
            affected.append("multiple_failed_logins")
        
        return affected
    
    def _get_anomaly_recommendations(self, anomaly_score: float) -> List[str]:
        """Get recommendations for anomalies"""
        recommendations = []
        
        if anomaly_score > 0.9:
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider system isolation")
        elif anomaly_score > 0.7:
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Review system logs")
        else:
            recommendations.append("Continue monitoring")
            recommendations.append("Document for future reference")
        
        return recommendations
    
    async def generate_defense_recommendations(self, threat_analysis: Dict) -> Dict:
        """Generate defense recommendations using AI"""
        try:
            # Extract defense features
            defense_features = self._extract_defense_features(threat_analysis)
            
            # Use defense optimizer model
            defense_predictions = self.defense_optimizer.predict(defense_features.reshape(1, -1))
            
            # Generate defense recommendations
            recommendations = self._generate_defense_strategies(defense_predictions[0], threat_analysis)
            
            return {
                "success": True,
                "defense_recommendations": recommendations,
                "defense_scores": defense_predictions[0].tolist(),
                "total_recommendations": len(recommendations)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating defense recommendations: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_defense_features(self, threat_analysis: Dict) -> np.ndarray:
        """Extract features for defense optimization"""
        features = []
        
        # Threat characteristics
        features.extend([
            len(threat_analysis.get("active_threats", [])),
            threat_analysis.get("threat_severity", 0.0),
            threat_analysis.get("attack_surface", 0.0),
            threat_analysis.get("vulnerability_count", 0)
        ])
        
        # Current defenses
        features.extend([
            len(threat_analysis.get("current_defenses", [])),
            threat_analysis.get("defense_effectiveness", 0.0),
            threat_analysis.get("response_time", 0.0),
            threat_analysis.get("coverage_gaps", 0)
        ])
        
        # Resource constraints
        features.extend([
            threat_analysis.get("budget_constraint", 0.0),
            threat_analysis.get("time_constraint", 0.0),
            threat_analysis.get("skill_constraint", 0.0),
            threat_analysis.get("compliance_requirements", 0)
        ])
        
        # Pad to required size
        while len(features) < 60:
            features.append(0.0)
        
        return np.array(features[:60])
    
    def _generate_defense_strategies(self, predictions: np.ndarray, threat_analysis: Dict) -> List[DefenseRecommendation]:
        """Generate defense strategies"""
        defense_strategies = [
            "preventive_defense",
            "detective_defense", 
            "corrective_defense",
            "deterrent_defense",
            "recovery_defense"
        ]
        
        recommendations = []
        
        for i, confidence in enumerate(predictions):
            if confidence > 0.5:
                strategy = defense_strategies[i]
                recommendation = self._create_defense_recommendation(strategy, confidence, threat_analysis)
                recommendations.append(recommendation)
                self.defense_recommendations.append(recommendation)
        
        return recommendations
    
    def _create_defense_recommendation(self, strategy: str, confidence: float, threat_analysis: Dict) -> DefenseRecommendation:
        """Create defense recommendation"""
        strategy_info = {
            "preventive_defense": {
                "description": "Implement preventive measures to stop threats before they occur",
                "steps": ["Deploy firewalls", "Implement access controls", "Use antivirus software"],
                "effectiveness": 0.8,
                "cost": "medium",
                "time": "1-2 weeks"
            },
            "detective_defense": {
                "description": "Implement detection mechanisms to identify threats quickly",
                "steps": ["Deploy IDS/IPS", "Implement logging", "Use SIEM systems"],
                "effectiveness": 0.7,
                "cost": "high",
                "time": "2-4 weeks"
            },
            "corrective_defense": {
                "description": "Implement corrective measures to respond to threats",
                "steps": ["Incident response plan", "Backup systems", "Recovery procedures"],
                "effectiveness": 0.6,
                "cost": "medium",
                "time": "1-3 weeks"
            },
            "deterrent_defense": {
                "description": "Implement deterrent measures to discourage attacks",
                "steps": ["Security awareness training", "Visible security measures", "Legal consequences"],
                "effectiveness": 0.5,
                "cost": "low",
                "time": "1-2 weeks"
            },
            "recovery_defense": {
                "description": "Implement recovery measures to restore systems after attacks",
                "steps": ["Backup strategies", "Disaster recovery plan", "Business continuity"],
                "effectiveness": 0.7,
                "cost": "high",
                "time": "4-8 weeks"
            }
        }
        
        info = strategy_info.get(strategy, strategy_info["preventive_defense"])
        
        return DefenseRecommendation(
            recommendation_id=f"defense_{strategy}_{int(time.time())}",
            threat_type=threat_analysis.get("primary_threat", "unknown"),
            priority="HIGH" if confidence > 0.8 else "MEDIUM" if confidence > 0.6 else "LOW",
            description=info["description"],
            implementation_steps=info["steps"],
            expected_effectiveness=info["effectiveness"],
            cost=info["cost"],
            time_to_implement=info["time"]
        )
    
    async def get_threat_monitoring_statistics(self) -> Dict:
        """Get threat monitoring statistics"""
        try:
            return {
                "success": True,
                "statistics": {
                    "total_threat_events": len(self.threat_events),
                    "total_vulnerability_alerts": len(self.vulnerability_alerts),
                    "total_defense_recommendations": len(self.defense_recommendations),
                    "total_threat_intelligence": len(self.threat_intelligence),
                    "active_threats": len([t for t in self.threat_events if t.status == "active"]),
                    "critical_threats": len([t for t in self.threat_events if t.severity == "CRITICAL"]),
                    "high_severity_vulns": len([v for v in self.vulnerability_alerts if v.severity == "HIGH"]),
                    "pending_recommendations": len([r for r in self.defense_recommendations if r.priority == "HIGH"])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_threat_monitoring_models(self, path: str = "ai_threat_monitoring_models"):
        """Save threat monitoring models to disk"""
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save models
            self.threat_detector.save(f"{path}/threat_detector.h5")
            self.vulnerability_analyzer.save(f"{path}/vulnerability_analyzer.h5")
            self.anomaly_detector.save(f"{path}/anomaly_detector.h5")
            self.defense_optimizer.save(f"{path}/defense_optimizer.h5")
            
            # Save threat cache
            with open(f"{path}/threat_cache.pkl", "wb") as f:
                pickle.dump(self.threat_cache, f)
            
            self.logger.info(f"Threat monitoring models saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving threat monitoring models: {str(e)}")
    
    def load_threat_monitoring_models(self, path: str = "ai_threat_monitoring_models"):
        """Load threat monitoring models from disk"""
        try:
            # Load models
            self.threat_detector = keras.models.load_model(f"{path}/threat_detector.h5")
            self.vulnerability_analyzer = keras.models.load_model(f"{path}/vulnerability_analyzer.h5")
            self.anomaly_detector = keras.models.load_model(f"{path}/anomaly_detector.h5")
            self.defense_optimizer = keras.models.load_model(f"{path}/defense_optimizer.h5")
            
            # Load threat cache
            with open(f"{path}/threat_cache.pkl", "rb") as f:
                self.threat_cache = pickle.load(f)
            
            self.logger.info(f"Threat monitoring models loaded from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading threat monitoring models: {str(e)}")