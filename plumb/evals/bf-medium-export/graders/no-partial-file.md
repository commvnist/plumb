---
type: llm
focus: {source: file, path: app/exports.py}
---
This is app/exports.py after the change. Pass if an export that fails part way (a crash, a
full disk, a database error mid-read) cannot leave a half-written CSV at the given path for
finance to pick up: for example it writes to a temporary file and renames it into place, or
removes the partial file on failure. Fail if it opens the given path for writing and writes the
rows straight into it.
