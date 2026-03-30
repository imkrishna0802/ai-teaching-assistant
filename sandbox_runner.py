# sandbox_runner.py
import subprocess
import tempfile
import os
import textwrap



def _run_docker(image: str,
                filename: str,
                compile_cmd: str,
                run_cmd: str,
                code: str,
                timeout: int = 5) -> dict:
    """
    Write code to a temp file, mount into Docker container, compile + run,
    and return stdout/stderr/exit_code.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(code))


        # mount temp dir read-only into /sandbox
        mount_arg = f"{tmpdir}:/sandbox:ro"


        docker_cmd = (
            f"docker run --rm --net=none "
            f"--cpus=0.5 --memory=256m --pids-limit=64 "
            f"-v {mount_arg} -w /sandbox {image} "
            f"/bin/bash -lc '{compile_cmd} && {run_cmd}'"
        )


        proc = subprocess.run(
            docker_cmd,
            shell=True,
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
        # Optional: keep Python execution as-is if you already have it.
        # Here we just run `python main.py` in the cpp image to reuse base.
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.py",
            compile_cmd="python -m py_compile main.py || true",
            run_cmd="python main.py",
            code=code,
        )


    if lang == "java":
        return _run_docker(
            image="code-sandbox-java",
            filename="Main.java",
            compile_cmd="javac Main.java",
            run_cmd="java Main",
            code=code,
        )


    if lang == "c":
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.c",
            compile_cmd="gcc main.c -o main",
            run_cmd="./main",
            code=code,
        )


    if lang in ("c++", "cpp"):
        return _run_docker(
            image="code-sandbox-cpp",
            filename="main.cpp",
            compile_cmd="g++ main.cpp -o main",
            run_cmd="./main",
            code=code,
        )


    raise ValueError(f"Unsupported language: {language}")