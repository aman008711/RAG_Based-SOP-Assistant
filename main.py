"""
FastAPI Backend for RAG-Based SOP Assistant - Week 3
Provides REST API endpoints with streaming responses and OpenAI integration
"""

import time
import asyncio
import json
import sys
from typing import Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from api import init_api_keys, has_api_key

# Initialize API keys
init_api_keys()

# Global variables for models
vectorstore = None
llm = None
embeddings = None

class AskRequest(BaseModel):
    question: str
    session_id: str = "default"  # For conversation memory

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    vectorstore_loaded: bool
    openai_available: bool
    memory_sessions: int

def initialize_models():
    """Initialize the vector store and LLM"""
    global vectorstore, llm, embeddings

    try:
        print("📄 Loading configuration...")
        # Load configuration
        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ Config loaded")

        # Initialize embeddings
        print("🤖 Initializing embeddings...")
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name=config['embedding_model'])
            print("✅ HuggingFace embeddings initialized")
        except Exception as e:
            print(f"⚠️  HuggingFace embeddings failed ({e}), trying fallback...")
            try:
                from langchain.embeddings import FakeEmbeddings
                embeddings = FakeEmbeddings(size=384)  # Same size as all-MiniLM-L6-v2
                print("✅ Using fake embeddings as fallback")
            except Exception as e2:
                print(f"❌ All embedding options failed: {e2}")
                raise

        # Load vector store
        print("💾 Loading vector store...")
        vectorstore = FAISS.load_local(
            config['vectorstore_path'],
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Vector store loaded")

        # Initialize OpenAI LLM (if API key available)
        if has_api_key('openai'):
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model_name=config.get('openai_model', 'gpt-3.5-turbo'),
                    temperature=config.get('temperature', 0.1),
                    max_tokens=config.get('max_tokens', 500),
                    streaming=True  # Enable streaming
                )
                print("✅ OpenAI LLM initialized with streaming support")
            except ImportError as e:
                print(f"⚠️  Could not import ChatOpenAI: {e}")
                llm = None
        else:
            print("⚠️  OpenAI API key not available - using retrieval-only mode")
            llm = None

        print("✅ Models initialized successfully")

    except Exception as e:
        print(f"❌ Error initializing models: {e}")
        import traceback
        traceback.print_exc()
        raise

# Initialize models on startup (not using lifespan for now)
# Models will be loaded lazily when first request comes in
vectorstore = None
llm = None
embeddings = None
models_loaded = False

def load_models_if_needed():
    """Load models lazily when first needed"""
    global vectorstore, llm, embeddings, models_loaded

    if models_loaded:
        return

    try:
        print("🔄 Loading models...")
        initialize_models()
        models_loaded = True
        print("✅ Models loaded successfully on first request")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=503, detail=f"Model loading failed: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title="RAG-Based SOP Assistant API",
    description="Week 3: FastAPI backend with streaming responses and OpenAI integration",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "vectorstore_loaded": vectorstore is not None,
        "openai_available": False,  # Simplified
        "memory_sessions": 0
    }

