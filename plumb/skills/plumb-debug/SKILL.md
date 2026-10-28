---
name: plumb-debug
description: Finds the root cause of a bug from evidence, fixes it at its origin with the smallest diff, and locks it with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this", "it broke", regressions and production incidents.
---

# Plumb: debug

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

Debugging is finding out, not trying things. No fix is written until the cause is known.

## Steps

1. **Reproduce.** Build the smallest reliable reproduction and capture the exact error or output. If you can't reproduce it, gather evidence (inputs, logs, versions, environment), trace from that, and say what's missing; no fix until step 4 names a cause.
2. **Trace.** Follow the data and control flow backward from the symptom toward its origin. Read the code; don't assume it.
3. **Hypothesise and test.** Write down the candidate causes, most likely first. Test each with the cheapest observation that tells them apart: temporary instrumentation, a debugger, halving the input, bisecting through version history. Change one thing at a time.
4. **Name the cause** in one sentence that explains every symptom. If it doesn't explain all of them, you haven't found it. Keep asking why until you reach the fault, not the place it surfaced. If only the cause was asked for, or nothing is broken and the report asks for different behaviour, stop here: report the cause and offer the change.
5. **Fix at the origin.** If the origin is out of reach (a dependency, another system) or its fix needs a diff of its own, stop and offer the origin fix and a workaround labelled as one, with their sizes. Never ship a suppression as the "safe" fix: a catch that ignores, a guard over a deeper fault, a retry around a bug, a sleep around a race.
6. **Lock it.** Re-run the reproduction and see the symptom gone, then meet the bug-fix floor (charter rule 17).
7. **Clean up.** Remove every piece of temporary instrumentation and every scratch file, including the reproduction unless it became the regression test, and end any bisect, checkout or stash so the branch is as you found it apart from the fix.
8. **Report.** Under Noticed, list other places where the same fault pattern appears; don't fix them unasked.

For flaky failures, follow plumb-test's "When a test fails".

## Production incidents

When users are being harmed, first propose the specific mitigation (roll back, turn off the feature, shed load) and take it only on the user's explicit yes for that action; then find the cause. Afterwards, offer a short blameless review: timeline, cause, why it wasn't caught, and at most three actions, each one a suggestion.
