#!/usr/bin/env python3
"""
Working RAG-Based SOP Assistant
Combines ingestion and retrieval into a single working system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🤖 RAG-Based SOP Assistant - Working Version")
    print("=" * 50)

    # Check if vectorstore exists
    vectorstore_path = "vectorstore/faiss_index"
    if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
        print("📂 No vectorstore found. Running ingestion first...")
        try:
            import sys
            sys.path.append('ingestion')
            from ingest import main as ingest_main
            ingest_main()
            print("✅ Ingestion completed!")
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            return
    else:
        print("✅ Vectorstore found - skipping ingestion")

    print("\n🔍 Starting interactive retrieval...")
    print("Type 'exit' to quit\n")

    # Start retrieval
    try:
        from retrieval.retrieve import retrieve_answer
        while True:
            question = input("Ask a question: ").strip()
            if question.lower() == 'exit':
                break
            if question:
                answer = retrieve_answer(question)
                print(f"\n{answer}\n")
            else:
                print("Please enter a question.\n")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")

if __name__ == "__main__":
    main()