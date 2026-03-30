import os
import pandas as pd
import streamlit as st

from chatbot import get_chatbot_response
from code_feedback import get_code_feedback
from router import classify_query
from logging_utils import log_interaction


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "support_open" not in st.session_state:
    st.session_state.support_open = False

if "support_messages" not in st.session_state:
    st.session_state.support_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I’m your support assistant 👋\n\n"
                "Ask me about setup issues, app usage, code feedback problems, "
                "FAISS indexing, API key errors, or dashboard issues."
            ),
        }
    ]


# ---------------- SUPPORT CHATBOT ----------------
def get_support_response(user_message: str) -> str:
    msg = user_message.lower().strip()

    if any(word in msg for word in ["hi", "hello", "hey", "hii"]):
        return (
            "Hello! I’m your support assistant.\n\n"
            "I can help with:\n"
            "- how to use this app\n"
            "- concept chat issues\n"
            "- code feedback issues\n"
            "- FAISS / ingest problems\n"
            "- missing package errors\n"
            "- Gemini API key setup\n"
            "- dashboard issues"
        )

    if "how to use" in msg or "use this app" in msg or "how does this work" in msg:
        return (
            "You can use this app in 3 parts:\n\n"
            "1. **Concept / Code Chat** → Ask doubts from course material.\n"
            "2. **Code Feedback** → Paste code and get debugging help.\n"
            "3. **Instructor Dashboard** → See interaction stats and logs."
        )

    if "faiss" in msg or "course material" in msg or "documents" in msg or "pdf" in msg or "ingest" in msg:
        return (
            "If course-material answers are not working, check these:\n\n"
            "1. Make sure the `faiss_index` folder exists.\n"
            "2. If it does not exist, run:\n"
            "   `python ingest.py`\n"
            "3. Restart Streamlit after indexing is complete."
        )

    if "modulenotfounderror" in msg or "module not found" in msg or "import error" in msg:
        return (
            "A package is missing. Try:\n\n"
            "`pip install -r requirements.txt`\n\n"
            "If needed, install specific packages:\n"
            "- `pip install langchain-community`\n"
            "- `pip install langchain-google-genai`\n"
            "- `pip install sentence-transformers`\n"
            "- `pip install faiss-cpu`\n"
            "- `pip install python-dotenv`"
        )

    if "api key" in msg or "google api key" in msg or "gemini" in msg:
        return (
            "Make sure your Gemini key is set correctly.\n\n"
            "Example in terminal:\n"
            "`export GOOGLE_API_KEY='your_api_key'`\n\n"
            "Or place it in a `.env` file:\n"
            "`GOOGLE_API_KEY=your_api_key`"
        )

    if "code feedback" in msg or "analyze code" in msg or "debug" in msg or "bug" in msg:
        return (
            "To use **Code Feedback**:\n\n"
            "1. Open the **Code Feedback** tab.\n"
            "2. Paste your code.\n"
            "3. Click **Analyze code**.\n\n"
            "If it fails, check whether your required packages are installed and whether your model/API setup is working."
        )

    if "dashboard" in msg or "logs" in msg or "analytics" in msg:
        return (
            "The dashboard reads data from:\n\n"
            "`logs/interactions.csv`\n\n"
            "If nothing shows there, interact with the app first and make sure `log_interaction()` is being called successfully."
        )

    if "streamlit" in msg or "localhost" in msg or "app not running" in msg or "how to run" in msg:
        return (
            "Run the app using:\n\n"
            "`streamlit run app.py`\n\n"
            "Then open the localhost URL shown in the terminal."
        )

    if "support button" in msg or "chat button" in msg or "bottom left" in msg:
        return (
            "The support button is the floating 🤖 button at the bottom-left corner. "
            "Click it to open the support chat."
        )

    return (
        "I can help with setup and common issues.\n\n"
        "Try asking things like:\n"
        "- How do I use this app?\n"
        "- Why is FAISS not loading?\n"
        "- Why am I getting ModuleNotFoundError?\n"
        "- How do I fix Gemini API key issues?\n"
        "- Why is the dashboard empty?"
    )


