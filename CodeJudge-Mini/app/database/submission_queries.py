"""Submission persistence that must be atomic.

The result rows and the final submission verdict are one logical operation:
either all of them are committed, or none of them are.  Callers pass the
already-computed testcase result dictionaries from the judge.
"""

from app.database.connection import get_connection


def save_submission_results(
    submission_id, testcase_results, final_status, execution_time
):
    """Persist testcase results and the final verdict in one transaction.

    ``testcase_results`` contains dictionaries with ``test_id``, ``status``
    and ``output`` keys, matching ``run_submission_all``'s result format.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        for result in testcase_results:
            cursor.execute("""
                INSERT INTO TestCaseResults
                    (submission_id, test_id, status, actual_output)
                VALUES (:submission_id, :test_id, :status, :actual_output)
            """, submission_id=submission_id,
                 test_id=result["test_id"], status=result["status"],
                 actual_output=result.get("output") or "")

        cursor.execute("""
            UPDATE Submissions
            SET execution_time = :execution_time,
                status = :status
            WHERE submission_id = :submission_id
        """, execution_time=execution_time, status=final_status,
             submission_id=submission_id)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


# Descriptive alias for callers that prefer the transaction's full intent.
save_results_and_verdict = save_submission_results
