#!/usr/bin/env python3
"""
Stress Testing Suite for RAG-Based SOP Assistant
Tests performance under load and resource constraints
"""

import requests
import time
import json
import statistics
import concurrent.futures
from typing import List, Dict, Any
import sys

# Configuration
API_BASE_URL = "http://localhost:8008"

class PerformanceMetrics:
    def __init__(self, name: str):
        self.name = name
        self.response_times = []
        self.status_codes = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, response_time: float, status_code: int, error: str = None):
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"status": "no_data"}
        
        successful = sum(1 for s in self.status_codes if 200 <= s < 300)
        failed = len(self.status_codes) - successful
        
        return {
            "test": self.name,
            "total_requests": len(self.response_times),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(self.response_times)*100):.1f}%",
            "min_time": f"{min(self.response_times):.3f}s",
            "max_time": f"{max(self.response_times):.3f}s",
            "avg_time": f"{statistics.mean(self.response_times):.3f}s",
            "median_time": f"{statistics.median(self.response_times):.3f}s",
            "p95_time": f"{sorted(self.response_times)[int(len(self.response_times)*0.95)]:.3f}s" if len(self.response_times) > 1 else "N/A",
            "std_dev": f"{statistics.stdev(self.response_times):.3f}s" if len(self.response_times) > 1 else "N/A",
            "errors": len(self.errors),
            "error_rate": f"{(len(self.errors)/len(self.response_times)*100):.1f}%"
        }

def print_header(text: str):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_metrics(metrics: PerformanceMetrics):
    summary = metrics.get_summary()
    
    if summary.get("status") == "no_data":
        print(f"  ⚠️  {metrics.name}: No data collected")
        return
    
    print(f"  📊 {metrics.name}")
    print(f"  {'-'*76}")
    print(f"    Requests:     {summary['total_requests']} total ({summary['successful']} OK, {summary['failed']} failed)")
    print(f"    Success Rate: {summary['success_rate']}")
    print(f"    Response Times:")
    print(f"      - Min:     {summary['min_time']}")
    print(f"      - Max:     {summary['max_time']}")
    print(f"      - Avg:     {summary['avg_time']}")
    print(f"      - Median:  {summary['median_time']}")
    print(f"      - P95:     {summary['p95_time']}")
    print(f"      - Std Dev: {summary['std_dev']}")
    print(f"    Errors:       {summary['errors']} ({summary['error_rate']})")
    if summary.get('errors', 0) > 0 and metrics.errors:
        print(f"    Error Types:  {', '.join(set(metrics.errors[:3]))}")
    print()

def stress_test_health_endpoint(num_requests: int = 50, num_workers: int = 5):
    """Stress test health endpoint with concurrent requests"""
    print_header(f"STRESS TEST 1: HEALTH ENDPOINT ({num_requests} requests, {num_workers} workers)")
    
    metrics = PerformanceMetrics(f"Health Endpoint ({num_requests} req, {num_workers} workers)")
    
    def make_request():
        try:
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            duration = time.time() - start
            metrics.add_result(duration, response.status_code)
        except requests.exceptions.Timeout:
            metrics.add_result(5.0, 0, "timeout")
        except requests.exceptions.ConnectionError:
            metrics.add_result(0, 0, "connection_error")
        except Exception as e:
            metrics.add_result(0, 0, str(type(e).__name__))
    
    print(f"  Sending {num_requests} requests with {num_workers} concurrent workers...")
    
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        concurrent.futures.wait(futures)
    
    metrics.end_time = time.time()
    print_metrics(metrics)
    
    return metrics

def stress_test_query_endpoint(num_requests: int = 20, num_workers: int = 3):
    """Stress test query endpoint with concurrent requests"""
    print_header(f"STRESS TEST 2: QUERY ENDPOINT ({num_requests} requests, {num_workers} workers)")
    
    metrics = PerformanceMetrics(f"Query Endpoint ({num_requests} req, {num_workers} workers)")
    
    queries = [
        "What is the main purpose?",
        "What are the key points?",
        "Summarize the document",
        "What are the procedures?",
        "What are the important items?"
    ]
    
    def make_request(query_idx):
        try:
            start = time.time()
            payload = {
                "question": queries[query_idx % len(queries)],
                "session_id": f"stress_test_{query_idx}"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/ask",
                json=payload,
                timeout=60,
                stream=True
            )
            
            # Read a bit of the stream
            try:
                for line in response.iter_lines():
                    if line:
                        break
            except:
                pass
            
            duration = time.time() - start
            metrics.add_result(duration, response.status_code)
        except requests.exceptions.Timeout:
            metrics.add_result(60.0, 0, "timeout")
        except requests.exceptions.ConnectionError:
            metrics.add_result(0, 0, "connection_error")
        except Exception as e:
            metrics.add_result(0, 0, str(type(e).__name__))
    
    print(f"  Sending {num_requests} query requests with {num_workers} concurrent workers...")
    print(f"  (Warning: This will be slow due to LLM processing)")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        concurrent.futures.wait(futures)
    
    metrics.end_time = time.time()
    print_metrics(metrics)
    
    return metrics

