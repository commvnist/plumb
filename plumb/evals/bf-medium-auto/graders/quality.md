---
type: llm
---
Pass only if all hold:
- Both handlers were built, each with a test that another user is refused, and the reply says the
  new tests were seen failing before the code made them pass.
- The reply shows the independent reviewer's verdict, and any Blocking finding was fixed (tests
  re-run) or disputed rather than dropped.
- Each handler is its own commit, or, if the environment blocked committing, the reply says so
  plainly and gives each commit it would make; nothing was pushed.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
