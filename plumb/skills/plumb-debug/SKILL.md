---
name: plumb-debug
description: Finds the root cause of a bug from evidence and fixes it at its origin with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this fail", regressions.
---

# Plumb: debug

## Steps

1. **Reproduce** the exact error; an intermittent one by forcing its cause.
2. **Trace** backward from the symptom; the nearest state that passes (the base branch, an earlier commit) bounds the cause, and halving what differs (commits, input, configuration) narrows it. Test each candidate cause alone, by a run whose outcome you predict first; say what each ruled out.
3. **Name the cause** a run confirmed, in one sentence; an unconfirmed one is a suspect, reported with its evidence and unfixed. Asked only why, stop here and offer the fix.
4. **Lock it** with one test that forces the cause and fails before the fix on every run.
5. **Fix at the origin** with the smallest diff, never a suppression.
6. **Clean up** instrumentation and scratch files, then rerun step 1's reproduction: while it fails, the bug isn't fixed.
7. **Report:** under Suggestions, other places with the same fault, unfixed.
