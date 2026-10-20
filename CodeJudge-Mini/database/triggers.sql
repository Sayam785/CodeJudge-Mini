-- Keep a status-change history for submissions.
CREATE OR REPLACE TRIGGER trg_submission_status_audit
AFTER UPDATE OF status ON Submissions
FOR EACH ROW
WHEN (OLD.status <> NEW.status)
BEGIN
    INSERT INTO SubmissionAudit (
        submission_id, old_status, new_status, changed_at, changed_by
    )
    VALUES (
        :NEW.submission_id,
        :OLD.status,
        :NEW.status,
        SYSTIMESTAMP,
        SYS_CONTEXT('USERENV', 'SESSION_USER')
    );
END;
/
