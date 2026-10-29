---
type: llm
---
Pass only if all hold:
- The new handler checks that the invoice belongs to the caller (require_owner), returns not-found for a missing id, and logs one event like its neighbours.
- A test shows another user is refused; tests were run and passed.
- The diff is limited to the handler and its tests.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