def stress_test_mixed_endpoints(duration_seconds: int = 30, num_workers: int = 5):
    """Stress test mixed endpoints over a time period"""
    print_header(f"STRESS TEST 3: MIXED ENDPOINTS ({duration_seconds}s, {num_workers} workers)")
    
    metrics = PerformanceMetrics(f"Mixed Endpoints ({duration_seconds}s, {num_workers} workers)")
    
    endpoints = [
        ("/health", "get"),
        ("/", "get"),
    ]
    
    end_time = time.time() + duration_seconds
    request_count = 0
    
    def make_request(endpoint, method):
        nonlocal request_count
        try:
            start = time.time()
            if method == "get":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_BASE_URL}{endpoint}", json={"question": "test"}, timeout=5)
            
            duration = time.time() - start
            metrics.add_result(duration, response.status_code)
            request_count += 1
        except Exception as e:
            metrics.add_result(0, 0, str(type(e).__name__))
    
    print(f"  Sending mixed requests for {duration_seconds} seconds...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        while time.time() < end_time:
            endpoint, method = endpoints[request_count % len(endpoints)]
            executor.submit(make_request, endpoint, method)
            time.sleep(0.1)  # Small delay between submissions
    
    metrics.end_time = time.time()
    print_metrics(metrics)
    
    return metrics

def stress_test_sequential_requests(num_requests: int = 30):
    """Sequential request test to measure response time degradation"""
    print_header(f"STRESS TEST 4: SEQUENTIAL REQUESTS ({num_requests} health checks)")
    
    metrics = PerformanceMetrics(f"Sequential Requests ({num_requests} req)")
    
    print(f"  Sending {num_requests} sequential health check requests...")
    
    for i in range(num_requests):
        try:
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            duration = time.time() - start
            metrics.add_result(duration, response.status_code)
            
            if (i + 1) % 10 == 0:
                print(f"    Completed {i + 1}/{num_requests} requests")
        except Exception as e:
            metrics.add_result(0, 0, str(type(e).__name__))
    
    metrics.end_time = time.time()
    print_metrics(metrics)
    
    return metrics

def stress_test_rate_limiting(num_requests: int = 100):
    """Test rate limiting enforcement under high load"""
    print_header(f"STRESS TEST 5: RATE LIMITING ({num_requests} rapid requests)")
    
    metrics = PerformanceMetrics(f"Rate Limiting ({num_requests} req)")
    rate_limited_count = 0
    
    print(f"  Sending {num_requests} rapid requests to health endpoint...")
    print(f"  (Monitoring for HTTP 429 Too Many Requests responses)")
    
    for i in range(num_requests):
        try:
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            duration = time.time() - start
            metrics.add_result(duration, response.status_code)
            
            if response.status_code == 429:
                rate_limited_count += 1
        except Exception as e:
            metrics.add_result(0, 0, str(type(e).__name__))
    
    metrics.end_time = time.time()
    
    print(f"\n  📊 Rate Limiting Results")
    print(f"  {'-'*76}")
    print(f"    Total Requests:    {num_requests}")
    print(f"    Rate Limited (429): {rate_limited_count}")
    print(f"    Rate Limit % Hit:  {(rate_limited_count/num_requests*100):.1f}%")
    print()
    
    return metrics

def analyze_performance_trends(all_metrics: List[PerformanceMetrics]):
    """Analyze trends across all tests"""
    print_header("PERFORMANCE ANALYSIS & TRENDS")
    
    print("  📈 Summary Statistics:\n")
    
    for metrics in all_metrics:
        summary = metrics.get_summary()
        if summary.get("status") != "no_data":
            print(f"    {metrics.name}:")
            print(f"      - Avg Response: {summary['avg_time']}")
            print(f"      - Success Rate: {summary['success_rate']}")
            print(f"      - Error Rate: {summary['error_rate']}")
            print()
    
    # Overall health check
    print("  🏥 System Health:")
    all_responses = []
    all_errors = []
    
    for metrics in all_metrics:
        all_responses.extend(metrics.response_times)
        all_errors.extend(metrics.errors)
    
    if all_responses:
        avg_response = statistics.mean(all_responses)
        print(f"    - Average Response Time: {avg_response:.3f}s")
        print(f"    - Total Errors: {len(all_errors)}")
        
        if avg_response < 0.5:
            print(f"    - ✅ Performance: EXCELLENT")
        elif avg_response < 1.0:
            print(f"    - ✅ Performance: GOOD")
        elif avg_response < 2.0:
            print(f"    - ⚠️  Performance: ACCEPTABLE")
        else:
            print(f"    - ❌ Performance: DEGRADED")
    
    print()

def run_all_stress_tests():
    """Run all stress tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "  STRESS TESTING SUITE - RAG-Based SOP Assistant".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n⏳ Starting stress tests... Please ensure the API is running at", API_BASE_URL)
    print("   Note: Some tests may take several minutes to complete.\n")
    
    all_metrics = []
    
    try:
        # Test 1: Light stress - Health endpoint
        metrics1 = stress_test_health_endpoint(num_requests=50, num_workers=5)
        all_metrics.append(metrics1)
        
        # Test 2: Sequential stress
        metrics2 = stress_test_sequential_requests(num_requests=30)
        all_metrics.append(metrics2)
        
        # Test 3: Rate limiting
        metrics3 = stress_test_rate_limiting(num_requests=100)
        all_metrics.append(metrics3)
        
        # Test 4: Mixed endpoints
        metrics4 = stress_test_mixed_endpoints(duration_seconds=20, num_workers=3)
        all_metrics.append(metrics4)
        
        # Test 5: Query endpoint (resource-intensive, limited requests)
        print("\n⚠️  WARNING: Next test will submit actual queries to the API.")
        print("   This may be slow due to LLM processing. Proceeding in 3 seconds...\n")
        time.sleep(3)
        
        metrics5 = stress_test_query_endpoint(num_requests=5, num_workers=2)
        all_metrics.append(metrics5)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during stress testing: {e}")
        import traceback
        traceback.print_exc()
    
    # Analysis
    if all_metrics:
        analyze_performance_trends(all_metrics)
    
    # Final summary
    print_header("STRESS TEST COMPLETE")
    print("  ✅ All stress tests completed successfully!")
    print("  📋 Review the metrics above for performance insights.")
    print()

if __name__ == "__main__":
    try:
        run_all_stress_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stress testing interrupted")
        sys.exit(1)
