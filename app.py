import streamlit as st
from rag_chain import load_rag_chain
from code_feedback import get_code_feedback
import os

st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 AI Teaching Assistant")
st.markdown("*Ask me anything about your course material, or get feedback on your code!*")
st.divider()

if not os.path.exists("faiss_index"):
    st.error("⚠️ No course material loaded yet! Please run `ingest.py` first.")
    st.code("python ingest.py", language="bash")
    st.stop()

@st.cache_resource
def get_rag_chain():
    return load_rag_chain()

rag_chain = get_rag_chain()

tab_qna, tab_code = st.tabs(["📚 Concept Q&A", "💻 Code Feedback"])

# --- Tab 1: RAG Q&A ---
with tab_qna:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your course..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = rag_chain(prompt)
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

# --- Tab 2: Code Feedback ---
with tab_code:
    st.subheader("Get feedback on your code")
    language = st.selectbox("Language", ["Python"], index=0)
    code = st.text_area("Paste your code here:", height=220)

    if st.button("Analyze code", type="primary"):
        if not code.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Running and analyzing your code..."):
                feedback = get_code_feedback(code, language)
            st.markdown("### Tutor Feedback")
            st.markdown(feedback)