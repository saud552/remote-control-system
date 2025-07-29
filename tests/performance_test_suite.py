"""
Performance Test Suite
Comprehensive performance and stress testing for the remote control system
"""

import asyncio
import time
import logging
import threading
import statistics
import psutil
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = None

@dataclass
class PerformanceTestResult:
    """Performance test result data structure"""
    test_name: str
    duration: float
    success_rate: float
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    throughput: float
    error_count: int
    total_requests: int
    metrics: List[PerformanceMetric]
    recommendations: List[str]

class PerformanceTestSuite:
    """Comprehensive performance and stress testing suite"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        
        # Test configuration
        self.config = {
            'api_base_url': 'http://localhost:8000',
            'web_base_url': 'http://localhost:5000',
            'test_duration': 300,  # 5 minutes
            'concurrent_users': 50,
            'request_timeout': 30,
            'ramp_up_time': 60,  # 1 minute
            'target_rps': 100,  # requests per second
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': 2.0,  # seconds
            'min_success_rate': 95.0,  # percentage
            'max_memory_usage': 500,  # MB
            'max_cpu_usage': 80.0,  # percentage
            'min_throughput': 50,  # requests per second
        }
        
        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'API Health Check Load Test',
                'endpoint': '/health',
                'method': 'GET',
                'expected_status': 200,
                'concurrent_users': 10,
                'duration': 60,
            },
            {
                'name': 'Device Management Load Test',
                'endpoint': '/api/devices',
                'method': 'GET',
                'expected_status': 200,
                'concurrent_users': 20,
                'duration': 120,
            },
            {
                'name': 'Monitoring API Load Test',
                'endpoint': '/api/monitoring/status',
                'method': 'GET',
                'expected_status': 200,
                'concurrent_users': 15,
                'duration': 90,
            },
            {
                'name': 'Alerts API Load Test',
                'endpoint': '/api/alerts',
                'method': 'GET',
                'expected_status': 200,
                'concurrent_users': 25,
                'duration': 120,
            },
            {
                'name': 'Web Interface Load Test',
                'endpoint': '/',
                'method': 'GET',
                'expected_status': 200,
                'concurrent_users': 30,
                'duration': 180,
            },
        ]
        
        # Performance monitoring
        self.performance_metrics = []
        self.system_metrics = []
        
    def run_all_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        self.logger.info("Starting comprehensive performance test suite")
        
        results = {}
        
        # Run individual test scenarios
        for scenario in self.test_scenarios:
            try:
                self.logger.info(f"Running {scenario['name']}...")
                result = self.run_load_test(scenario)
                results[scenario['name']] = result
                
            except Exception as e:
                self.logger.error(f"Error in {scenario['name']}: {str(e)}")
                results[scenario['name']] = PerformanceTestResult(
                    test_name=scenario['name'],
                    duration=0,
                    success_rate=0,
                    avg_response_time=0,
                    max_response_time=0,
                    min_response_time=0,
                    throughput=0,
                    error_count=0,
                    total_requests=0,
                    metrics=[],
                    recommendations=[f"Test failed: {str(e)}"]
                )
        
        # Run stress tests
        results['Stress Test'] = self.run_stress_test()
        results['Memory Leak Test'] = self.run_memory_leak_test()
        results['Concurrent Connection Test'] = self.run_concurrent_connection_test()
        
        return self.generate_performance_report(results)
    
    def run_load_test(self, scenario: Dict[str, Any]) -> PerformanceTestResult:
        """Run load test for a specific scenario"""
        start_time = time.time()
        response_times = []
        errors = []
        successful_requests = 0
        total_requests = 0
        
        # Start system monitoring
        monitoring_thread = threading.Thread(
            target=self.monitor_system_resources,
            args=(scenario['duration'],)
        )
        monitoring_thread.start()
        
        # Calculate requests per second based on duration and concurrent users
        total_requests_target = scenario['concurrent_users'] * scenario['duration']
        requests_per_second = total_requests_target / scenario['duration']
        
        # Run load test
        with ThreadPoolExecutor(max_workers=scenario['concurrent_users']) as executor:
            futures = []
            
            for i in range(total_requests_target):
                future = executor.submit(
                    self.make_request,
                    scenario['method'],
                    f"{self.config['api_base_url']}{scenario['endpoint']}",
                    scenario['expected_status']
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    total_requests += 1
                    
                    if result['success']:
                        successful_requests += 1
                        response_times.append(result['response_time'])
                    else:
                        errors.append(result['error'])
                        
                except Exception as e:
                    total_requests += 1
                    errors.append(str(e))
        
        # Calculate metrics
        duration = time.time() - start_time
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        throughput = successful_requests / duration if duration > 0 else 0
        
        # Generate recommendations
        recommendations = self.generate_performance_recommendations(
            success_rate, avg_response_time, throughput, len(errors)
        )
        
        # Create performance metrics
        metrics = [
            PerformanceMetric('success_rate', success_rate, '%', datetime.now()),
            PerformanceMetric('avg_response_time', avg_response_time, 'seconds', datetime.now()),
            PerformanceMetric('throughput', throughput, 'requests/second', datetime.now()),
            PerformanceMetric('error_count', len(errors), 'count', datetime.now()),
        ]
        
        return PerformanceTestResult(
            test_name=scenario['name'],
            duration=duration,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            throughput=throughput,
            error_count=len(errors),
            total_requests=total_requests,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def run_stress_test(self) -> PerformanceTestResult:
        """Run stress test to find system limits"""
        self.logger.info("Running stress test...")
        
        start_time = time.time()
        max_concurrent_users = 0
        max_throughput = 0
        breaking_point = None
        
        # Gradually increase load until system breaks
        for concurrent_users in range(10, 200, 10):
            try:
                # Run short test with current load
                test_result = self.run_quick_load_test(concurrent_users, 30)
                
                if test_result['success_rate'] >= self.thresholds['min_success_rate']:
                    max_concurrent_users = concurrent_users
                    max_throughput = test_result['throughput']
                else:
                    breaking_point = concurrent_users
                    break
                    
            except Exception as e:
                breaking_point = concurrent_users
                break
        
        duration = time.time() - start_time
        
        recommendations = [
            f"Maximum concurrent users: {max_concurrent_users}",
            f"Maximum throughput: {max_throughput:.2f} requests/second",
            f"Breaking point: {breaking_point} concurrent users"
        ]
        
        metrics = [
            PerformanceMetric('max_concurrent_users', max_concurrent_users, 'users', datetime.now()),
            PerformanceMetric('max_throughput', max_throughput, 'requests/second', datetime.now()),
            PerformanceMetric('breaking_point', breaking_point or 0, 'users', datetime.now()),
        ]
        
        return PerformanceTestResult(
            test_name="Stress Test",
            duration=duration,
            success_rate=100 if breaking_point else 0,
            avg_response_time=0,
            max_response_time=0,
            min_response_time=0,
            throughput=max_throughput,
            error_count=0,
            total_requests=0,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def run_memory_leak_test(self) -> PerformanceTestResult:
        """Run memory leak detection test"""
        self.logger.info("Running memory leak test...")
        
        start_time = time.time()
        memory_readings = []
        
        # Monitor memory usage over time
        for i in range(60):  # 1 minute test
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_readings.append(memory_mb)
            
            # Make some requests to simulate normal usage
            for _ in range(10):
                try:
                    requests.get(f"{self.config['api_base_url']}/health", timeout=5)
                except:
                    pass
            
            time.sleep(1)
        
        duration = time.time() - start_time
        
        # Analyze memory trend
        if len(memory_readings) > 10:
            initial_memory = statistics.mean(memory_readings[:10])
            final_memory = statistics.mean(memory_readings[-10:])
            memory_increase = final_memory - initial_memory
            
            # Check for memory leak (more than 50MB increase)
            has_memory_leak = memory_increase > 50
            
            recommendations = [
                f"Initial memory: {initial_memory:.2f} MB",
                f"Final memory: {final_memory:.2f} MB",
                f"Memory increase: {memory_increase:.2f} MB",
                "Memory leak detected" if has_memory_leak else "No memory leak detected"
            ]
        else:
            memory_increase = 0
            has_memory_leak = False
            recommendations = ["Insufficient data for memory leak analysis"]
        
        metrics = [
            PerformanceMetric('initial_memory', memory_readings[0] if memory_readings else 0, 'MB', datetime.now()),
            PerformanceMetric('final_memory', memory_readings[-1] if memory_readings else 0, 'MB', datetime.now()),
            PerformanceMetric('memory_increase', memory_increase, 'MB', datetime.now()),
        ]
        
        return PerformanceTestResult(
            test_name="Memory Leak Test",
            duration=duration,
            success_rate=100,
            avg_response_time=0,
            max_response_time=0,
            min_response_time=0,
            throughput=0,
            error_count=0,
            total_requests=0,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def run_concurrent_connection_test(self) -> PerformanceTestResult:
        """Test concurrent connection handling"""
        self.logger.info("Running concurrent connection test...")
        
        start_time = time.time()
        successful_connections = 0
        failed_connections = 0
        connection_times = []
        
        # Test concurrent connections
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            
            for i in range(100):
                future = executor.submit(self.test_connection)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result['success']:
                        successful_connections += 1
                        connection_times.append(result['time'])
                    else:
                        failed_connections += 1
                        
                except Exception as e:
                    failed_connections += 1
        
        duration = time.time() - start_time
        success_rate = (successful_connections / 100 * 100) if successful_connections > 0 else 0
        avg_connection_time = statistics.mean(connection_times) if connection_times else 0
        
        recommendations = [
            f"Successful connections: {successful_connections}/100",
            f"Failed connections: {failed_connections}/100",
            f"Average connection time: {avg_connection_time:.3f}s"
        ]
        
        metrics = [
            PerformanceMetric('successful_connections', successful_connections, 'count', datetime.now()),
            PerformanceMetric('failed_connections', failed_connections, 'count', datetime.now()),
            PerformanceMetric('avg_connection_time', avg_connection_time, 'seconds', datetime.now()),
        ]
        
        return PerformanceTestResult(
            test_name="Concurrent Connection Test",
            duration=duration,
            success_rate=success_rate,
            avg_response_time=avg_connection_time,
            max_response_time=max(connection_times) if connection_times else 0,
            min_response_time=min(connection_times) if connection_times else 0,
            throughput=successful_connections / duration if duration > 0 else 0,
            error_count=failed_connections,
            total_requests=100,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def run_quick_load_test(self, concurrent_users: int, duration: int) -> Dict[str, Any]:
        """Run a quick load test for stress testing"""
        response_times = []
        successful_requests = 0
        total_requests = 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            # Calculate total requests
            total_requests = concurrent_users * duration
            
            for i in range(total_requests):
                future = executor.submit(
                    self.make_request,
                    'GET',
                    f"{self.config['api_base_url']}/health",
                    200
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    total_requests += 1
                    
                    if result['success']:
                        successful_requests += 1
                        response_times.append(result['response_time'])
                        
                except Exception:
                    pass
        
        test_duration = time.time() - start_time
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        throughput = successful_requests / test_duration if test_duration > 0 else 0
        
        return {
            'success_rate': success_rate,
            'throughput': throughput,
            'avg_response_time': statistics.mean(response_times) if response_times else 0
        }
    
    def make_request(self, method: str, url: str, expected_status: int) -> Dict[str, Any]:
        """Make a single HTTP request"""
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=self.config['request_timeout'])
            elif method.upper() == 'POST':
                response = requests.post(url, timeout=self.config['request_timeout'])
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                return {
                    'success': True,
                    'response_time': response_time,
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'Expected status {expected_status}, got {response.status_code}',
                    'response_time': response_time
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test a single connection"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.config['api_base_url']}/health", timeout=5)
            connection_time = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'time': connection_time,
                'status_code': response.status_code
            }
            
        except Exception as e:
            connection_time = time.time() - start_time
            return {
                'success': False,
                'time': connection_time,
                'error': str(e)
            }
    
    def monitor_system_resources(self, duration: int):
        """Monitor system resources during test"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_mb = memory.used / 1024 / 1024
                
                # Network I/O
                network = psutil.net_io_counters()
                
                self.system_metrics.append({
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_mb,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                })
                
            except Exception as e:
                self.logger.error(f"Error monitoring system resources: {str(e)}")
    
    def generate_performance_recommendations(self, success_rate: float, avg_response_time: float, 
                                          throughput: float, error_count: int) -> List[str]:
        """Generate performance recommendations based on test results"""
        recommendations = []
        
        # Success rate recommendations
        if success_rate < self.thresholds['min_success_rate']:
            recommendations.append(f"Success rate ({success_rate:.1f}%) is below threshold ({self.thresholds['min_success_rate']}%)")
            recommendations.append("Consider optimizing error handling and retry mechanisms")
        
        # Response time recommendations
        if avg_response_time > self.thresholds['max_response_time']:
            recommendations.append(f"Average response time ({avg_response_time:.3f}s) exceeds threshold ({self.thresholds['max_response_time']}s)")
            recommendations.append("Consider optimizing database queries and caching")
        
        # Throughput recommendations
        if throughput < self.thresholds['min_throughput']:
            recommendations.append(f"Throughput ({throughput:.2f} req/s) is below threshold ({self.thresholds['min_throughput']} req/s)")
            recommendations.append("Consider horizontal scaling or load balancing")
        
        # Error count recommendations
        if error_count > 0:
            recommendations.append(f"Detected {error_count} errors during testing")
            recommendations.append("Review error logs and improve error handling")
        
        # Positive feedback
        if success_rate >= 98 and avg_response_time < 1.0:
            recommendations.append("Excellent performance! System is performing well under load")
        
        return recommendations
    
    def generate_performance_report(self, results: Dict[str, PerformanceTestResult]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        total_tests = len(results)
        passed_tests = 0
        total_duration = 0
        overall_success_rate = 0
        overall_avg_response_time = 0
        
        # Calculate overall metrics
        for result in results.values():
            total_duration += result.duration
            overall_success_rate += result.success_rate
            overall_avg_response_time += result.avg_response_time
            
            if result.success_rate >= self.thresholds['min_success_rate']:
                passed_tests += 1
        
        if total_tests > 0:
            overall_success_rate /= total_tests
            overall_avg_response_time /= total_tests
        
        # Generate charts
        self.generate_performance_charts(results)
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'overall_success_rate': overall_success_rate,
                'overall_avg_response_time': overall_avg_response_time,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': results,
            'system_metrics': self.system_metrics,
            'recommendations': self.generate_overall_recommendations(results)
        }
        
        return report
    
    def generate_performance_charts(self, results: Dict[str, PerformanceTestResult]):
        """Generate performance charts"""
        try:
            # Response time comparison chart
            test_names = list(results.keys())
            avg_response_times = [results[name].avg_response_time for name in test_names]
            
            plt.figure(figsize=(12, 8))
            
            # Subplot 1: Response Times
            plt.subplot(2, 2, 1)
            plt.bar(test_names, avg_response_times)
            plt.title('Average Response Times')
            plt.ylabel('Response Time (seconds)')
            plt.xticks(rotation=45)
            
            # Subplot 2: Success Rates
            success_rates = [results[name].success_rate for name in test_names]
            plt.subplot(2, 2, 2)
            plt.bar(test_names, success_rates)
            plt.title('Success Rates')
            plt.ylabel('Success Rate (%)')
            plt.xticks(rotation=45)
            
            # Subplot 3: Throughput
            throughputs = [results[name].throughput for name in test_names]
            plt.subplot(2, 2, 3)
            plt.bar(test_names, throughputs)
            plt.title('Throughput')
            plt.ylabel('Requests per Second')
            plt.xticks(rotation=45)
            
            # Subplot 4: Error Counts
            error_counts = [results[name].error_count for name in test_names]
            plt.subplot(2, 2, 4)
            plt.bar(test_names, error_counts)
            plt.title('Error Counts')
            plt.ylabel('Error Count')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig('performance_test_results.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
    
    def generate_overall_recommendations(self, results: Dict[str, PerformanceTestResult]) -> List[str]:
        """Generate overall recommendations based on all test results"""
        recommendations = []
        
        # Analyze overall performance
        avg_success_rate = statistics.mean([r.success_rate for r in results.values()])
        avg_response_time = statistics.mean([r.avg_response_time for r in results.values()])
        total_errors = sum([r.error_count for r in results.values()])
        
        if avg_success_rate < 95:
            recommendations.append("Overall success rate is below 95%. Review system stability")
        
        if avg_response_time > 1.5:
            recommendations.append("Average response time is high. Consider performance optimizations")
        
        if total_errors > 0:
            recommendations.append(f"Total errors across all tests: {total_errors}. Review error handling")
        
        # Check for specific issues
        stress_test = results.get('Stress Test')
        if stress_test and stress_test.success_rate < 90:
            recommendations.append("System shows signs of stress under high load. Consider scaling")
        
        memory_test = results.get('Memory Leak Test')
        if memory_test:
            memory_increase = next((m.value for m in memory_test.metrics if m.metric_name == 'memory_increase'), 0)
            if memory_increase > 50:
                recommendations.append("Potential memory leak detected. Review memory management")
        
        return recommendations

def main():
    """Run the performance test suite"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run test suite
    test_suite = PerformanceTestSuite()
    report = test_suite.run_all_performance_tests()
    
    # Print report
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUITE REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"\nSummary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed Tests: {summary['passed_tests']}")
    print(f"  Failed Tests: {summary['failed_tests']}")
    print(f"  Overall Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"  Overall Avg Response Time: {summary['overall_avg_response_time']:.3f}s")
    print(f"  Total Duration: {summary['total_duration']:.2f}s")
    
    print(f"\nDetailed Results:")
    for test_name, result in report['detailed_results'].items():
        print(f"  {test_name}:")
        print(f"    Success Rate: {result.success_rate:.1f}%")
        print(f"    Avg Response Time: {result.avg_response_time:.3f}s")
        print(f"    Throughput: {result.throughput:.2f} req/s")
        print(f"    Errors: {result.error_count}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    print("\n" + "="*60)
    
    return report

if __name__ == "__main__":
    main()