import streamlit as st

def render_header():
    st.markdown(
        "<h2 style='text-align:center;'>🤖 AskBuddy</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:gray;'>Your AI assistant with memory</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
