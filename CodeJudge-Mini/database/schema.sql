-- CodeJudge-Mini schema for Oracle Database 21c XE (service XEPDB1).
-- Run this script while connected to the application schema.

CREATE TABLE Users (
    user_id NUMBER GENERATED ALWAYS AS IDENTITY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    created_at TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE Problems (
    problem_id NUMBER GENERATED ALWAYS AS IDENTITY,
    title VARCHAR2(150) NOT NULL,
    description CLOB NOT NULL,
    difficulty VARCHAR2(10) DEFAULT 'Easy' NOT NULL,
    input_format CLOB NOT NULL,
    output_format CLOB NOT NULL,
    sample_input CLOB NOT NULL,
    sample_output CLOB NOT NULL,
    time_limit NUMBER(8, 3) DEFAULT 2 NOT NULL,
    created_at TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_problems PRIMARY KEY (problem_id),
    CONSTRAINT ck_problems_difficulty CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    CONSTRAINT ck_problems_time_limit CHECK (time_limit > 0)
);

CREATE TABLE TestCases (
    test_id NUMBER GENERATED ALWAYS AS IDENTITY,
    problem_id NUMBER NOT NULL,
    input_data CLOB NOT NULL,
    expected_output CLOB NOT NULL,
    CONSTRAINT pk_testcases PRIMARY KEY (test_id),
    CONSTRAINT uq_testcases_problem_test UNIQUE (problem_id, test_id),
    CONSTRAINT fk_testcases_problem FOREIGN KEY (problem_id)
        REFERENCES Problems(problem_id) ON DELETE CASCADE
);

CREATE TABLE Submissions (
    submission_id NUMBER GENERATED ALWAYS AS IDENTITY,
    user_id NUMBER NOT NULL,
    problem_id NUMBER NOT NULL,
    source_code CLOB NOT NULL,
    status VARCHAR2(30) DEFAULT 'PENDING' NOT NULL,
    execution_time NUMBER(12, 6),
    submitted_at TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_submissions PRIMARY KEY (submission_id),
    CONSTRAINT fk_submissions_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_submissions_problem FOREIGN KEY (problem_id)
        REFERENCES Problems(problem_id),
    CONSTRAINT ck_submissions_status CHECK (
        status IN (
            'PENDING', 'RUNNING', 'ACCEPTED', 'WRONG_ANSWER',
            'COMPILATION_ERROR', 'RUNTIME_ERROR',
            'TIME_LIMIT_EXCEEDED', 'INTERNAL_ERROR'
        )
    ),
    CONSTRAINT ck_submissions_execution_time CHECK (
        execution_time IS NULL OR execution_time >= 0
    )
);

CREATE TABLE TestCaseResults (
    result_id NUMBER GENERATED ALWAYS AS IDENTITY,
    submission_id NUMBER NOT NULL,
    test_id NUMBER NOT NULL,
    status VARCHAR2(30) NOT NULL,
    actual_output CLOB,
    CONSTRAINT pk_testcaseresults PRIMARY KEY (result_id),
    CONSTRAINT uq_results_submission_test UNIQUE (submission_id, test_id),
    CONSTRAINT fk_results_submission FOREIGN KEY (submission_id)
        REFERENCES Submissions(submission_id) ON DELETE CASCADE,
    CONSTRAINT fk_results_testcase FOREIGN KEY (test_id)
        REFERENCES TestCases(test_id),
    CONSTRAINT ck_results_status CHECK (
        status IN (
            'ACCEPTED', 'WRONG_ANSWER', 'COMPILATION_ERROR',
            'RUNTIME_ERROR', 'TIME_LIMIT_EXCEEDED', 'INTERNAL_ERROR'
        )
    )
);

CREATE TABLE SubmissionAudit (
    audit_id NUMBER GENERATED ALWAYS AS IDENTITY,
    submission_id NUMBER NOT NULL,
    old_status VARCHAR2(30),
    new_status VARCHAR2(30) NOT NULL,
    changed_at TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    changed_by VARCHAR2(128) DEFAULT SYS_CONTEXT('USERENV', 'SESSION_USER') NOT NULL,
    CONSTRAINT pk_submission_audit PRIMARY KEY (audit_id),
    CONSTRAINT fk_audit_submission FOREIGN KEY (submission_id)
        REFERENCES Submissions(submission_id) ON DELETE CASCADE
);
