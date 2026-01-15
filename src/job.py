import threading
import subprocess
import tempfile
import shutil
import os
import time


class JobError():
    def __init__(self, job_submission = None, job_config=None):
        self.job_submission = job_submission
        self.job_config = job_config

        self.path = None
        self.file = None
        self.initial_size = None

    def make_file(self):
        self.path = os.path.join(tempfile.gettempdir(), f"{self.job_submission.name}.err")

        self.file = open(self.path, "w")
        self.file.write(f"\n[{time.strftime('%H:%M:%S')}] Launching: {self.job_config.file_path}\n")
        self.file.flush()

        self.initial_size = os.stat(self.file.fileno()).st_size

    def clean(self):
        self.file.flush()
        final_size = os.stat(self.file.fileno()).st_size
        self.file.close()

        if final_size > self.initial_size:
            has_error = True
        else:
            has_error = False

        if has_error == True:
            new_path = os.path.expanduser(f"~/cluster/parallel/errors/{self.job_submission.name}.err")
            shutil.move(self.path, new_path)

            print(f"Process failure! See log: {new_path}.")
        else:
            os.remove(self.path)


class JobOutput():
    def __init__(self, job_submission = None, job_config = None):
        self.job_submission = job_submission
        self.job_config = job_config

        if not self.job_config.has_output:
            self.file = subprocess.DEVNULL
            self.out_path = None

    def make_file(self):
        out_dir = os.path.expanduser("~/cluster/parallel/output")
        self.out_path = os.path.join(out_dir, f"{self.job_submission.name}.out")
        self.file = open(self.out_path, "w")

    def clean(self):
        if self.job_config.has_output:
            self.file.close()


class Job():
    def __init__(self, job_submission = None, job_config = None):
        self.job_submission = job_submission
        self.job_config = job_config

        self.job_error = JobError(
            job_submission = self.job_submission,
            job_config = self.job_config
        )
        self.job_error.make_file()

        self.job_output = JobOutput(
                job_submission = job_submission,
                job_config = job_config
        )
        self.job_output.make_file()

        self.proc = None
        self.returncode = None


    def start(self):
        proc = subprocess.Popen(
                [self.job_config.lang, self.job_config.file_path],
                stdout = self.job_output.file,
                stderr = self.job_error.file,
                stdin = subprocess.DEVNULL
        )

        self.proc = proc

        lifecycle = threading.Thread(
            target = self._run_lifecycle,
            daemon = True,
            name = f"Job-{self.job_submission.name}"
        )

        lifecycle.start()

    def stop(self):
        self.proc.terminate()

        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()

    def clean(self):
        self.job_error.clean()
        self.job_output.clean()

        os.remove(self.job_config.file_path)
        os.remove(self.job_submission.path)

    def _run_lifecycle(self):
        try:
            self.proc.wait(timeout=self.job_config.walltime)

        except subprocess.TimeoutExpired:
            self.stop()

        self.proc.wait()
        self.proc.poll()

        self.returncode = self.proc.returncode 
        self.clean()
