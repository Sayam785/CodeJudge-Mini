"""The single lazy daemon worker for queued submissions."""

from __future__ import annotations

import ctypes
import logging
import os
import threading
from typing import Any, Callable, Optional

from app.os_engine.queue import Job, SubmissionQueue, submission_queue
from app.os_engine.scheduler import FCFSScheduler, scheduler

logger = logging.getLogger(__name__)

_worker: Optional["SubmissionWorker"] = None
_worker_lock = threading.Lock()


class AdministratorExecutionError(PermissionError):
    """Raised instead of running untrusted submissions as Administrator."""


def is_windows_administrator() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        # A restricted or unusual Windows Python has no admin API available;
        # inability to prove administrator status is treated as non-admin.
        return False


def _default_handler(job: Job) -> dict[str, object]:
    from app.judge.handler import handle_submission

    return handle_submission(job)


# Public compatibility seam: tests and deployments can replace this callable
# without importing an Oracle-backed module.
process_submission = _default_handler


def _default_status_updater(submission_id: int, status: str) -> Any:
    from app.judge.handler import update_submission_status

    return update_submission_status(submission_id, status)


class SubmissionWorker(threading.Thread):
    def __init__(
        self,
        *,
        queue: SubmissionQueue = submission_queue,
        scheduler_: FCFSScheduler = scheduler,
        handler: Callable[[Job], dict[str, object]] | None = None,
        status_updater: Callable[[int, str], Any] = _default_status_updater,
    ) -> None:
        super().__init__(name="CodeJudgeWorker", daemon=True)
        self.queue = queue
        self.scheduler = scheduler_
        self.handler = handler or process_submission
        self.status_updater = status_updater
        self._shutdown = threading.Event()

    def stop(self) -> None:
        self._shutdown.set()

    def run(self) -> None:
        while not self._shutdown.is_set():
            job = self.queue.dequeue(timeout=0.1)
            if job is None:
                continue
            self.scheduler.mark_running(job)
            status = "INTERNAL_ERROR"
            try:
                result = self.handler(job)
                status = str(result.get("status", "INTERNAL_ERROR")).upper()
            except Exception:
                logger.exception("Submission processing failed")
                try:
                    self.status_updater(job.submission_id, "INTERNAL_ERROR")
                except Exception:
                    logger.exception("Could not save internal error status")
            finally:
                self.scheduler.mark_completed(job, status)
                self.queue.task_done()


def start_worker() -> SubmissionWorker:
    """Start exactly one daemon worker, lazily and safely."""
    global _worker
    if is_windows_administrator():
        raise AdministratorExecutionError(
            "CodeJudge refuses to run submissions from a Windows Administrator account."
        )
    with _worker_lock:
        if _worker is None or not _worker.is_alive():
            _worker = SubmissionWorker()
            _worker.start()
        return _worker


def stop_worker(timeout: Optional[float] = 5.0) -> None:
    """Request a stop and wait for the daemon to finish its current job."""
    global _worker
    with _worker_lock:
        current = _worker
    if current is None:
        return
    current.stop()
    if current is not threading.current_thread():
        current.join(timeout=timeout)
    with _worker_lock:
        if _worker is current and not current.is_alive():
            _worker = None


def worker() -> Optional[SubmissionWorker]:
    return _worker
