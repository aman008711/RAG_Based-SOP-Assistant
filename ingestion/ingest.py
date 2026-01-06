from email import policy
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from ..utils.chunker import chunk_text
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PDF_PATH = os.path.join(BASE_DIR, "data", "pdf", "policy.pdf")
VECTORSTORE_PATH = "../vectorstore/faiss_index"

def main():
    if not os.path.exists(PDF_PATH):
        print("❌ PDF not found")
        return

    # 1️⃣ Load PDF
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    # 2️⃣ Chunking (enterprise-style)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    # 3️⃣ Embeddings (HuggingFace – free and open source)
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # 4️⃣ FAISS Vector Store
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    vectorstore.save_local(VECTORSTORE_PATH)

# Example inside your loop that splits PDF into chunks
for doc in docs:
    text = doc.page_content
    source = doc.metadata.get("source", "Unknown")
    page = doc.metadata.get("page", "N/A")
    chunked_docs = chunk_text(text, source, page)

print("✅ Week 1 completed: Ingestion + FAISS index created")
if __name__ == "__main__":
        main()