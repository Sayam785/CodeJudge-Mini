"""Database-facing submission handler.

The handler is deliberately dependency-injected.  Production uses the
existing query module lazily; tests can provide a small fake database and a
fake process function without an Oracle installation.
"""

from __future__ import annotations

from contextlib import contextmanager, nullcontext
from typing import Any, Callable, Iterable, Mapping


def _queries() -> Any:
    # Importing this lazily keeps OS/judge unit tests independent of Oracle.
    from app.database import queries

    return queries


def update_submission_status(submission_id: int, status: str) -> Any:
    return _queries().update_submission_status(submission_id, status)


def get_testcases_for_problem(problem_id: int) -> Any:
    return _queries().get_testcases_for_problem(problem_id)


def save_testcase_result(
    submission_id: int, test_id: Any, status: str, actual_output: str
) -> Any:
    return _queries().save_testcase_result(
        submission_id, test_id, status, actual_output
    )


def update_submission_execution_time(
    submission_id: int, execution_time: float
) -> Any:
    return _queries().update_submission_execution_time(
        submission_id, execution_time
    )


class _QueriesAdapter:
    """Adapter for the legacy function-based database layer."""

    def __init__(self) -> None:
        self._connection: Any | None = None

    @contextmanager
    def transaction(self) -> Any:
        """Use one connection for the final result write set."""
        try:
            from app.database.connection import get_connection

            connection = get_connection()
        except Exception:
            # Unit tests may patch the legacy query seams without installing
            # Oracle.  In that case the patched functions remain usable.
            yield self
            return
        self._connection = connection
        try:
            yield self
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            self._connection = None
            connection.close()

    def _execute(self, statement: str, **parameters: Any) -> Any:
        if self._connection is None:
            raise RuntimeError("database operation requires an active transaction")
        cursor = self._connection.cursor()
        try:
            return cursor.execute(statement, parameters)
        finally:
            cursor.close()

    def update_status(self, submission_id: int, status: str) -> Any:
        if self._connection is not None:
            return self._execute(
                """
                UPDATE Submissions
                SET status = :status
                WHERE submission_id = :submission_id
                """,
                status=status,
                submission_id=submission_id,
            )
        return update_submission_status(submission_id, status)

    def get_testcases(self, problem_id: int) -> Any:
        return get_testcases_for_problem(problem_id)

    def save_result(
        self, submission_id: int, test_id: Any, status: str, output: str
    ) -> Any:
        if self._connection is not None:
            return self._execute(
                """
                INSERT INTO TestCaseResults
                    (submission_id, test_id, status, actual_output)
                VALUES (:submission_id, :test_id, :status, :actual_output)
                """,
                submission_id=submission_id,
                test_id=test_id,
                status=status,
                actual_output=output or "",
            )
        return save_testcase_result(submission_id, test_id, status, output)

    def update_execution_time(self, submission_id: int, value: float) -> Any:
        if self._connection is not None:
            return self._execute(
                """
                UPDATE Submissions
                SET execution_time = :execution_time
                WHERE submission_id = :submission_id
                """,
                execution_time=value,
                submission_id=submission_id,
            )
        return update_submission_execution_time(submission_id, value)


def _adapter(db: Any | None) -> Any:
    if db is None:
        return _QueriesAdapter()
    return db


def _method(db: Any, names: tuple[str, ...], fallback: Callable[..., Any]) -> Callable[..., Any]:
    for name in names:
        method = getattr(db, name, None)
        if callable(method):
            return method
    return fallback


def _transaction(db: Any) -> Any:
    transaction = getattr(db, "transaction", None)
    if callable(transaction):
        return transaction()
    return nullcontext()


def _job_parts(job: Any) -> tuple[int, int, str, float]:
    def get(name: str) -> Any:
        if isinstance(job, Mapping):
            return job[name]
        return getattr(job, name)

    return (
        int(get("submission_id")),
        int(get("problem_id")),
        str(get("source_code")),
        float(get("time_limit")),
    )


def _internal_result(message: str) -> dict[str, object]:
    return {
        "status": "INTERNAL_ERROR",
        "message": message,
        "execution_time": 0.0,
        "testcases": [],
    }


def handle_submission(
    job: Any,
    *,
    db: Any | None = None,
    process_fn: Callable[..., dict[str, object]] | None = None,
) -> dict[str, object]:
    """Run a queued submission and commit all result rows as one unit."""
    submission_id, problem_id, source_code, time_limit = _job_parts(job)
    database = _adapter(db)
    set_status = _method(database, ("update_status", "update_submission_status"), update_submission_status)
    load_cases = _method(
        database,
        ("get_testcases", "get_testcases_for_problem"),
        get_testcases_for_problem,
    )
    save_result = _method(
        database,
        ("save_result", "save_testcase_result"),
        save_testcase_result,
    )
    set_execution_time = _method(
        database,
        ("update_execution_time", "update_submission_execution_time"),
        update_submission_execution_time,
    )

    try:
        set_status(submission_id, "RUNNING")
        testcases = load_cases(problem_id)
        if process_fn is None:
            from app.os_engine.process import run_submission

            process_fn = run_submission
        result = process_fn(submission_id, source_code, time_limit, testcases)
        result = dict(result)

        # The result rows, execution time, and final verdict share one
        # transaction whenever the supplied DB layer exposes one.
        with _transaction(database):
            for case in result.get("testcases", []) or []:
                save_result(
                    submission_id,
                    case.get("test_id"),
                    case.get("status", "INTERNAL_ERROR"),
                    case.get("output", "") or "",
                )
            set_execution_time(
                submission_id, float(result.get("execution_time", 0.0) or 0.0)
            )
            set_status(submission_id, result.get("status", "INTERNAL_ERROR"))
        return result
    except Exception as exc:
        # A failed DB write or process is itself a judgeable outcome.  Try the
        # status write outside the transaction so a rollback cannot hide it.
        try:
            set_status(submission_id, "INTERNAL_ERROR")
        except Exception:
            pass
        return _internal_result(str(exc))


def process_submission(job: Any, **kwargs: Any) -> dict[str, object]:
    """Alias used by older worker integrations."""
    return handle_submission(job, **kwargs)


def run_submission_all(
    submission_id: int,
    source_code: str,
    time_limit: float,
    testcases: Iterable[object],
) -> dict[str, object]:
    """Expose the low-level judge through the handler module as well."""
    from app.os_engine.process import run_submission

    return run_submission(submission_id, source_code, time_limit, testcases)
