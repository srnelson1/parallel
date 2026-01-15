import os
import tempfile

CLOCK = [3600, 60, 1]

class Submission():
    def __init__(self, submission_path = None):
        self.path = submission_path
        self.file_path = None
        self.lang = None
        self.walltime = None

    def build_job(self):
        with open(self.path, "r") as f:
            lines = [next(f) for line in range(0, 3)]
            script = f.read()

        self.file_path = self._build_file_script(script)
        self.lang = lines[0].replace("#", "").strip()
        self.walltime = self._compute_walltime(lines[1])
        self.has_output = self._has_output(lines[2])

    def _build_file_script(self, script):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(script)
            return tmp.name

    def _compute_walltime(self, line):
        if ":" in line:
            walltime = line.replace("#", "").strip()
            l = [int(x) for x in walltime.split(":")]
            return sum(x*y for x, y in zip(l, CLOCK))

        else:
            return None

    def _has_output(self, line):
        line = line.replace("#", "").strip()
        if line == "TRUE":
            return True
        else:
            return False
