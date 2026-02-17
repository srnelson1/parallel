
This is a scrappy python program used for running jobs in parallel. Each job takes the form:

BOF

\#@#COMMAND=
\#@#WALLTIME=HH:MM:SS
\#@#HAS_OUTPUT

SCRIPT

EOF

The lines \#@# may appear in any order, but they must take place in the first three lines of the file. These are options for the job. SCRIPT is the script to be executed. COMMAND specifies what commands the job should be run with. For example, if the file must be run with a language LANG, either a shebang can be included in the SCRIPT section, or one might write COMMAND=LANG,-f,-g,-h where LANG is the language to pipe the script to, and -f, -g, -h are flags it must be run with. WALLTIME specifies how long the job runs. If no WALLTIME is given, the job runs indefinitely. HAS_OUTPUT states whether or not stdout of the job should be redirected to an output file. It takes HAS_OUTPUT=FALSE or HAS_OUTPUT=TRUE. If HAS_OUTPUT is not specified, it defaults to FALSE.

To start, begin by running watch_dir.py in src/. Job's are submitted by placing the job's file in jobs/. Any errors corresponding to a particular job are automatically placed in errors/. If output is set to TRUE, Job outputs appear in outputs/.

By default, the maximum number of active jobs at any one time is 9. This can be altered by changing the number JOB_COUNT in src/dir_watch.py.
