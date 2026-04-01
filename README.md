# AI Teaching Assistant

An AI-powered teaching platform built for students and instructors. It combines course-material Q&A, code feedback, an instructor analytics dashboard, and **Zoiee** — a personal AI study buddy that chats, builds study plans, and runs quizzes.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Ingesting Course Material](#ingesting-course-material)
- [Security Fixes Applied](#security-fixes-applied)

---

## Overview

The AI Teaching Assistant is a Streamlit web application that lets students ask questions from their course material, get code reviewed and debugged, and interact with Zoiee — an AI study companion. Instructors can monitor all interactions through a built-in analytics dashboard.

The app uses **Retrieval-Augmented Generation (RAG)** to ground answers in actual course documents (PDFs), so responses are relevant and accurate to the syllabus.

---

## Features

### 📚 Concept / Code Chat
- Ask any question from the course material
- The app automatically detects whether the question is conceptual or code-related
- Conceptual questions are answered using RAG (course PDFs + Gemini LLM)
- Code questions are routed to the code feedback engine

### 💻 Code Feedback
- Paste any Python code and get detailed AI feedback
- Code is executed in a sandboxed subprocess with a timeout
- Feedback covers: logic correctness, bug hints, style suggestions, and debugging tips
- Encourages learning — gives hints, not direct solutions

### 📊 Instructor Dashboard
- Tracks every interaction (question, answer, intent, timestamp)
- Displays total interactions and average question length
- Bar chart breakdown of question types (concept vs code vs support)
- Table of the 20 most recent interactions

### 🤖 Zoiee — AI Study Buddy
- **Chat:** Conversational AI assistant with short-term memory (last 6 messages)
- **Study Plan:** Generates a personalised day-by-day study plan based on topic, number of days, and hours per day. Downloadable as a Markdown file
- **Quiz:** Generates MCQ quizzes on any topic with configurable difficulty (Easy / Medium / Hard) and question count. Grades answers instantly, shows score, percentage, motivational remark, and per-question explanations

### 💬 Floating Support Chat
- Always-visible support bot in the bottom-left corner
- Handles common issues: FAISS setup, API key errors, missing packages, app usage

---

## Project Structure

```
ai-teaching-assistant/
│
├── app.py                  # Main Streamlit app — all tabs and UI
├── chatbot.py              # Loads RAG chain and exposes get_chatbot_response()
├── rag_chain.py            # RAG pipeline: embeddings + FAISS + Gemini LLM
├── code_feedback.py        # Code analysis using Gemini with sandbox output
├── code_sandbox.py         # Runs Python code in a subprocess with timeout
├── sandbox_runner.py       # Docker-based multi-language code execution (Python, Java, C, C++)
├── router.py               # Classifies user input as 'code' or 'concept'
├── ingest.py               # Loads PDFs, chunks them, builds FAISS index
├── logging_utils.py        # Logs every interaction to logs/interactions.csv
├── zoiee.py                # Zoiee AI engine: chat, study plan, quiz generation & grading
├── zoiee_ui.py             # Zoiee Streamlit UI (chat, study plan, quiz tabs)
├── support_chat.py         # Standalone support chat component
├── test_embed.py           # Quick test script for Google embedding API
│
├── documents/              # Drop your course PDFs here
│   └── java_intro.pdf.pdf
│
├── faiss_index/            # Auto-generated after running ingest.py
│   ├── index.faiss
│   └── index.pkl
│
├── logs/
│   └── interactions.csv    # Auto-generated interaction log
│
├── static/
│   └── bot.png
│
├── docker/
│   ├── cpp/Dockerfile      # Docker image for C/C++ sandbox
│   └── java/Dockerfile     # Docker image for Java sandbox
│
├── .streamlit/
│   └── config.toml         # Streamlit server config
│
├── .env                    # API keys (not committed to git)
└── README.md
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **Streamlit** | Web UI framework — tabs, chat, forms, charts |
| **HTML / CSS** | Custom dark-themed styling injected via `st.markdown` |

### AI & LLM
| Technology | Purpose |
|---|---|
| **Google Gemini 2.5 Flash** (`gemini-2.5-flash`) | Main LLM for all AI responses — chat, code feedback, study plans, quiz generation |
| **LangChain** (`langchain`, `langchain-core`, `langchain-community`) | LLM orchestration, document loading, text splitting, vector store integration |
| **langchain-google-genai** | LangChain wrapper for Google Generative AI / Gemini |

### Embeddings & Vector Search
| Technology | Purpose |
|---|---|
| **HuggingFace Sentence Transformers** (`sentence-transformers/all-MiniLM-L6-v2`) | Converts text chunks into vector embeddings |
| **FAISS** (`faiss-cpu`) | Local vector store for fast similarity search over course documents |

### Document Processing
| Technology | Purpose |
|---|---|
| **PyPDFLoader** (`langchain-community`) | Loads and parses PDF course materials |
| **RecursiveCharacterTextSplitter** | Splits documents into 500-character chunks with 50-character overlap |

### Code Execution
| Technology | Purpose |
|---|---|
| **Python subprocess** | Runs student Python code in an isolated subprocess with a 3-second timeout |
| **Docker** | Containerised sandbox for multi-language execution (Java, C, C++) with CPU/memory limits |
| **tempfile** | Creates temporary files for safe code execution |

### Data & Logging
| Technology | Purpose |
|---|---|
| **pandas** | Reads and displays interaction logs in the dashboard |
| **CSV** | Flat-file storage for interaction logs (`logs/interactions.csv`) |
| **python-dotenv** | Loads environment variables from `.env` file |

### Security
| Technology | Purpose |
|---|---|
| **os.path.realpath** | Path traversal prevention in sandbox file handling |
| **Input sanitization (regex)** | Strips control characters from user queries before LLM/vector store use |
| **Allowlists** | Docker image and filename allowlists in sandbox runner |
| **shell=False** | All subprocess calls use list-based commands, no shell injection risk |

---

## How It Works

### RAG Pipeline (Concept Chat)
```
PDF Documents
     ↓
PyPDFLoader → RecursiveCharacterTextSplitter (500 chars, 50 overlap)
     ↓
HuggingFace Embeddings (all-MiniLM-L6-v2)
     ↓
FAISS Vector Store (saved to faiss_index/)
     ↓
User Query → Sanitize → Similarity Search (top 3 chunks)
     ↓
Gemini 2.5 Flash (context + question → answer)
```

### Code Feedback Pipeline
```
User pastes code
     ↓
code_sandbox.py → subprocess.run() with 3s timeout
     ↓
stdout + stderr + exit_code captured
     ↓
Gemini 2.5 Flash (code + output → feedback with hints)
```

### Zoiee Quiz Pipeline
```
User picks topic + difficulty + question count
     ↓
Gemini 2.5 Flash → JSON array of MCQ questions
     ↓
Validated (structure check: 4 options, int answer index 0-3)
     ↓
User answers all questions
     ↓
grade_quiz() → score, percentage, per-question explanations
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip
- A Google Gemini API key (get one free at https://aistudio.google.com/app/apikey)

### Install dependencies

```bash
pip install streamlit
pip install langchain langchain-core langchain-community langchain-google-genai
pip install langchain-huggingface
pip install sentence-transformers
pip install faiss-cpu
pip install python-dotenv
pip install pandas
pip install pypdf
```

Or if a `requirements.txt` is present:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Never commit this file. It is already listed in `.gitignore`.

---

## Running the App

### Step 1 — Ingest your course material

Place your PDF files inside the `documents/` folder, then run:

```bash
python ingest.py
```

This will:
- Load all PDFs from `documents/`
- Split them into chunks
- Generate embeddings
- Save the FAISS index to `faiss_index/`

### Step 2 — Start the app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

---

## Security Fixes Applied

The following security issues were identified and fixed during development:

| Issue | File | Fix |
|---|---|---|
| Hardcoded credentials (CWE-798) | `app.py`, `support_chat.py` | All credentials moved to `.env` via `python-dotenv` |
| NoSQL Injection (CWE-943) | `router.py` | Input sanitized with regex before pattern matching |
| Path Traversal (CWE-22) | `sandbox_runner.py` | `os.path.realpath` + `startswith` check added |
| OS Command Injection (CWE-77/78/88) | `sandbox_runner.py`, `code_sandbox.py` | `shell=False` enforced; commands passed as lists; Docker image allowlist added |
| Vector Embedding Weaknesses (CWE-200/284/20) | `rag_chain.py` | Input validation and length limiting before vector store queries |
| Naive datetime (timezone issues) | `logging_utils.py` | Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)` |
| Large function (maintainability) | `app.py` | Quick-reply logic extracted into `_handle_quick_reply()` helper |
| Missing f-string prefix (bug) | `code_sandbox.py` | Fixed `"...{timeout}..."` → `f"...{timeout}..."` |

---

## Notes

- The `faiss_index/` folder must exist before starting the app. Run `ingest.py` first.
- The app currently supports Python for live code execution. Java, C, and C++ require Docker images (`code-sandbox-java`, `code-sandbox-cpp`) to be built from the `docker/` folder.
- Zoiee's quiz feature requires a valid Gemini API key since it calls the LLM to generate questions dynamically.
- Interaction logs are stored in `logs/interactions.csv` and grow with every chat message sent.
