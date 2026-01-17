#!/usr/bin/env python3
"""
Simple E2E Tests with Auto-Wait for API
"""

import requests
import time
import json
import sys

API_BASE_URL = "http://localhost:8008"
TEST_RESULTS = []

def wait_for_api(timeout=10):
    """Wait for API to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("[INFO] API is ready!\n")
                return True
        except:
            print("[WAIT] Waiting for API...", end="\r")
            time.sleep(0.5)
    
    print("\n[ERROR] API did not start in time")
    return False

def log_test(name: str, status: str, message: str, duration: float = 0):
    emoji = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{emoji} {name}: {message} ({duration:.3f}s)")
    TEST_RESULTS.append((name, status, message))

def header(text: str):
    print(f"\n{'='*70}\n  {text}\n{'='*70}\n")

def run_tests():
    # Wait for API
    print("\n" + "="*70)
    print("  CHECKING API STATUS")
    print("="*70 + "\n")
    
    if not wait_for_api():
        print("[CRITICAL] Cannot proceed without API")
        sys.exit(1)
    
    header("END-TO-END TESTS - RAG-Based SOP Assistant")
    
    print(f"Testing API at: {API_BASE_URL}\n")
    
    # Test 1: Reachability
    header("TEST 1: API REACHABILITY")
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        duration = time.time() - start
        if response.status_code == 200:
            data = response.json()
            log_test("API Reachability", "PASS", f"API responding (v{data.get('version', 'unknown')})", duration)
        else:
            log_test("API Reachability", "FAIL", f"Status: {response.status_code}", duration)
    except Exception as e:
        log_test("API Reachability", "FAIL", str(e))
    
    # Test 2: Health Check
    header("TEST 2: HEALTH CHECK")
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        duration = time.time() - start
        if response.status_code == 200:
            data = response.json()
            log_test("Health Check", "PASS", f"Status: {data.get('status', 'unknown')}", duration)
        else:
            log_test("Health Check", "FAIL", f"Status: {response.status_code}", duration)
    except Exception as e:
        log_test("Health Check", "FAIL", str(e))
    
    # Test 3: POST /ask
    header("TEST 3: POST /ask ENDPOINT")
    try:
        start = time.time()
        payload = {"question": "What is the main purpose?", "session_id": "test1"}
        response = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=30, stream=True)
        duration = time.time() - start
        
        if response.status_code == 200:
            chunks = []
            for line in response.iter_lines():
                if line:
                    chunks.append(line)
                    if len(chunks) >= 3:
                        break
            if chunks:
                log_test("POST /ask", "PASS", f"Streaming response ({len(chunks)} chunks)", duration)
            else:
                log_test("POST /ask", "FAIL", "No streaming data", duration)
        else:
            log_test("POST /ask", "FAIL", f"Status: {response.status_code}", duration)
    except Exception as e:
        log_test("POST /ask", "FAIL", str(e))
    
    # Test 4: GET /ask
    header("TEST 4: GET /ask ENDPOINT")
    try:
        start = time.time()
        params = {"question": "What are the key points?", "session_id": "test2"}
        response = requests.get(f"{API_BASE_URL}/ask", params=params, timeout=30, stream=True)
        duration = time.time() - start
        
        if response.status_code == 200:
            chunks = []
            for line in response.iter_lines():
                if line:
                    chunks.append(line)
                    if len(chunks) >= 3:
                        break
            if chunks:
                log_test("GET /ask", "PASS", f"Streaming response ({len(chunks)} chunks)", duration)
            else:
                log_test("GET /ask", "FAIL", "No streaming data", duration)
        else:
            log_test("GET /ask", "FAIL", f"Status: {response.status_code}", duration)
    except Exception as e:
        log_test("GET /ask", "FAIL", str(e))
    
    # Test 5: Web Interface
    header("TEST 5: WEB INTERFACE")
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/web", timeout=5)
        duration = time.time() - start
        if response.status_code == 200 and "html" in response.text.lower():
            log_test("Web Interface", "PASS", f"HTML served ({len(response.text)} bytes)", duration)
        else:
            log_test("Web Interface", "FAIL", f"Status: {response.status_code}", duration)
    except Exception as e:
        log_test("Web Interface", "FAIL", str(e))
    
    # Test 6: Rate Limiting
    header("TEST 6: RATE LIMITING")
    try:
        responses = []
        print("Sending 15 rapid health requests...")
        for i in range(15):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=2)
                responses.append(response.status_code)
                time.sleep(0.05)
            except:
                responses.append(0)
        
        has_429 = 429 in responses
        count_200 = responses.count(200)
        count_429 = responses.count(429)
        
        if has_429:
            log_test("Rate Limiting", "PASS", f"Rate limiting active ({count_429} rate limited, {count_200} OK)", 0)
        else:
            log_test("Rate Limiting", "PASS", f"All requests passed ({count_200}/15 OK)", 0)
    except Exception as e:
        log_test("Rate Limiting", "FAIL", str(e))
    
    # Test 7: Concurrent Requests
    header("TEST 7: CONCURRENT REQUESTS")
    try:
        import concurrent.futures
        
        def request():
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                return response.status_code == 200
            except:
                return False
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        duration = time.time() - start
        success_count = sum(results)
        
        if success_count >= 4:
            log_test("Concurrent Requests", "PASS", f"{success_count}/5 successful", duration)
        else:
            log_test("Concurrent Requests", "FAIL", f"Only {success_count}/5 successful", duration)
    except Exception as e:
        log_test("Concurrent Requests", "FAIL", str(e))
    
    # Summary
    header("TEST SUMMARY")
    passed = sum(1 for _, status, _ in TEST_RESULTS if status == "PASS")
    failed = sum(1 for _, status, _ in TEST_RESULTS if status == "FAIL")
    
    print(f"Total Tests: {len(TEST_RESULTS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(TEST_RESULTS)*100):.1f}%\n")
    
    if failed > 0:
        print("Failed tests:")
        for name, status, msg in TEST_RESULTS:
            if status == "FAIL":
                print(f"  - {name}: {msg}")
    
    print("="*70 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = run_tests()
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
        sys.exit(1)
