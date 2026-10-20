CREATE OR REPLACE VIEW submission_history_view AS
SELECT
    s.submission_id,
    s.user_id,
    s.problem_id,
    p.title AS problem_title,
    s.status,
    s.execution_time,
    s.submitted_at,
    u.username
FROM Submissions s
JOIN Problems p
    ON s.problem_id = p.problem_id
JOIN Users u ON u.user_id = s.user_id;

CREATE OR REPLACE VIEW problem_summary_view AS
SELECT
    p.problem_id,
    p.title,
    p.time_limit,
    COUNT(t.test_id) AS testcase_count
FROM Problems p
LEFT JOIN TestCases t
    ON t.problem_id = p.problem_id
GROUP BY p.problem_id, p.title, p.time_limit;

CREATE OR REPLACE VIEW submission_results_view AS
SELECT
    r.result_id,
    r.submission_id,
    r.test_id,
    r.status,
    r.actual_output,
    s.user_id,
    s.problem_id,
    p.title AS problem_title
FROM TestCaseResults r
JOIN Submissions s
    ON s.submission_id = r.submission_id
JOIN Problems p
    ON p.problem_id = s.problem_id;

CREATE OR REPLACE VIEW user_stats_view AS
SELECT u.user_id,
       COUNT(s.submission_id) AS total_submissions,
       SUM(CASE WHEN s.status = 'ACCEPTED' THEN 1 ELSE 0 END) AS accepted_count,
       CASE WHEN COUNT(s.submission_id) = 0 THEN 0
            ELSE ROUND(100 * SUM(CASE WHEN s.status = 'ACCEPTED' THEN 1 ELSE 0 END)
                       / COUNT(s.submission_id), 2)
       END AS acceptance_ratio
FROM Users u LEFT JOIN Submissions s ON s.user_id = u.user_id
GROUP BY u.user_id;
