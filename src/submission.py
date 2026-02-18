import os
import tempfile

CLOCK = [3600, 60, 1]

class JobConfig():
    def __init__(self, 
                 root_dir,
                 file_path=None,
                 subproc=None,
                 walltime=None,
                 has_output=False
                 ):
        self.file_path = file_path
        self.root_dir = root_dir
        self.subproc = [self.file_path]
        self.walltime = walltime
        self.has_output = has_output


class JobSubmission():
    def __init__(self,
                 submission_path,
                 root_dir):
        self.path = submission_path
        self.name = os.path.basename(self.path)
        self.root_dir = root_dir

    def configure_job(self):
        with open(self.path, "r") as f:
            lines = f.readlines()

        config_lines = [line for line in lines if line[:3] == "#@#"]
        script = lines[3:]

        return self._format_config(config_lines, script)


    def _format_config(self, config_lines, script):
        config_lines = [line[3:].strip() for line in config_lines]

        job_config = JobConfig(
            root_dir=self.root_dir
        )

        subproc_config = []

        for i, line in enumerate(config_lines):
            if line.startswith("COMMAND"):
                for item in self._get_command(line):
                    subproc_config.append(item)

            elif line.startswith("WALLTIME"):
                job_config.walltime = self._get_walltime(line)

            elif line.startswith("HAS_OUTPUT"):
                job_config.has_output= self._has_output(line) 

        subproc_config.append( self._build_file_script(script) )
        job_config.subproc = [x for x in subproc_config if x != None]

        return job_config

    @staticmethod
    def _build_file_script(script):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            script = "".join(script)
            tmp.write(script)
            return tmp.name

    @staticmethod
    def _get_command(line):
        return line[8:].split(",")

    @staticmethod
    def _get_walltime(line):
        walltime = line[9:]
        l = [int(x) for x in walltime.split(":")]

        return sum(x*y for x, y in zip(l, CLOCK))

    @staticmethod
    def _has_output(line):
        line = line[11:]

        if line == "TRUE":
            return True
        else:
            return False


def main():
    job_config = JobSubmission(
        submission_path="/Users/sethnelson/Desktop/test/test_submission.txt",
        root_dir="/Users/sethnelson/Desktop/test"
    ).configure_job()

    print(job_config.file_path, "\n", job_config.root_dir, "\n", job_config.subproc, "\n", job_config.walltime, "\n", job_config.has_output)

if __name__ == "__main__":
    main()
