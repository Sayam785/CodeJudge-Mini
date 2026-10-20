# CodeJudge-Mini final report

## Files created or repaired

The project now includes the Oracle scripts, Flask factory and routes, session
authentication, normalized C judge process pipeline, FCFS queue/scheduler,
single lazy worker, live result and OS monitor pages, analytics, tests, demos,
and the four viva documents under `docs/`.

## Checks actually run in this workspace

* `python -m compileall -q app tests` — passed during implementation.
* `python tests/demo_race_condition.py` — passed and showed one admitted job.
* `python tests/demo_concurrency.py` — passed and showed FIFO order `[1, 2, 3, 4, 5]`.
* GCC smoke checks — correct output was accepted; compilation error and an
  infinite loop produced structured compilation/time-limit results.
* `python -m unittest discover -s tests -v` — **9 tests passed**. The worker
  recovery test intentionally logs a traceback for the simulated exception,
  then confirms the worker continues.
* Flask route-map smoke check — passed; all required routes imported without
  an Oracle connection.

## Not tested here

Oracle 21c XE was not available in this worker environment, so the SQL*Plus
scripts, Oracle CLOB/identity behavior, Flask registration/login against the
real database, and end-to-end browser flow require manual verification.

## Manual end-to-end acceptance test

Run the seven SQL scripts in README order, start Flask, register, open
`Sum of Two Numbers`, submit a program that prints the sum, and confirm
`ACCEPTED` plus three testcase rows. Submit a wrong program, a syntax error,
and `while(1){}` with a short problem time limit to demonstrate the other
verdicts. Check `/history`, `/os-monitor`, `/analytics`, and the
`SubmissionAudit` rows in Oracle.

## Known limitations

Execution is intentionally not sandboxed. The output cap is reported as a
runtime error because the required Oracle status check constraint does not
include a separate output-limit status. Phase 3 items listed in README are not
implemented.
