<<<<<<< HEAD

# RAG-Based SOP Assistant

'''A **RAG (Retrieval-Augmented Generation) based SOP Assistant** that allows users to query PDFs and get accurate, document-based answers.
=======
# RAG-Based SOP Assistant

A **RAG (Retrieval-Augmented Generation) based SOP Assistant** that allows users to query PDFs and get accurate, document-based answers.
>>>>>>> a8d9ec04a1fb2516541dfe259fa8f4d25914e854

---

## Overview

This project enables semantic search and question answering over policy documents using **Hugging Face embeddings** and **FAISS vector store**, without relying on paid APIs.

---

## 🟢 Week 1 – Document Preparation

In Week 1, we prepared the document so the system can understand it.

### Steps

1. **PDF Loading**
   Loaded the policy PDF from the `data/pdf` folder.

2. **Text Chunking**
   Split the PDF into small text chunks.
   *Reason:* Large documents cannot be searched efficiently as a whole.

3. **Embeddings Creation**
   Each chunk was converted into a numerical vector using
   `HuggingFace sentence-transformers (all-MiniLM-L6-v2)`.

4. **FAISS Vector Store**
   Stored all embeddings in **FAISS** for fast semantic search.

5. **Index Saved**
   Saved the vector index locally as `index.faiss` and `index.pkl`.

### ✅ Outcome

* PDF is now searchable
* Semantic understanding is enabled
* Foundation for question answering is ready

---

## 🟢 Week 2 – Retrieval & Question Answering

In Week 2, the system was enabled to answer user questions using the document.

### Steps

1. **Load FAISS Index**
   Reused the vector index from Week 1.

2. **User Question Input**
   User types a question in natural language.

3. **Semantic Search**
   FAISS finds the most relevant document chunks.

4. **Context-Based Answering**

   * If information exists → answer is shown from the document.
   * If information does NOT exist → system responds:

   > “This information is not available in the provided documents.”

5. **Hallucination Control**
   The system does not answer questions outside the document.

### ✅ Outcome

* Accurate document-based answers
* No hallucinated or random responses
* Safe and reliable QA system
<<<<<<< HEAD
* **Modern Web Interface** with chat history and improved UX
* **Multiple PDF Support** for comprehensive document analysis
* **Optimized Performance** with model caching for fast loading
=======
>>>>>>> a8d9ec04a1fb2516541dfe259fa8f4d25914e854

---

## 🤗 Why We Used Hugging Face

### Reasons

1. **Free & Open Source** – No payment or API key required
2. **Company-Friendly** – Suitable for internal and secure environments
3. **High-Quality Embeddings** – Strong semantic understanding via sentence-transformers
4. **Avoid OpenAI Cost Issues** – Works locally, no paid credits required
5. **Scalable** – Can later switch to any LLM if needed

> That’s why we chose **Hugging Face + FAISS**.

---

## Project Structure

```
<<<<<<< HEAD
config.yaml          # Configuration settings
api.py               # API key management
main.py              # Week 3 FastAPI server
static/              # Web interface files
  index.html         # Streaming chat interface
data/pdf/            # Sample PDF files
ingestion/           # Code to ingest PDFs into the vector store
retrieval/           # Code to query vector store and generate responses
vectorstore/         # FAISS index storage
performance_test_week3.py  # Week 3 performance testing
requirements.txt     # Project dependencies
README.md            # Project documentation
```

---

## Configuration

Customize your assistant by editing `config.yaml`:

```yaml
# API Keys (Optional - leave empty if not using)
# huggingface_token: "your_token"     # For faster downloads
# openai_api_key: ""                  # If using OpenAI services
# anthropic_api_key: ""               # If using Anthropic Claude

# Embedding model settings
embedding_model: "all-MiniLM-L6-v2"  # Change embedding model
max_distance: 1.2                   # Similarity threshold (higher = more permissive)

# Text processing
chunk_size: 800                     # Text chunk size
chunk_overlap: 150                  # Overlap between chunks

# File paths
pdf_directory: "data/pdf"           # PDF source directory
vectorstore_path: "vectorstore/faiss_index"  # Index storage

# UI settings
page_title: "SOP Assistant"          # App title
page_icon: "📚"                     # App icon
layout: "wide"                      # App layout

# Search settings
max_results: 3                      # Number of results to show
show_page_numbers: true             # Display page numbers
show_confidence_scores: true        # Show confidence levels
=======
.env/              # Environment variables
venv/              # Virtual environment (ignored in GitHub)
data/pdf/          # Sample PDF files
ingestion/         # Code to ingest PDFs into the vector store
retrieval/         # Code to query vector store and generate responses
vectorstore/       # FAISS index storage
requirements.txt   # Project dependencies
README.md          # Project documentation
>>>>>>> a8d9ec04a1fb2516541dfe259fa8f4d25914e854
```

---

## Setup

```bash
git clone https://github.com/vishakha489/RAG-Based-SOP-Assistant.git
cd RAG-Based-SOP-Assistant
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

<<<<<<< HEAD
### API Keys (Optional)
For the current setup with `all-MiniLM-L6-v2`, **no API keys are required**. 

If you want to use other models or services:
1. Copy `.env.example` to `.env`
2. Add your API keys to `config.yaml` or `.env`
3. The system will automatically use them when available

---

## 🟢 Week 3 – FastAPI Backend & Streaming

In Week 3, we added a production-ready FastAPI backend with streaming responses and OpenAI integration.

### Features Implemented

1. **FastAPI Endpoints**
   - `/ask` - Streaming question answering
   - `/health` - API health check
   - `/web` - Web interface for testing

2. **Streaming Responses**
   - Typewriter effect (word-by-word streaming)
   - Server-Sent Events (SSE)
   - Real-time token streaming

3. **OpenAI Integration**
   - GPT-3.5-turbo for enhanced responses
   - Conversational memory
   - LangChain chat chains

4. **Performance Monitoring**
   - TTFT (Time To First Token) measurement
   - Target: < 1 second
   - Comprehensive performance testing

### Setup for Week 3

1. **Install new dependencies:**
```bash
pip install -r requirements.txt
```

2. **Add OpenAI API Key** (for LLM features):
```yaml
# In config.yaml
openai_api_key: "your-openai-api-key-here"
```

3. **Start FastAPI Server:**
```bash
python main.py
```

4. **Access the API:**
   - **API Docs:** http://localhost:8000/docs
   - **Web Interface:** http://localhost:8000/web
   - **Health Check:** http://localhost:8000/health

### Testing the API

**Using curl:**
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the employee onboarding process?", "session_id": "test"}'
```

**Performance Testing:**
```bash
python performance_test_week3.py
```

### API Response Format

**Streaming Response:**
```json
data: {"ttft": 0.234}
data: {"token": "The "}
data: {"token": "employee "}
data: {"token": "onboarding "}
data: {"complete": true, "sources": [...]}
```

---

## 🚀 Quick Start (Working Solution)

### Option 1: Streamlit Web Interface (Recommended)
1. Process documents:
```bash
python -c "import sys; sys.path.append('ingestion'); from ingest import main; main()"
```
2. Start the web interface:
```bash
streamlit run app.py
```
3. Open browser to `http://localhost:8501`

### Option 2: Command Line Interface
1. Process documents:
```bash
python -c "import sys; sys.path.append('ingestion'); from ingest import main; main()"
```
2. Start interactive assistant:
```bash
python rag_assistant.py
```

### Option 3: Test Everything
```bash
python test_ingestion_retrieval.py
=======
---

## Usage

1. Place your PDF files in `data/pdf/`.
2. Run ingestion script:

```bash
python ingestion/ingest.py
```

3. Run retrieval script:

```bash
python retrieval/retrieve.py
>>>>>>> a8d9ec04a1fb2516541dfe259fa8f4d25914e854
```

---

## License

<<<<<<< HEAD
MIT License'''











'''# 1. Activate virtual environment
venv\Scripts\activate

# 2. Install/update dependencies (if needed)
pip install -r requirements.txt

# 3. Process PDF documents
python -c "import sys; sys.path.append('ingestion'); from ingest import main; main()"

# 4. Choose your interface:
# Option A: Web interface (recommended)
streamlit run app.py

# Option B: Command line interface
python rag_assistant.py'''
=======
# RAG_Based-SOP-Assistant

=======
MIT License
>>>>>>> a8d9ec04a1fb2516541dfe259fa8f4d25914e854
