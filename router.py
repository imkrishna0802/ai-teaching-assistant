import re

CODE_KEYWORDS = [
    "error", "traceback", "Exception", "bug", "doesn't work", "does not work",
    "stack overflow", "segmentation fault", "NullPointerException",
    "IndexOutOfBounds", "compile", "compilation", "runtime"
]

CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
MAX_INPUT_LENGTH = 5000


def _sanitize(text: str) -> str:
    """Strip control characters and limit input length."""
    text = text[:MAX_INPUT_LENGTH]
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def classify_query(text: str) -> str:
    """
    Returns 'code' if it looks like a debugging/code question,
    otherwise 'concept'.
    """
    text = _sanitize(text)
    t = text.lower()

    if CODE_BLOCK_PATTERN.search(text):
        return "code"

    if t.count(";") + t.count("{") + t.count("}") > 3:
        return "code"

    if any(kw in t for kw in CODE_KEYWORDS):
        return "code"

    return "concept"