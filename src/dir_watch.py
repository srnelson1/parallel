from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from job import Job
from submission import Submission

import time
import os


WATCH_DIR = os.path.expanduser("~/cluster/parallel/jobs")


class Handler(FileSystemEventHandler):
    def __init__(self):
        pass

    def on_created(self, event):
        time.sleep(1)
        
        submission = Submission(event.src_path)
        submission.build_job()

        job = Job(
            submission_path = submission.path,
            file_path = submission.file_path, 
            lang = submission.lang,
            walltime = submission.walltime,
            has_output = submission.has_output
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
