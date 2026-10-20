# File guide

Each entry gives a plain-English purpose and the main caller.

* `app.py` starts the Flask app; it calls `app.create_app`.
* `config.py` contains environment-driven settings; imported by the app and submit route.
* `requirements.txt` lists Flask and python-oracledb; used by pip.
* `.gitignore` excludes environments, caches, secrets, and generated submissions.
* `app/__init__.py` builds the Flask factory; called by `app.py`.
* `app/routes/__init__.py` marks the route folder as a Python package; imported by route modules.
* `app/database/__init__.py` marks the database folder as a Python package; used by database imports.
* `app/os_engine/__init__.py` marks the OS folder as a Python package; used by worker imports.
* `app/judge/__init__.py` marks the judge folder as a Python package; used by handler imports.
* `app/routes/auth.py` registers, logs in, hashes passwords, and logs out; called by the factory.
* `app/routes/common.py` provides `login_required`; called by protected route modules.
* `app/routes/dashboard.py` renders statistics; called by browser `/dashboard`.
* `app/routes/problems.py` lists and searches problems; called by the navbar.
* `app/routes/problem.py` loads one problem and attempts; called by the problem table.
* `app/routes/submit.py` validates and creates a pending job; called by the editor form.
* `app/routes/result.py` renders and serves live submission JSON; called by result.js.
* `app/routes/history.py` renders filtered paginated history; called by the navbar.
* `app/routes/os_monitor.py` exposes scheduler metrics; called by monitor.js.
* `app/routes/analytics.py` renders GROUP BY reports; called by the navbar.
* `app/database/connection.py` opens thin-mode Oracle connections; called by database queries.
* `app/database/queries.py` contains read queries and identity inserts; called by routes.
* `app/database/submission_queries.py` writes testcase rows and final verdict atomically; called by handler.
* `app/judge/handler.py` connects worker results to Oracle; called by worker.
* `app/os_engine/queue.py` validates and stores FIFO Jobs; called by scheduler and worker.
* `app/os_engine/scheduler.py` records FCFS state and timing; called by submit and monitor routes.
* `app/os_engine/worker.py` runs the one lazy daemon consumer; called on first submit.
* `app/os_engine/process.py` compiles and executes C child processes; called by handler.
* `app/judge/compiler.py`, `executor.py`, `evaluator.py`, and `judge.py` are legacy compatible judge helpers retained from the supplied project; only the newer process API is used by the worker.
* `database/schema.sql` creates normalized Oracle tables and constraints; run first in SQL*Plus.
* `database/seed.sql` inserts ten problems and thirty title-looked-up tests; run second.
* `database/indexes.sql` adds lookup indexes; run third.
* `database/views.sql` adds history, stats, and summary views; run fourth.
* `database/triggers.sql` adds the status audit trigger; run fifth.
* `database/queries.sql` holds twelve viva queries; read or run individually.
* `database/verify.sql` proves objects and row counts; run last.
* `templates/*.html` are Jinja pages; returned by route functions.
* `templates/base.html` supplies navbar, flashes, footer, and shared layout; extended by every page.
* `templates/login.html` and `register.html` render auth forms; returned by `auth.py`.
* `templates/dashboard.html` renders user statistics; returned by `dashboard.py`.
* `templates/problems.html` and `problem.html` render browsing and the editor; returned by problem routes.
* `templates/result.html` hosts live result polling; returned by `result.py`.
* `templates/history.html` renders filters and pagination; returned by `history.py`.
* `templates/os_monitor.html` and `analytics.html` render OS/DBMS reports; returned by their route modules.
* `templates/404.html` is the friendly missing-page state; returned by the app error handler.
* `static/css/style.css` is the product-like responsive style; loaded by base.html.
* `static/js/app.js` is the retained small global script from the supplied project; it is safe for shared pages.
* `static/js/editor.js` adds Tab insertion and reset; loaded by problem.html.
* `static/js/result.js` polls the result API; loaded by result.html.
* `static/js/monitor.js` polls scheduler metrics; loaded by os_monitor.html.
* `tests/test_os.py` tests queue, lock, worker recovery, and timing; run by unittest.
* `tests/test_judge.py` tests GCC, compile errors, timeout, and transaction seam; run by unittest.
* `tests/test_database.py` checks required SQL scripts and seed counts without Oracle.
* `tests/demo_race_condition.py` demonstrates concurrent duplicate admission; run directly.
* `tests/demo_concurrency.py` demonstrates FIFO worker completion; run directly.
* `docs/OS_CONCEPTS.md`, `DBMS_CONCEPTS.md`, and `VIVA_QA.md` explain viva concepts; read before evaluation.
* `FINAL_REPORT.md` separates performed checks, unavailable checks, and limitations.
