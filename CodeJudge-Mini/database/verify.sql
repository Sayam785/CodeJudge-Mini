-- SQL*Plus smoke verification for CodeJudge-Mini.
-- Usage: @verify.sql while connected to the application schema in XEPDB1.
SET ECHO ON
SET FEEDBACK ON
SET HEADING ON
SET LINESIZE 180
SET LONG 2000
SET PAGESIZE 100
WHENEVER SQLERROR EXIT SQL.SQLCODE

PROMPT === Oracle instance and schema ===
SELECT SYS_CONTEXT('USERENV', 'DB_NAME') AS database_name,
       SYS_CONTEXT('USERENV', 'SERVICE_NAME') AS service_name,
       USER AS schema_name
FROM dual;

PROMPT === Required tables ===
SELECT table_name
FROM user_tables
WHERE table_name IN (
    'USERS', 'PROBLEMS', 'TESTCASES', 'SUBMISSIONS',
    'TESTCASERESULTS', 'SUBMISSIONAUDIT'
)
ORDER BY table_name;

PROMPT === Row counts ===
SELECT 'PROBLEMS' AS object_name, COUNT(*) AS row_count FROM Problems
UNION ALL
SELECT 'TESTCASES', COUNT(*) FROM TestCases
UNION ALL
SELECT 'USERS', COUNT(*) FROM Users
UNION ALL
SELECT 'SUBMISSIONS', COUNT(*) FROM Submissions
UNION ALL
SELECT 'TESTCASERESULTS', COUNT(*) FROM TestCaseResults
UNION ALL
SELECT 'SUBMISSIONAUDIT', COUNT(*) FROM SubmissionAudit;

PROMPT === Every seeded problem has exactly three test cases ===
SELECT p.problem_id, p.title, COUNT(t.test_id) AS testcase_count
FROM Problems p
LEFT JOIN TestCases t ON t.problem_id = p.problem_id
GROUP BY p.problem_id, p.title
ORDER BY p.problem_id;

PROMPT === Identity columns ===
SELECT table_name, column_name, generation_type
FROM user_tab_identity_cols
WHERE table_name IN (
    'USERS', 'PROBLEMS', 'TESTCASES', 'SUBMISSIONS',
    'TESTCASERESULTS', 'SUBMISSIONAUDIT'
)
ORDER BY table_name;

PROMPT === Constraints, indexes, views, and trigger ===
SELECT constraint_name, table_name, constraint_type, status
FROM user_constraints
WHERE table_name IN (
    'USERS', 'PROBLEMS', 'TESTCASES', 'SUBMISSIONS',
    'TESTCASERESULTS', 'SUBMISSIONAUDIT'
)
ORDER BY table_name, constraint_name;

SELECT index_name, table_name
FROM user_indexes
WHERE table_name IN (
    'USERS', 'PROBLEMS', 'TESTCASES', 'SUBMISSIONS',
    'TESTCASERESULTS', 'SUBMISSIONAUDIT'
)
ORDER BY table_name, index_name;

SELECT view_name FROM user_views
WHERE view_name IN (
    'SUBMISSION_HISTORY_VIEW', 'PROBLEM_SUMMARY_VIEW',
    'SUBMISSION_RESULTS_VIEW', 'USER_STATS_VIEW'
)
ORDER BY view_name;

SELECT trigger_name, status
FROM user_triggers
WHERE trigger_name = 'TRG_SUBMISSION_STATUS_AUDIT';

SHOW ERRORS TRIGGER trg_submission_status_audit

PROMPT === Verification complete ===
EXIT SUCCESS
