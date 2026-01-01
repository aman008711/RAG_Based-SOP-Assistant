import streamlit as st
import os
import yaml
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Import and initialize API keys
from api import init_api_keys
init_api_keys()

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Page configuration
st.set_page_config(
    page_title=config['page_title'],
    page_icon=config['page_icon'],
    layout=config['layout'],
    initial_sidebar_state="expanded"
)

# Cache the embeddings model (loads only once)
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name=config['embedding_model'])

# Cache the vector store (loads only once)
@st.cache_resource
def load_vectorstore():
    embeddings = load_embeddings()
    return FAISS.load_local(
        config['vectorstore_path'],
        embeddings,
        allow_dangerous_deserialization=True
    )

# Load cached resources
embeddings = load_embeddings()
vectorstore = load_vectorstore()

# Optimized retrieve function
def retrieve_answer(query):
    results = vectorstore.similarity_search_with_score(query, k=config['max_results'])

    if not results:
        return "❌ **Not Found**: This information is not available in the provided documents."

    best_doc, best_score = results[0]

    if best_score > config['max_distance']:
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
    results = vectorstore.similarity_search_with_score(query, k=config['max_results'])

    if not results:
        return "❌ **Not Found**: This information is not available in the provided documents."

        best_doc, best_score = results[0]

    if best_score > config['max_distance']:
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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .sidebar-content {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown('<h1 class="main-header">📚 RAG-Based SOP Assistant</h1>', unsafe_allow_html=True)
#st.markdown('<p class="subtitle">Ask intelligent questions </p>', unsafe_allow_html=True)

# Show loading status
#with st.spinner("Loading AI models..."):
    # This will trigger the cached loading
    #if vectorstore and embeddings:
        #st.success(" ")
    #else:
        #st.error("Failed to load models. Please check your configuration.")

#st.markdown("---")'''

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Info")

    # Status indicator
    try:
        if vectorstore:
            
            doc_count = len(vectorstore.docstore._dict)
            st.info(f"📄 {doc_count} documents indexed")
        else:
            st.error("❌ Vector store not found. Please run ingestion first.")
    except Exception as e:
        st.error(f"❌ Error checking vector store: {str(e)}")

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # Usage instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        1. **Ask Questions**: Type your question in natural language
        2. **Get Answers**: Receive document-based responses with source references
        3. **Chat History**: Previous conversations are saved during your session
        4. **Clear Chat**: Use the button above to start fresh
        """)

    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **RAG-Based SOP Assistant** uses:
        - **Retrieval-Augmented Generation** for accurate answers
        - **FAISS vector store** for fast semantic search
        - **HuggingFace embeddings** for document understanding
        - **Local processing** - no data sent to external APIs
        """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching documents..."):
            try:
                answer = retrieve_answer(prompt)
                st.markdown(answer)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                error_msg = f"❌ Sorry, an error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: #666; font-size: 0.8rem;">Built with Streamlit & LangChain</div>', unsafe_allow_html=True)