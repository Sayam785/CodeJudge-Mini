# Viva questions and short answers

## Operating Systems (12)

1. **What is a process?** A running program with its own OS-managed execution state.
2. **How is a child created?** `subprocess.Popen` asks Windows to create the compiled executable process.
3. **Why use files for I/O?** They demonstrate stdin/stdout/stderr redirection and make comparison deterministic.
4. **What is an exit status?** A number returned by the child; non-zero means the program failed.
5. **How is timeout measured?** With `time.perf_counter()` around the child lifetime.
6. **Why call wait after kill?** To reap the child and avoid a zombie/process handle leak.
7. **What is FCFS?** First-Come-First-Served: the earliest queued job runs first.
8. **What is waiting time?** Time from enqueue until the worker starts the job.
9. **What is turnaround time?** Time from enqueue until completion.
10. **What is producer-consumer here?** Flask request threads produce jobs and the worker consumes them.
11. **Why is a Lock needed?** It protects the shared scheduler table from concurrent updates.
12. **Why only one worker?** Phase 2 demonstrates FCFS simply; a pool is Phase 3.

## DBMS (13)

13. **Why identity columns?** Oracle safely generates unique primary keys.
14. **Why not SELECT MAX(id)?** Two concurrent sessions could read the same maximum; RETURNING gives this insert's ID.
15. **What is a primary key?** A unique, non-null row identifier.
16. **What is a foreign key?** A constraint that keeps a child reference valid.
17. **Why three tables for problems, submissions and tests?** They remove duplication and follow normalization.
18. **What is 3NF?** Non-key columns depend on the key, the whole key, and nothing but the key.
19. **Why use a CLOB?** Statements and source code can be larger than short VARCHAR2 fields.
20. **What is an index?** A lookup structure that reduces table scanning for common predicates.
21. **What is a view?** A stored SELECT that presents joined or aggregated data without duplicating it.
22. **What does the trigger record?** Every status transition in SubmissionAudit.
23. **What is a transaction?** One logical unit of work that commits or rolls back together.
24. **Explain ACID here.** Atomic result saving, constraint consistency, Oracle isolation, and durable commits.
25. **Why bind variables?** They prevent SQL injection and let Oracle reuse parsed statements.
