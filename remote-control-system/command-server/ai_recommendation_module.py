"""
AI Recommendation Module - Phase 5
Advanced AI-powered recommendation system for attack strategies
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
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib

@dataclass
class TargetProfile:
    """Target profile for recommendations"""
    target_id: str
    target_type: str
    os_info: str
    services: List[str]
    vulnerabilities: List[str]
    defenses: List[str]
    attack_history: List[str]
    success_rate: float
    difficulty_score: float

@dataclass
class ToolProfile:
    """Tool profile for recommendations"""
    tool_id: str
    tool_name: str
    tool_type: str
    capabilities: List[str]
    success_rate: float
    performance_metrics: Dict
    compatibility: List[str]
    requirements: List[str]

@dataclass
class AttackStrategy:
    """Attack strategy recommendation"""
    strategy_id: str
    target_id: str
    tools_recommended: List[str]
    approach: str
    expected_success_rate: float
    estimated_duration: float
    risk_level: str
    complexity: str
    prerequisites: List[str]
    alternatives: List[str]

@dataclass
class PerformanceOptimization:
    """Performance optimization recommendation"""
    optimization_id: str
    optimization_type: str
    current_performance: float
    expected_improvement: float
    recommendations: List[str]
    implementation_steps: List[str]
    priority: str

class AIRecommendationModule:
    """Advanced AI-powered recommendation system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.target_profiles: List[TargetProfile] = []
        self.tool_profiles: List[ToolProfile] = []
        self.attack_strategies: List[AttackStrategy] = []
        self.performance_optimizations: List[PerformanceOptimization] = []
        
        # AI Models
        self.tool_recommender = None
        self.strategy_predictor = None
        self.performance_optimizer = None
        self.success_predictor = None
        
        # Data storage
        self.recommendation_cache = {}
        self.performance_history = {}
        
        # Initialize AI models
        self._initialize_ai_models()
        self._load_default_profiles()
    
    def _initialize_ai_models(self):
        """Initialize AI models for recommendations"""
        try:
            # Tool recommendation model
            self.tool_recommender = self._create_tool_recommender()
            
            # Strategy prediction model
            self.strategy_predictor = self._create_strategy_predictor()
            
            # Performance optimization model
            self.performance_optimizer = self._create_performance_optimizer()
            
            # Success prediction model
            self.success_predictor = self._create_success_predictor()
            
            self.logger.info("AI recommendation models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AI recommendation models: {str(e)}")
    
    def _create_tool_recommender(self):
        """Create tool recommendation model"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(100,)),
            layers.Dropout(0.4),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(20, activation='softmax')  # 20 tool categories
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_strategy_predictor(self) -> keras.Model:
        """Create strategy prediction model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(50,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(10, activation='softmax')  # 10 strategy types
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_performance_optimizer(self) -> keras.Model:
        """Create performance optimization model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(40,)),
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
    
    def _create_success_predictor(self) -> keras.Model:
        """Create success prediction model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(60,)),
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
    
    def _load_default_profiles(self):
        """Load default target and tool profiles"""
        try:
            # Default target profiles
            default_targets = [
                TargetProfile(
                    target_id="windows_server",
                    target_type="server",
                    os_info="Windows Server 2019",
                    services=["http", "https", "ssh", "rdp"],
                    vulnerabilities=["weak_password", "outdated_software", "open_ports"],
                    defenses=["firewall", "antivirus", "ids"],
                    attack_history=["brute_force", "exploit"],
                    success_rate=0.75,
                    difficulty_score=0.6
                ),
                TargetProfile(
                    target_id="linux_server",
                    target_type="server",
                    os_info="Ubuntu 20.04",
                    services=["ssh", "http", "https", "ftp"],
                    vulnerabilities=["default_credentials", "misconfigured_firewall"],
                    defenses=["iptables", "fail2ban"],
                    attack_history=["dictionary_attack", "exploit"],
                    success_rate=0.65,
                    difficulty_score=0.7
                ),
                TargetProfile(
                    target_id="android_device",
                    target_type="mobile",
                    os_info="Android 11",
                    services=["adb", "http", "https"],
                    vulnerabilities=["weak_encryption", "outdated_apps"],
                    defenses=["antivirus", "firewall"],
                    attack_history=["payload_injection", "exploit"],
                    success_rate=0.85,
                    difficulty_score=0.4
                )
            ]
            
            # Default tool profiles
            default_tools = [
                ToolProfile(
                    tool_id="metasploit",
                    tool_name="Metasploit Framework",
                    tool_type="exploitation",
                    capabilities=["payload_injection", "exploit_execution", "privilege_escalation"],
                    success_rate=0.8,
                    performance_metrics={"cpu_usage": 0.3, "memory_usage": 0.4},
                    compatibility=["windows", "linux", "android"],
                    requirements=["ruby", "postgresql"]
                ),
                ToolProfile(
                    tool_id="nmap",
                    tool_name="Nmap",
                    tool_type="reconnaissance",
                    capabilities=["port_scanning", "service_detection", "os_detection"],
                    success_rate=0.95,
                    performance_metrics={"cpu_usage": 0.1, "memory_usage": 0.2},
                    compatibility=["windows", "linux"],
                    requirements=["python"]
                ),
                ToolProfile(
                    tool_id="hashcat",
                    tool_name="Hashcat",
                    tool_type="password_cracking",
                    capabilities=["hash_cracking", "gpu_acceleration", "dictionary_attack"],
                    success_rate=0.7,
                    performance_metrics={"cpu_usage": 0.8, "memory_usage": 0.6},
                    compatibility=["windows", "linux"],
                    requirements=["gpu", "wordlists"]
                ),
                ToolProfile(
                    tool_id="wifijammer",
                    tool_name="WiFiJammer",
                    tool_type="wireless",
                    capabilities=["deauth_attack", "channel_hopping", "evil_twin"],
                    success_rate=0.75,
                    performance_metrics={"cpu_usage": 0.2, "memory_usage": 0.3},
                    compatibility=["linux"],
                    requirements=["wireless_card", "monitor_mode"]
                )
            ]
            
            self.target_profiles.extend(default_targets)
            self.tool_profiles.extend(default_tools)
            
            self.logger.info("Default profiles loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading default profiles: {str(e)}")
    
    async def recommend_best_tools(self, target_info: Dict) -> Dict:
        """Recommend best tools for a target"""
        try:
            # Extract target features
            target_features = self._extract_target_features(target_info)
            
            # Use tool recommender model
            tool_predictions = self.tool_recommender.predict(target_features.reshape(1, -1))
            
            # Get top tool recommendations
            top_tools = self._get_top_tool_recommendations(tool_predictions[0], target_info)
            
            return {
                "success": True,
                "recommended_tools": top_tools,
                "confidence_scores": tool_predictions[0].tolist(),
                "reasoning": self._generate_tool_reasoning(target_info, top_tools)
            }
            
        except Exception as e:
            self.logger.error(f"Error recommending tools: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_target_features(self, target_info: Dict) -> np.ndarray:
        """Extract features for tool recommendation"""
        features = []
        
        # Target type encoding
        target_types = ["server", "desktop", "mobile", "network", "web"]
        target_type_idx = target_types.index(target_info.get("target_type", "server"))
        features.extend([1 if i == target_type_idx else 0 for i in range(len(target_types))])
        
        # OS encoding
        os_types = ["windows", "linux", "android", "ios", "macos"]
        os_type = target_info.get("os_info", "").lower()
        os_type_idx = next((i for i, os in enumerate(os_types) if os in os_type), 0)
        features.extend([1 if i == os_type_idx else 0 for i in range(len(os_types))])
        
        # Services encoding
        services = ["http", "https", "ssh", "ftp", "rdp", "telnet", "smtp", "dns"]
        target_services = target_info.get("services", [])
        features.extend([1 if service in target_services else 0 for service in services])
        
        # Vulnerabilities encoding
        vuln_types = ["weak_password", "outdated_software", "open_ports", "default_credentials", 
                     "misconfigured_firewall", "weak_encryption", "sql_injection", "xss"]
        target_vulns = target_info.get("vulnerabilities", [])
        features.extend([1 if vuln in target_vulns else 0 for vuln in vuln_types])
        
        # Defenses encoding
        defense_types = ["firewall", "antivirus", "ids", "ips", "encryption", "mfa"]
        target_defenses = target_info.get("defenses", [])
        features.extend([1 if defense in target_defenses else 0 for defense in defense_types])
        
        # Performance metrics
        features.extend([
            target_info.get("cpu_usage", 0.0),
            target_info.get("memory_usage", 0.0),
            target_info.get("network_usage", 0.0),
            target_info.get("difficulty_score", 0.5)
        ])
        
        # Pad to required size
        while len(features) < 100:
            features.append(0.0)
        
        return np.array(features[:100])
    
    def _get_top_tool_recommendations(self, predictions: np.ndarray, target_info: Dict) -> List[Dict]:
        """Get top tool recommendations based on predictions"""
        # Tool categories mapping
        tool_categories = [
            "reconnaissance", "exploitation", "password_cracking", "wireless",
            "web_application", "mobile", "network", "forensics", "social_engineering",
            "physical", "post_exploitation", "persistence", "privilege_escalation",
            "lateral_movement", "data_exfiltration", "defense_evasion", "command_control",
            "execution", "discovery", "collection"
        ]
        
        # Get top 5 tool categories
        top_indices = np.argsort(predictions)[-5:][::-1]
        
        recommendations = []
        for idx in top_indices:
            category = tool_categories[idx]
            confidence = predictions[idx]
            
            # Find best tools for this category
            category_tools = [tool for tool in self.tool_profiles if tool.tool_type == category]
            if category_tools:
                best_tool = max(category_tools, key=lambda t: t.success_rate)
                recommendations.append({
                    "tool_id": best_tool.tool_id,
                    "tool_name": best_tool.tool_name,
                    "category": category,
                    "confidence": float(confidence),
                    "success_rate": best_tool.success_rate,
                    "capabilities": best_tool.capabilities
                })
        
        return recommendations
    
    def _generate_tool_reasoning(self, target_info: Dict, recommended_tools: List[Dict]) -> str:
        """Generate reasoning for tool recommendations"""
        reasoning_parts = []
        
        target_type = target_info.get("target_type", "unknown")
        os_info = target_info.get("os_info", "unknown")
        
        for tool in recommended_tools:
            if tool["category"] == "reconnaissance":
                reasoning_parts.append(f"Reconnaissance tools recommended for initial target analysis")
            elif tool["category"] == "exploitation":
                reasoning_parts.append(f"Exploitation tools suitable for {target_type} targets")
            elif tool["category"] == "password_cracking":
                reasoning_parts.append(f"Password cracking tools for credential-based attacks")
            elif tool["category"] == "wireless":
                reasoning_parts.append(f"Wireless tools for network-based attacks")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Tools selected based on target characteristics"
    
    async def optimize_attack_strategies(self, target_id: str, current_performance: Dict) -> Dict:
        """Optimize attack strategies for better performance"""
        try:
            # Extract performance features
            performance_features = self._extract_performance_features(current_performance)
            
            # Use performance optimizer model
            optimization_score = self.performance_optimizer.predict(performance_features.reshape(1, -1))[0]
            
            # Generate optimization recommendations
            optimizations = self._generate_performance_optimizations(target_id, current_performance, optimization_score)
            
            return {
                "success": True,
                "optimization_score": float(optimization_score),
                "optimizations": optimizations,
                "expected_improvement": self._calculate_expected_improvement(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing strategies: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_performance_features(self, performance: Dict) -> np.ndarray:
        """Extract features for performance optimization"""
        features = [
            performance.get("cpu_usage", 0.0),
            performance.get("memory_usage", 0.0),
            performance.get("network_usage", 0.0),
            performance.get("disk_usage", 0.0),
            performance.get("success_rate", 0.0),
            performance.get("attack_duration", 0.0),
            performance.get("error_rate", 0.0),
            performance.get("resource_efficiency", 0.0),
            performance.get("tool_effectiveness", 0.0),
            performance.get("target_resistance", 0.0),
            # Add more performance features
        ]
        
        # Pad to required size
        while len(features) < 40:
            features.append(0.0)
        
        return np.array(features[:40])
    
    def _generate_performance_optimizations(self, target_id: str, performance: Dict, optimization_score: float) -> List[PerformanceOptimization]:
        """Generate performance optimization recommendations"""
        optimizations = []
        
        # CPU optimization
        if performance.get("cpu_usage", 0.0) > 0.8:
            optimizations.append(PerformanceOptimization(
                optimization_id=f"cpu_opt_{int(time.time())}",
                optimization_type="cpu_optimization",
                current_performance=performance.get("cpu_usage", 0.0),
                expected_improvement=0.2,
                recommendations=[
                    "Reduce concurrent processes",
                    "Use more efficient algorithms",
                    "Implement process prioritization"
                ],
                implementation_steps=[
                    "Monitor CPU usage patterns",
                    "Identify resource-intensive processes",
                    "Implement load balancing"
                ],
                priority="HIGH"
            ))
        
        # Memory optimization
        if performance.get("memory_usage", 0.0) > 0.8:
            optimizations.append(PerformanceOptimization(
                optimization_id=f"memory_opt_{int(time.time())}",
                optimization_type="memory_optimization",
                current_performance=performance.get("memory_usage", 0.0),
                expected_improvement=0.15,
                recommendations=[
                    "Implement memory pooling",
                    "Use more efficient data structures",
                    "Reduce memory leaks"
                ],
                implementation_steps=[
                    "Profile memory usage",
                    "Identify memory leaks",
                    "Implement garbage collection"
                ],
                priority="HIGH"
            ))
        
        # Success rate optimization
        if performance.get("success_rate", 0.0) < 0.5:
            optimizations.append(PerformanceOptimization(
                optimization_id=f"success_opt_{int(time.time())}",
                optimization_type="success_rate_optimization",
                current_performance=performance.get("success_rate", 0.0),
                expected_improvement=0.3,
                recommendations=[
                    "Improve target reconnaissance",
                    "Use more effective tools",
                    "Enhance attack timing"
                ],
                implementation_steps=[
                    "Analyze failed attacks",
                    "Identify weak points",
                    "Implement better strategies"
                ],
                priority="MEDIUM"
            ))
        
        return optimizations
    
    def _calculate_expected_improvement(self, optimizations: List[PerformanceOptimization]) -> float:
        """Calculate expected improvement from optimizations"""
        total_improvement = 0.0
        
        for opt in optimizations:
            if opt.priority == "HIGH":
                total_improvement += opt.expected_improvement * 0.4
            elif opt.priority == "MEDIUM":
                total_improvement += opt.expected_improvement * 0.3
            else:
                total_improvement += opt.expected_improvement * 0.2
        
        return min(total_improvement, 1.0)
    
    async def predict_attack_success(self, target_info: Dict, strategy_info: Dict) -> Dict:
        """Predict success probability of an attack strategy"""
        try:
            # Extract strategy features
            strategy_features = self._extract_strategy_features(target_info, strategy_info)
            
            # Use success predictor model
            success_probability = self.success_predictor.predict(strategy_features.reshape(1, -1))[0]
            
            # Generate success recommendations
            recommendations = self._generate_success_recommendations(success_probability, target_info, strategy_info)
            
            return {
                "success": True,
                "success_probability": float(success_probability),
                "risk_level": self._assess_risk_level(success_probability),
                "recommendations": recommendations,
                "confidence": self._calculate_prediction_confidence(strategy_features)
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting attack success: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_strategy_features(self, target_info: Dict, strategy_info: Dict) -> np.ndarray:
        """Extract features for success prediction"""
        features = []
        
        # Target features
        features.extend([
            target_info.get("difficulty_score", 0.5),
            len(target_info.get("vulnerabilities", [])),
            len(target_info.get("defenses", [])),
            target_info.get("success_rate", 0.0)
        ])
        
        # Strategy features
        features.extend([
            len(strategy_info.get("tools", [])),
            strategy_info.get("complexity", 0.5),
            strategy_info.get("duration", 0.0),
            strategy_info.get("risk_level", 0.5)
        ])
        
        # Tool effectiveness
        tools = strategy_info.get("tools", [])
        tool_effectiveness = 0.0
        for tool_id in tools:
            tool = next((t for t in self.tool_profiles if t.tool_id == tool_id), None)
            if tool:
                tool_effectiveness += tool.success_rate
        features.append(tool_effectiveness / len(tools) if tools else 0.0)
        
        # Pad to required size
        while len(features) < 60:
            features.append(0.0)
        
        return np.array(features[:60])
    
    def _assess_risk_level(self, success_probability: float) -> str:
        """Assess risk level based on success probability"""
        if success_probability > 0.8:
            return "LOW"
        elif success_probability > 0.6:
            return "MEDIUM"
        elif success_probability > 0.4:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _generate_success_recommendations(self, success_probability: float, target_info: Dict, strategy_info: Dict) -> List[str]:
        """Generate recommendations based on success prediction"""
        recommendations = []
        
        if success_probability > 0.8:
            recommendations.append("High success probability - proceed with confidence")
            recommendations.append("Consider scaling up the attack")
        elif success_probability > 0.6:
            recommendations.append("Moderate success probability - proceed with caution")
            recommendations.append("Consider additional reconnaissance")
        elif success_probability > 0.4:
            recommendations.append("Low success probability - consider alternatives")
            recommendations.append("Enhance target analysis")
        else:
            recommendations.append("Very low success probability - revise strategy")
            recommendations.append("Consider different approach entirely")
        
        # Target-specific recommendations
        if target_info.get("difficulty_score", 0.5) > 0.7:
            recommendations.append("High difficulty target - use advanced techniques")
        
        if len(target_info.get("defenses", [])) > 3:
            recommendations.append("Multiple defenses detected - use stealth techniques")
        
        return recommendations
    
    def _calculate_prediction_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence in prediction based on feature quality"""
        # Simple confidence calculation based on feature completeness
        non_zero_features = np.count_nonzero(features)
        total_features = len(features)
        confidence = non_zero_features / total_features
        
        return min(confidence, 1.0)
    
    async def get_recommendation_statistics(self) -> Dict:
        """Get recommendation system statistics"""
        try:
            return {
                "success": True,
                "statistics": {
                    "total_targets": len(self.target_profiles),
                    "total_tools": len(self.tool_profiles),
                    "total_strategies": len(self.attack_strategies),
                    "total_optimizations": len(self.performance_optimizations),
                    "average_tool_success_rate": np.mean([t.success_rate for t in self.tool_profiles]),
                    "average_target_difficulty": np.mean([t.difficulty_score for t in self.target_profiles]),
                    "recommendation_cache_size": len(self.recommendation_cache),
                    "performance_history_size": len(self.performance_history)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_recommendation_models(self, path: str = "ai_recommendation_models"):
        """Save recommendation models to disk"""
        try:
            os.makedirs(path, exist_ok=True)
            
            # Save models
            self.tool_recommender.save(f"{path}/tool_recommender.h5")
            self.strategy_predictor.save(f"{path}/strategy_predictor.h5")
            self.performance_optimizer.save(f"{path}/performance_optimizer.h5")
            self.success_predictor.save(f"{path}/success_predictor.h5")
            
            # Save recommendation cache
            with open(f"{path}/recommendation_cache.pkl", "wb") as f:
                pickle.dump(self.recommendation_cache, f)
            
            self.logger.info(f"Recommendation models saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving recommendation models: {str(e)}")
    
    def load_recommendation_models(self, path: str = "ai_recommendation_models"):
        """Load recommendation models from disk"""
        try:
            # Load models
            self.tool_recommender = keras.models.load_model(f"{path}/tool_recommender.h5")
            self.strategy_predictor = keras.models.load_model(f"{path}/strategy_predictor.h5")
            self.performance_optimizer = keras.models.load_model(f"{path}/performance_optimizer.h5")
            self.success_predictor = keras.models.load_model(f"{path}/success_predictor.h5")
            
            # Load recommendation cache
            with open(f"{path}/recommendation_cache.pkl", "rb") as f:
                self.recommendation_cache = pickle.load(f)
            
            self.logger.info(f"Recommendation models loaded from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading recommendation models: {str(e)}")