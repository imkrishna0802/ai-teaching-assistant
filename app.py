import os
import streamlit as st
import pandas as pd

from rag_chain import load_rag_chain
from code_feedback import get_code_feedback
from router import classify_query
from logging_utils import log_interaction


st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 AI Teaching Assistant")
st.markdown("*Ask me anything about your course material, or get feedback on your code!*")
st.divider()

# Check FAISS index
if not os.path.exists("faiss_index"):
    st.error("⚠️ No course material loaded yet! Please run `ingest.py` first.")
    st.code("python ingest.py", language="bash")
    st.stop()


@st.cache_resource
def get_rag_chain():
    return load_rag_chain()


rag_chain = get_rag_chain()

tab_qna, tab_code, tab_dashboard = st.tabs(
    ["📚 Concept / Code Chat", "💻 Code Feedback (manual)", "📊 Instructor Dashboard"]
)

# --- Tab 1: Mixed Q&A with routing ---
with tab_qna:
    st.markdown("Ask conceptual questions or paste code with errors; I will decide whether to explain or debug.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question or paste code..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        intent = classify_query(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Handling your {intent} question..."):
                try:
                    if intent == "code":
                        answer = get_code_feedback(prompt, "python")
                    else:
                        answer = rag_chain(prompt)
                except Exception as e:
                    answer = "Sorry, something went wrong while processing your request."
                    st.error(str(e))
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        log_interaction(prompt, answer, intent)

# --- Tab 2: Code Feedback (explicit) ---
with tab_code:
    st.subheader("Get feedback on your code")
    language = st.selectbox("Language", ["Python"], index=0)
    code = st.text_area("Paste your code here:", height=220)

    if st.button("Analyze code", type="primary"):
        if not code.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Running and analyzing your code..."):
                try:
                    feedback = get_code_feedback(code, language)
                except Exception as e:
                    feedback = "Sorry, something went wrong while analyzing your code."
                    st.error(str(e))
            st.markdown("### Tutor Feedback")
            st.markdown(feedback)
            log_interaction(code, feedback, intent="code_manual")

# --- Tab 3: Instructor Dashboard ---
with tab_dashboard:
    st.subheader("Instructor Dashboard")

    log_path = "logs/interactions.csv"
    if not os.path.exists(log_path):
        st.info("No data yet. Interact with the assistant to generate logs.")
    else:
        df = pd.read_csv(log_path)

        st.markdown("**Total interactions:** " + str(len(df)))

        if "intent" in df.columns:
            st.markdown("#### Questions by type")
            intent_counts = df["intent"].value_counts()
            st.bar_chart(intent_counts)

        df["question_len"] = df["question"].astype(str).str.len()
        st.markdown("**Average question length:** " + str(round(df["question_len"].mean(), 2)))

        st.markdown("#### Recent interactions")
        st.dataframe(df.tail(20), use_container_width=True)