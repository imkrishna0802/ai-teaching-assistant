# sandbox_runner.py
import subprocess
import tempfile
import os
import textwrap

ALLOWED_IMAGES = {"code-sandbox-cpp", "code-sandbox-java"}
ALLOWED_FILENAMES = {"main.py", "Main.java", "main.c", "main.cpp"}


def _run_docker(image: str,
                filename: str,
                compile_cmd: list,
                run_cmd: list,
                code: str,
                timeout: int = 5) -> dict:
    """
    Write code to a temp file, mount into Docker container, compile + run,
    and return stdout/stderr/exit_code.
    """
    if image not in ALLOWED_IMAGES:
        raise ValueError(f"Disallowed Docker image: {image}")
    if filename not in ALLOWED_FILENAMES:
        raise ValueError(f"Disallowed filename: {filename}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Prevent path traversal: resolve and verify file stays inside tmpdir
        file_path = os.path.realpath(os.path.join(tmpdir, filename))
        if not file_path.startswith(os.path.realpath(tmpdir)):
            raise ValueError("Path traversal detected")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(code))

        # Build command as a list — no shell=True
        docker_cmd = [
            "docker", "run", "--rm", "--net=none",
            "--cpus=0.5", "--memory=256m", "--pids-limit=64",
            "-v", f"{tmpdir}:/sandbox:ro",
            "-w", "/sandbox",
            image,
            "/bin/bash", "-lc",
            " && ".join(compile_cmd + run_cmd),
        ]

        proc = subprocess.run(
            docker_cmd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout
        )


        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
        }



def execute_code(language: str, code: str) -> dict:
    """
    Execute code in the appropriate Docker image based on language.
    Supports: python, java, c, c++.
    """
    lang = language.strip().lower()


    if lang == "python":
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.py",
            compile_cmd=["python", "-m", "py_compile", "main.py"],
            run_cmd=["python", "main.py"],
            code=code,
        )


    if lang == "java":
        return _run_docker(
            image="code-sandbox-java",
            filename="Main.java",
            compile_cmd=["javac", "Main.java"],
            run_cmd=["java", "Main"],
            code=code,
        )


    if lang == "c":
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.c",
            compile_cmd=["gcc", "main.c", "-o", "main"],
            run_cmd=["./main"],
            code=code,
        )


    if lang in ("c++", "cpp"):
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.cpp",
            compile_cmd=["g++", "main.cpp", "-o", "main"],
            run_cmd=["./main"],
            code=code,
        )


    raise ValueError(f"Unsupported language: {language}")