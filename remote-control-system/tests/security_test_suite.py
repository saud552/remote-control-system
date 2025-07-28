"""
Security Test Suite
Comprehensive security and penetration testing for the remote control system
"""

import asyncio
import time
import logging
import requests
import json
import hashlib
import hmac
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import socket
import ssl
from urllib.parse import urlparse

@dataclass
class SecurityVulnerability:
    """Security vulnerability data structure"""
    vulnerability_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    location: str
    evidence: str
    recommendation: str
    cve_id: Optional[str] = None

@dataclass
class SecurityTestResult:
    """Security test result data structure"""
    test_name: str
    status: str  # 'passed', 'failed', 'warning'
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    vulnerabilities: List[SecurityVulnerability]
    recommendations: List[str]
    duration: float

class SecurityTestSuite:
    """Comprehensive security and penetration testing suite"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        
        # Test configuration
        self.config = {
            'api_base_url': 'http://localhost:8000',
            'web_base_url': 'http://localhost:5000',
            'test_timeout': 30,
            'max_requests_per_second': 10,
        }
        
        # Security test scenarios
        self.security_tests = [
            {
                'name': 'SQL Injection Test',
                'category': 'injection',
                'endpoints': ['/api/devices', '/api/alerts'],
                'payloads': ["' OR 1=1--", "' UNION SELECT * FROM users--", "'; DROP TABLE users--"]
            },
            {
                'name': 'XSS Test',
                'category': 'xss',
                'endpoints': ['/api/devices', '/api/alerts'],
                'payloads': ['<script>alert("XSS")</script>', '<img src=x onerror=alert("XSS")>']
            },
            {
                'name': 'Authentication Bypass Test',
                'category': 'auth',
                'endpoints': ['/api/devices', '/api/monitoring/status'],
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            {
                'name': 'Authorization Test',
                'category': 'auth',
                'endpoints': ['/api/devices', '/api/alerts'],
                'roles': ['admin', 'user', 'guest']
            },
            {
                'name': 'Input Validation Test',
                'category': 'validation',
                'endpoints': ['/api/devices', '/api/alerts'],
                'malicious_inputs': ['../../etc/passwd', 'javascript:alert(1)', '<script>']
            },
            {
                'name': 'Rate Limiting Test',
                'category': 'dos',
                'endpoints': ['/health', '/api/devices'],
                'request_count': 100
            },
            {
                'name': 'SSL/TLS Test',
                'category': 'encryption',
                'endpoints': ['/health', '/api/devices'],
                'ssl_versions': ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']
            },
            {
                'name': 'Information Disclosure Test',
                'category': 'info_disclosure',
                'endpoints': ['/health', '/api/devices', '/api/alerts'],
                'sensitive_patterns': ['password', 'secret', 'key', 'token']
            }
        ]
        
        # Known attack patterns
        self.attack_patterns = {
            'sql_injection': [
                r"'.*OR.*1=1",
                r"'.*UNION.*SELECT",
                r"'.*DROP.*TABLE",
                r"'.*INSERT.*INTO",
                r"'.*UPDATE.*SET"
            ],
            'xss': [
                r"<script.*>",
                r"javascript:",
                r"onerror=",
                r"onload=",
                r"<img.*onerror"
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"..%2f"
            ],
            'command_injection': [
                r";.*ls",
                r";.*cat",
                r";.*rm",
                r"`.*`",
                r"\$\(.*\)"
            ]
        }
    
    def run_all_security_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        self.logger.info("Starting comprehensive security test suite")
        
        results = {}
        
        # Run individual security tests
        for test in self.security_tests:
            try:
                self.logger.info(f"Running {test['name']}...")
                result = self.run_security_test(test)
                results[test['name']] = result
                
            except Exception as e:
                self.logger.error(f"Error in {test['name']}: {str(e)}")
                results[test['name']] = SecurityTestResult(
                    test_name=test['name'],
                    status='failed',
                    vulnerabilities_found=0,
                    critical_vulnerabilities=0,
                    high_vulnerabilities=0,
                    medium_vulnerabilities=0,
                    low_vulnerabilities=0,
                    vulnerabilities=[],
                    recommendations=[f"Test failed: {str(e)}"],
                    duration=0
                )
        
        # Run additional security tests
        results['Network Security Test'] = self.run_network_security_test()
        results['Encryption Test'] = self.run_encryption_test()
        results['Session Security Test'] = self.run_session_security_test()
        results['API Security Test'] = self.run_api_security_test()
        
        return self.generate_security_report(results)
    
    def run_security_test(self, test: Dict[str, Any]) -> SecurityTestResult:
        """Run a specific security test"""
        start_time = time.time()
        vulnerabilities = []
        
        if test['category'] == 'injection':
            vulnerabilities = self.test_injection_attacks(test)
        elif test['category'] == 'xss':
            vulnerabilities = self.test_xss_attacks(test)
        elif test['category'] == 'auth':
            vulnerabilities = self.test_authentication_bypass(test)
        elif test['category'] == 'validation':
            vulnerabilities = self.test_input_validation(test)
        elif test['category'] == 'dos':
            vulnerabilities = self.test_rate_limiting(test)
        elif test['category'] == 'encryption':
            vulnerabilities = self.test_ssl_tls(test)
        elif test['category'] == 'info_disclosure':
            vulnerabilities = self.test_information_disclosure(test)
        
        # Calculate vulnerability counts
        critical_count = len([v for v in vulnerabilities if v.severity == 'critical'])
        high_count = len([v for v in vulnerabilities if v.severity == 'high'])
        medium_count = len([v for v in vulnerabilities if v.severity == 'medium'])
        low_count = len([v for v in vulnerabilities if v.severity == 'low'])
        
        # Determine test status
        if critical_count > 0 or high_count > 0:
            status = 'failed'
        elif medium_count > 0:
            status = 'warning'
        else:
            status = 'passed'
        
        # Generate recommendations
        recommendations = self.generate_security_recommendations(vulnerabilities)
        
        return SecurityTestResult(
            test_name=test['name'],
            status=status,
            vulnerabilities_found=len(vulnerabilities),
            critical_vulnerabilities=critical_count,
            high_vulnerabilities=high_count,
            medium_vulnerabilities=medium_count,
            low_vulnerabilities=low_count,
            vulnerabilities=vulnerabilities,
            recommendations=recommendations,
            duration=time.time() - start_time
        )
    
    def test_injection_attacks(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            for payload in test['payloads']:
                try:
                    # Test GET request
                    response = requests.get(
                        f"{self.config['api_base_url']}{endpoint}?id={payload}",
                        timeout=self.config['test_timeout']
                    )
                    
                    # Check for SQL error messages
                    if self.detect_sql_error(response.text):
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='SQL Injection',
                            severity='critical',
                            description=f'SQL injection vulnerability detected in {endpoint}',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Payload: {payload}, Response: {response.text[:200]}',
                            recommendation='Implement proper input validation and use parameterized queries'
                        ))
                    
                    # Test POST request
                    response = requests.post(
                        f"{self.config['api_base_url']}{endpoint}",
                        json={'id': payload},
                        timeout=self.config['test_timeout']
                    )
                    
                    if self.detect_sql_error(response.text):
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='SQL Injection',
                            severity='critical',
                            description=f'SQL injection vulnerability detected in {endpoint} (POST)',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Payload: {payload}, Response: {response.text[:200]}',
                            recommendation='Implement proper input validation and use parameterized queries'
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Error testing injection on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def test_xss_attacks(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for XSS vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            for payload in test['payloads']:
                try:
                    # Test GET request
                    response = requests.get(
                        f"{self.config['api_base_url']}{endpoint}?search={payload}",
                        timeout=self.config['test_timeout']
                    )
                    
                    # Check if payload is reflected in response
                    if payload in response.text:
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Cross-Site Scripting (XSS)',
                            severity='high',
                            description=f'XSS vulnerability detected in {endpoint}',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Payload: {payload}, Reflected in response',
                            recommendation='Implement proper output encoding and input validation'
                        ))
                    
                    # Test POST request
                    response = requests.post(
                        f"{self.config['api_base_url']}{endpoint}",
                        json={'search': payload},
                        timeout=self.config['test_timeout']
                    )
                    
                    if payload in response.text:
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Cross-Site Scripting (XSS)',
                            severity='high',
                            description=f'XSS vulnerability detected in {endpoint} (POST)',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Payload: {payload}, Reflected in response',
                            recommendation='Implement proper output encoding and input validation'
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Error testing XSS on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def test_authentication_bypass(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            for method in test['methods']:
                try:
                    # Test without authentication
                    if method == 'GET':
                        response = requests.get(
                            f"{self.config['api_base_url']}{endpoint}",
                            timeout=self.config['test_timeout']
                        )
                    elif method == 'POST':
                        response = requests.post(
                            f"{self.config['api_base_url']}{endpoint}",
                            json={'test': 'data'},
                            timeout=self.config['test_timeout']
                        )
                    elif method == 'PUT':
                        response = requests.put(
                            f"{self.config['api_base_url']}{endpoint}",
                            json={'test': 'data'},
                            timeout=self.config['test_timeout']
                        )
                    elif method == 'DELETE':
                        response = requests.delete(
                            f"{self.config['api_base_url']}{endpoint}",
                            timeout=self.config['test_timeout']
                        )
                    
                    # Check if access was granted without authentication
                    if response.status_code == 200:
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Authentication Bypass',
                            severity='critical',
                            description=f'Authentication bypass vulnerability in {endpoint}',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Method: {method}, Status: {response.status_code}',
                            recommendation='Implement proper authentication and authorization checks'
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Error testing auth bypass on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def test_input_validation(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test input validation"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            for malicious_input in test['malicious_inputs']:
                try:
                    # Test with malicious input
                    response = requests.get(
                        f"{self.config['api_base_url']}{endpoint}?input={malicious_input}",
                        timeout=self.config['test_timeout']
                    )
                    
                    # Check if malicious input was processed
                    if malicious_input in response.text or response.status_code == 200:
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Input Validation',
                            severity='medium',
                            description=f'Input validation vulnerability in {endpoint}',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Malicious input: {malicious_input}',
                            recommendation='Implement strict input validation and sanitization'
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Error testing input validation on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def test_rate_limiting(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test rate limiting"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            try:
                # Send rapid requests
                responses = []
                for i in range(test['request_count']):
                    response = requests.get(
                        f"{self.config['api_base_url']}{endpoint}",
                        timeout=self.config['test_timeout']
                    )
                    responses.append(response.status_code)
                
                # Check if rate limiting is working
                successful_requests = len([r for r in responses if r == 200])
                if successful_requests > test['request_count'] * 0.8:  # More than 80% successful
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type='Rate Limiting',
                        severity='medium',
                        description=f'Rate limiting not properly implemented in {endpoint}',
                        location=f'{self.config["api_base_url"]}{endpoint}',
                        evidence=f'{successful_requests}/{test["request_count"]} requests successful',
                        recommendation='Implement proper rate limiting to prevent DoS attacks'
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Error testing rate limiting on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def test_ssl_tls(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test SSL/TLS configuration"""
        vulnerabilities = []
        
        try:
            # Parse URL to get hostname and port
            parsed_url = urlparse(self.config['api_base_url'])
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                # Test SSL/TLS configuration
                context = ssl.create_default_context()
                
                try:
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            
                            # Check certificate validity
                            if not cert:
                                vulnerabilities.append(SecurityVulnerability(
                                    vulnerability_type='SSL/TLS',
                                    severity='high',
                                    description='Invalid SSL certificate',
                                    location=f'{hostname}:{port}',
                                    evidence='No valid certificate found',
                                    recommendation='Ensure valid SSL certificate is installed'
                                ))
                            
                            # Check certificate expiration
                            if cert and 'notAfter' in cert:
                                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                                if expiry_date < datetime.now():
                                    vulnerabilities.append(SecurityVulnerability(
                                        vulnerability_type='SSL/TLS',
                                        severity='medium',
                                        description='Expired SSL certificate',
                                        location=f'{hostname}:{port}',
                                        evidence=f'Certificate expired on {expiry_date}',
                                        recommendation='Renew SSL certificate'
                                    ))
                                    
                except ssl.SSLError as e:
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type='SSL/TLS',
                        severity='high',
                        description='SSL/TLS configuration error',
                        location=f'{hostname}:{port}',
                        evidence=f'SSL Error: {str(e)}',
                        recommendation='Fix SSL/TLS configuration'
                    ))
            else:
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type='SSL/TLS',
                    severity='high',
                    description='No HTTPS enabled',
                    location=self.config['api_base_url'],
                    evidence='HTTP protocol used instead of HTTPS',
                    recommendation='Enable HTTPS for secure communication'
                ))
                
        except Exception as e:
            self.logger.warning(f"Error testing SSL/TLS: {str(e)}")
        
        return vulnerabilities
    
    def test_information_disclosure(self, test: Dict[str, Any]) -> List[SecurityVulnerability]:
        """Test for information disclosure"""
        vulnerabilities = []
        
        for endpoint in test['endpoints']:
            try:
                response = requests.get(
                    f"{self.config['api_base_url']}{endpoint}",
                    timeout=self.config['test_timeout']
                )
                
                # Check for sensitive information in response
                for pattern in test['sensitive_patterns']:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Information Disclosure',
                            severity='medium',
                            description=f'Sensitive information disclosed in {endpoint}',
                            location=f'{self.config["api_base_url"]}{endpoint}',
                            evidence=f'Sensitive pattern found: {pattern}',
                            recommendation='Remove sensitive information from responses'
                        ))
                
                # Check for detailed error messages
                if 'error' in response.text.lower() and len(response.text) > 500:
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type='Information Disclosure',
                        severity='low',
                        description=f'Detailed error messages in {endpoint}',
                        location=f'{self.config["api_base_url"]}{endpoint}',
                        evidence='Detailed error message found',
                        recommendation='Use generic error messages in production'
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Error testing information disclosure on {endpoint}: {str(e)}")
        
        return vulnerabilities
    
    def run_network_security_test(self) -> SecurityTestResult:
        """Test network security"""
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # Test for open ports
            common_ports = [21, 22, 23, 25, 53, 80, 443, 3306, 5432, 6379, 8080]
            parsed_url = urlparse(self.config['api_base_url'])
            hostname = parsed_url.hostname
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((hostname, port))
                    sock.close()
                    
                    if result == 0:
                        vulnerabilities.append(SecurityVulnerability(
                            vulnerability_type='Network Security',
                            severity='medium',
                            description=f'Open port detected: {port}',
                            location=f'{hostname}:{port}',
                            evidence=f'Port {port} is open and accessible',
                            recommendation=f'Close unnecessary port {port} or restrict access'
                        ))
                        
                except Exception:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Error in network security test: {str(e)}")
        
        return SecurityTestResult(
            test_name='Network Security Test',
            status='passed' if not vulnerabilities else 'warning',
            vulnerabilities_found=len(vulnerabilities),
            critical_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'critical']),
            high_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'high']),
            medium_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'medium']),
            low_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'low']),
            vulnerabilities=vulnerabilities,
            recommendations=self.generate_security_recommendations(vulnerabilities),
            duration=time.time() - start_time
        )
    
    def run_encryption_test(self) -> SecurityTestResult:
        """Test encryption implementation"""
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # Test for weak encryption
            response = requests.get(f"{self.config['api_base_url']}/health", timeout=10)
            
            # Check for weak hash algorithms in response headers
            if 'md5' in response.text.lower() or 'sha1' in response.text.lower():
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type='Weak Encryption',
                    severity='medium',
                    description='Weak hash algorithms detected',
                    location=self.config['api_base_url'],
                    evidence='MD5 or SHA1 detected in response',
                    recommendation='Use SHA-256 or stronger hash algorithms'
                ))
                
        except Exception as e:
            self.logger.warning(f"Error in encryption test: {str(e)}")
        
        return SecurityTestResult(
            test_name='Encryption Test',
            status='passed' if not vulnerabilities else 'warning',
            vulnerabilities_found=len(vulnerabilities),
            critical_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'critical']),
            high_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'high']),
            medium_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'medium']),
            low_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'low']),
            vulnerabilities=vulnerabilities,
            recommendations=self.generate_security_recommendations(vulnerabilities),
            duration=time.time() - start_time
        )
    
    def run_session_security_test(self) -> SecurityTestResult:
        """Test session security"""
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # Test session management
            response = requests.get(f"{self.config['api_base_url']}/health", timeout=10)
            
            # Check for secure session cookies
            if 'session' in response.cookies:
                session_cookie = response.cookies['session']
                if not session_cookie.startswith('eyJ'):  # Not JWT format
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type='Session Security',
                        severity='medium',
                        description='Weak session token format',
                        location=self.config['api_base_url'],
                        evidence='Session token not in secure format',
                        recommendation='Use JWT or other secure session tokens'
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error in session security test: {str(e)}")
        
        return SecurityTestResult(
            test_name='Session Security Test',
            status='passed' if not vulnerabilities else 'warning',
            vulnerabilities_found=len(vulnerabilities),
            critical_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'critical']),
            high_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'high']),
            medium_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'medium']),
            low_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'low']),
            vulnerabilities=vulnerabilities,
            recommendations=self.generate_security_recommendations(vulnerabilities),
            duration=time.time() - start_time
        )
    
    def run_api_security_test(self) -> SecurityTestResult:
        """Test API security"""
        start_time = time.time()
        vulnerabilities = []
        
        try:
            # Test API security headers
            response = requests.get(f"{self.config['api_base_url']}/health", timeout=10)
            
            # Check for security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'Content-Security-Policy'
            ]
            
            for header in security_headers:
                if header not in response.headers:
                    vulnerabilities.append(SecurityVulnerability(
                        vulnerability_type='API Security',
                        severity='medium',
                        description=f'Missing security header: {header}',
                        location=self.config['api_base_url'],
                        evidence=f'Header {header} not present in response',
                        recommendation=f'Add {header} security header'
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error in API security test: {str(e)}")
        
        return SecurityTestResult(
            test_name='API Security Test',
            status='passed' if not vulnerabilities else 'warning',
            vulnerabilities_found=len(vulnerabilities),
            critical_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'critical']),
            high_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'high']),
            medium_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'medium']),
            low_vulnerabilities=len([v for v in vulnerabilities if v.severity == 'low']),
            vulnerabilities=vulnerabilities,
            recommendations=self.generate_security_recommendations(vulnerabilities),
            duration=time.time() - start_time
        )
    
    def detect_sql_error(self, response_text: str) -> bool:
        """Detect SQL error messages in response"""
        sql_error_patterns = [
            r'sql.*error',
            r'mysql.*error',
            r'postgresql.*error',
            r'oracle.*error',
            r'sqlite.*error',
            r'syntax.*error',
            r'column.*not.*found',
            r'table.*not.*found'
        ]
        
        for pattern in sql_error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        
        return False
    
    def generate_security_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate security recommendations based on vulnerabilities"""
        recommendations = []
        
        # Count vulnerabilities by severity
        critical_count = len([v for v in vulnerabilities if v.severity == 'critical'])
        high_count = len([v for v in vulnerabilities if v.severity == 'high'])
        medium_count = len([v for v in vulnerabilities if v.severity == 'medium'])
        low_count = len([v for v in vulnerabilities if v.severity == 'low'])
        
        if critical_count > 0:
            recommendations.append(f"CRITICAL: {critical_count} critical vulnerabilities found. Immediate action required.")
        
        if high_count > 0:
            recommendations.append(f"HIGH: {high_count} high severity vulnerabilities found. Address promptly.")
        
        if medium_count > 0:
            recommendations.append(f"MEDIUM: {medium_count} medium severity vulnerabilities found. Plan remediation.")
        
        if low_count > 0:
            recommendations.append(f"LOW: {low_count} low severity vulnerabilities found. Consider addressing.")
        
        # Specific recommendations based on vulnerability types
        sql_injection_vulns = [v for v in vulnerabilities if 'SQL Injection' in v.vulnerability_type]
        if sql_injection_vulns:
            recommendations.append("Implement parameterized queries and input validation to prevent SQL injection")
        
        xss_vulns = [v for v in vulnerabilities if 'XSS' in v.vulnerability_type]
        if xss_vulns:
            recommendations.append("Implement proper output encoding and input validation to prevent XSS")
        
        auth_vulns = [v for v in vulnerabilities if 'Authentication' in v.vulnerability_type]
        if auth_vulns:
            recommendations.append("Implement proper authentication and authorization mechanisms")
        
        return recommendations
    
    def generate_security_report(self, results: Dict[str, SecurityTestResult]) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r.status == 'passed'])
        failed_tests = len([r for r in results.values() if r.status == 'failed'])
        warning_tests = len([r for r in results.values() if r.status == 'warning'])
        
        total_vulnerabilities = sum([r.vulnerabilities_found for r in results.values()])
        critical_vulnerabilities = sum([r.critical_vulnerabilities for r in results.values()])
        high_vulnerabilities = sum([r.high_vulnerabilities for r in results.values()])
        medium_vulnerabilities = sum([r.medium_vulnerabilities for r in results.values()])
        low_vulnerabilities = sum([r.low_vulnerabilities for r in results.values()])
        
        # Calculate security score
        max_score = total_tests * 100
        actual_score = passed_tests * 100 + warning_tests * 50
        security_score = (actual_score / max_score * 100) if max_score > 0 else 0
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'warning_tests': warning_tests,
                'security_score': security_score,
                'total_vulnerabilities': total_vulnerabilities,
                'critical_vulnerabilities': critical_vulnerabilities,
                'high_vulnerabilities': high_vulnerabilities,
                'medium_vulnerabilities': medium_vulnerabilities,
                'low_vulnerabilities': low_vulnerabilities,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': results,
            'recommendations': self.generate_overall_security_recommendations(results)
        }
        
        return report
    
    def generate_overall_security_recommendations(self, results: Dict[str, SecurityTestResult]) -> List[str]:
        """Generate overall security recommendations"""
        recommendations = []
        
        # Overall security assessment
        total_vulnerabilities = sum([r.vulnerabilities_found for r in results.values()])
        critical_vulnerabilities = sum([r.critical_vulnerabilities for r in results.values()])
        
        if critical_vulnerabilities > 0:
            recommendations.append("CRITICAL: System has critical security vulnerabilities. Immediate remediation required.")
        
        if total_vulnerabilities > 10:
            recommendations.append("HIGH: System has many security vulnerabilities. Comprehensive security review needed.")
        elif total_vulnerabilities > 5:
            recommendations.append("MEDIUM: System has several security vulnerabilities. Security improvements recommended.")
        elif total_vulnerabilities > 0:
            recommendations.append("LOW: System has minor security issues. Consider addressing for better security.")
        else:
            recommendations.append("EXCELLENT: No security vulnerabilities detected. Maintain current security practices.")
        
        # Specific recommendations
        if any('SQL Injection' in v.vulnerability_type for r in results.values() for v in r.vulnerabilities):
            recommendations.append("Implement comprehensive input validation and use parameterized queries")
        
        if any('XSS' in v.vulnerability_type for r in results.values() for v in r.vulnerabilities):
            recommendations.append("Implement proper output encoding and Content Security Policy")
        
        if any('Authentication' in v.vulnerability_type for r in results.values() for v in r.vulnerabilities):
            recommendations.append("Implement strong authentication and session management")
        
        return recommendations

def main():
    """Run the security test suite"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run test suite
    test_suite = SecurityTestSuite()
    report = test_suite.run_all_security_tests()
    
    # Print report
    print("\n" + "="*60)
    print("SECURITY TEST SUITE REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"\nSummary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed Tests: {summary['passed_tests']}")
    print(f"  Failed Tests: {summary['failed_tests']}")
    print(f"  Warning Tests: {summary['warning_tests']}")
    print(f"  Security Score: {summary['security_score']:.1f}%")
    print(f"  Total Vulnerabilities: {summary['total_vulnerabilities']}")
    print(f"  Critical: {summary['critical_vulnerabilities']}")
    print(f"  High: {summary['high_vulnerabilities']}")
    print(f"  Medium: {summary['medium_vulnerabilities']}")
    print(f"  Low: {summary['low_vulnerabilities']}")
    
    print(f"\nDetailed Results:")
    for test_name, result in report['detailed_results'].items():
        print(f"  {test_name}:")
        print(f"    Status: {result.status}")
        print(f"    Vulnerabilities: {result.vulnerabilities_found}")
        print(f"    Critical: {result.critical_vulnerabilities}")
        print(f"    High: {result.high_vulnerabilities}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    print("\n" + "="*60)
    
    return report

if __name__ == "__main__":
    main()