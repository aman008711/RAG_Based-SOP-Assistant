#!/usr/bin/env python3
"""
Test Runner - Execute E2E and Stress Tests for RAG-Based SOP Assistant
"""

import subprocess
import sys
import time
import os

def print_banner(text: str):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def check_api_running():
    """Check if API is running"""
    import requests
    try:
        response = requests.get("http://localhost:8008/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print_banner("🧪 TESTING SUITE LAUNCHER")
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    if not check_api_running():
        print("❌ API is not running at http://localhost:8008")
        print("\n📝 To start the API, run in another terminal:")
        print("   python main.py")
        print("\n⏳ Waiting for API to become available...")
        
        for i in range(30):  # Wait up to 30 seconds
            print(f"   Attempt {i+1}/30...", end="\r")
            time.sleep(1)
            if check_api_running():
                print("✅ API is now running!                    ")
                break
        else:
            print("\n❌ API did not start in time")
            sys.exit(1)
    else:
        print("✅ API is running and responding\n")
    
    # Run E2E tests
    print_banner("📋 RUNNING END-TO-END TESTS")
    
    print("Starting E2E test suite...")
    print("This will test all endpoints and basic functionality.\n")
    
    result = subprocess.run(
        [sys.executable, "test_e2e.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)) or "."
    )
    
    if result.returncode != 0:
        print("\n⚠️  Some E2E tests failed. Review output above.")
    else:
        print("\n✅ All E2E tests passed!")
    
    # Confirm before stress testing
    print("\n" + "="*80)
    response = input("Run stress tests? (y/n): ").strip().lower()
    
    if response == 'y':
        print_banner("💪 RUNNING STRESS TESTS")
        
        print("Starting stress test suite...")
        print("This will test performance under load.\n")
        
        subprocess.run(
            [sys.executable, "test_stress.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)) or "."
        )
    
    print_banner("✅ TESTING COMPLETE")
    print("Review the output above for detailed results.")

if __name__ == "__main__":
    main()
