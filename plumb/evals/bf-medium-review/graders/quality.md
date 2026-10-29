---
type: llm
---
Pass only if all hold:
- The verdict is request changes.
- A Blocking finding says the test row that pinned the cap (9 years -> 100) was deleted instead of updated, so the changed cap is now untested, and the fix is to assert the new cap (for example 9 years -> 150).
- The review ran or traced the tests rather than trusting "Tests pass".
- It changed no files.
