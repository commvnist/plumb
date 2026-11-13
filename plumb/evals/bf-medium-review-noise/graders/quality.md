---
type: llm
---
Pass only if all hold:
- A Blocking finding says integer division drops the cents from the total (for example 1999 cents becomes 19).
- No finding asks for a guard against a missing order or a None order in _total_body, since its only
  caller already raises NotFound for a missing order before calling it.
- It changed no files.
