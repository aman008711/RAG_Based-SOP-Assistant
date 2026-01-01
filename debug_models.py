#!/usr/bin/env python3
"""
Test script to debug model loading issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("Testing imports...")
    try:
        from api import init_api_keys, has_api_key
        print("✅ API imports successful")
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

    try:
        import yaml
        print("✅ YAML import successful")
    except Exception as e:
        print(f"❌ YAML import failed: {e}")
        return False

    try:
        from langchain_community.vectorstores import FAISS
        print("✅ FAISS import successful")
    except Exception as e:
        print(f"❌ FAISS import failed: {e}")
        return False

    return True

def test_config():
    print("\nTesting config loading...")
    try:
        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✅ Config loaded: embedding_model={config['embedding_model']}")
        return config
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return None

def test_embeddings(config):
    print("\nTesting embeddings...")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'])
        print("✅ Embeddings created successfully")
        return embeddings
    except Exception as e:
        print(f"❌ Embeddings creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_vectorstore(config, embeddings):
    print("\nTesting vectorstore loading...")
    try:
        from langchain_community.vectorstores import FAISS
        vectorstore = FAISS.load_local(
            config['vectorstore_path'],
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Vectorstore loaded successfully")
        return vectorstore
    except Exception as e:
        print(f"❌ Vectorstore loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🔍 Debugging model loading issues...\n")

    if not test_imports():
        return

    config = test_config()
    if not config:
        return

    embeddings = test_embeddings(config)
    if not embeddings:
        return

    vectorstore = test_vectorstore(config, embeddings)
    if not vectorstore:
        return

    print("\n✅ All tests passed! Model loading should work.")

if __name__ == "__main__":
    main()