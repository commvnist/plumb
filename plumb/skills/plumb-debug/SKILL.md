---
name: plumb-debug
description: Finds the root cause of a bug from evidence and fixes it at its origin with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this fail", regressions.
---

# Plumb: debug

## Steps

1. **Reproduce** the exact error; an intermittent one by forcing its cause. What won't reproduce gets evidence, not a fix.
2. **Trace** backward from the symptom; test each candidate cause.
3. **Name the cause** in one sentence.
4. **Lock it** with one test that fails before the fix on every run.
5. **Fix at the origin** with the smallest diff, never a suppression.
6. **Clean up** instrumentation and scratch files.
7. **Report:** under Why, the cause and the observation that established it (command or file:line); under Suggestions, other places with the same fault, unfixed.
