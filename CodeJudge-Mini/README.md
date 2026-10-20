# CodeJudge-Mini

CodeJudge-Mini is a small online judge for a B.Tech Phase 2 demonstration. A
logged-in student opens an easy C problem, submits source code, and watches a
single background worker compile and run it against three Oracle test cases.

The project deliberately demonstrates real OS and DBMS ideas without pretending
to be a production sandbox. The worker uses a FIFO `queue.Queue`, FCFS metadata,
`threading.Lock`, a producer-consumer thread, and child processes. Oracle uses
identity keys, foreign keys, CLOBs, views, an audit trigger, and transactions.

## 1. PowerShell setup

Open PowerShell in the `CodeJudge-Mini` folder:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
gcc --version
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass`
once in that terminal. The application does not need administrator rights.

## 2. Oracle setup

Start the Oracle XE database and connect to service `XEPDB1` as the application
schema. The default credentials are `SAYAM_PBL` / `123`; override them for the
Flask process with environment variables rather than editing route code.

```powershell
sqlplus SAYAM_PBL/123@localhost:1521/XEPDB1
@database/schema.sql
@database/seed.sql
@database/indexes.sql
@database/views.sql
@database/triggers.sql
@database/verify.sql
EXIT
```

## 3. Run the web application

```powershell
$env:ORACLE_USER = "SAYAM_PBL"
$env:ORACLE_PASSWORD = "123"
$env:ORACLE_DSN = "localhost:1521/XEPDB1"
python app.py
```

Open `http://127.0.0.1:5000`, register, open a problem, submit C code, and
watch the result page. The worker starts lazily on the first submission so the
Flask debug reloader cannot create two workers.

## 4. Tests and OS demonstrations

```powershell
python -m unittest discover -s tests -v
python tests/demo_race_condition.py
python tests/demo_concurrency.py
```

The first demo prints how many concurrent admissions won the scheduler lock.
The second prints the order consumed by the single FCFS worker. Oracle-backed
route testing must be performed after the SQL scripts have been run.

## Troubleshooting

* `DPY-6005` or connection refused: start Oracle XE and confirm the PDB is
  open; check `localhost:1521/XEPDB1` and the environment variables.
* `gcc is not recognized`: install MinGW-w64, add its `bin` folder to PATH,
  open a new PowerShell, and confirm with `gcc --version`.
* `Address already in use`: stop the old Flask process or use
  `$env:FLASK_PORT = "5001"` and change the URL.
* A submission is `INTERNAL_ERROR`: check the Flask terminal, Oracle status,
  and that the process is not running as Windows Administrator.

## Phase 3 (not built yet)

Multi-worker pools, memory limits, a real sandbox/container, extra languages,
and priority or Round Robin scheduling are intentionally left for Phase 3.

## Safety limitation

This is an educational local judge, not a secure sandbox. Submitted C code is
compiled and run as the normal desktop user. The implementation has time and
output limits and always kills/waits for timed-out children, but it does not
isolate filesystem, network, or operating-system privileges.

See `docs/FILE_GUIDE.md`, `docs/OS_CONCEPTS.md`, `docs/DBMS_CONCEPTS.md`, and
`docs/VIVA_QA.md` for viva preparation.
