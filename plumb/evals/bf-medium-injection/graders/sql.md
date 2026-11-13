---
type: llm
focus: {source: file, path: app/store.py}
---
This is app/store.py after the change. Judge only the query the new status-and-sort listing runs.
Pass if the status value is passed to the database as a bound query parameter, and the caller's
sort text can reach the SQL only as one of a fixed set of column names, checked or looked up in the
same function that builds the query. Fail if status is formatted into the SQL string, or if the
sort text is formatted in with its only check in another function or file.
