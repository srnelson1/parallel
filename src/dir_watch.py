from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from job import Job
from submission import JobSubmission

import time
import os


WATCH_DIR = os.path.expanduser("~/cluster/parallel/jobs")


class Handler(FileSystemEventHandler):
    def __init__(self):
        pass

    def on_created(self, event):
        time.sleep(1)
        job_submission = JobSubmission(event.src_path)
        job_config = job_submission.configure_job()

        job = Job(
            job_submission = job_submission,
            job_config = job_config
        )
        job.start()


def main():
    observer = Observer()
    observer.schedule(
        Handler(),
        WATCH_DIR, 
        recursive=True
    )

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
