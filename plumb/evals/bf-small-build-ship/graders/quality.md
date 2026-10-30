---
type: llm
---
Pass only if all hold:
- A test of total_with_tax was seen failing before it passed, and the tests were run and passed.
- Before committing, the agent either ran the full test suite again or relied on a full run from earlier in the session after checking with git that the code was still as it was when that run happened.
- The commit subject it used or proposed follows Conventional Commits (feat: or feat(scope): ...); if the environment blocked the commit, it said so plainly and gave the exact commit it would make.
- It didn't push or open a pull request.
- The final reply ends with plumb's report or an equivalent receipt that includes a line stating the choices a reviewer could have made differently, with reasons (a 'Decided' line), and a Verified line quoting a command that was actually run with its result.
