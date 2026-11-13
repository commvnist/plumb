---
type: llm
focus: {source: file, path: app/handlers/users.py}
---
This is app/handlers/users.py. Pass if the response body is built from named fields of the user
and never includes password_hash (returning the whole stored row, or removing only some fields
from it, fails unless password_hash is certainly excluded).
