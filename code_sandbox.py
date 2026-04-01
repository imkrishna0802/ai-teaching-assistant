import subprocess
import tempfile
import textwrap
from dataclasses import dataclass


@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timeout: bool


def run_python_code(code: str, timeout: int = 3) -> SandboxResult:
    # Dedent in case it comes from an indented block
    code = textwrap.dedent(code)

    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    # Run the file in a subprocess with time limit
    try:
        completed = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return SandboxResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            timeout=False,
        )
    except subprocess.TimeoutExpired as e:
        return SandboxResult(
            stdout=e.stdout or "",
            stderr=f"Execution timed out after {timeout} seconds.",
            exit_code=-1,
            timeout=True,
        )