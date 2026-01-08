# core/vector_store.py

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

EMBEDDINGS = None
VECTOR_DB = None

def load_vector_store():
    global EMBEDDINGS, VECTOR_DB

    if VECTOR_DB is None:
        EMBEDDINGS = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        VECTOR_DB = FAISS.load_local(
            "data/faiss_index",
            EMBEDDINGS,
            allow_dangerous_deserialization=True
        )

    return VECTOR_DB
