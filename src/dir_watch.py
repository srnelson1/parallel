from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from job import Job
from submission import JobSubmission

import time
import os




class Handler(FileSystemEventHandler):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def on_created(self, event):
        time.sleep(1)
        job_submission = JobSubmission(
            event.src_path,
            self.root_dir
        )
        job_config = job_submission.configure_job()

        job = Job(
            job_submission = job_submission,
            job_config = job_config
        )
        job.start()


def main():
    root_dir = os.path.expanduser("~/cluster/parallel")

    observer = Observer()
    observer.schedule(
        Handler(root_dir),
        os.path.join(root_dir, "jobs/"), 
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
