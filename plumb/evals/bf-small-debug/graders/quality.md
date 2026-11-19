---
type: llm
---
Pass only if all hold:
- The reply names the cause (the thousands separator is not removed before Decimal parses the text).
- The fix is in parse_price itself, small, and doesn't catch or hide the error.
- A regression test was added for the comma case (whether it was seen red is graded by red-run). Any other new test covers a separate input outcome the fix had to decide, not the comma case again.
- No unrelated code was changed or reformatted.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
