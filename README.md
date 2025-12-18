# RAG-Based SOP Assistant

A **RAG (Retrieval-Augmented Generation) based SOP Assistant** that allows users to query PDFs and get accurate, document-based answers.

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
.env/              # Environment variables
venv/              # Virtual environment (ignored in GitHub)
data/pdf/          # Sample PDF files
ingestion/         # Code to ingest PDFs into the vector store
retrieval/         # Code to query vector store and generate responses
vectorstore/       # FAISS index storage
requirements.txt   # Project dependencies
README.md          # Project documentation
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
```

---

## License

MIT License
