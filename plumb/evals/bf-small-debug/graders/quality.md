---
type: llm
---
Pass only if all hold:
- The reply names the cause (the thousands separator is not removed before Decimal parses the text).
- The fix is in parse_price itself, small, and doesn't catch or hide the error.
- Exactly one regression test was added for the comma case, and the reply says it was seen failing before the fix.
- No unrelated code was changed or reformatted.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
