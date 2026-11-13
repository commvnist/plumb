---
name: plumb-debug
description: Finds the root cause of a bug from evidence and fixes it at its origin with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this fail", regressions.
---

# Plumb: debug

## Steps

1. **Reproduce** the exact error.
2. **Trace** backward from the symptom.
3. **Hypothesise and test** each candidate cause.
4. **Name the cause** in one sentence.
5. **Fix at the origin,** with the smallest diff, never a suppression.
6. **Lock it** with one test that fails without the fix.
7. **Clean up** instrumentation and scratch files.
8. **Report** the cause with the observation that established it, by command or file:line; list other places with the same fault under Noticed, unfixed.