def render_support_chat():
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

    .support-btn button {
        width: 62px !important;
        height: 62px !important;
        border-radius: 999px !important;
        border: none !important;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
        color: white !important;
        font-size: 1.5rem !important;
        box-shadow: 0 18px 40px rgba(6, 182, 212, 0.30) !important;
    }

    .support-panel .stTextInput input {
        background: rgba(15, 23, 42, 0.92) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        border-radius: 12px !important;
    }

    @media (max-width: 900px) {
        .support-toggle-wrap {
            left: 14px;
            bottom: 14px;
        }

        .support-panel {
            left: 14px;
            bottom: 84px;
            width: calc(100vw - 28px);
            max-width: 360px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="support-toggle-wrap support-btn">', unsafe_allow_html=True)
        if st.button("🤖", key="floating_support_btn"):
            st.session_state.support_open = not st.session_state.support_open
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.support_open:
        st.markdown('<div class="support-panel">', unsafe_allow_html=True)
        st.markdown('<div class="support-heading">Support Chat</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="support-caption">Help with setup, errors, and app usage</div>',
            unsafe_allow_html=True
        )

        quick1, quick2 = st.columns(2)
        with quick1:
            if st.button("How to use", key="quick_use_btn"):
                user_msg = "How do I use this app?"
                st.session_state.support_messages.append({"role": "user", "content": user_msg})
                st.session_state.support_messages.append(
                    {"role": "assistant", "content": get_support_response(user_msg)}
                )
                st.rerun()

            if st.button("Fix FAISS", key="quick_faiss_btn"):
                user_msg = "FAISS is not working"
                st.session_state.support_messages.append({"role": "user", "content": user_msg})
                st.session_state.support_messages.append(
                    {"role": "assistant", "content": get_support_response(user_msg)}
                )
                st.rerun()

        with quick2:
            if st.button("API key help", key="quick_api_btn"):
                user_msg = "How to set Gemini API key?"
                st.session_state.support_messages.append({"role": "user", "content": user_msg})
                st.session_state.support_messages.append(
                    {"role": "assistant", "content": get_support_response(user_msg)}
                )
                st.rerun()

            if st.button("Import error", key="quick_import_btn"):
                user_msg = "ModuleNotFoundError"
                st.session_state.support_messages.append({"role": "user", "content": user_msg})
                st.session_state.support_messages.append(
                    {"role": "assistant", "content": get_support_response(user_msg)}
                )
                st.rerun()

        st.markdown("---")

        for msg in st.session_state.support_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        support_prompt = st.text_input("Type your support message...", key="support_text_input")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Send", key="send_support_btn"):
                if support_prompt.strip():
                    st.session_state.support_messages.append({"role": "user", "content": support_prompt})
                    support_answer = get_support_response(support_prompt)
                    st.session_state.support_messages.append({"role": "assistant", "content": support_answer})
                    log_interaction(support_prompt, support_answer, intent="support")
                    st.rerun()

        with c2:
            if st.button("Clear", key="clear_support_btn"):
                st.session_state.support_messages = [
                    {
                        "role": "assistant",
                        "content": (
                            "Hi! I’m your support assistant 👋\n\n"
                            "Ask me about setup issues, app usage, code feedback problems, "
                            "FAISS indexing, API key errors, or dashboard issues."
                        ),
                    }
                ]
                st.rerun()

        with c3:
            if st.button("Close", key="close_support_btn"):
                st.session_state.support_open = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------- CUSTOM CSS ----------------
def load_custom_css():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(168, 85, 247, 0.16), transparent 24%),
            radial-gradient(circle at bottom left, rgba(34, 211, 238, 0.16), transparent 26%),
            linear-gradient(180deg, #020617 0%, #020617 100%);
        color: #e5e7eb;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .top-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(129, 140, 248, 0.22);
        color: #c4b5fd;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: clamp(2.2rem, 5vw, 4rem);
        font-weight: 800;
        line-height: 1.08;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #ffffff 0%, #c4b5fd 45%, #67e8f9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        line-height: 1.8;
        max-width: 760px;
        margin-bottom: 1.5rem;
    }

    .glass-card {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
    }

    .feature-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 18px;
        padding: 18px;
        min-height: 140px;
    }

    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .feature-text {
        color: #94a3b8;
        font-size: 0.92rem;
        line-height: 1.65;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 18px;
        color: #cbd5e1;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.16), rgba(6, 182, 212, 0.16));
        color: white !important;
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.92) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        border-radius: 14px !important;
    }

    .stSelectbox > div > div {
        background: rgba(15, 23, 42, 0.92) !important;
        border-radius: 14px !important;
    }

    .stButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        background: rgba(15, 23, 42, 0.92) !important;
        color: white !important;
        font-weight: 650 !important;
    }

    .stButton > button:hover {
        border-color: rgba(139, 92, 246, 0.45) !important;
    }

    [data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.62);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 18px;
        padding: 10px;
    }

    .section-heading {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.15rem;
    }

    .section-sub {
        color: #94a3b8;
        margin-bottom: 1rem;
    }

    .metric-chip {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }

    .metric-num {
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 800;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------- DATA CHECK ----------------
if not os.path.exists("faiss_index"):
    st.error("⚠️ No course material loaded yet! Please run `ingest.py` first.")
    st.code("python ingest.py", language="bash")
    st.stop()


# ---------------- LOAD CSS ----------------
load_custom_css()


# ---------------- HERO ----------------
hero_col1, hero_col2 = st.columns([1.3, 0.7], gap="large")

with hero_col1:
    st.markdown('<div class="top-badge">AI-powered teaching platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">Your personal AI tutor for concepts, coding, and feedback.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'Ask questions from your course material, debug code, and review learning activity '
        'through a simple interface designed for students and instructors.'
        '</div>',
        unsafe_allow_html=True
    )

with hero_col2:
    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:1rem;font-weight:700;color:#f8fafc;margin-bottom:8px;">Quick Overview</div>
            <div style="color:#94a3b8;line-height:1.8;font-size:0.95rem;">
                • Concept explanations<br>
                • Code debugging support<br>
                • Manual code review<br>
                • Interaction analytics
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")

f1, f2, f3 = st.columns(3, gap="medium")
with f1:
    st.markdown(
        """
        <div class="feature-box">
            <div class="feature-title">📚 Concept Chat</div>
            <div class="feature-text">
                Ask doubts from your course material and get clear, easy-to-understand explanations.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f2:
    st.markdown(
        """
        <div class="feature-box">
            <div class="feature-title">💻 Code Feedback</div>
            <div class="feature-text">
                Paste your code and receive help with bugs, improvements, and logic corrections.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:
    st.markdown(
        """
        <div class="feature-box">
            <div class="feature-title">📊 Dashboard</div>
            <div class="feature-text">
                Track interaction history, question types, and recent learning activity.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")


# ---------------- TABS ----------------
tab_qna, tab_code, tab_dashboard = st.tabs(
    ["📚 Concept / Code Chat", "💻 Code Feedback", "📊 Instructor Dashboard"]
)


# ---------------- TAB 1 ----------------
with tab_qna:
    st.markdown('<div class="section-heading">Ask anything</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Ask conceptual questions or paste code. The assistant will explain or debug based on your input.</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a question or paste code...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        intent = classify_query(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Handling your {intent} request..."):
                try:
                    if intent == "code":
                        answer = get_code_feedback(prompt, "python")
                    else:
                        answer = get_chatbot_response(prompt)
                except Exception as e:
                    answer = "Sorry, something went wrong while processing your request."
                    st.error(str(e))

            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        log_interaction(prompt, answer, intent)

    if st.button("Clear Main Chat"):
        st.session_state.messages = []
        st.rerun()


# ---------------- TAB 2 ----------------
with tab_code:
    st.markdown('<div class="section-heading">Manual code review</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Paste your code below and get detailed feedback from the assistant.</div>',
        unsafe_allow_html=True
    )

    language = st.selectbox("Language", ["Python"], index=0)
    code = st.text_area("Paste your code here:", height=280)

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


# ---------------- TAB 3 ----------------
with tab_dashboard:
    st.markdown('<div class="section-heading">Instructor Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">View interaction stats and recent activity.</div>',
        unsafe_allow_html=True
    )

    log_path = "logs/interactions.csv"

    if not os.path.exists(log_path):
        st.info("No data yet. Interact with the assistant to generate logs.")
    else:
        df = pd.read_csv(log_path)

        total_interactions = len(df)

        avg_len = 0
        if "question" in df.columns and len(df) > 0:
            df["question_len"] = df["question"].astype(str).str.len()
            avg_len = round(df["question_len"].mean(), 2)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"""
                <div class="metric-chip">
                    <div class="metric-num">{total_interactions}</div>
                    <div class="metric-label">Total Interactions</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-chip">
                    <div class="metric-num">{avg_len}</div>
                    <div class="metric-label">Average Question Length</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("")

        if "intent" in df.columns:
            st.markdown("#### Questions by type")
            intent_counts = df["intent"].value_counts()
            st.bar_chart(intent_counts)

        st.markdown("#### Recent interactions")
        st.dataframe(df.tail(20), use_container_width=True)


# ---------------- FLOATING SUPPORT CHAT ----------------
render_support_chat()