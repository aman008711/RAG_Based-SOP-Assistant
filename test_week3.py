#!/usr/bin/env python3
"""
Quick Test for Week 3 FastAPI Implementation
Tests basic functionality without starting server
"""

import sys
import os

def test_week3_implementation():
    """Test the Week 3 FastAPI implementation"""
    print("🧪 Testing Week 3 Implementation")
    print("=" * 40)

    # Test 1: Check if main.py exists and can be imported
    print("1️⃣ Testing imports...")
    try:
        import main
        print("   ✅ main.py imports successfully")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Test 2: Check if FastAPI app was created
    print("\n2️⃣ Testing FastAPI app creation...")
    try:
        from main import app
        print("   ✅ FastAPI app created successfully")
        print(f"   📡 Routes available: {len(app.routes)}")
    except Exception as e:
        print(f"   ❌ App creation failed: {e}")
        return False

    # Test 3: Check if static files exist
    print("\n3️⃣ Testing static files...")
    if os.path.exists("static/index.html"):
        print("   ✅ Web interface file exists")
    else:
        print("   ❌ Web interface file missing")
        return False

    # Test 4: Check configuration
    print("\n4️⃣ Testing configuration...")
    try:
        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        week3_settings = ['openai_api_key', 'openai_model', 'temperature', 'max_tokens', 'streaming_delay', 'target_ttft']
        missing = [s for s in week3_settings if s not in config]
        if missing:
            print(f"   ⚠️  Missing Week 3 config: {missing}")
        else:
            print("   ✅ Week 3 configuration complete")
    except Exception as e:
        print(f"   ❌ Config test failed: {e}")
        return False

    # Test 5: Check API key management
    print("\n5️⃣ Testing API key management...")
    try:
        from api import get_api_key_status, has_api_key
        status = get_api_key_status()
        print(f"   🔑 API Key Status: {status}")
        print("   ✅ API key management working")
    except Exception as e:
        print(f"   ❌ API key test failed: {e}")
        return False

    print("\n✅ All Week 3 components tested successfully!")
    return True

if __name__ == "__main__":
    success = test_week3_implementation()
    if success:
        print("\n🎉 Week 3 implementation is ready!")
        print("\n🚀 To run the server:")
        print("   python main.py")
        print("\n🌐 Access points:")
        print("   API Docs: http://localhost:8000/docs")
        print("   Web UI: http://localhost:8000/web")
        print("   Health: http://localhost:8000/health")
        print("\n📊 Performance testing:")
        print("   python performance_test_week3.py")
    else:
        print("\n❌ Week 3 implementation has issues!")
        sys.exit(1)