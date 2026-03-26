import streamlit as st

# ---------- BASIC PAGE SETUP ----------
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
)

# ---------- FLOATING BOT (CSS + HTML via markdown) ----------
FLOATING_BOT = """
<style>
#float-bot {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00e0ff, #007bff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.35);
  cursor: pointer;
  z-index: 9999;
  animation: float 3s ease-in-out infinite;
}
#float-bot img {
  width: 60%;
}
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%    { transform: translateY(-10px); }
}

/* typing animation dots used in chat */
.typing-dot {
  width: 8px;
  height: 8px;
  margin: 0 2px;
  border-radius: 50%;
  background: #22d3ee;
  display: inline-block;
  animation: blink 1s infinite alternate;
}
.typing-dot:nth-child(2) { animation-delay: .2s; }
.typing-dot:nth-child(3) { animation-delay: .4s; }

@keyframes blink {
  from { opacity: 0.2; transform: translateY(0); }
  to   { opacity: 1;   transform: translateY(-2px); }
}
</style>

<div id="float-bot">
  <img src="app/static/bot.png">
</div>
"""

st.markdown(FLOATING_BOT, unsafe_allow_html=True)

# ---------- MAIN HEADER ----------
st.title("AI Teaching Assistant")
st.caption("Ask me about your course material or get feedback on your code.")

# ---------- LAYOUT WITH TABS ----------
tab1, tab2, tab3 = st.tabs(
    ["💬 Concept / Code Chat", "🧑‍💻 Code Feedback (manual)", "📊 Instructor Dashboard"]
)

# ---------- SESSION STATE FOR CHAT ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

BOT_AVATAR_URL = "app/static/bot.png"   # served via static folder

# ---------- TAB 1: CHAT ----------
with tab1:
    st.subheader("Chat with your AI Tutor")

    # Show existing conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", None)):
            st.markdown(msg["content"])

    # User input at the bottom
    prompt = st.chat_input("Ask anything about concepts or code...")

    if prompt:
        # 1. show user message
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "avatar": "👨‍🎓"}
        )
        with st.chat_message("user", avatar="👨‍🎓"):
            st.markdown(prompt)

        # 2. show typing animation (fake streaming)
        with st.chat_message("assistant", avatar=BOT_AVATAR_URL):
            typing_placeholder = st.empty()
            typing_placeholder.markdown(
                '<span class="typing-dot"></span>'
                '<span class="typing-dot"></span>'
                '<span class="typing-dot"></span>',
                unsafe_allow_html=True,
            )

        # 3. here you would call your real LLM / backend
        # For demo, just echo
        answer = (
            f"I received: `{prompt}`.\n\n"
            "(Here I would explain the concept or review your code.)"
        )

        # 4. replace typing dots with real answer
        with st.chat_message("assistant", avatar=BOT_AVATAR_URL):
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "avatar": BOT_AVATAR_URL}
        )

# ---------- TAB 2: MANUAL CODE FEEDBACK ----------
with tab2:
    st.subheader("Get feedback on your code")

    lang = st.selectbox("Language", ["Python", "Java", "C++"])
    code = st.text_area("Paste your code here:", height=220)
    if st.button("Analyze code"):
        st.info("This is where you'll call your code analysis logic.")

# ---------- TAB 3: INSTRUCTOR DASHBOARD ----------
with tab3:
    st.subheader("Instructor dashboard (placeholder)")
    st.write("You can add analytics and student progress here later.")