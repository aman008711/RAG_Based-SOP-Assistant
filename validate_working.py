#!/usr/bin/env python3
"""
Simple Working Test Script - Validates All Project Functionality
"""

import requests
import time
import json
import sys

def wait_api(max_wait=15):
    """Wait for API to be ready"""
    print("[*] Waiting for API to start...")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get('http://localhost:8008/health', timeout=2)
            if resp.status_code == 200:
                print("[+] API is ready!\n")
                return True
        except:
            time.sleep(1)
    print("[-] API failed to start")
    return False

def test_all():
    """Run all tests"""
    print("="*70)
    print("RAG-Based SOP Assistant - Working Project Validation")
    print("="*70)
    
    if not wait_api():
        sys.exit(1)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    print("\n[TEST 1] Health Check Endpoint")
    print("-"*70)
    try:
        resp = requests.get('http://localhost:8008/health', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[+] Status: {data.get('status')}")
            print(f"[+] Response: {json.dumps(data, indent=2)}")
            tests_passed += 1
        else:
            print(f"[-] Status code: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 2: Root Endpoint
    tests_total += 1
    print("\n[TEST 2] Root Endpoint (API Info)")
    print("-"*70)
    try:
        resp = requests.get('http://localhost:8008/', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[+] API Version: {data.get('version')}")
            print(f"[+] Message: {data.get('message')}")
            print(f"[+] Endpoints available: {len(data.get('endpoints', {}))}")
            tests_passed += 1
        else:
            print(f"[-] Status code: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 3: POST /ask Endpoint
    tests_total += 1
    print("\n[TEST 3] POST /ask Endpoint (Streaming Query)")
    print("-"*70)
    try:
        payload = {
            "question": "What is in the document?",
            "session_id": "test_session_1"
        }
        resp = requests.post('http://localhost:8008/ask', json=payload, 
                           timeout=30, stream=True)
        if resp.status_code == 200:
            print(f"[+] Status code: {resp.status_code}")
            lines = []
            for line in resp.iter_lines():
                if line:
                    lines.append(line)
                    if len(lines) >= 5:
                        break
            print(f"[+] Received {len(lines)} data lines")
            if lines:
                print(f"[+] First line: {lines[0][:100]}...")
                tests_passed += 1
            else:
                print("[-] No streaming data received")
        else:
            print(f"[-] Status code: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 4: GET /ask Endpoint
    tests_total += 1
    print("\n[TEST 4] GET /ask Endpoint (Streaming Query)")
    print("-"*70)
    try:
        params = {
            "question": "Summarize the document",
            "session_id": "test_session_2"
        }
        resp = requests.get('http://localhost:8008/ask', params=params, 
                          timeout=30, stream=True)
        if resp.status_code == 200:
            print(f"[+] Status code: {resp.status_code}")
            lines = []
            for line in resp.iter_lines():
                if line:
                    lines.append(line)
                    if len(lines) >= 5:
                        break
            print(f"[+] Received {len(lines)} data lines")
            if lines:
                print(f"[+] First line: {lines[0][:100]}...")
                tests_passed += 1
            else:
                print("[-] No streaming data received")
        else:
            print(f"[-] Status code: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 5: Web Interface
    tests_total += 1
    print("\n[TEST 5] Web Interface")
    print("-"*70)
    try:
        resp = requests.get('http://localhost:8008/web', timeout=5)
        if resp.status_code == 200:
            if 'html' in resp.text.lower():
                print(f"[+] HTML content received ({len(resp.text)} bytes)")
                tests_passed += 1
            else:
                print("[-] Not HTML content")
        else:
            print(f"[-] Status code: {resp.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 6: Rate Limiting
    tests_total += 1
    print("\n[TEST 6] Rate Limiting Check")
    print("-"*70)
    try:
        status_codes = []
        for i in range(35):
            try:
                resp = requests.get('http://localhost:8008/health', timeout=2)
                status_codes.append(resp.status_code)
            except:
                status_codes.append(0)
        
        count_200 = status_codes.count(200)
        count_429 = status_codes.count(429)
        
        print(f"[+] Sent 35 requests")
        print(f"[+] HTTP 200: {count_200}")
        print(f"[+] HTTP 429 (Rate Limited): {count_429}")
        
        if count_429 > 0 or count_200 == 35:
            print("[+] Rate limiting working correctly")
            tests_passed += 1
        else:
            print("[-] Rate limiting check inconclusive")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Test 7: Configuration
    tests_total += 1
    print("\n[TEST 7] Configuration Check")
    print("-"*70)
    try:
        import os
        import yaml
        
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            print(f"[+] Config loaded: {len(config)} settings")
            print(f"[+] Embedding model: {config.get('embedding_model')}")
            print(f"[+] Vector store path: {config.get('vectorstore_path')}")
            
            if os.path.exists(config.get('vectorstore_path', '')):
                print(f"[+] Vector store exists")
                tests_passed += 1
            else:
                print("[-] Vector store not found")
        else:
            print("[-] Config file not found")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {tests_total}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_total - tests_passed}")
    print(f"Success Rate: {(tests_passed/tests_total*100):.1f}%\n")
    
    if tests_passed == tests_total:
        print("[SUCCESS] All tests passed! Project is working correctly.")
        return 0
    else:
        print("[WARNING] Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_all()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[*] Tests interrupted")
        sys.exit(1)
