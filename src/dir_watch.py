from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from job import Job
from submission import JobSubmission

import signal
import time
import os
from pathlib import Path

JOB_COUNT = 9

class GracefulExit(Exception):
    pass

def raise_graceful_exit(*args):
    raise GracefulExit()

class Handler(FileSystemEventHandler):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.active_jobs = 0
        self.job_queue = []
        self.started_jobs = []

        self._start()

    def on_created(self, event):
        job = self._new_job(event.src_path)

        if self.active_jobs < JOB_COUNT:
            time.sleep(1)
            job.start()

            self.started_jobs.append(job)

            self.active_jobs += 1
        else:
            self.job_queue.append(job)

    def on_deleted(self, event):
        if self.job_queue != []:
            job = self.job_queue.pop()
            job.start()

            self.started_jobs.append(job)

        else:
            self.active_jobs -= 1

    def _new_job(self, job_path):
        job_submission = JobSubmission(
            job_path,
            self.root_dir
        )
        job_config = job_submission.configure_job()

        job = Job(
            job_submission = job_submission,
            job_config = job_config
        )

        return job

    def _start(self):
        jobs_path = Path(self.root_dir / "jobs")
        job_paths = [path for path in list(jobs_path.iterdir()) if not path.name.startswith(".")]

        for path in job_paths:
            job = self._new_job(str(path))

            if self.active_jobs < JOB_COUNT:
                time.sleep(1)
                job.start()

                self.started_jobs.append(job)

                self.active_jobs += 1
            else:
                self.job_queue.append(job)

def clean_jobs(handler):
    for job in handler.started_jobs:
        if job.returncode == None:
            job.stop()

    if job.lifecycle.is_alive():
        job.lifecycle.join(timeout=1.0)

def start_lifecycle():
    signal.signal(signal.SIGTERM, raise_graceful_exit)
    root_dir = Path(__file__).resolve().parent.parent

    observer = Observer()
    handler = Handler(root_dir)
    observer.schedule(
        handler,
        str(root_dir / "jobs/"), 
        recursive=True
    )

    observer.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, GracefulExit):
        observer.stop()
        observer.join()
        clean_jobs(handler)




def main():
    start_lifecycle()


if __name__ == "__main__":
    main()
