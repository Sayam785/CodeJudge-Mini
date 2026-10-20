"""Small, parameterized queries used by the Flask routes.

LOB values are converted to Python strings while the cursor is still open;
Oracle temporary LOB handles are not safe to read after cursor close.
"""

import threading

import oracledb

from app.database.connection import get_connection
from app.database.submission_queries import save_submission_results


# The existing worker calls the three compatibility functions below in order.
# Keep their values in memory until the final status call, then let
# save_submission_results commit testcase rows and the verdict atomically.
_pending_results = {}
_pending_execution_times = {}
_pending_lock = threading.Lock()


def _generated_id(cursor, variable):
    value = variable.getvalue()

    if isinstance(value, (list, tuple)):
        value = value[0]

    return int(value)


def get_problems():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT problem_id, title, description, time_limit
            FROM Problems
            ORDER BY problem_id
        """)

        problems = []

        for problem_id, title, description, time_limit in cursor.fetchall():
            description_text = description.read() if description else ""

            problems.append(
                (problem_id, title, description_text, time_limit)
            )

        return problems

    finally:
        cursor.close()
        connection.close()


def get_problem_by_id(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT problem_id, title, description, time_limit
            FROM Problems
            WHERE problem_id = :problem_id
        """, problem_id=problem_id)

        row = cursor.fetchone()

        if row is None:
            return None

        description = row[2].read() if row[2] else ""

        return (row[0], row[1], description, row[3])

    finally:
        cursor.close()
        connection.close()


