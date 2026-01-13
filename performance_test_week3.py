#!/usr/bin/env python3
"""
Performance Testing for Week 3 - RAG-Based SOP Assistant
Measures TTFT (Time To First Token) and other performance metrics
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any
import asyncio
import yaml

def load_config():
    """Load configuration from YAML file"""
    with open("config.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def start_fastapi_server():
    """Start the FastAPI server in background"""
    import subprocess
    import sys
    import os

    print("🚀 Starting FastAPI server...")
    server_process = subprocess.Popen([
        sys.executable, "main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())

    # Wait for server to start
    time.sleep(3)

    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server started successfully")
            return server_process
        else:
            print("❌ Server health check failed")
            server_process.terminate()
            return None
    except:
        print("❌ Could not connect to server")
        server_process.terminate()
        return None

def measure_ttft_streaming(question: str) -> Dict[str, Any]:
    """Measure TTFT for streaming response"""
    start_time = time.time()

    try:
        response = requests.post(
            "http://localhost:8000/ask",
            json={"question": question, "session_id": "perf_test"},
            stream=True,
            timeout=30
        )

        ttft = None
        first_token_time = None
        total_tokens = 0
        complete_time = None

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    try:
                        event = json.loads(data)

                        if 'ttft' in event and ttft is None:
                            ttft = event['ttft']
                            first_token_time = time.time() - start_time

                        if 'token' in event:
                            total_tokens += 1

                        if event.get('complete', False):
                            complete_time = time.time() - start_time
                            break

                    except json.JSONDecodeError:
                        continue

        return {
            'question': question,
            'ttft': ttft,
            'first_token_time': first_token_time,
            'total_tokens': total_tokens,
            'total_time': complete_time,
            'success': True
        }

    except Exception as e:
        return {
            'question': question,
            'error': str(e),
            'success': False
        }

def run_performance_tests():
    """Run comprehensive performance tests"""
    config = load_config()

    print("🎯 Week 3 Performance Testing - RAG-Based SOP Assistant")
    print("=" * 60)

    # Test questions
    test_questions = [
        "What is the procedure for employee onboarding?",
        "How to handle customer complaints?",
        "What are the safety protocols in the workplace?",
        "Explain the leave policy for employees",
        "What is the IT support process?"
    ]

    # Start server
    server_process = start_fastapi_server()
    if not server_process:
        print("❌ Could not start FastAPI server. Aborting tests.")
        return

    try:
        print(f"\n📊 Testing {len(test_questions)} questions...")
        print(f"🎯 Target TTFT: < {config.get('target_ttft', 1.0)} seconds\n")

        results = []

        for i, question in enumerate(test_questions, 1):
            print(f"🔍 Test {i}/{len(test_questions)}: {question[:50]}...")

            result = measure_ttft_streaming(question)
            results.append(result)

            if result['success']:
                ttft = result.get('ttft', 0)
                status = "✅" if ttft < config.get('target_ttft', 1.0) else "❌"
                print(f"   {status} TTFT: {ttft:.3f}s")
                print(f"   📝 Tokens: {result.get('total_tokens', 0)}")
                print(f"   💰 Cost: ${result.get('cost', 0):.4f}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

            print()

        # Calculate statistics
        successful_results = [r for r in results if r['success']]
        ttft_values = [r['ttft'] for r in successful_results if r.get('ttft')]

        if ttft_values:
            print("📈 PERFORMANCE SUMMARY")
            print("=" * 30)
            print(f"✅ Successful tests: {len(successful_results)}/{len(test_questions)}")
            print(".3f")
            # Check target achievement
            target_ttft = config.get('target_ttft', 1.0)
            avg_ttft = statistics.mean(ttft_values)
            target_achieved = avg_ttft < target_ttft

            print(f"\n🎯 Target TTFT (< {target_ttft}s): {'✅ ACHIEVED' if target_achieved else '❌ NOT ACHIEVED'}")

            if not target_achieved:
                print("\n💡 OPTIMIZATION SUGGESTIONS:")
                print("- Reduce chunk_size in config.yaml")
                print("- Increase chunk_overlap for better context")
                print("- Optimize embedding model (try smaller model)")
                print("- Check OpenAI API latency")
                print("- Consider caching frequent queries")

        else:
            print("❌ No successful tests - check server logs")

    finally:
        # Cleanup
        print("\n🔄 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Performance testing completed")

if __name__ == "__main__":
    run_performance_tests()