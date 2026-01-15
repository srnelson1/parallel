import threading
import subprocess
import tempfile
import shutil
import os
import time

class Job():
    def __init__(self, submission_path=None, file_path=None, lang=None, walltime=None, has_output=None):
        self.submission_path = submission_path
        self.file_path = file_path
        self.lang = lang
        self.walltime = walltime
        self.has_output = has_output

        self.proc = None
        self.returncode = None
        self.err_file = None
        self.err_path = None
        self.out_file = None
        self.out_path = None

        self.submission_name = os.path.basename(self.submission_path)


    def start(self):
        if self.has_output == True:
            self.out_file = self._out_file()
        else:
            self.out_file = subprocess.DEVNULL
        self._error_file()

        proc = subprocess.Popen(
                [self.lang, self.file_path],
                stdout = self.out_file,
                stderr = self.err_file,
                stdin = subprocess.DEVNULL
        )

        self.proc = proc

        lifecycle = threading.Thread(
            target = self._run_lifecycle,
            daemon = True,
            name = f"Job-{os.path.basename(self.file_path)}"
        )

        lifecycle.start()


    def stop(self):
        self.proc.terminate()

        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()


    def is_running(self):
        return self.proc.poll() == None

    def clean(self):
        self.err_file.close()

        if self.has_output == True:
            self.out_file.close()

        if self._errored() == False:
            os.remove(self.err_path)
        else:
            new_path = os.path.expanduser(f"~/cluster/parallel/errors/{self.submission_name}.err")
            shutil.move(self.err_path, new_path)

            print(f"Process failure! See log: {new_path}.")
            

        os.remove(self.file_path)
        os.remove(self.submission_path)

    def _out_file(self):
        out_dir = os.path.expanduser("~/cluster/parallel/output")
        self.out_path = os.path.join(out_dir, f"{self.submission_name}.out")
        out_file = open(self.out_path, "w")

        return out_file


    def _error_file(self):
        self.err_path = os.path.join(tempfile.gettempdir(), f"{self.submission_name}.err")

        self.err_file = open(self.err_path, "w")
        self.err_file.write(f"\n[{time.strftime('%H:%M:%S')}] Launching: {self.file_path}\n")
        self.err_file.flush()

    def _errored(self):
        with open(self.err_path, "r") as err_file:
            text = err_file.read()
            if "error" in text.lower() or self.returncode != 0: #some languages return 0 even on error
                return True

        return False

    def _run_lifecycle(self):
        try:
            self.proc.wait(timeout=self.walltime)

        except subprocess.TimeoutExpired:
            self.stop()

        self.proc.wait()
        self.proc.poll()

        self.returncode = self.proc.returncode 
        self.clean()
