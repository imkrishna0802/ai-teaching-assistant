import streamlit as st
from zoiee import zoiee_chat, generate_study_plan, generate_quiz, grade_quiz


def _init_state():
    defaults = {
        "zoiee_messages": [{"role": "assistant", "content": "Hi! I'm **Zoiee**, your personal AI study buddy! Ask me anything, request a study plan, or take a quiz. Let's learn together!"}],
        "zoiee_tab": "Chat",
        "quiz_questions": [],
        "quiz_answers": [],
        "quiz_submitted": False,
        "quiz_result": None,
        "study_plan_output": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _zoiee_css():
    st.markdown("""
    <style>
    .zoiee-header {
        background: linear-gradient(135deg, #6366f1, #06b6d4);
        border-radius: 20px;
        padding: 20px 28px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .zoiee-name {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        letter-spacing: 1px;
    }
    .zoiee-tagline {
        color: rgba(255,255,255,0.82);
        font-size: 0.95rem;
        margin-top: 2px;
    }
    .quiz-option-correct {
        background: rgba(34,197,94,0.15);
        border: 1px solid rgba(34,197,94,0.4);
        border-radius: 10px;
        padding: 8px 14px;
        color: #86efac;
    }
    .quiz-option-wrong {
        background: rgba(239,68,68,0.15);
        border: 1px solid rgba(239,68,68,0.4);
        border-radius: 10px;
        padding: 8px 14px;
        color: #fca5a5;
    }
    .score-card {
        background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(6,182,212,0.18));
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #818cf8, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .score-remark {
        color: #cbd5e1;
        font-size: 1rem;
        margin-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── CHAT TAB ────────────────────────────────────────────────────────────────

def _render_chat():
    for msg in st.session_state.zoiee_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask Zoiee anything...")
    if user_input:
        st.session_state.zoiee_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Zoiee is thinking..."):
                reply = zoiee_chat(user_input, st.session_state.zoiee_messages[:-1])
            st.markdown(reply)

        st.session_state.zoiee_messages.append({"role": "assistant", "content": reply})

    if st.button("Clear Chat", key="zoiee_clear_chat"):
        st.session_state.zoiee_messages = [
            {"role": "assistant", "content": "Chat cleared! I'm Zoiee — ready to help you learn!"}
        ]
        st.rerun()


# ─── STUDY PLAN TAB ──────────────────────────────────────────────────────────

def _render_study_plan():
    st.markdown("#### Generate a personalised study plan")

    col1, col2, col3 = st.columns(3)
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. Python basics, Data Structures")
    with col2:
        days = st.number_input("Days", min_value=1, max_value=30, value=7)
    with col3:
        hours = st.number_input("Hours/day", min_value=0.5, max_value=12.0, value=2.0, step=0.5)

    if st.button("Generate Study Plan", type="primary", key="gen_plan_btn"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Zoiee is crafting your study plan..."):
                plan = generate_study_plan(topic.strip(), int(days), hours)
            st.session_state.study_plan_output = plan

    if st.session_state.study_plan_output:
        st.markdown("---")
        st.markdown(st.session_state.study_plan_output)
        st.download_button(
            label="Download Study Plan",
            data=st.session_state.study_plan_output,
            file_name="zoiee_study_plan.md",
            mime="text/markdown",
            key="download_plan_btn"
        )


# ─── QUIZ TAB ────────────────────────────────────────────────────────────────

def _render_quiz():
    st.markdown("#### Take a quiz and get instant results")

    if not st.session_state.quiz_questions:
        col1, col2, col3 = st.columns(3)
        with col1:
            q_topic = st.text_input("Quiz Topic", placeholder="e.g. Java OOP, Python loops")
        with col2:
            num_q = st.selectbox("Questions", [3, 5, 7, 10], index=1)
        with col3:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Start Quiz", type="primary", key="start_quiz_btn"):
            if not q_topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Zoiee is preparing your quiz..."):
                    questions = generate_quiz(q_topic.strip(), num_q, difficulty)
                if not questions:
                    st.error("Could not generate quiz. Please try a different topic.")
                else:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = [-1] * len(questions)
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_result = None
                    st.rerun()

    elif not st.session_state.quiz_submitted:
        st.markdown(f"**{len(st.session_state.quiz_questions)} questions — answer all and submit!**")
        st.markdown("---")

        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            choice = st.radio(
                label=f"q_{i}",
                options=q["options"],
                index=None,
                key=f"quiz_q_{i}",
                label_visibility="collapsed"
            )
            if choice is not None:
                st.session_state.quiz_answers[i] = q["options"].index(choice)
            st.markdown("")

        col_sub, col_reset = st.columns([1, 4])
        with col_sub:
            if st.button("Submit Quiz", type="primary", key="submit_quiz_btn"):
                if -1 in st.session_state.quiz_answers:
                    st.warning("Please answer all questions before submitting.")
                else:
                    result = grade_quiz(
                        st.session_state.quiz_questions,
                        st.session_state.quiz_answers
                    )
                    st.session_state.quiz_result = result
                    st.session_state.quiz_submitted = True
                    st.rerun()
        with col_reset:
            if st.button("Cancel Quiz", key="cancel_quiz_btn"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = []
                st.rerun()

    else:
        result = st.session_state.quiz_result
        st.markdown(
            f"""<div class="score-card">
                <div class="score-number">{result['score']} / {result['total']}</div>
                <div style="color:#94a3b8;font-size:1.1rem;">{result['percentage']}%</div>
                <div class="score-remark">{result['remark']}</div>
            </div>""",
            unsafe_allow_html=True
        )

        st.markdown("#### Review Answers")
        for i, r in enumerate(result["results"]):
            icon = "✅" if r["is_correct"] else "❌"
            with st.expander(f"{icon} Q{i+1}. {r['question']}"):
                if r["is_correct"]:
                    st.markdown(f'<div class="quiz-option-correct">Your answer: {r["your_answer"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quiz-option-wrong">Your answer: {r["your_answer"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quiz-option-correct">Correct answer: {r["correct_answer"]}</div>', unsafe_allow_html=True)
                st.info(f"**Explanation:** {r['explanation']}")

        if st.button("Take Another Quiz", type="primary", key="retry_quiz_btn"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_result = None
            st.rerun()


# ─── MAIN RENDER ─────────────────────────────────────────────────────────────

def render_zoiee():
    _init_state()
    _zoiee_css()

    st.markdown("""
    <div class="zoiee-header">
        <div style="font-size:2.4rem;">🤖</div>
        <div>
            <div class="zoiee-name">Zoiee</div>
            <div class="zoiee-tagline">Your AI study buddy — chat, plan, and quiz your way to success!</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    chat_tab, plan_tab, quiz_tab = st.tabs(["💬 Chat with Zoiee", "📅 Study Plan", "🧠 Quiz"])

    with chat_tab:
        _render_chat()

    with plan_tab:
        _render_study_plan()

    with quiz_tab:
        _render_quiz()
