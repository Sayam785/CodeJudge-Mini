-- Foreign-key and common lookup indexes. Primary/unique constraints already
-- create indexes for their own key columns.

CREATE INDEX idx_submissions_user
ON Submissions(user_id);

CREATE INDEX idx_submissions_user_date
ON Submissions(user_id, submitted_at);

CREATE INDEX idx_submissions_problem
ON Submissions(problem_id);

CREATE INDEX idx_submissions_submitted_at
ON Submissions(submitted_at);

CREATE INDEX idx_submissions_status
ON Submissions(status);

CREATE INDEX idx_testcases_problem
ON TestCases(problem_id);

CREATE INDEX idx_results_submission
ON TestCaseResults(submission_id);

CREATE INDEX idx_results_test
ON TestCaseResults(test_id);

CREATE INDEX idx_audit_submission
ON SubmissionAudit(submission_id);

CREATE INDEX idx_audit_changed_at
ON SubmissionAudit(changed_at);
