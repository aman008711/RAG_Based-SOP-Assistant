#!/usr/bin/env python3
"""
Performance Test for RAG-Based SOP Assistant
Tests loading times and query performance
"""

import time
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

def test_performance():
    print("🚀 RAG-Based SOP Assistant - Performance Test")
    print("=" * 50)

    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Test embeddings loading
    start_time = time.time()
    embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'])
    embed_time = time.time() - start_time
    print(".2f")
    # Test vector store loading
    start_time = time.time()
    vectorstore = FAISS.load_local(
        config['vectorstore_path'],
        embeddings,
        allow_dangerous_deserialization=True
    )
    vs_time = time.time() - start_time
    print(".2f")
    doc_count = len(vectorstore.docstore._dict)
    print(f"📄 Documents indexed: {doc_count}")

    # Test query performance
    test_queries = [
        "leave policy",
        "employee benefits",
        "termination procedure"
    ]

    print("\n🔍 Query Performance:")
    for query in test_queries:
        start_time = time.time()
        results = vectorstore.similarity_search_with_score(query, k=config['max_results'])
        query_time = time.time() - start_time
        result_count = len(results)
        print(".3f")
    total_time = embed_time + vs_time
    print(".2f")
    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    test_performance()