import streamlit as st

def render_empty_state():
    if not st.session_state.messages:
        st.markdown(
            """
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 45vh;
                color: #9ca3af;
                font-size: 1.35rem;
            ">
                Ask me anything..?
            </div>
            """,
            unsafe_allow_html=True
        )


def render_latest_messages(limit: int = 2):
    """
    Show only the last N messages in main chat UI
    """
    for message in st.session_state.messages[-limit:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_user_message(query: str):
    with st.chat_message("user"):
        st.markdown(query)


def render_ai_stream(llm, lc_messages):
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for chunk in llm.stream(lc_messages):
            if chunk.content:
                full_response += chunk.content
                placeholder.markdown(full_response)

    return full_response
