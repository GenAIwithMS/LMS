# Live tests (need the running server and the demo database)

These are not part of `pytest tests`. They talk to a running backend on
http://localhost:5000 and change its database, so **back up the database first**
and restore it afterwards.

- `e2e_school_term.py` - one school term from start to end (admin, teachers, students),
  81 checked steps. Logs in about 8 times, so it needs a fresh login-limit minute.
- `load_run.py <requests per round> <parallel> <rounds> [label]` - many users at once,
  e.g. `load_run.py 1000 200 3`. Prints success rate, response times and errors.
  Delete the state file it prints about between databases.

See `RELIABILITY_TEST_REPORT.md` in the project folder for the results.
