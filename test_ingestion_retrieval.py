#!/usr/bin/env python3
"""
Test script to verify ingestion and retrieval integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ingestion_retrieval():
    print("🧪 Testing ingestion and retrieval integration...")

    # Test 1: Check if vectorstore exists
    vectorstore_path = "vectorstore/faiss_index"
    if os.path.exists(vectorstore_path):
        print("✅ Vectorstore directory exists")
        if os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
            print("✅ FAISS index file exists")
        else:
            print("❌ FAISS index file missing")
            return False
    else:
        print("❌ Vectorstore directory missing - run ingestion first")
        return False

    # Test 2: Load models (similar to main.py)
    try:
        from api import init_api_keys
        init_api_keys()

        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'])

        from langchain_community.vectorstores import FAISS
        vectorstore = FAISS.load_local(
            config['vectorstore_path'],
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

    # Test 3: Test retrieval
    try:
        question = "What is the salary policy?"
        docs = vectorstore.similarity_search_with_score(question, k=3)

        if not docs:
            print("❌ No documents found for test query")
            return False

        print(f"✅ Retrieval successful - found {len(docs)} documents")

        # Show sample result
        best_doc, best_score = docs[0]
        print(f"📄 Sample result: {best_doc.page_content[:200]}...")
        print(f"📊 Score: {best_score:.3f}")

    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        return False

    # Test 4: Test API-like response generation
    try:
        response = f"## Answer to: *{question}*\n\n"

        for i, (doc, score) in enumerate(docs[:3], 1):
            page = doc.metadata.get("page", "N/A")
            content = doc.page_content.strip()[:400] + "..."
            response += f"### Source {i} - Page {int(page) + 1}\n{content}\n\n"

        print("✅ API response generation successful")
        print(f"📝 Response length: {len(response)} characters")

    except Exception as e:
        print(f"❌ API response generation failed: {e}")
        return False

    print("\n🎉 All tests passed! Ingestion and retrieval are working properly.")
    return True

if __name__ == "__main__":
    success = test_ingestion_retrieval()
    sys.exit(0 if success else 1)