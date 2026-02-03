import streamlit as st

def render_sidebar():
    st.header("⚙️ AskBuddy Settings")

    # Ensure defaults (defensive, safe)
    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = False

    if "memory_enabled" not in st.session_state:
        st.session_state.memory_enabled = True

    st.session_state.memory_enabled = st.toggle(
        "🧠 Memory",
        value=st.session_state.memory_enabled
    )

    st.session_state.rag_enabled = st.toggle(
        "📄 Document RAG",
        value=st.session_state.rag_enabled
    )

    uploaded_file = None

    if st.session_state.rag_enabled:
        st.markdown("### 📄 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload PDF or TXT",
            type=["pdf", "txt"]
        )

    st.session_state.uploaded_file = uploaded_file

    st.markdown("---")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.summary = ""
        st.session_state.doc_indexed = False
        st.rerun()
