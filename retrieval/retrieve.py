from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTORSTORE_PATH = "vectorstore/faiss_index"
MAX_DISTANCE = 0.9

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

def retrieve_answer(query: str):
    results = vectorstore.similarity_search_with_score(query, k=3)

    if not results:
        return {
            "answer": "This information is not available in the provided documents.",
            "sources": []
        }

    best_doc, best_score = results[0]

    if best_score > MAX_DISTANCE:
        return {
            "answer": "This information is not available in the provided documents.",
            "sources": []
        }

    answer_text = ""
    sources = []

    for doc, score in results:
        answer_text += doc.page_content[:400] + "\n\n"

        sources.append({
            "document": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "N/A"),
            "score": round(score, 3)
        })

    return {
        "answer": answer_text.strip(),
        "sources": sources
    }
