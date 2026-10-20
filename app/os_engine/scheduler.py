"""FCFS scheduling and observable submission state."""

from collections import deque
from threading import Lock
import time
from typing import Any, Mapping, Optional

from app.os_engine.queue import Job, SubmissionQueue, submission_queue


class DuplicateSubmissionError(ValueError):
    """Raised when a submission is scheduled more than once."""


class FCFSScheduler:
    """A mutex-protected FCFS scheduler around a :class:`SubmissionQueue`.

    The queue owns FIFO storage; this class owns the metadata needed by the
    UI and worker.  ``_pending_order`` lets ``queue_position`` be exact while
    the queue is being consumed by another thread.
    """

    def __init__(self, queue: Optional[SubmissionQueue] = None):
        self.queue = queue or SubmissionQueue()
        self._lock = Lock()
        self._jobs: dict[int, dict[str, Any]] = {}
        self._pending_order: deque[int] = deque()
        self._metrics = {
            "submitted": 0,
            "completed": 0,
            "internal_errors": 0,
            "accepted": 0,
            "wrong_answer": 0,
            "compilation_error": 0,
            "runtime_error": 0,
            "time_limit_exceeded": 0,
            "output_limit_exceeded": 0,
        }

    def schedule(self, value: Job | Mapping[str, Any]) -> Job:
        job = Job.from_value(value)
        with self._lock:
            if job.submission_id in self._jobs:
                raise DuplicateSubmissionError(
                    f"submission {job.submission_id} has already been scheduled"
                )
            # Put occurs under the same lock as the table update.  If a
            # bounded queue rejects the put, metadata is rolled back.
            self.queue.enqueue(job)
            self._jobs[job.submission_id] = {
                "job": job,
                "state": "PENDING",
                "enqueued_at": time.perf_counter(),
                "started_at": None,
                "finished_at": None,
                "waiting_time": None,
                "run_time": None,
                "turnaround_time": None,
            }
            self._pending_order.append(job.submission_id)
            self._metrics["submitted"] += 1
        return job

    def mark_running(self, job_or_submission: Job | int) -> None:
        submission_id = self._submission_id(job_or_submission)
        with self._lock:
            entry = self._jobs.get(submission_id)
            if entry is None:
                return
            try:
                self._pending_order.remove(submission_id)
            except ValueError:
                pass
            entry["state"] = "RUNNING"
            entry["started_at"] = time.perf_counter()
            entry["waiting_time"] = entry["started_at"] - entry["enqueued_at"]

    def mark_completed(self, job_or_submission: Job | int, status: str) -> None:
        submission_id = self._submission_id(job_or_submission)
        normalized = str(status or "INTERNAL_ERROR").upper()
        with self._lock:
            entry = self._jobs.get(submission_id)
            if entry is None:
                return
            entry["finished_at"] = time.perf_counter()
            entry["run_time"] = (
                entry["finished_at"] - entry["started_at"]
                if entry["started_at"] is not None else 0.0
            )
            entry["turnaround_time"] = entry["finished_at"] - entry["enqueued_at"]
            entry["state"] = "FAILED" if normalized == "INTERNAL_ERROR" else "COMPLETED"
            entry["status"] = normalized
            self._metrics["completed"] += 1
            key = normalized.lower()
            if key in self._metrics:
                self._metrics[key] += 1
            if normalized == "INTERNAL_ERROR":
                self._metrics["internal_errors"] += 1

    def state(self, submission_id: int) -> Optional[str]:
        with self._lock:
            entry = self._jobs.get(int(submission_id))
            return entry["state"] if entry else None

    def queue_position(self, submission_id: int) -> Optional[int]:
        """Return a one-based FCFS position, or ``None`` once dequeued."""
        with self._lock:
            try:
                return list(self._pending_order).index(int(submission_id)) + 1
            except (ValueError, TypeError):
                return None

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return dict(self._metrics)

    def average_waiting_time(self) -> float:
        with self._lock:
            values = [
                entry["waiting_time"] for entry in self._jobs.values()
                if entry.get("waiting_time") is not None
            ]
            return sum(values) / len(values) if values else 0.0

    def jobs(self) -> dict[int, dict[str, Any]]:
        with self._lock:
            return {
                submission_id: dict(entry)
                for submission_id, entry in self._jobs.items()
            }

    def reset(self) -> None:
        with self._lock:
            self.queue.clear()
            self._jobs.clear()
            self._pending_order.clear()
            for key in self._metrics:
                self._metrics[key] = 0

    @staticmethod
    def _submission_id(value: Job | int) -> int:
        return value.submission_id if isinstance(value, Job) else int(value)


scheduler = FCFSScheduler(submission_queue)


def schedule_submission(job: Job | Mapping[str, Any]) -> Job:
    """Schedule a validated submission using the process-wide scheduler."""
    return scheduler.schedule(job)


def pending_jobs() -> int:
    return scheduler.queue.size()


def queue_position(submission_id: int) -> Optional[int]:
    return scheduler.queue_position(submission_id)


def job_state(submission_id: int) -> Optional[str]:
    return scheduler.state(submission_id)


def scheduler_metrics() -> dict[str, int]:
    return scheduler.metrics()


def state(submission_id: int) -> Optional[str]:
    return scheduler.state(submission_id)


def metrics() -> dict[str, int]:
    return scheduler.metrics()


def average_waiting_time() -> float:
    return scheduler.average_waiting_time()
