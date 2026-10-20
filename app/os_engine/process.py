"""Compiler and sandbox process primitives used by the judge handler."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Iterable, Mapping, Sequence

MAX_OUTPUT_BYTES = 1024 * 1024
COMPILATION_TIMEOUT_SECONDS = 10.0


def normalize_output(output: str | bytes | None) -> str:
    """Apply the judge's whitespace-insensitive comparison rule."""
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    return " ".join((output or "").split())


def evaluate_output(actual_output: str, expected_output: str) -> str:
    return (
        "ACCEPTED"
        if normalize_output(actual_output) == normalize_output(expected_output)
        else "WRONG_ANSWER"
    )


def _read_text(path: Path, limit: int = MAX_OUTPUT_BYTES) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="replace")
    except OSError:
        return ""


def _compile(source_path: Path, executable_path: Path) -> dict[str, object]:
    stderr_path = source_path.with_suffix(".compile.stderr")
    stdout_path = source_path.with_suffix(".compile.stdout")
    try:
        with (
            stdout_path.open("wb") as stdout,
            stderr_path.open("wb") as stderr,
        ):
            result = subprocess.run(
                ["gcc", str(source_path), "-o", str(executable_path), "-lm"],
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                timeout=COMPILATION_TIMEOUT_SECONDS,
                check=False,
            )
    except FileNotFoundError:
        return {
            "success": False,
            "error": "GCC was not found. Install GCC and add it to PATH.",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Compilation timed out."}
    except OSError as exc:
        return {"success": False, "error": str(exc)}

    error = _read_text(stderr_path)
    if result.returncode != 0:
        return {"success": False, "error": error or "Compilation failed."}
    return {"success": True, "error": ""}


def execute_program(
    executable_path: str | os.PathLike[str],
    input_data: str | bytes,
    time_limit: float,
    *,
    output_limit: int = MAX_OUTPUT_BYTES,
) -> dict[str, object]:
    """Execute one binary using redirected files and an explicit watchdog.

    ``subprocess.run(timeout=...)`` does not give this judge enough control over
    the output cap.  The watchdog therefore measures with ``perf_counter``,
    kills on either limit, and always waits for the child before returning.
    """
    started = time.perf_counter()
    input_bytes = input_data.encode("utf-8") if isinstance(input_data, str) else input_data
    with tempfile.TemporaryDirectory(prefix="codejudge-run-") as work_dir:
        work = Path(work_dir)
        stdin_path = work / "stdin"
        stdout_path = work / "stdout"
        stderr_path = work / "stderr"
        stdin_path.write_bytes(input_bytes or b"")

        process: subprocess.Popen[bytes] | None = None
        status = "EXECUTED"
        error = ""
        try:
            with (
                stdin_path.open("rb") as stdin,
                stdout_path.open("wb") as stdout,
                stderr_path.open("wb") as stderr,
            ):
                process = subprocess.Popen(
                    [str(executable_path)],
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr,
                )
                while process.poll() is None:
                    elapsed = time.perf_counter() - started
                    try:
                        output_size = stdout_path.stat().st_size
                        error_size = stderr_path.stat().st_size
                    except OSError:
                        output_size = error_size = 0
                    if output_size + error_size > output_limit:
                        status = "RUNTIME_ERROR"
                        error = "Program output exceeded 1 MB."
                        process.kill()
                        process.wait()
                        break
                    if elapsed >= float(time_limit):
                        # The child may have exited between poll() above and
                        # the clock check; do not report a timeout for that
                        # race.
                        if process.poll() is not None:
                            break
                        status = "TIME_LIMIT_EXCEEDED"
                        error = "Execution time limit exceeded."
                        process.kill()
                        process.wait()
                        break
                    time.sleep(0.002)

                if process.poll() is None:
                    process.wait()
                elif status == "EXECUTED":
                    process.wait()
        except OSError as exc:
            status = "RUNTIME_ERROR"
            error = str(exc)

        stdout_text = _read_text(stdout_path, output_limit)
        stderr_text = _read_text(stderr_path, output_limit)
        elapsed = time.perf_counter() - started

        try:
            final_output_size = stdout_path.stat().st_size + stderr_path.stat().st_size
        except OSError:
            final_output_size = 0
        if status == "EXECUTED" and final_output_size > output_limit:
            status = "RUNTIME_ERROR"
            error = "Program output exceeded 1 MB."
        if status == "EXECUTED" and process is not None and process.returncode != 0:
            status = "RUNTIME_ERROR"
            error = stderr_text
        return {
            "status": status,
            "output": stdout_text,
            "error": error or stderr_text,
            "stderr": stderr_text,
            "execution_time": elapsed,
        }


def _case_parts(case: object) -> tuple[object, str, str]:
    if isinstance(case, Mapping):
        return (
            case.get("test_id", case.get("id")),
            case.get("input", case.get("input_data", "")) or "",
            case.get("expected_output", case.get("expected", "")) or "",
        )
    test_id, input_data, expected_output = case  # type: ignore[misc]
    return test_id, input_data or "", expected_output or ""


def run_submission(
    submission_id: int,
    source_code: str,
    time_limit: float,
    testcases: Iterable[object],
) -> dict[str, object]:
    """Compile a C submission and return structured per-testcase results."""
    cases = [_case_parts(case) for case in testcases]
    started = time.perf_counter()
    if not cases:
        return {
            "status": "INTERNAL_ERROR",
            "message": "No test cases are configured for this problem.",
            "execution_time": 0.0,
            "testcases": [],
        }

    root = Path("submissions")
    root.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix=f"submission-{int(submission_id)}-", dir=root))
    source_path = work_dir / "program.c"
    executable_name = "program.exe" if os.name == "nt" else "program"
    executable_path = work_dir / executable_name
    source_path.write_text(source_code, encoding="utf-8")

    try:
        compilation = _compile(source_path, executable_path)
        if not compilation["success"]:
            return {
                "status": "COMPILATION_ERROR",
                "message": compilation["error"],
                "execution_time": 0.0,
                "testcases": [],
            }

        results: list[dict[str, object]] = []
        total_time = 0.0
        for test_id, input_data, expected_output in cases:
            execution = execute_program(executable_path, input_data, time_limit)
            case_status = str(execution["status"])
            if case_status == "EXECUTED":
                case_status = evaluate_output(
                    str(execution["output"]), str(expected_output)
                )
            total_time += float(execution["execution_time"])
            results.append(
                {
                    "test_id": test_id,
                    "status": case_status,
                    "output": execution["output"],
                    "message": execution["error"],
                    "error": execution["error"],
                    "execution_time": execution["execution_time"],
                }
            )

        statuses = [str(result["status"]) for result in results]
        if "TIME_LIMIT_EXCEEDED" in statuses:
            final_status = "TIME_LIMIT_EXCEEDED"
        elif "RUNTIME_ERROR" in statuses:
            final_status = "RUNTIME_ERROR"
        elif "WRONG_ANSWER" in statuses:
            final_status = "WRONG_ANSWER"
        else:
            final_status = "ACCEPTED"
        return {
            "status": final_status,
            "message": "",
            "execution_time": total_time,
            "testcases": results,
        }
    except Exception as exc:
        return {
            "status": "INTERNAL_ERROR",
            "message": str(exc),
            "execution_time": time.perf_counter() - started,
            "testcases": [],
        }
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def process_submission(job: object, **kwargs: object) -> dict[str, object]:
    """Compatibility entry point: route a queued job through the DB handler."""
    from app.judge.handler import handle_submission

    return handle_submission(job, **kwargs)


# Name used by some callers that treat the process module as the judge API.
run_submission_all = run_submission
