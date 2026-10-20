import subprocess
import time


def execute_program(executable_path, input_data, time_limit):
    started = time.perf_counter()

    try:
        result = subprocess.run(
            [executable_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=max(0.1, float(time_limit)),
            check=False
        )

        elapsed = time.perf_counter() - started

        if result.returncode != 0:
            return {
                "status": "RUNTIME_ERROR",
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": elapsed
            }

        return {
            "status": "EXECUTED",
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": elapsed
        }

    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - started

        return {
            "status": "TIME_LIMIT_EXCEEDED",
            "output": "",
            "error": "Execution time limit exceeded.",
            "execution_time": elapsed
        }

    except OSError as exc:
        return {
            "status": "RUNTIME_ERROR",
            "output": "",
            "error": str(exc),
            "execution_time": time.perf_counter() - started
        }