#!/usr/bin/env python3
"""
Configuration Validator for RAG-Based SOP Assistant
Validates the config.yaml file and shows current settings
"""

import os
import yaml
import sys

def validate_config():
    """Validate configuration file and display settings"""

    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

    if not os.path.exists(config_path):
        print("❌ config.yaml not found!")
        return False

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        print("✅ Configuration loaded successfully!")
        print("\n📋 Current Settings:")
        print("=" * 50)

        # API Keys status
        print("🔑 API Keys:")
        api_keys = {
            'Hugging Face Token': config.get('huggingface_token'),
            'OpenAI API Key': config.get('openai_api_key'),
            'Anthropic API Key': config.get('anthropic_api_key')
        }

        for name, key in api_keys.items():
            if key and key.strip():
                print(f"  ✅ {name}: Configured")
            else:
                print(f"  ⚪ {name}: Not set")

        print()

        # Embedding settings
        print(f"🤖 Embedding Model: {config.get('embedding_model', 'Not set')}")
        print(f"📏 Max Distance: {config.get('max_distance', 'Not set')}")

        # Text processing
        print(f"📄 Chunk Size: {config.get('chunk_size', 'Not set')}")
        print(f"🔗 Chunk Overlap: {config.get('chunk_overlap', 'Not set')}")

        # Paths
        print(f"📁 PDF Directory: {config.get('pdf_directory', 'Not set')}")
        print(f"💾 Vector Store Path: {config.get('vectorstore_path', 'Not set')}")

        # UI settings
        print(f"🎨 Page Title: {config.get('page_title', 'Not set')}")
        print(f"📱 Layout: {config.get('layout', 'Not set')}")

        # Week 3 - FastAPI & OpenAI Settings
        print(f"🤖 OpenAI Model: {config.get('openai_model', 'Not set')}")
        print(f"🌡️ Temperature: {config.get('temperature', 'Not set')}")
        print(f"📝 Max Tokens: {config.get('max_tokens', 'Not set')}")
        print(f"⚡ Streaming Delay: {config.get('streaming_delay', 'Not set')}")
        print(f"🎯 Target TTFT: {config.get('target_ttft', 'Not set')}s")

        # Validate paths
        pdf_dir = config.get('pdf_directory', 'data/pdf')
        if os.path.exists(pdf_dir):
            pdf_count = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
            print(f"📚 PDFs Found: {pdf_count} files")
        else:
            print(f"⚠️  PDF Directory not found: {pdf_dir}")

        vectorstore_path = config.get('vectorstore_path', 'vectorstore/faiss_index')
        if os.path.exists(vectorstore_path):
            print(f"✅ Vector Store: Ready")
        else:
            print(f"⚠️  Vector Store not found: {vectorstore_path}")

        return True

    except yaml.YAMLError as e:
        print(f"❌ YAML Error in config.yaml: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False

if __name__ == "__main__":
    print("🔧 RAG-Based SOP Assistant - Configuration Validator")
    print("=" * 55)
    success = validate_config()
    sys.exit(0 if success else 1)