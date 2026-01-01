import yaml
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import glob
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import and initialize API keys
from api import init_api_keys
init_api_keys()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration
config_path = os.path.join(BASE_DIR, "config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Set paths from config
PDF_DIR = os.path.join(BASE_DIR, config['pdf_directory'])
VECTORSTORE_PATH = os.path.join(BASE_DIR, config['vectorstore_path'])

def main():
    # Find all PDF files in the directory
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {PDF_DIR}")
        return

    print(f"📂 Found {len(pdf_files)} PDF file(s)")

    all_documents = []
    for pdf_path in pdf_files:
        print(f"📖 Processing: {os.path.basename(pdf_path)}")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        all_documents.extend(documents)

    print(f"📄 Total pages loaded: {len(all_documents)}")

    # 2️⃣ Chunking (enterprise-style)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['chunk_size'],
        chunk_overlap=config['chunk_overlap']
    )
    chunks = splitter.split_documents(all_documents)

    print(f"✂️ Total chunks created: {len(chunks)}")

    # 3️⃣ Embeddings (HuggingFace – free and open source)
    embeddings = HuggingFaceEmbeddings(
        model_name=config['embedding_model']
    )

    # 4️⃣ FAISS Vector Store
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    vectorstore.save_local(VECTORSTORE_PATH)

    print("✅ Ingestion completed: FAISS index created successfully")
    print(f"📊 Index saved to: {VECTORSTORE_PATH}")
    print(f"🔍 Ready to answer questions about {len(pdf_files)} document(s)")

if __name__ == "__main__":
    main()