#!/usr/bin/env python3
"""Debug script for RAG-Based SOP Assistant"""

import os
import yaml
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import and initialize API keys
from api import init_api_keys
init_api_keys()

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

VECTORSTORE_PATH = config['vectorstore_path']

# Check if vector store exists
if not os.path.exists(VECTORSTORE_PATH):
    print(f"❌ Vector store not found at {VECTORSTORE_PATH}")
    exit(1)

print("✅ Vector store directory exists")

# Load embeddings
embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'])
print("✅ Embeddings model loaded")

# Load FAISS index
try:
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("✅ Vector store loaded successfully")
except Exception as e:
    print(f"❌ Error loading vector store: {e}")
    exit(1)

# Check vector store contents
try:
    doc_count = len(vectorstore.docstore._dict)
    print(f"📄 Vector store contains {doc_count} documents")
except:
    print("⚠️ Could not count documents")

# Test similarity search
test_queries = [
    "leave",
    "policy",
    "what is the leave policy",
    "vacation",
    "holiday"
]

print("\n🔍 Testing similarity search:")
for query in test_queries:
    try:
        results = vectorstore.similarity_search_with_score(query, k=3)
        print(f"\nQuery: '{query}'")
        print(f"  Found {len(results)} results")

        for i, (doc, score) in enumerate(results[:2]):
            print(".3f")
            print(f"    Content preview: {doc.page_content[:100]}...")

        if not results or results[0][1] > config['max_distance']:
            print(f"  ❌ Would be filtered out (max_distance = {config['max_distance']})")
        else:
            print("  ✅ Would pass filter")

    except Exception as e:
        print(f"❌ Error with query '{query}': {e}")