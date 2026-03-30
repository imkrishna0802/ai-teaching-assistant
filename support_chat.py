import streamlit as st

def get_support_response(user_message: str) -> str:
    msg = user_message.lower().strip()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "Hi! I'm your support assistant. Ask me about setup issues, errors, or how to use this app."

    if "how to use" in msg or "use this app" in msg:
        return (
            "Use this app in 3 parts:\n\n"
            "1. Concept / Code Chat\n"
            "2. Code Feedback\n"
            "3. Instructor Dashboard"
        )

    if "faiss" in msg or "ingest" in msg or "course material" in msg:
        return (
            "Check that the `faiss_index` folder exists. "
            "If not, run `python ingest.py` and restart Streamlit."
        )

    if "module not found" in msg or "modulenotfounderror" in msg or "import error" in msg:
        return (
            "A dependency is missing. Try:\n\n"
            "`pip install -r requirements.txt`\n\n"
            "Or install specific packages like:\n"
            "- langchain-community\n"
            "- langchain-google-genai\n"
            "- sentence-transformers\n"
            "- faiss-cpu"
        )

    if "api key" in msg or "gemini" in msg:
        return (
            "Set your API key using:\n\n"
            "`export GOOGLE_API_KEY='your_key'`\n\n"
            "or add it in a `.env` file."
        )

    return (
        "I can help with:\n"
        "- app usage\n"
        "- FAISS issues\n"
        "- import/module errors\n"
        "- Gemini API key setup\n"
        "- dashboard/help issues"
    )


def render_support_chat():
    if "support_open" not in st.session_state:
        st.session_state.support_open = False

    if "support_messages" not in st.session_state:
        st.session_state.support_messages = [
            {
                "role": "assistant",
                "content": "Hi! I’m your support assistant 👋 Ask me anything about this app."
            }
        ]

    st.markdown("""
    <style>
    .support-toggle-wrap {
        position: fixed;
        left: 20px;
        bottom: 20px;
        z-index: 999999;
    }

    .support-panel {
        position: fixed;
        left: 20px;
        bottom: 95px;
        width: 360px;
        max-height: 520px;
        overflow-y: auto;
        background: rgba(6, 12, 28, 0.98);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        padding: 14px;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
        z-index: 999998;
    }

    .support-heading {
        font-size: 1rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .support-caption {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="support-toggle-wrap">', unsafe_allow_html=True)
        if st.button("🤖", key="floating_support_btn"):
            st.session_state.support_open = not st.session_state.support_open
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.support_open:
        st.markdown('<div class="support-panel">', unsafe_allow_html=True)
        st.markdown('<div class="support-heading">Support Chat</div>', unsafe_allow_html=True)
        st.markdown('<div class="support-caption">Help with setup, errors, and usage</div>', unsafe_allow_html=True)

        for msg in st.session_state.support_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_msg = st.text_input("Type your problem...", key="support_text_input")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send", key="send_support_msg"):
                if user_msg.strip():
                    st.session_state.support_messages.append({"role": "user", "content": user_msg})
                    reply = get_support_response(user_msg)
                    st.session_state.support_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

        with col2:
            if st.button("Close", key="close_support_panel"):
                st.session_state.support_open = False
                st.rerun()

        if st.button("Clear Chat", key="clear_support_chat_btn"):
            st.session_state.support_messages = [
                {
                    "role": "assistant",
                    "content": "Hi! I’m your support assistant 👋 Ask me anything about this app."
                }
            ]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)