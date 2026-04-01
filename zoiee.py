import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
_llm_strict = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)


def _invoke(llm, prompt: str) -> str:
    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)


# ─── CHAT ────────────────────────────────────────────────────────────────────

def zoiee_chat(user_message: str, history: list[dict]) -> str:
    history_text = ""
    for msg in history[-6:]:
        role = "Student" if msg["role"] == "user" else "Zoiee"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are Zoiee, a friendly and encouraging AI study assistant.
You help students learn, create study plans, and quiz them on topics.
Keep responses concise, warm, and motivating.

Conversation so far:
{history_text}
Student: {user_message}
Zoiee:"""
    return _invoke(_llm, prompt)


# ─── STUDY PLAN ──────────────────────────────────────────────────────────────

def generate_study_plan(topic: str, days: int, hours_per_day: float) -> str:
    prompt = f"""You are Zoiee, an expert study planner.
Create a detailed {days}-day study plan for the topic: "{topic}"
The student can study {hours_per_day} hours per day.

Format the plan exactly like this:
## Day 1 — <title>
- **Goal:** <what to achieve>
- **Topics:** <specific subtopics>
- **Activities:** <reading, practice, exercises>
- **Time:** {hours_per_day} hours

Repeat for each day. End with a short motivational note.
Be specific, practical, and encouraging."""
    return _invoke(_llm, prompt)


# ─── QUIZ ────────────────────────────────────────────────────────────────────

def generate_quiz(topic: str, num_questions: int, difficulty: str) -> list[dict]:
    prompt = f"""You are Zoiee. Generate a quiz on "{topic}".
Difficulty: {difficulty}
Number of questions: {num_questions}

Return ONLY a valid JSON array. No explanation, no markdown, no code block.
Each item must have exactly these keys:
- "question": string
- "options": array of exactly 4 strings (A, B, C, D without the letter prefix)
- "answer": integer 0-3 (index of correct option)
- "explanation": string (brief explanation of the correct answer)

Example:
[{{"question":"What is X?","options":["A","B","C","D"],"answer":0,"explanation":"Because..."}}]"""

    raw = _invoke(_llm_strict, prompt)

    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    try:
        questions = json.loads(raw)
        # Validate structure
        validated = []
        for q in questions:
            if all(k in q for k in ("question", "options", "answer", "explanation")):
                if isinstance(q["options"], list) and len(q["options"]) == 4:
                    if isinstance(q["answer"], int) and 0 <= q["answer"] <= 3:
                        validated.append(q)
        return validated
    except (json.JSONDecodeError, ValueError):
        return []


def grade_quiz(questions: list[dict], user_answers: list[int]) -> dict:
    score = 0
    results = []
    for i, (q, user_ans) in enumerate(zip(questions, user_answers)):
        correct = q["answer"]
        is_correct = user_ans == correct
        if is_correct:
            score += 1
        results.append({
            "question": q["question"],
            "your_answer": q["options"][user_ans] if user_ans >= 0 else "Not answered",
            "correct_answer": q["options"][correct],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    total = len(questions)
    percentage = round((score / total) * 100) if total > 0 else 0

    if percentage >= 90:
        remark = "Outstanding! You've mastered this topic!"
    elif percentage >= 75:
        remark = "Great job! A little more practice and you'll ace it!"
    elif percentage >= 50:
        remark = "Good effort! Review the explanations and try again."
    else:
        remark = "Keep going! Every attempt makes you stronger. Review and retry!"

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "remark": remark,
        "results": results,
    }
