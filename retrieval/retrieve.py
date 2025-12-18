from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTORSTORE_PATH = "vectorstore/faiss_index"

# Load embeddings (same model as Week 1)
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# Load FAISS index
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# Distance threshold (lower = more similar)
MAX_DISTANCE = 0.9

def retrieve_answer(query):
    results = vectorstore.similarity_search_with_score(query, k=3)

    if not results:
        return "This information is not available in the provided documents."

    best_doc, best_score = results[0]

    if best_score > MAX_DISTANCE:
        return "This information is not available in the provided documents."

    response = "Answer based on retrieved documents:\n"

    for doc, score in results:
        page = doc.metadata.get("page", "N/A")
        response += f"\n[Page {page}] {doc.page_content[:400]}...\n"

    return response


if __name__ == "__main__":
    while True:
        q = input("\nAsk a question: ")
        if q.lower() == "exit":
            break
        print(retrieve_answer(q))