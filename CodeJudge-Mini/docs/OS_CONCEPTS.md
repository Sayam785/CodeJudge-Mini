# Operating Systems concepts

| Concept | Exact implementation | Viva explanation |
|---|---|---|
| Process creation | `app/os_engine/process.py: execute_program` uses `subprocess.Popen` | The OS creates a child process for each test case. |
| I/O redirection | `execute_program` opens `stdin`, `stdout`, and `stderr` files | The child reads input from a file and writes output to files instead of the terminal. |
| Exit status | `execute_program` checks `process.returncode` | A non-zero exit code becomes `RUNTIME_ERROR`. |
| Time limit and termination | `execute_program` measures `time.perf_counter`, calls `kill()` and then `wait()` | The watchdog terminates slow children and waits so no zombie remains. |
| Output limit | `execute_program` checks redirected file sizes | A program producing over 1 MB is killed and reported as a runtime error. |
| FCFS scheduling | `app/os_engine/scheduler.py: FCFSScheduler.schedule` | Jobs enter a FIFO queue and the oldest ready job runs first. |
| Waiting time | `FCFSScheduler.mark_running` | Start time minus enqueue time is the queue waiting time. |
| Run/burst time | `FCFSScheduler.mark_completed` | Finish time minus start time is the CPU burst approximation. |
| Turnaround time | `FCFSScheduler.mark_completed` | Finish time minus enqueue time includes waiting plus execution. |
| Producer-consumer | `app/os_engine/queue.py` and `worker.py` | Flask requests produce jobs; one background thread consumes them. |
| Critical section | `FCFSScheduler` methods protected by `_lock` | The shared job table and metrics are updated atomically. |
| Mutex | `threading.Lock` in `scheduler.py` and worker startup lock | Only one thread can update the protected section at a time. |
| Race condition | `tests/demo_race_condition.py` | Concurrent duplicate admissions show why the scheduler lock matters. |
| Graceful shutdown | `SubmissionWorker.stop` and `stop_worker` | A `threading.Event` asks the worker to stop after its current work. |

The project deliberately has one worker for Phase 2. A worker pool is Phase 3.
