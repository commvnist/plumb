---
name: plumb-debug
description: Finds the root cause of a bug from evidence, fixes it at its origin with the smallest diff, and locks it with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this fail", "it broke", regressions and production incidents.
---

# Plumb: debug

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

No fix is written until the cause is known.

## Steps

1. **Reproduce.** Build the smallest reliable reproduction and capture the exact error.
2. **Trace.** Follow the data backward from the symptom toward its origin.
3. **Hypothesise and test.** Test each candidate cause with the cheapest observation that tells them apart.
4. **Name the cause** in one sentence that explains every symptom.
5. **Fix at the origin,** with the smallest diff; never a suppression (a catch that ignores, a retry, a sleep).
6. **Lock it.** One test that fails without the fix; run the project's checks again.
7. **Clean up.** Remove all temporary instrumentation and scratch files.
8. **Report.** State the cause on the Why line with the observation that established it, by command or file:line. List other places with the same fault under Noticed; don't fix them unasked.
