import re

CODE_KEYWORDS = [
    "error", "traceback", "Exception", "bug", "doesn't work", "does not work",
    "stack overflow", "segmentation fault", "NullPointerException",
    "IndexOutOfBounds", "compile", "compilation", "runtime"
]

CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)


def classify_query(text: str) -> str:
    """
    Returns 'code' if it looks like a debugging/code question,
    otherwise 'concept'.
    """
    t = text.lower()

    # If there's a fenced code block, treat as code
    if CODE_BLOCK_PATTERN.search(text):
        return "code"

    # If it contains multiple semicolons/braces, likely code
    if t.count(";") + t.count("{") + t.count("}") > 3:
        return "code"

    # Keywords
    if any(kw in t for kw in CODE_KEYWORDS):
        return "code"

    return "concept"