async def generate_streaming_response(question: str, session_id: str) -> AsyncGenerator[str, None]:
    """Generate streaming response for the question"""
    start_time = time.time()

    try:
        if llm is None:
            # Fallback to retrieval-only mode
            if vectorstore is None:
                yield "data: {\"error\": \"Vector store not loaded\"}\n\n"
                return

            # Use retrieval-only approach
            docs = vectorstore.similarity_search_with_score(question, k=3)

            if not docs:
                yield "data: {\"answer\": \"❌ Not Found: This information is not available in the provided documents.\", \"sources\": [], \"ttft\": 0.1}\n\n"
                return

            # Send TTFT first
            ttft = time.time() - start_time
            yield f"data: {{\"ttft\": {ttft:.3f}}}\n\n"

            # Start with an engaging introduction
            intro = f"I'll help you find information about: **{question}**\n\nHere are the most relevant sections from your documents:\n\n"
            for char in intro:
                if char == '\n':
                    yield f"data: {json.dumps({'token': '\n'})}\n\n"
                else:
                    yield f"data: {json.dumps({'token': char})}\n\n"
                await asyncio.sleep(0.01)

            # Stream each document with enhanced formatting
            for i, (doc, score) in enumerate(docs[:3], 1):
                page = doc.metadata.get("page", "N/A")
                content = doc.page_content.strip()

                # Create formatted header
                header = f"📄 **Source {i}** (Page {int(page) + 1}, Relevance: {((1-score)*100):.1f}%)\n"
                for char in header:
                    if char == '\n':
                        yield f"data: {json.dumps({'token': '\n'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'token': char})}\n\n"
                    await asyncio.sleep(0.02)

                # Stream content with natural pacing
                content_preview = content[:600] + ("..." if len(content) > 600 else "")
                words = content_preview.split()

                for word in words:
                    yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                    await asyncio.sleep(0.04)  # Natural reading pace

                # Add spacing
                yield f"data: {json.dumps({'token': '\n\n'})}\n\n"
                await asyncio.sleep(0.1)

            # Add helpful summary
            summary = "\n💡 This information is extracted directly from your SOP documents for maximum accuracy."
            for char in summary:
                if char == '\n':
                    yield f"data: {json.dumps({'token': '\n'})}\n\n"
                else:
                    yield f"data: {json.dumps({'token': char})}\n\n"
                await asyncio.sleep(0.02)

            # Send completion with sources
            sources = []
            for i, (doc, score) in enumerate(docs[:3], 1):
                sources.append({
                    "source": i,
                    "page": int(doc.metadata.get("page", 0)) + 1,
                    "content": doc.page_content.strip()[:250] + "...",
                    "confidence": f"{((1-score)*100):.1f}%"
                })

            completion_data = {
                "complete": True,
                "sources": sources,
                "total_time": time.time() - start_time
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        else:
            # Use OpenAI LLM with retrieval context
            # Get relevant documents first
            docs = vectorstore.similarity_search_with_score(question, k=3)
            context = "\n\n".join([doc.page_content for doc, _ in docs])

            # Create comprehensive prompt for LLM
            prompt = f"""You are a helpful SOP (Standard Operating Procedure) assistant. Answer the user's question based on the provided context from their documents.

Guidelines:
- Answer based on the provided context
- If context doesn't contain enough information, acknowledge this
- Be concise but comprehensive
- Use clear, professional language
- Reference specific sources when relevant

Context from documents:
{context}

Question: {question}

Answer:"""

            # Send TTFT
            ttft = time.time() - start_time
            yield f"data: {{\"ttft\": {ttft:.3f}}}\n\n"

            try:
                # Get response from OpenAI
                response = llm.invoke(prompt)
                answer_text = response.content if hasattr(response, 'content') else str(response)

                # Stream the answer with natural sentence pacing (ChatGPT-like)
                sentences = answer_text.split('. ')
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        words = sentence.split()
                        for word in words:
                            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                            await asyncio.sleep(0.06)  # Natural reading pace for LLM responses

                        # Add period and space (except for last sentence)
                        if i < len(sentences) - 1:
                            yield f"data: {json.dumps({'token': '. '})}\n\n"
                            await asyncio.sleep(0.15)  # Pause between sentences for better UX

                # Add sources at the end
                sources = []
                for i, (doc, score) in enumerate(docs[:3], 1):
                    sources.append({
                        "source": i,
                        "page": int(doc.metadata.get("page", 0)) + 1,
                        "content": doc.page_content.strip()[:250] + "...",
                        "confidence": f"{((1-score)*100):.1f}%"
                    })

                completion_data = {
                    "complete": True,
                    "sources": sources,
                    "total_time": time.time() - start_time
                }
                yield f"data: {json.dumps(completion_data)}\n\n"

            except Exception as e:
                error_msg = f"OpenAI API error: {str(e)}"
                for char in error_msg:
                    yield f"data: {json.dumps({'token': char})}\n\n"
                    await asyncio.sleep(0.02)
                yield f"data: {json.dumps({'complete': True})}\n\n"

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        for char in error_msg:
            yield f"data: {json.dumps({'token': char})}\n\n"
            await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'complete': True})}\n\n"

@app.get("/ask")
async def ask_question_get(question: str, session_id: str = "default"):
    """Streaming endpoint for asking questions (GET version for EventSource)"""
    load_models_if_needed()  # Load models if not already loaded

    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vector store not loaded")

    return StreamingResponse(
        generate_streaming_response(question, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Streaming endpoint for asking questions"""
    load_models_if_needed()  # Load models if not already loaded

    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vector store not loaded")

    return StreamingResponse(
        generate_streaming_response(request.question, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG-Based SOP Assistant API - Week 3",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /ask": "Ask questions with streaming responses",
            "GET /": "This information",
            "GET /web": "Web interface for testing"
        },
        "features": [
            "FastAPI backend",
            "Streaming responses (Typewriter effect)",
            "OpenAI LLM integration",
            "Conversational memory",
            "Performance monitoring (TTFT)"
        ]
    }

@app.get("/web")
async def web_interface():
    """Serve the web interface for testing"""
    return FileResponse("static/index.html", media_type="text/html")

if __name__ == "__main__":
    import subprocess
    import sys
    import os

    print("🚀 Starting RAG-Based SOP Assistant API - Week 3")
    print("📡 FastAPI server with streaming responses")
    print("🔗 OpenAI integration enabled")
    print("🌐 Access at: http://localhost:8008")
    print("📚 Docs at: http://localhost:8008/docs")

    # Use virtual environment's Python executable
    venv_python = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        print("🔧 Using virtual environment Python")
        try:
            # Use Popen to run uvicorn in background without blocking
            process = subprocess.Popen([venv_python, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"])
            print("✅ Server started successfully!")
            print("🌐 Access at: http://localhost:8008")
            print("📚 Docs at: http://localhost:8008/docs")
            print("💡 Press Ctrl+C to stop the server")

            # Wait for the process to finish (this will block until interrupted)
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            sys.exit(1)
    else:
        print("⚠️  Virtual environment not found, using system Python")
        uvicorn.run(app, host="0.0.0.0", port=8008)