def create_user(username, email, password):
    """Insert a user and return its identity-generated primary key."""
    connection = get_connection()
    cursor = connection.cursor()
    new_id = cursor.var(oracledb.NUMBER)

    try:
        cursor.execute("""
            INSERT INTO Users (username, email, password_hash)
            VALUES (:username, :email, :password_hash)
            RETURNING user_id INTO :new_id
        """, {
            "username": username,
            "email": email,
            "password_hash": password,
            "new_id": new_id,
        })

        connection.commit()

        return _generated_id(cursor, new_id)

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_user_by_username(username):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, username, email, password_hash
            FROM Users
            WHERE username = :username
        """, username=username)

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def get_submission_history(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT s.submission_id,
                   p.title,
                   s.status,
                   s.execution_time,
                   s.submitted_at
            FROM Submissions s
            JOIN Problems p
              ON p.problem_id = s.problem_id
            WHERE s.user_id = :user_id
            ORDER BY s.submitted_at DESC
        """, user_id=user_id)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_sample_testcase(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT input_data, expected_output
            FROM TestCases
            WHERE problem_id = :problem_id
            ORDER BY test_id
            FETCH FIRST 1 ROWS ONLY
        """, problem_id=problem_id)

        row = cursor.fetchone()

        if row is None:
            return ("", "")

        input_data = row[0].read() if row[0] else ""
        expected_output = row[1].read() if row[1] else ""

        return (input_data, expected_output)

    finally:
        cursor.close()
        connection.close()


def create_submission(user_id, problem_id, source_code):
    """Insert a pending submission and return its identity-generated ID."""
    connection = get_connection()
    cursor = connection.cursor()
    new_id = cursor.var(oracledb.NUMBER)

    try:
        cursor.execute("""
            INSERT INTO Submissions (
                user_id,
                problem_id,
                source_code,
                status
            )
            VALUES (
                :user_id,
                :problem_id,
                :source_code,
                'PENDING'
            )
            RETURNING submission_id INTO :new_id
        """, {
            "user_id": user_id,
            "problem_id": problem_id,
            "source_code": source_code,
            "new_id": new_id,
        })

        connection.commit()

        return _generated_id(cursor, new_id)

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def update_submission_status(submission_id, status):
    with _pending_lock:
        has_pending = (
            submission_id in _pending_results
            or submission_id in _pending_execution_times
        )

        if has_pending and status not in ("PENDING", "RUNNING"):
            results = _pending_results.pop(submission_id, [])
            execution_time = _pending_execution_times.pop(
                submission_id, None
            )

            save_submission_results(
                submission_id,
                results,
                status,
                execution_time or 0
            )

            return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Submissions
            SET status = :status
            WHERE submission_id = :submission_id
        """, status=status, submission_id=submission_id)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_problem_time_limit(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT time_limit
            FROM Problems
            WHERE problem_id = :problem_id
        """, problem_id=problem_id)

        row = cursor.fetchone()

        return row[0] if row else None

    finally:
        cursor.close()
        connection.close()


def get_testcases_for_problem(problem_id):
    """Return test cases as (test_id, input, expected_output)."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT test_id, input_data, expected_output
            FROM TestCases
            WHERE problem_id = :problem_id
            ORDER BY test_id
        """, problem_id=problem_id)

        testcases = []

        for test_id, input_data, expected_output in cursor.fetchall():
            input_text = input_data.read() if input_data else ""
            expected_text = (
                expected_output.read() if expected_output else ""
            )

            testcases.append(
                (test_id, input_text, expected_text)
            )

        return testcases

    finally:
        cursor.close()
        connection.close()


def save_testcase_result(
    submission_id,
    test_id,
    status,
    actual_output
):
    """Buffer a result for the worker's eventual atomic final-status write."""
    with _pending_lock:
        _pending_results.setdefault(submission_id, []).append({
            "test_id": test_id,
            "status": status,
            "output": actual_output or "",
        })


def update_submission_execution_time(submission_id, execution_time):
    with _pending_lock:
        if submission_id in _pending_results:
            _pending_execution_times[submission_id] = execution_time
            return

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Submissions
            SET execution_time = :execution_time
            WHERE submission_id = :submission_id
        """, execution_time=execution_time, submission_id=submission_id)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def get_dashboard_stats(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Calculate dashboard statistics from existing submissions.
        cursor.execute("""
            SELECT COUNT(*),
                   NVL(
                       SUM(
                           CASE
                               WHEN status = 'ACCEPTED' THEN 1
                               ELSE 0
                           END
                       ),
                       0
                   ),
                   COUNT(
                       DISTINCT CASE
                           WHEN status = 'ACCEPTED' THEN problem_id
                       END
                   )
            FROM Submissions
            WHERE user_id = :user_id
        """, user_id=user_id)

        total, accepted, solved = cursor.fetchone()

        ratio = (
            round((accepted * 100.0 / total), 2)
            if total
            else 0
        )

        return {
            "total": total or 0,
            "accepted": accepted or 0,
            "ratio": ratio,
            "solved": solved or 0,
        }

    finally:
        cursor.close()
        connection.close()


def get_recent_submissions(user_id, limit=8):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT s.submission_id,
                   s.problem_id,
                   p.title,
                   s.status,
                   s.execution_time,
                   s.submitted_at
            FROM Submissions s
            JOIN Problems p
              ON p.problem_id = s.problem_id
            WHERE s.user_id = :user_id
            ORDER BY s.submitted_at DESC
            FETCH FIRST :limit ROWS ONLY
        """, user_id=user_id, limit=int(limit))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_problem_detail(problem_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT problem_id, title, description, time_limit
            FROM Problems
            WHERE problem_id = :problem_id
        """, problem_id=problem_id)

        row = cursor.fetchone()

        if row is None:
            return None

        values = list(row)
        values[2] = values[2].read() if values[2] else ""

        return tuple(values)

    finally:
        cursor.close()
        connection.close()


def get_problem_attempts(user_id, problem_id, limit=5):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT submission_id,
                   status,
                   execution_time,
                   submitted_at
            FROM Submissions
            WHERE user_id = :user_id
              AND problem_id = :problem_id
            ORDER BY submitted_at DESC
            FETCH FIRST :limit ROWS ONLY
        """, user_id=user_id, problem_id=problem_id, limit=int(limit))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_submission_detail(user_id, submission_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT s.submission_id,
                   s.problem_id,
                   p.title,
                   s.status,
                   s.execution_time,
                   s.submitted_at
            FROM Submissions s
            JOIN Problems p
              ON p.problem_id = s.problem_id
            WHERE s.user_id = :user_id
              AND s.submission_id = :submission_id
        """, user_id=user_id, submission_id=submission_id)

        submission = cursor.fetchone()

        if submission is None:
            return None

        cursor.execute("""
            SELECT r.test_id,
                   r.status,
                   r.actual_output,
                   t.expected_output,
                   t.input_data
            FROM TestCaseResults r
            JOIN TestCases t
              ON t.test_id = r.test_id
            WHERE r.submission_id = :submission_id
            ORDER BY r.test_id
        """, submission_id=submission_id)

        results = []

        for test_id, status, actual, expected, input_data in cursor.fetchall():
            results.append({
                "test_id": test_id,
                "status": status,
                "actual_output": actual.read() if actual else "",
                "expected_output": expected.read() if expected else "",
                "input_data": input_data.read() if input_data else "",
            })

        return {
            "submission": submission,
            "results": results,
        }

    finally:
        cursor.close()
        connection.close()


def get_history_page(user_id, status=None, page=1, page_size=10):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Normalize pagination inputs.
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        offset = (page - 1) * page_size

        # Shared filtering condition.
        where = "s.user_id = :user_id"

        # Parameters used ONLY by the paginated history query.
        history_params = {
            "user_id": user_id,
            "offset": offset,
            "page_size": page_size,
        }

        # Parameters used ONLY by the count query.
        count_params = {
            "user_id": user_id,
        }

        if status:
            where += " AND s.status = :status"

            history_params["status"] = status
            count_params["status"] = status

        # Fetch the requested page.
        cursor.execute(f"""
            SELECT s.submission_id,
                   s.problem_id,
                   p.title,
                   s.status,
                   s.execution_time,
                   s.submitted_at
            FROM Submissions s
            JOIN Problems p
              ON p.problem_id = s.problem_id
            WHERE {where}
            ORDER BY s.submitted_at DESC
            OFFSET :offset ROWS
            FETCH NEXT :page_size ROWS ONLY
        """, history_params)

        rows = cursor.fetchall()

        # Count all matching submissions.
        # This query does NOT contain :offset or :page_size.
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM Submissions s
            JOIN Problems p
              ON p.problem_id = s.problem_id
            WHERE {where}
        """, count_params)

        total = cursor.fetchone()[0]

        return rows, total

    finally:
        cursor.close()
        connection.close()


def get_analytics():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT p.title,
                   COUNT(s.submission_id),
                   SUM(
                       CASE
                           WHEN s.status = 'ACCEPTED' THEN 1
                           ELSE 0
                       END
                   )
            FROM Problems p
            LEFT JOIN Submissions s
              ON s.problem_id = p.problem_id
            GROUP BY p.problem_id, p.title
            ORDER BY p.problem_id
        """)

        per_problem = cursor.fetchall()

        cursor.execute("""
            SELECT u.username,
                   COUNT(s.submission_id) AS total,
                   SUM(
                       CASE
                           WHEN s.status = 'ACCEPTED' THEN 1
                           ELSE 0
                       END
                   ) AS accepted
            FROM Users u
            JOIN Submissions s
              ON s.user_id = u.user_id
            GROUP BY u.user_id, u.username
            ORDER BY accepted DESC, total DESC, u.username
            FETCH FIRST 10 ROWS ONLY
        """)

        top_users = cursor.fetchall()

        return per_problem, top_users

    finally:
        cursor.close()
        connection.close()