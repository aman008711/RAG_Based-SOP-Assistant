#!/usr/bin/env python3
"""
Optimized RAG-Based SOP Assistant
- Vector DB loaded once
- Retriever cached
- Fast query execution
"""

import sys
import os

# Ensure project root in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ================== Imports ==================
from core.vector_store import load_vector_store
from langchain_community.llms import Ollama   # change if using other LLM

# ================== Load heavy objects ONCE ==================

# Load vector database (cached)
vector_db = load_vector_store()

# Create retriever (optimized)
retriever = vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Load LLM once
llm = Ollama(model="llama3")

# ================== Core RAG Function ==================

def get_answer(query: str):
    """
    Retrieve relevant documents and generate answer
    """
    docs = retriever.get_relevant_documents(query)

    if not docs:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    context = "\n\n".join(doc.page_content for doc in docs)

    final_answer = llm.invoke(
        context + "\n\nQuestion: " + query
    )

    sources = [
        {
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page")
        }
        for doc in docs
    ]

    return {
        "answer": final_answer,
        "sources": sources
    }

# ================== CLI MODE (Optional) ==================

def main():
    print("🤖 RAG-Based SOP Assistant")
    print("=" * 50)

    # Check if vectorstore exists
    vectorstore_path = "vectorstore/faiss_index"
    if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
        print("📂 No vectorstore found. Running ingestion...")
        try:
            from ingestion.ingest import main as ingest_main
            ingest_main()
            print("✅ Ingestion completed!")
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            return
    else:
        print("✅ Vectorstore found - skipping ingestion")

    print("\n🔍 Ask questions (type 'exit' to quit)\n")

    try:
        while True:
            question = input("❓ Question: ").strip()
            if question.lower() == "exit":
                break

            if question:
                response = get_answer(question)
                print("\n🧠 Answer:")
                print(response["answer"])
                print("\n📄 Sources:")
                for src in response["sources"]:
                    print(src)
                print("-" * 40)
            else:
                print("⚠️ Please enter a question")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

# ================== Entry Point ==================

if __name__ == "__main__":
    main()
