import os
import yaml
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import and initialize API keys
from api import init_api_keys
init_api_keys()

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Set paths from config
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "..", config['vectorstore_path'])

# Load embeddings (same model as Week 1)
embeddings = HuggingFaceEmbeddings(
    model_name=config['embedding_model']
)

# Load FAISS index
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# Distance threshold (lower = more similar)
MAX_DISTANCE = config['max_distance']

def retrieve_answer(query):
    results = vectorstore.similarity_search_with_score(query, k=config['max_results'])

    if not results:
        return "❌ **Not Found**: This information is not available in the provided documents."

    best_doc, best_score = results[0]

    if best_score > MAX_DISTANCE:
        return "❌ **Not Found**: This information is not available in the provided documents."

    response = f"## Answer to: *{query}*\n\n"

    for i, (doc, score) in enumerate(results[:config['max_results']], 1):
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.strip()

        if config['show_confidence_scores']:
            confidence = "High" if score < 0.5 else "Medium" if score < 0.8 else "Low"
            confidence_text = f" (Confidence: {confidence})"
        else:
            confidence_text = ""

        if config['show_page_numbers']:
            page_text = f" - Page {int(page) + 1}"
        else:
            page_text = ""

        response += f"### Source {i}{page_text}{confidence_text}\n"
        response += f"{content[:600]}...\n\n"

    return response


if __name__ == "__main__":
    while True:
        q = input("\nAsk a question: ")
        if q.lower() == "exit":
            break
        print(retrieve_answer(q))