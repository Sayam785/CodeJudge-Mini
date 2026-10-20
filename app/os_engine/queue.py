"""The submission queue used by the judge worker.

The queue deliberately contains a small, immutable value object rather than
unvalidated dictionaries.  This makes the boundary between the Flask route
and the asynchronous worker explicit and keeps bad jobs out of the queue.
"""

from dataclasses import dataclass
from math import isfinite
from queue import Empty, Queue
from typing import Any, Mapping, Optional

MAX_SOURCE_BYTES = 64 * 1024


class JobValidationError(ValueError):
    """Raised when a value cannot be converted into a valid :class:`Job`."""


@dataclass(frozen=True, slots=True)
class Job:
    """A validated submission waiting to be judged."""

    submission_id: int
    problem_id: int
    source_code: str
    time_limit: float

    def __post_init__(self) -> None:
        if isinstance(self.submission_id, bool) or not isinstance(
            self.submission_id, int
        ) or self.submission_id <= 0:
            raise JobValidationError("submission_id must be a positive integer")
        if isinstance(self.problem_id, bool) or not isinstance(
            self.problem_id, int
        ) or self.problem_id <= 0:
            raise JobValidationError("problem_id must be a positive integer")
        if not isinstance(self.source_code, str) or not self.source_code.strip():
            raise JobValidationError("source_code must be a non-empty string")
        if len(self.source_code.encode("utf-8")) > MAX_SOURCE_BYTES:
            raise JobValidationError("source_code must be 64 KB or smaller")
        if isinstance(self.time_limit, bool) or not isinstance(
            self.time_limit, (int, float)
        ) or not isfinite(float(self.time_limit)) or self.time_limit <= 0:
            raise JobValidationError("time_limit must be a positive number")

        # Store a stable float even when callers supplied an integer.
        object.__setattr__(self, "time_limit", float(self.time_limit))

    @classmethod
    def from_value(cls, value: Any) -> "Job":
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise JobValidationError("submission job must be a Job or mapping")

        required = ("submission_id", "problem_id", "source_code", "time_limit")
        missing = [name for name in required if name not in value]
        if missing:
            raise JobValidationError(
                "Submission job is missing required fields: " + ", ".join(missing)
            )
        try:
            if isinstance(value["submission_id"], bool) or isinstance(
                value["problem_id"], bool
            ) or isinstance(value["time_limit"], bool):
                raise JobValidationError("boolean job fields are not valid")
            for field in ("submission_id", "problem_id"):
                raw_id = value[field]
                if not isinstance(raw_id, int) and not (
                    isinstance(raw_id, str) and raw_id.isdigit()
                ):
                    raise JobValidationError(f"{field} must be an integer")
            return cls(
                submission_id=int(value["submission_id"]),
                problem_id=int(value["problem_id"]),
                source_code=value["source_code"],
                time_limit=float(value["time_limit"]),
            )
        except (TypeError, ValueError, OverflowError) as exc:
            if isinstance(exc, JobValidationError):
                raise
            raise JobValidationError(str(exc)) from exc

    def __getitem__(self, key: str) -> Any:
        """Retain dictionary-style access for existing integrations."""
        return getattr(self, key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "submission_id": self.submission_id,
            "problem_id": self.problem_id,
            "source_code": self.source_code,
            "time_limit": self.time_limit,
        }


class SubmissionQueue:
    """A real, thread-safe FIFO :class:`queue.Queue` of :class:`Job` values."""

    def __init__(self, maxsize: int = 0):
        self._queue: Queue[Job] = Queue(maxsize=maxsize)

    def enqueue(self, job: Job | Mapping[str, Any]) -> Job:
        # Convert and validate before calling put: invalid jobs never mutate
        # the queue, even if validation itself raises.
        validated = Job.from_value(job)
        self._queue.put(validated)
        return validated

    def dequeue(self, timeout: Optional[float] = 1) -> Optional[Job]:
        try:
            if timeout is None:
                return self._queue.get()
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def task_done(self) -> None:
        self._queue.task_done()

    def join(self) -> None:
        self._queue.join()

    def size(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()

    def clear(self) -> None:
        """Remove pending jobs (mainly useful for isolated test fixtures)."""
        while True:
            try:
                self._queue.get_nowait()
            except Empty:
                return
            else:
                self._queue.task_done()


submission_queue = SubmissionQueue()
