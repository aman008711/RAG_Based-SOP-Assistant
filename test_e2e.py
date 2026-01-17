#!/usr/bin/env python3
"""
End-to-End Testing Suite for RAG-Based SOP Assistant
Tests all endpoints and core functionality
"""

import requests
import time
import json
from typing import Dict, Any, List
import sys

# Configuration
API_BASE_URL = "http://localhost:8008"
TEST_RESULTS = []

class TestResult:
    def __init__(self, test_name: str, status: str, message: str, duration: float = 0):
        self.test_name = test_name
        self.status = status
        self.message = message
        self.duration = duration
        self.timestamp = time.time()

    def __str__(self):
        emoji = "✅" if self.status == "PASS" else "❌"
        return f"{emoji} {self.test_name}: {self.message} ({self.duration:.3f}s)"

def print_header(text: str):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_test(result: TestResult):
    print(f"  {result}")
    TEST_RESULTS.append(result)

def test_api_reachability():
    """Test 1: Basic API Reachability"""
    print_header("TEST 1: API REACHABILITY")
    
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print_test(TestResult("API Reachability", "PASS", 
                f"API responding. Version: {data.get('version', 'unknown')}", duration))
            return True
        else:
            print_test(TestResult("API Reachability", "FAIL", 
                f"Unexpected status code: {response.status_code}", duration))
            return False
    except requests.exceptions.ConnectionError:
        print_test(TestResult("API Reachability", "FAIL", 
            f"Cannot connect to {API_BASE_URL}. Is the API running?", 0))
        return False
    except Exception as e:
        print_test(TestResult("API Reachability", "FAIL", str(e), 0))
        return False

def test_health_endpoint():
    """Test 2: Health Check Endpoint"""
    print_header("TEST 2: HEALTH CHECK ENDPOINT")
    
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "timestamp", "vectorstore_loaded"]
            if all(field in data for field in required_fields):
                print_test(TestResult("Health Check", "PASS", 
                    f"Status: {data['status']}, Vectorstore: {data['vectorstore_loaded']}", duration))
                return True
            else:
                print_test(TestResult("Health Check", "FAIL", 
                    f"Missing fields. Got: {list(data.keys())}", duration))
                return False
        else:
            print_test(TestResult("Health Check", "FAIL", 
                f"Status code: {response.status_code}", duration))
            return False
    except Exception as e:
        print_test(TestResult("Health Check", "FAIL", str(e), 0))
        return False

def test_query_post_endpoint():
    """Test 3: POST /ask Endpoint"""
    print_header("TEST 3: POST /ASK ENDPOINT (STREAMING)")
    
    try:
        start = time.time()
        payload = {
            "question": "What is the main purpose of this document?",
            "session_id": "test_session_1"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json=payload,
            timeout=30,
            stream=True
        )
        duration = time.time() - start
        
        if response.status_code == 200:
            # Collect streaming data
            chunks = []
            try:
                for line in response.iter_lines():
                    if line:
                        chunks.append(line)
                        if len(chunks) >= 5:  # Get first few chunks
                            break
            except:
                pass
            
            if chunks:
                print_test(TestResult("POST /ask", "PASS", 
                    f"Streaming response received ({len(chunks)} chunks)", duration))
                return True
            else:
                print_test(TestResult("POST /ask", "FAIL", 
                    "No streaming data received", duration))
                return False
        else:
            print_test(TestResult("POST /ask", "FAIL", 
                f"Status code: {response.status_code}", duration))
            return False
    except requests.exceptions.Timeout:
        print_test(TestResult("POST /ask", "FAIL", "Request timeout", 30))
        return False
    except Exception as e:
        print_test(TestResult("POST /ask", "FAIL", str(e), 0))
        return False

def test_query_get_endpoint():
    """Test 4: GET /ask Endpoint"""
    print_header("TEST 4: GET /ASK ENDPOINT (STREAMING)")
    
    try:
        start = time.time()
        params = {
            "question": "What are the key points?",
            "session_id": "test_session_2"
        }
        
        response = requests.get(
            f"{API_BASE_URL}/ask",
            params=params,
            timeout=30,
            stream=True
        )
        duration = time.time() - start
        
        if response.status_code == 200:
            chunks = []
            try:
                for line in response.iter_lines():
                    if line:
                        chunks.append(line)
                        if len(chunks) >= 5:
                            break
            except:
                pass
            
            if chunks:
                print_test(TestResult("GET /ask", "PASS", 
                    f"Streaming response received ({len(chunks)} chunks)", duration))
                return True
            else:
                print_test(TestResult("GET /ask", "FAIL", 
                    "No streaming data received", duration))
                return False
        else:
            print_test(TestResult("GET /ask", "FAIL", 
                f"Status code: {response.status_code}", duration))
            return False
    except requests.exceptions.Timeout:
        print_test(TestResult("GET /ask", "FAIL", "Request timeout", 30))
        return False
    except Exception as e:
        print_test(TestResult("GET /ask", "FAIL", str(e), 0))
        return False

