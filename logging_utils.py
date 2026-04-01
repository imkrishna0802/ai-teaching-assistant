import csv
import os
from datetime import datetime, timezone

LOG_PATH = "logs/interactions.csv"


def log_interaction(user_question: str, answer: str, intent: str):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.exists(LOG_PATH)

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "intent", "question", "answer"])
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            intent,
            user_question,
            answer[:500],  # truncate
        ])