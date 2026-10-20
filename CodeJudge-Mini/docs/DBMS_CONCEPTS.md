# DBMS concepts

## ER diagram in text

`Users (1) -> (N) Submissions (N) -> (1) Problems (1) -> (N) TestCases`

`Submissions (1) -> (N) TestCaseResults (N) -> (1) TestCases`

`Submissions (1) -> (N) SubmissionAudit`

## Design and implementation

The tables in `database/schema.sql` are in third normal form. A user stores
only user attributes, a problem stores only problem attributes, and test-case
input/output is stored once under its problem. Submission facts depend on the
submission key, while testcase results depend on the `(submission_id,
test_id)` relationship. There are no repeating groups or transitive user or
problem attributes in the submission rows.

Every primary key is an Oracle `GENERATED ALWAYS AS IDENTITY` column. Foreign
keys connect the relationships; unique constraints protect username, email,
and one result per test case; NOT NULL and CHECK constraints protect required
values, difficulty, verdicts, and positive limits. `seed.sql` looks up each
parent problem by title and never assumes an identity value.

`indexes.sql` indexes foreign keys and common history lookups, including the
requested submission user/date access path. `submission_history_view` joins
Submissions, Problems, and Users. `user_stats_view` uses GROUP BY to calculate
total submissions, accepted submissions, and acceptance ratio. The other views
make test-case and problem summaries easy to query.

`triggers.sql` contains an AFTER UPDATE OF status trigger. The real lifecycle
is `PENDING -> RUNNING -> verdict`; each change inserts old status, new status,
timestamp, and database session user into SubmissionAudit.

## Transactions and ACID

`app/judge/handler.py` opens one transaction around testcase result inserts,
execution time update, and final verdict update. `submission_queries.py` uses
commit on success and rollback on any exception. Atomicity prevents half a
submission from appearing; consistency is enforced by constraints; isolation
comes from Oracle transaction handling; durability follows commit. All SQL
values are bind variables. CLOBs are read before cursor/connection closure and
identity IDs are obtained with `RETURNING ... INTO`.
