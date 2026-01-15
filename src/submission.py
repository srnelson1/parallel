import os
import tempfile

CLOCK = [3600, 60, 1]

class JobConfig():
    def __init__(self, job_submission_path=None, submission_name=None, file_path=None, lang=None, walltime=None, has_output=None):
        self.file_path = file_path
        self.lang = lang
        self.walltime = walltime
        self.has_output = has_output


class JobSubmission():
    def __init__(self, job_submission_path = None):
        self.path = job_submission_path
        self.name = os.path.basename(job_submission_path)

    def configure_job(self):
        with open(self.path, "r") as f:
            lines = [next(f) for line in range(0, 3)]
            script = f.read()

        self.job_config = JobConfig(
            file_path = self._build_file_script(script),
            lang = lines[0].replace("#", "").strip(),
            walltime = self._compute_walltime(lines[1]),
            has_output = self._has_output(lines[2])
        )

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
