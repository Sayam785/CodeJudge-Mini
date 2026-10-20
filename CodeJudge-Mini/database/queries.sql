-- Twelve read-only viva queries. Bind values are shown with a colon.
-- 1 JOIN: user's latest submissions
SELECT u.username, p.title, s.status, s.submitted_at FROM Submissions s JOIN Users u ON u.user_id=s.user_id JOIN Problems p ON p.problem_id=s.problem_id WHERE u.user_id=:user_id ORDER BY s.submitted_at DESC;
-- 2 GROUP BY: verdict counts
SELECT status, COUNT(*) AS total FROM Submissions GROUP BY status ORDER BY total DESC;
-- 3 GROUP BY + HAVING: active problems
SELECT problem_id, COUNT(*) AS total FROM Submissions GROUP BY problem_id HAVING COUNT(*) >= :minimum_submissions;
-- 4 Subquery: users with an accepted solution
SELECT username FROM Users WHERE user_id IN (SELECT user_id FROM Submissions WHERE status='ACCEPTED');
-- 5 Ranking: fastest accepted submission for every problem
SELECT * FROM (SELECT problem_id, submission_id, execution_time, ROW_NUMBER() OVER (PARTITION BY problem_id ORDER BY execution_time) AS rank_no FROM Submissions WHERE status='ACCEPTED') WHERE rank_no=1;
-- 6 Top users by accepted count
SELECT u.username, COUNT(*) AS accepted_count FROM Users u JOIN Submissions s ON s.user_id=u.user_id WHERE s.status='ACCEPTED' GROUP BY u.user_id,u.username ORDER BY accepted_count DESC FETCH FIRST 10 ROWS ONLY;
-- 7 Acceptance ratio per problem
SELECT p.title, COUNT(s.submission_id) AS attempts, SUM(CASE WHEN s.status='ACCEPTED' THEN 1 ELSE 0 END) AS accepted, ROUND(100*SUM(CASE WHEN s.status='ACCEPTED' THEN 1 ELSE 0 END)/NULLIF(COUNT(s.submission_id),0),2) AS ratio FROM Problems p LEFT JOIN Submissions s ON s.problem_id=p.problem_id GROUP BY p.problem_id,p.title ORDER BY ratio DESC NULLS LAST;
-- 8 One problem and its test cases
SELECT p.title,t.test_id,t.input_data,t.expected_output FROM Problems p JOIN TestCases t ON t.problem_id=p.problem_id WHERE p.problem_id=:problem_id ORDER BY t.test_id;
-- 9 View: dashboard statistics for one user
SELECT * FROM user_stats_view WHERE user_id=:user_id;
-- 10 Audit lifecycle of one submission
SELECT old_status,new_status,changed_at FROM SubmissionAudit WHERE submission_id=:submission_id ORDER BY changed_at;
-- 11 Problems with at least three test cases
SELECT problem_id,title,testcase_count FROM problem_summary_view WHERE testcase_count >= 3;
-- 12 Users whose acceptance ratio is above the class average
SELECT username FROM user_stats_view JOIN Users USING(user_id) WHERE acceptance_ratio > (SELECT AVG(acceptance_ratio) FROM user_stats_view);
