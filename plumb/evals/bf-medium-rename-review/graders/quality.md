---
type: llm
---
The branch renames a persisted column in one step, and order responses return the stored row, so
the API field changes name too. Pass only if all hold:
- The verdict is request changes, with a Blocking finding that the rename breaks whatever still
  reads or writes the old name: the running version during a deploy, a rollback, or API clients
  that read "status".
- The fix it gives stages the change (add the new column or field, move readers and writers, then
  drop the old), rather than only asking for more tests.
- It changed no files.
