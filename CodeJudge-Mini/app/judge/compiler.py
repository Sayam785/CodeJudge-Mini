import os
import subprocess
from pathlib import Path


BASE_DIR = Path("submissions")
SOURCE_DIR = BASE_DIR / "source"
EXECUTABLE_DIR = BASE_DIR / "executable"


def compile_c(submission_id, source_code):
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTABLE_DIR.mkdir(parents=True, exist_ok=True)

    source_path = SOURCE_DIR / f"{submission_id}.c"
    executable_name = (
        f"{submission_id}.exe"
        if os.name == "nt"
        else str(submission_id)
    )
    executable_path = EXECUTABLE_DIR / executable_name

    source_path.write_text(source_code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["gcc", str(source_path), "-o", str(executable_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
    except FileNotFoundError:
        return {
            "success": False,
            "path": None,
            "error": "GCC was not found. Install GCC and add it to PATH."
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "path": None,
            "error": "Compilation timed out."
        }

    if result.returncode != 0:
        return {
            "success": False,
            "path": None,
            "error": result.stderr
        }

    return {
        "success": True,
        "path": str(executable_path.resolve()),
        "error": ""
    }