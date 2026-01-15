
This is a scrappy python program used for running jobs in parallel. Each job takes the form:

BOF
\###lang
\###walltime
\###has_output

SCRIPT
EOF

where "lang" is the language interpreter, "walltime" is the length of time the job is permitted to run, and "has_output" indicates whether or not the jobs output from stdout should be piped to a file in outputs/. Note that has_outut accepts "TRUE" to indicate output. Anything else is treated as false. If walltime is not given, it automatically sets to None, and the job runs indefinitely.

To start, begin by running watch_dir.py in src/. Job's are submitted by placing the job's file in jobs/. Any errors corresponding to a particular job are automatically placed in errors/. If output is set to TRUE, Job outputs appear in outputs/.
