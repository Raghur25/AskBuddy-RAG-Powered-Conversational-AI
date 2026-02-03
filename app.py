from dotenv import load_dotenv
load_dotenv()
import uuid

import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rag.loader import load_pdf, load_txt
from rag.vectorstore import get_chroma_client, create_collection
from rag.retriever import add_documents, retrieve_context

from db.crud import (
    get_messages,
    get_summary,
    save_message,
    save_summary
)


# ---------- UI IMPORTS ----------
from ui.header import render_header
from ui.sidebar import render_sidebar
from ui.chat import (
    render_empty_state,
    render_user_message,
    render_ai_stream
)
from ui.chat import render_latest_messages


# ---------- PAGE CONFIG (MUST BE FIRST STREAMLIT CALL) ----------
st.set_page_config(
    page_title="AskBuddy",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- LOAD CSS ----------
def load_css(path: str):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("ui/styles.css")

# ---------- CONFIG ----------
MAX_MESSAGES = 6

llm = ChatOpenAI(
    model="qwen3",
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = SystemMessage(
    content="""
You are AskBuddy, an AI QnA assistant.
Be concise, accurate, and clear.
Avoid unnecessary verbosity.
Explain concepts simply and give examples only when helpful.
"""
)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "rag_enabled" not in st.session_state:
    st.session_state.rag_enabled = False
    
if "vector_collection" not in st.session_state:
    client = get_chroma_client()
    st.session_state.vector_collection = create_collection(client)

if "session_id" not in st.session_state:
    st.session_state.session_id = st.query_params.get(
        "sid", str(uuid.uuid4())
    )
    st.query_params["sid"] = st.session_state.session_id

    
# ---------- LOAD CHAT FROM DB (ONCE) ----------
if "db_loaded" not in st.session_state:
    db_messages = get_messages(st.session_state.session_id)

    st.session_state.messages = [
        {"role": msg.role, "content": msg.content}
        for msg in db_messages
    ]

    st.session_state.summary = get_summary(st.session_state.session_id)
    st.session_state.db_loaded = True

    

# ---------- HANDLE DOCUMENT UPLOAD ----------
if st.session_state.rag_enabled and hasattr(st.session_state, "uploaded_file"):
    uploaded_file = st.session_state.uploaded_file

    if uploaded_file is not None:
        # Avoid re-indexing same file multiple times
        if st.session_state.get("last_uploaded_filename") != uploaded_file.name:

            if uploaded_file.type == "application/pdf":
                text = load_pdf(uploaded_file)
            else:
                text = load_txt(uploaded_file)

            add_documents(st.session_state.vector_collection, text)

            st.session_state.last_uploaded_filename = uploaded_file.name
            if not st.session_state.get("doc_indexed"):
                st.success(" Document indexed successfully")
                st.session_state.doc_indexed = True


# ---------- RENDER UI ----------
render_sidebar()
render_header()
render_empty_state()
render_latest_messages()

# ---------- USER INPUT ----------
query = st.chat_input("Ask anything…")

if query:
    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )
    
    # save user message
    save_message(
        st.session_state.session_id,
        "user",
        query
    )

    render_user_message(query)

    # ---------- MEMORY (SLIDING WINDOW SUMMARY ONLY) ----------
    if st.session_state.memory_enabled:
        if len(st.session_state.messages) > MAX_MESSAGES:
            old_messages = st.session_state.messages[:-MAX_MESSAGES]

            summary_prompt = [
                SystemMessage(
                    content="Summarize the conversation briefly and accurately."
                ),
                HumanMessage(
                    content="\n".join(
                        f"{m['role']}: {m['content']}" for m in old_messages
                    )
                )
            ]

            summary_response = llm.invoke(summary_prompt)

            st.session_state.summary = (
                st.session_state.summary + " " + summary_response.content.strip()
            ).strip()

            save_summary(
                st.session_state.session_id,
                st.session_state.summary
            )

            # keep only recent messages
            st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

    

    # ---------- BUILD CONTEXT ----------
    lc_messages = [SYSTEM_PROMPT]
     
    
    if (
        st.session_state.rag_enabled
        and st.session_state.get("last_uploaded_filename")
        ):
        context, sources = retrieve_context(
        st.session_state.vector_collection,
        query
        )
        
        st.session_state.last_sources = sources   


        lc_messages.append(
            SystemMessage(
                content=f"""
                    Use the following document context to answer the user's question.
                    If the answer is not found in the document, say you don't know.

                    Document context:
                    {context}
                        """
                )
            )



    if st.session_state.memory_enabled and st.session_state.summary:
        lc_messages.append(
            SystemMessage(
                content=f"Conversation summary so far: {st.session_state.summary}"
            )
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))

    # ---------- STREAM RESPONSE ----------
    try:
        full_response = render_ai_stream(llm, lc_messages)

        st.session_state.messages.append(
            {"role": "ai", "content": full_response}
        )
        
        save_message(
        st.session_state.session_id,
        "ai",
        full_response
        )
        
        
        # ---------- SHOW SOURCES UI (STEP 4) ----------
        if st.session_state.rag_enabled and st.session_state.get("last_sources"):
            with st.expander("📚 Sources used"):
                for i, src in enumerate(st.session_state.last_sources, 1):
                    st.markdown(f"**Source {i}:**")
                    st.markdown(src)
                    st.markdown("---")

    except Exception as e:
        st.error("⚠️ Model is not reachable")
        st.exception(e)
