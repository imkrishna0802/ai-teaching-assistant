from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from code_sandbox import run_python_code, SandboxResult

load_dotenv()


def get_code_feedback(code: str, language: str = "python") -> str:
    # 1) Run the code if Python (you can extend to Java later)
    if language.lower() != "python":
        run_info = SandboxResult(
            stdout="",
            stderr=f"Runtime not implemented for language: {language}",
            exit_code=-1,
            timeout=False,
        )
    else:
        run_info = run_python_code(code)

    # 2) Build analysis prompt
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )

    prompt = f"""
You are a programming tutor reviewing a student's code.

Language: {language}

Student's code:
```{language}
{code}
```

Program output:
STDOUT:
{run_info.stdout}

STDERR:
{run_info.stderr}

Exit code: {run_info.exit_code}
Timed out: {run_info.timeout}

Your tasks:
1. Briefly identify what the student is trying to do.
2. Explain whether the code is logically correct. If not, describe the bug in simple terms.
3. Give HINTS for fixing the code instead of directly giving a full solution.
4. Comment on style and readability (variable names, structure) with 2–3 concrete suggestions.
5. If the code timed out or crashed, explain why and how the student can debug it.

Keep the tone encouraging and focused on learning, not judging.
"""

    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)