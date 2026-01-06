import streamlit as st
import os
import yaml
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------------------
# Load configuration
# ---------------------------
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title=config["page_title"],
    page_icon=config["page_icon"],
    layout=config["layout"]
)

# ---------------------------
# Cache resources
# ---------------------------
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name=config["embedding_model"])

@st.cache_resource
def load_vectorstore():
    embeddings = load_embeddings()
    return FAISS.load_local(
        config["vectorstore_path"],
        embeddings,
        allow_dangerous_deserialization=True
    )

embeddings = load_embeddings()
vectorstore = load_vectorstore()

# ---------------------------
# Retrieval function (STRING return)
# ---------------------------
def retrieve_answer(query: str) -> str:
    results = vectorstore.similarity_search_with_score(
        query, k=config["max_results"]
    )

    if not results:
        return "❌ This information is not available in the provided documents."

    best_doc, best_score = results[0]

    if best_score > config["max_distance"]:
        return "❌ This information is not available in the provided documents."

    response = f"## Answer to: *{query}*\n\n"

    for i, (doc, score) in enumerate(results, start=1):
        page = doc.metadata.get("page", "N/A")
        content = doc.page_content.strip()

        response += f"### Source {i} (Page {page})\n"
        response += f"{content[:600]}...\n\n"

    return response

# ---------------------------
# UI Styling
# ---------------------------
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Title
# ---------------------------
st.markdown(
    '<h1 class="main-header">📚 RAG-Based SOP Assistant</h1>',
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Info")

    try:
        doc_count = len(vectorstore.docstore._dict)
        st.success(f"📄 {doc_count} documents indexed")
    except Exception:
        st.error("Vectorstore not loaded")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------
# Chat history
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat input
# ---------------------------
if prompt := st.chat_input("Ask a question..."):
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching documents..."):
            try:
                answer = retrieve_answer(prompt)
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                error_msg = f"❌ Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown(
    "<center>Built with Streamlit & LangChain</center>",
    unsafe_allow_html=True
)
