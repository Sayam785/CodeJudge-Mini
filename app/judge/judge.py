from app.judge.compiler import compile_c
from app.judge.executor import execute_program
from app.judge.evaluator import evaluate_output


def run_submission(submission_id, source_code, time_limit,
                   sample_input, expected_output):
    """Backward-compatible single-test-case interface."""
    result = run_submission_all(
        submission_id,
        source_code,
        time_limit,
        [(0, sample_input, expected_output)]
    )

    return {
        "status": result["status"],
        "output": (
            result["testcases"][0]["output"]
            if result["testcases"] else ""
        ),
        "message": result.get("message", ""),
        "execution_time": result["execution_time"]
    }


def run_submission_all(submission_id, source_code, time_limit, testcases):
    compilation = compile_c(submission_id, source_code)

    if not compilation["success"]:
        return {
            "status": "COMPILATION_ERROR",
            "message": compilation["error"],
            "execution_time": 0.0,
            "testcases": []
        }

    results = []
    total_time = 0.0

    try:
        for test_id, input_data, expected_output in testcases:
            execution = execute_program(
                compilation["path"],
                input_data or "",
                time_limit
            )

            total_time += execution["execution_time"]

            if execution["status"] == "TIME_LIMIT_EXCEEDED":
                verdict = "TIME_LIMIT_EXCEEDED"
            elif execution["status"] == "RUNTIME_ERROR":
                verdict = "RUNTIME_ERROR"
            else:
                verdict = evaluate_output(
                    execution["output"],
                    expected_output or ""
                )

            results.append({
                "test_id": test_id,
                "status": verdict,
                "output": execution["output"],
                "message": execution["error"],
                "execution_time": execution["execution_time"]
            })

            # Stop early on a failing test case.
            if verdict != "ACCEPTED":
                break

        if not results:
            final_status = "INTERNAL_ERROR"
        elif any(r["status"] == "TIME_LIMIT_EXCEEDED" for r in results):
            final_status = "TIME_LIMIT_EXCEEDED"
        elif any(r["status"] == "RUNTIME_ERROR" for r in results):
            final_status = "RUNTIME_ERROR"
        elif any(r["status"] == "WRONG_ANSWER" for r in results):
            final_status = "WRONG_ANSWER"
        elif len(results) == len(testcases):
            final_status = "ACCEPTED"
        else:
            final_status = "INTERNAL_ERROR"

        return {
            "status": final_status,
            "message": "",
            "execution_time": total_time,
            "testcases": results
        }

    finally:
        # Remove generated executable and source after evaluation.
        import os
        for path in (
            f"submissions/source/{submission_id}.c",
            compilation["path"]
        ):
            try:
                os.remove(path)
            except OSError:
                pass