def test_web_interface():
    """Test 5: Web Interface"""
    print_header("TEST 5: WEB INTERFACE")
    
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/web", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            if "html" in response.text.lower() or response.headers.get("content-type", "").lower().startswith("text/html"):
                print_test(TestResult("Web Interface", "PASS", 
                    f"HTML content served ({len(response.text)} bytes)", duration))
                return True
            else:
                print_test(TestResult("Web Interface", "FAIL", 
                    "Response is not HTML", duration))
                return False
        else:
            print_test(TestResult("Web Interface", "FAIL", 
                f"Status code: {response.status_code}", duration))
            return False
    except Exception as e:
        print_test(TestResult("Web Interface", "FAIL", str(e), 0))
        return False

def test_error_handling_invalid_request():
    """Test 6: Error Handling - Invalid Request"""
    print_header("TEST 6: ERROR HANDLING - INVALID REQUEST")
    
    try:
        start = time.time()
        # Send invalid JSON
        response = requests.post(
            f"{API_BASE_URL}/ask",
            data="invalid json",
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        duration = time.time() - start
        
        if response.status_code >= 400:
            print_test(TestResult("Invalid Request Handling", "PASS", 
                f"Properly rejected invalid request (HTTP {response.status_code})", duration))
            return True
        else:
            print_test(TestResult("Invalid Request Handling", "FAIL", 
                f"Should reject invalid JSON, got HTTP {response.status_code}", duration))
            return False
    except Exception as e:
        print_test(TestResult("Invalid Request Handling", "FAIL", str(e), 0))
        return False

def test_concurrent_requests():
    """Test 7: Concurrent Request Handling"""
    print_header("TEST 7: CONCURRENT REQUEST HANDLING")
    
    import concurrent.futures
    
    def make_health_request():
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    try:
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_health_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start
        success_count = sum(results)
        
        if success_count >= 4:  # At least 80% success
            print_test(TestResult("Concurrent Requests", "PASS", 
                f"{success_count}/5 concurrent requests successful", duration))
            return True
        else:
            print_test(TestResult("Concurrent Requests", "FAIL", 
                f"Only {success_count}/5 concurrent requests succeeded", duration))
            return False
    except Exception as e:
        print_test(TestResult("Concurrent Requests", "FAIL", str(e), 0))
        return False

def test_response_format():
    """Test 8: Response Format Validation"""
    print_header("TEST 8: RESPONSE FORMAT VALIDATION")
    
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            required_keys = ["message", "version", "endpoints", "features"]
            
            if all(key in data for key in required_keys):
                print_test(TestResult("Response Format", "PASS", 
                    f"All required fields present in response", duration))
                return True
            else:
                missing = [k for k in required_keys if k not in data]
                print_test(TestResult("Response Format", "FAIL", 
                    f"Missing fields: {missing}", duration))
                return False
        else:
            print_test(TestResult("Response Format", "FAIL", 
                f"Status code: {response.status_code}", duration))
            return False
    except json.JSONDecodeError:
        print_test(TestResult("Response Format", "FAIL", 
            "Response is not valid JSON", duration))
        return False
    except Exception as e:
        print_test(TestResult("Response Format", "FAIL", str(e), 0))
        return False

def test_rate_limiting():
    """Test 9: Rate Limiting"""
    print_header("TEST 9: RATE LIMITING")
    
    try:
        # Try to exceed health endpoint limit (30/minute)
        # We'll send more than reasonable in quick succession
        start = time.time()
        responses = []
        
        print("  Sending 15 rapid health check requests...")
        for i in range(15):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=2)
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            except:
                responses.append(0)
        
        duration = time.time() - start
        
        # Check if we got any 429 (Too Many Requests)
        has_429 = 429 in responses
        success_count = responses.count(200)
        
        if has_429:
            print_test(TestResult("Rate Limiting", "PASS", 
                f"Rate limiting enforced (429 received). {success_count}/15 successful", duration))
            return True
        else:
            print_test(TestResult("Rate Limiting", "FAIL", 
                f"No rate limiting detected (no 429 responses)", duration))
            return False
    except Exception as e:
        print_test(TestResult("Rate Limiting", "FAIL", str(e), 0))
        return False

def run_all_e2e_tests():
    """Run all end-to-end tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "  END-TO-END TESTING SUITE - RAG-Based SOP Assistant".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    print("\n⏳ Starting tests... Please ensure the API is running at", API_BASE_URL)
    
    # Run tests in sequence
    tests = [
        test_api_reachability,
        test_health_endpoint,
        test_response_format,
        test_query_post_endpoint,
        test_query_get_endpoint,
        test_web_interface,
        test_error_handling_invalid_request,
        test_concurrent_requests,
        test_rate_limiting,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for r in TEST_RESULTS if r.status == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r.status == "FAIL")
    total = len(TEST_RESULTS)
    
    print(f"\n  Total Tests: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Success Rate: {(passed/total*100):.1f}%\n")
    
    if failed > 0:
        print("  Failed Tests:")
        for result in TEST_RESULTS:
            if result.status == "FAIL":
                print(f"    - {result.test_name}: {result.message}")
    
    print("\n" + "="*70 + "\n")
    
    return passed, failed, total

if __name__ == "__main__":
    passed, failed, total = run_all_e2e_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
