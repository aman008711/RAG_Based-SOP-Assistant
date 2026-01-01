from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
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

    print("✅ Week 1 completed: Ingestion + FAISS index created")

if __name__ == "__main__":
    main()

































































