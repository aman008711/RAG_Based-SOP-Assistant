#!/usr/bin/env python3
"""Comprehensive health check for RAG-Based SOP Assistant"""

import sys
import os
sys.path.insert(0, os.getcwd())

print('🧪 COMPREHENSIVE PROJECT HEALTH CHECK')
print('=' * 60)

# Test 1: Core imports
print('\n1️⃣ Testing core module imports...')
try:
    import yaml
    import fastapi
    import langchain_community
    import faiss
    import streamlit
    print('   ✅ All core dependencies available')
except ImportError as e:
    print(f'   ❌ Missing dependency: {e}')

# Test 2: Config loading
print('\n2️⃣ Testing config loading...')
try:
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print(f'   ✅ Config loaded: {len(config)} settings found')
except Exception as e:
    print(f'   ❌ Config error: {e}')

# Test 3: Vector store check
print('\n3️⃣ Checking vector store...')
try:
    import os
    vectorstore_path = 'vectorstore/faiss_index'
    if os.path.exists(vectorstore_path):
        files = os.listdir(vectorstore_path)
        print(f'   ✅ Vector store ready: {len(files)} files found')
    else:
        print(f'   ⚠️  Vector store not found at {vectorstore_path}')
except Exception as e:
    print(f'   ❌ Vector store error: {e}')

# Test 4: API files
print('\n4️⃣ Testing API modules...')
try:
    import api
    import api_backend
    print('   ✅ API modules loaded successfully')
except Exception as e:
    print(f'   ❌ API import error: {e}')

# Test 5: Main modules
print('\n5️⃣ Testing main application modules...')
try:
    import main
    print('   ✅ main.py loaded')
except Exception as e:
    print(f'   ❌ main.py error: {e}')

# Test 6: Ingestion module
print('\n6️⃣ Testing ingestion module...')
try:
    import ingestion.ingest
    print('   ✅ ingestion.ingest loaded')
except Exception as e:
    print(f'   ❌ ingestion error: {e}')

# Test 7: Retrieval module
print('\n7️⃣ Testing retrieval module...')
try:
    import retrieval.retrieve
    print('   ✅ retrieval.retrieve loaded')
except Exception as e:
    print(f'   ❌ retrieval error: {e}')

# Test 8: rag_assistant (known issue)
print('\n8️⃣ Testing rag_assistant module...')
try:
    import rag_assistant
    print('   ✅ rag_assistant loaded')
except Exception as e:
    print(f'   ❌ rag_assistant error: {e}')

print('\n' + '=' * 60)
print('✅ Health check complete!')
