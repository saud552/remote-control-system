"""
AI Analysis Module - Phase 5
Advanced AI-powered analysis of attack results and patterns
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
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib

@dataclass
class AttackResult:
    """Attack result data structure"""
    attack_id: str
    attack_type: str
    target: str
    success: bool
    duration: float
    data_captured: Dict
    vulnerabilities_found: List[str]
    tools_used: List[str]
    timestamp: float
    performance_metrics: Dict
    error_logs: List[str]

@dataclass
class PatternAnalysis:
    """Pattern analysis result"""
    pattern_id: str
    pattern_type: str
    confidence: float
    frequency: int
    targets: List[str]
    tools: List[str]
    success_rate: float
    recommendations: List[str]

@dataclass
class VulnerabilityAnalysis:
    """Vulnerability analysis result"""
    vuln_id: str
    vuln_type: str
    severity: str
    affected_targets: List[str]
    exploitability: float
    impact_score: float
    remediation: str
    detection_method: str

@dataclass
class SmartReport:
    """Intelligent report structure"""
    report_id: str
    report_type: str
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    risk_assessment: Dict
    next_actions: List[str]
    generated_at: float

class AIAnalysisModule:
    """Advanced AI-powered analysis module"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.attack_results: List[AttackResult] = []
        self.patterns: List[PatternAnalysis] = []
        self.vulnerabilities: List[VulnerabilityAnalysis] = []
        self.reports: List[SmartReport] = []
        
        # AI Models
        self.pattern_classifier = None
        self.vulnerability_detector = None
        self.success_predictor = None
        self.threat_analyzer = None
        
        # Data storage
        self.analysis_cache = {}
        self.model_cache = {}
        
        # Initialize AI models
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for analysis"""
        try:
            # Pattern classification model
            self.pattern_classifier = self._create_pattern_classifier()
            
            # Vulnerability detection model
            self.vulnerability_detector = self._create_vulnerability_detector()
            
            # Success prediction model
            self.success_predictor = self._create_success_predictor()
            
            # Threat analysis model
            self.threat_analyzer = self._create_threat_analyzer()
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AI models: {str(e)}")
    
    def _create_pattern_classifier(self) -> keras.Model:
        """Create pattern classification model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(50,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(10, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_vulnerability_detector(self) -> keras.Model:
        """Create vulnerability detection model"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(100,)),
            layers.Dropout(0.4),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_success_predictor(self) -> keras.Model:
        """Create success prediction model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(30,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_threat_analyzer(self) -> keras.Model:
        """Create threat analysis model"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(75,)),
            layers.Dropout(0.4),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dense(5, activation='softmax')  # 5 threat levels
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    async def analyze_attack_results(self, attack_results: List[Dict]) -> Dict:
        """Analyze attack results using AI"""
        try:
            # Convert to AttackResult objects
            results = []
            for result_data in attack_results:
                result = AttackResult(
                    attack_id=result_data.get("attack_id", ""),
                    attack_type=result_data.get("attack_type", ""),
                    target=result_data.get("target", ""),
                    success=result_data.get("success", False),
                    duration=result_data.get("duration", 0.0),
                    data_captured=result_data.get("data_captured", {}),
                    vulnerabilities_found=result_data.get("vulnerabilities_found", []),
                    tools_used=result_data.get("tools_used", []),
                    timestamp=result_data.get("timestamp", time.time()),
                    performance_metrics=result_data.get("performance_metrics", {}),
                    error_logs=result_data.get("error_logs", [])
                )
                results.append(result)
            
            # Add to analysis cache
            self.attack_results.extend(results)
            
            # Perform AI analysis
            analysis_results = await self._perform_ai_analysis(results)
            
            return {
                "success": True,
                "analysis": analysis_results,
                "total_results": len(self.attack_results)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing attack results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_ai_analysis(self, results: List[AttackResult]) -> Dict:
        """Perform comprehensive AI analysis"""
        try:
            analysis = {}
            
            # Pattern analysis
            patterns = await self._analyze_patterns(results)
            analysis["patterns"] = patterns
            
            # Vulnerability analysis
            vulnerabilities = await self._analyze_vulnerabilities(results)
            analysis["vulnerabilities"] = vulnerabilities
            
            # Success prediction
            predictions = await self._predict_success(results)
            analysis["predictions"] = predictions
            
            # Threat analysis
            threats = await self._analyze_threats(results)
            analysis["threats"] = threats
            
            # Generate smart report
            report = await self._generate_smart_report(analysis)
            analysis["report"] = report
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error performing AI analysis: {str(e)}")
            return {}
    
    async def _analyze_patterns(self, results: List[AttackResult]) -> List[PatternAnalysis]:
        """Analyze attack patterns using AI"""
        try:
            patterns = []
            
            # Extract features for pattern analysis
            features = self._extract_pattern_features(results)
            
            # Use clustering to identify patterns
            if len(features) > 1:
                scaler = StandardScaler()
                scaled_features = scaler.fit_transform(features)
                
                # K-means clustering
                kmeans = KMeans(n_clusters=min(5, len(scaled_features)), random_state=42)
                clusters = kmeans.fit_predict(scaled_features)
                
                # Analyze each cluster
                for cluster_id in set(clusters):
                    cluster_results = [r for i, r in enumerate(results) if clusters[i] == cluster_id]
                    
                    if cluster_results:
                        pattern = self._create_pattern_analysis(cluster_results, cluster_id)
                        patterns.append(pattern)
            
            # Update patterns cache
            self.patterns.extend(patterns)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {str(e)}")
            return []
    
    def _extract_pattern_features(self, results: List[AttackResult]) -> np.ndarray:
        """Extract features for pattern analysis"""
        features = []
        
        for result in results:
            feature_vector = [
                float(result.success),
                result.duration,
                len(result.data_captured),
                len(result.vulnerabilities_found),
                len(result.tools_used),
                len(result.error_logs),
                result.timestamp % 86400,  # Time of day
                hash(result.attack_type) % 1000,  # Attack type hash
                hash(result.target) % 1000,  # Target hash
                # Performance metrics
                result.performance_metrics.get("cpu_usage", 0.0),
                result.performance_metrics.get("memory_usage", 0.0),
                result.performance_metrics.get("network_usage", 0.0),
                # Add more features as needed
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def _create_pattern_analysis(self, results: List[AttackResult], cluster_id: int) -> PatternAnalysis:
        """Create pattern analysis from cluster results"""
        # Analyze common characteristics
        attack_types = Counter([r.attack_type for r in results])
        targets = Counter([r.target for r in results])
        tools = Counter([tool for r in results for tool in r.tools_used])
        
        # Calculate success rate
        success_rate = sum(1 for r in results if r.success) / len(results)
        
        # Generate recommendations
        recommendations = self._generate_pattern_recommendations(results, success_rate)
        
        return PatternAnalysis(
            pattern_id=f"pattern_{cluster_id}_{int(time.time())}",
            pattern_type=attack_types.most_common(1)[0][0] if attack_types else "unknown",
            confidence=success_rate,
            frequency=len(results),
            targets=list(targets.keys()),
            tools=list(tools.keys()),
            success_rate=success_rate,
            recommendations=recommendations
        )
    
    def _generate_pattern_recommendations(self, results: List[AttackResult], success_rate: float) -> List[str]:
        """Generate recommendations based on pattern analysis"""
        recommendations = []
        
        if success_rate > 0.8:
            recommendations.append("High success rate - continue with similar approach")
        elif success_rate < 0.3:
            recommendations.append("Low success rate - consider alternative strategies")
        
        # Analyze tool effectiveness
        tool_success = defaultdict(list)
        for result in results:
            for tool in result.tools_used:
                tool_success[tool].append(result.success)
        
        for tool, successes in tool_success.items():
            tool_rate = sum(successes) / len(successes)
            if tool_rate > 0.7:
                recommendations.append(f"Tool {tool} shows high effectiveness")
            elif tool_rate < 0.3:
                recommendations.append(f"Consider replacing tool {tool}")
        
        # Analyze target vulnerabilities
        all_vulns = [vuln for r in results for vuln in r.vulnerabilities_found]
        vuln_counter = Counter(all_vulns)
        
        for vuln, count in vuln_counter.most_common(3):
            if count > 2:
                recommendations.append(f"Vulnerability {vuln} appears frequently")
        
        return recommendations
    
    async def _analyze_vulnerabilities(self, results: List[AttackResult]) -> List[VulnerabilityAnalysis]:
        """Analyze vulnerabilities using AI"""
        try:
            vulnerabilities = []
            
            # Extract vulnerability features
            vuln_features = self._extract_vulnerability_features(results)
            
            if len(vuln_features) > 0:
                # Use vulnerability detector model
                predictions = self.vulnerability_detector.predict(vuln_features)
                
                # Analyze each vulnerability
                for i, result in enumerate(results):
                    for vuln in result.vulnerabilities_found:
                        vuln_analysis = self._create_vulnerability_analysis(
                            vuln, result, predictions[i] if i < len(predictions) else 0.5
                        )
                        vulnerabilities.append(vuln_analysis)
            
            # Update vulnerabilities cache
            self.vulnerabilities.extend(vulnerabilities)
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"Error analyzing vulnerabilities: {str(e)}")
            return []
    
    def _extract_vulnerability_features(self, results: List[AttackResult]) -> np.ndarray:
        """Extract features for vulnerability analysis"""
        features = []
        
        for result in results:
            for vuln in result.vulnerabilities_found:
                feature_vector = [
                    float(result.success),
                    result.duration,
                    len(result.data_captured),
                    len(result.tools_used),
                    hash(vuln) % 1000,
                    hash(result.attack_type) % 1000,
                    hash(result.target) % 1000,
                    result.performance_metrics.get("cpu_usage", 0.0),
                    result.performance_metrics.get("memory_usage", 0.0),
                    # Add more vulnerability-specific features
                ]
                features.append(feature_vector)
        
        return np.array(features) if features else np.array([])
    
    def _create_vulnerability_analysis(self, vuln: str, result: AttackResult, confidence: float) -> VulnerabilityAnalysis:
        """Create vulnerability analysis"""
        # Determine severity based on success and impact
        severity = "HIGH" if result.success and confidence > 0.7 else "MEDIUM" if confidence > 0.4 else "LOW"
        
        # Calculate exploitability score
        exploitability = confidence * (1.0 if result.success else 0.5)
        
        # Calculate impact score
        impact_score = len(result.data_captured) * 0.1 + len(result.vulnerabilities_found) * 0.2
        
        return VulnerabilityAnalysis(
            vuln_id=f"vuln_{hash(vuln)}_{int(time.time())}",
            vuln_type=vuln,
            severity=severity,
            affected_targets=[result.target],
            exploitability=exploitability,
            impact_score=impact_score,
            remediation=self._generate_remediation(vuln, result),
            detection_method=result.attack_type
        )
    
    def _generate_remediation(self, vuln: str, result: AttackResult) -> str:
        """Generate remediation recommendations"""
        remediations = {
            "weak_password": "Implement strong password policies and multi-factor authentication",
            "outdated_software": "Update software to latest versions and apply security patches",
            "misconfigured_firewall": "Review and fix firewall configurations",
            "open_ports": "Close unnecessary ports and implement port scanning",
            "weak_encryption": "Upgrade to strong encryption algorithms",
            "default_credentials": "Change default credentials and implement credential management",
            "sql_injection": "Implement input validation and use parameterized queries",
            "xss": "Implement output encoding and content security policies",
            "csrf": "Implement CSRF tokens and validate requests",
            "file_upload": "Validate file types and implement secure file handling"
        }
        
        return remediations.get(vuln.lower(), "Implement security best practices and regular audits")
    
    async def _predict_success(self, results: List[AttackResult]) -> Dict:
        """Predict success of future attacks"""
        try:
            predictions = {}
            
            # Extract features for prediction
            features = self._extract_prediction_features(results)
            
            if len(features) > 0:
                # Use success predictor model
                success_probs = self.success_predictor.predict(features)
                
                # Analyze predictions
                avg_success_prob = np.mean(success_probs)
                high_success_count = np.sum(success_probs > 0.7)
                
                predictions = {
                    "average_success_probability": float(avg_success_prob),
                    "high_success_predictions": int(high_success_count),
                    "recommendations": self._generate_success_recommendations(avg_success_prob)
                }
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting success: {str(e)}")
            return {}
    
    def _extract_prediction_features(self, results: List[AttackResult]) -> np.ndarray:
        """Extract features for success prediction"""
        features = []
        
        for result in results:
            feature_vector = [
                float(result.success),
                result.duration,
                len(result.data_captured),
                len(result.vulnerabilities_found),
                len(result.tools_used),
                len(result.error_logs),
                result.performance_metrics.get("cpu_usage", 0.0),
                result.performance_metrics.get("memory_usage", 0.0),
                result.performance_metrics.get("network_usage", 0.0),
                # Add more prediction features
            ]
            features.append(feature_vector)
        
        return np.array(features) if features else np.array([])
    
    def _generate_success_recommendations(self, avg_success_prob: float) -> List[str]:
        """Generate recommendations based on success prediction"""
        recommendations = []
        
        if avg_success_prob > 0.8:
            recommendations.append("High success probability - proceed with current strategy")
        elif avg_success_prob > 0.6:
            recommendations.append("Moderate success probability - consider minor adjustments")
        elif avg_success_prob > 0.4:
            recommendations.append("Low success probability - consider alternative approaches")
        else:
            recommendations.append("Very low success probability - revise strategy completely")
        
        return recommendations
    
    async def _analyze_threats(self, results: List[AttackResult]) -> Dict:
        """Analyze threats using AI"""
        try:
            threats = {}
            
            # Extract threat features
            threat_features = self._extract_threat_features(results)
            
            if len(threat_features) > 0:
                # Use threat analyzer model
                threat_levels = self.threat_analyzer.predict(threat_features)
                
                # Analyze threat levels
                avg_threat_level = np.mean(threat_levels)
                max_threat_level = np.max(threat_levels)
                
                threats = {
                    "average_threat_level": float(avg_threat_level),
                    "maximum_threat_level": float(max_threat_level),
                    "threat_distribution": threat_levels.tolist(),
                    "recommendations": self._generate_threat_recommendations(avg_threat_level)
                }
            
            return threats
            
        except Exception as e:
            self.logger.error(f"Error analyzing threats: {str(e)}")
            return {}
    
    def _extract_threat_features(self, results: List[AttackResult]) -> np.ndarray:
        """Extract features for threat analysis"""
        features = []
        
        for result in results:
            feature_vector = [
                float(result.success),
                len(result.data_captured),
                len(result.vulnerabilities_found),
                len(result.tools_used),
                result.duration,
                len(result.error_logs),
                result.performance_metrics.get("cpu_usage", 0.0),
                result.performance_metrics.get("memory_usage", 0.0),
                # Add more threat-specific features
            ]
            features.append(feature_vector)
        
        return np.array(features) if features else np.array([])
    
    def _generate_threat_recommendations(self, avg_threat_level: float) -> List[str]:
        """Generate recommendations based on threat analysis"""
        recommendations = []
        
        if avg_threat_level > 0.8:
            recommendations.append("High threat level detected - implement immediate defenses")
            recommendations.append("Consider isolating affected systems")
        elif avg_threat_level > 0.6:
            recommendations.append("Moderate threat level - enhance monitoring")
            recommendations.append("Review and update security policies")
        elif avg_threat_level > 0.4:
            recommendations.append("Low threat level - maintain current defenses")
        else:
            recommendations.append("Minimal threat level - continue monitoring")
        
        return recommendations
    
    async def _generate_smart_report(self, analysis: Dict) -> SmartReport:
        """Generate intelligent report from analysis"""
        try:
            # Extract key findings
            key_findings = []
            
            # Pattern findings
            if "patterns" in analysis:
                for pattern in analysis["patterns"]:
                    key_findings.append(f"Pattern {pattern.pattern_type}: {pattern.success_rate:.1%} success rate")
            
            # Vulnerability findings
            if "vulnerabilities" in analysis:
                high_severity_vulns = [v for v in analysis["vulnerabilities"] if v.severity == "HIGH"]
                if high_severity_vulns:
                    key_findings.append(f"Found {len(high_severity_vulns)} high-severity vulnerabilities")
            
            # Success predictions
            if "predictions" in analysis:
                pred = analysis["predictions"]
                key_findings.append(f"Success probability: {pred.get('average_success_probability', 0):.1%}")
            
            # Threat findings
            if "threats" in analysis:
                threats = analysis["threats"]
                key_findings.append(f"Threat level: {threats.get('average_threat_level', 0):.1%}")
            
            # Generate recommendations
            recommendations = self._generate_smart_recommendations(analysis)
            
            # Generate next actions
            next_actions = self._generate_next_actions(analysis)
            
            # Create report
            report = SmartReport(
                report_id=f"report_{int(time.time())}",
                report_type="comprehensive_analysis",
                summary=self._generate_summary(analysis),
                key_findings=key_findings,
                recommendations=recommendations,
                risk_assessment=self._assess_risk(analysis),
                next_actions=next_actions,
                generated_at=time.time()
            )
            
            # Add to reports cache
            self.reports.append(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating smart report: {str(e)}")
            return SmartReport(
                report_id=f"error_report_{int(time.time())}",
                report_type="error",
                summary="Error generating report",
                key_findings=[],
                recommendations=[],
                risk_assessment={},
                next_actions=[],
                generated_at=time.time()
            )
    
    def _generate_smart_recommendations(self, analysis: Dict) -> List[str]:
        """Generate smart recommendations from analysis"""
        recommendations = []
        
        # Pattern-based recommendations
        if "patterns" in analysis:
            for pattern in analysis["patterns"]:
                if pattern.success_rate > 0.8:
                    recommendations.append(f"Continue using {pattern.pattern_type} approach")
                elif pattern.success_rate < 0.3:
                    recommendations.append(f"Consider alternative to {pattern.pattern_type}")
        
        # Vulnerability-based recommendations
        if "vulnerabilities" in analysis:
            high_vulns = [v for v in analysis["vulnerabilities"] if v.severity == "HIGH"]
            if high_vulns:
                recommendations.append("Prioritize remediation of high-severity vulnerabilities")
        
        # Success prediction recommendations
        if "predictions" in analysis:
            pred = analysis["predictions"]
            if pred.get("average_success_probability", 0) > 0.7:
                recommendations.append("High success probability - proceed with confidence")
            elif pred.get("average_success_probability", 0) < 0.4:
                recommendations.append("Low success probability - revise strategy")
        
        # Threat-based recommendations
        if "threats" in analysis:
            threats = analysis["threats"]
            if threats.get("average_threat_level", 0) > 0.7:
                recommendations.append("High threat level - implement immediate defenses")
        
        return recommendations
    
    def _generate_next_actions(self, analysis: Dict) -> List[str]:
        """Generate next actions from analysis"""
        actions = []
        
        # Based on patterns
        if "patterns" in analysis:
            actions.append("Continue monitoring successful patterns")
            actions.append("Investigate failed patterns for improvement")
        
        # Based on vulnerabilities
        if "vulnerabilities" in analysis:
            actions.append("Prioritize vulnerability remediation")
            actions.append("Implement additional security controls")
        
        # Based on predictions
        if "predictions" in analysis:
            actions.append("Adjust strategy based on success predictions")
        
        # Based on threats
        if "threats" in analysis:
            actions.append("Enhance threat monitoring")
            actions.append("Update incident response procedures")
        
        return actions
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Generate summary from analysis"""
        summary_parts = []
        
        if "patterns" in analysis:
            pattern_count = len(analysis["patterns"])
            summary_parts.append(f"Identified {pattern_count} attack patterns")
        
        if "vulnerabilities" in analysis:
            vuln_count = len(analysis["vulnerabilities"])
            summary_parts.append(f"Found {vuln_count} vulnerabilities")
        
        if "predictions" in analysis:
            pred = analysis["predictions"]
            success_prob = pred.get("average_success_probability", 0)
            summary_parts.append(f"Success probability: {success_prob:.1%}")
        
        if "threats" in analysis:
            threats = analysis["threats"]
            threat_level = threats.get("average_threat_level", 0)
            summary_parts.append(f"Threat level: {threat_level:.1%}")
        
        return ". ".join(summary_parts) if summary_parts else "No significant findings"
    
    def _assess_risk(self, analysis: Dict) -> Dict:
        """Assess overall risk from analysis"""
        risk_score = 0.0
        risk_factors = []
        
        # Pattern-based risk
        if "patterns" in analysis:
            for pattern in analysis["patterns"]:
                if pattern.success_rate > 0.8:
                    risk_score += 0.3
                    risk_factors.append("High success attack patterns")
        
        # Vulnerability-based risk
        if "vulnerabilities" in analysis:
            high_vulns = [v for v in analysis["vulnerabilities"] if v.severity == "HIGH"]
            if high_vulns:
                risk_score += 0.4
                risk_factors.append(f"{len(high_vulns)} high-severity vulnerabilities")
        
        # Threat-based risk
        if "threats" in analysis:
            threats = analysis["threats"]
            threat_level = threats.get("average_threat_level", 0)
            if threat_level > 0.7:
                risk_score += 0.3
                risk_factors.append("High threat level detected")
        
        return {
            "overall_risk_score": min(risk_score, 1.0),
            "risk_level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW",
            "risk_factors": risk_factors
        }
    
    async def get_analysis_statistics(self) -> Dict:
        """Get analysis statistics"""
        try:
            return {
                "success": True,
                "statistics": {
                    "total_attack_results": len(self.attack_results),
                    "total_patterns": len(self.patterns),
                    "total_vulnerabilities": len(self.vulnerabilities),
                    "total_reports": len(self.reports),
                    "successful_attacks": sum(1 for r in self.attack_results if r.success),
                    "average_success_rate": sum(1 for r in self.attack_results if r.success) / len(self.attack_results) if self.attack_results else 0,
                    "high_severity_vulnerabilities": len([v for v in self.vulnerabilities if v.severity == "HIGH"]),
                    "recent_analysis": len([r for r in self.attack_results if time.time() - r.timestamp < 3600])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_latest_report(self) -> Dict:
        """Get the latest analysis report"""
        try:
            if self.reports:
                latest_report = max(self.reports, key=lambda r: r.generated_at)
                return {
                    "success": True,
                    "report": asdict(latest_report)
                }
            else:
                return {
                    "success": False,
                    "error": "No reports available"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_models(self, path: str = "ai_models"):
        """Save AI models to disk"""
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save models
            self.pattern_classifier.save(f"{path}/pattern_classifier.h5")
            self.vulnerability_detector.save(f"{path}/vulnerability_detector.h5")
            self.success_predictor.save(f"{path}/success_predictor.h5")
            self.threat_analyzer.save(f"{path}/threat_analyzer.h5")
            
            # Save analysis cache
            with open(f"{path}/analysis_cache.pkl", "wb") as f:
                pickle.dump(self.analysis_cache, f)
            
            self.logger.info(f"AI models saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self, path: str = "ai_models"):
        """Load AI models from disk"""
        try:
            # Load models
            self.pattern_classifier = keras.models.load_model(f"{path}/pattern_classifier.h5")
            self.vulnerability_detector = keras.models.load_model(f"{path}/vulnerability_detector.h5")
            self.success_predictor = keras.models.load_model(f"{path}/success_predictor.h5")
            self.threat_analyzer = keras.models.load_model(f"{path}/threat_analyzer.h5")
            
            # Load analysis cache
            with open(f"{path}/analysis_cache.pkl", "rb") as f:
                self.analysis_cache = pickle.load(f)
            
            self.logger.info(f"AI models loaded from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")