---
name: plumb-debug
description: Finds the root cause of a bug from evidence, fixes it at its origin with the smallest diff, and locks it with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this fail", "it broke", regressions and production incidents.
---

# Plumb: debug

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

Debugging is finding out, not trying things. No fix is written until the cause is known.

## Steps

1. **Reproduce.** Build the smallest reliable reproduction and capture the exact error or output, and run the project's checks relevant to that code as a baseline (charter rule 15). Reproduce and probe where it affects nothing real; anything else needs a yes (charter rule 2). If you can't reproduce it, gather evidence (inputs, logs, versions, environment), trace from that, and say what's missing.
2. **Trace.** Follow the data and control flow backward from the symptom toward its origin. Read the code; don't assume it.
3. **Hypothesise and test.** Write down the candidate causes, most likely first. Test each with the cheapest observation that tells them apart: temporary instrumentation, a debugger, halving the input, bisecting through version history. Change one thing at a time.
4. **Name the cause** in one sentence that explains every symptom. If it doesn't explain all of them, you haven't found it, or there is more than one bug: name each cause and fix each in its own diff. Keep asking why until you reach the fault, not the place it surfaced. If only the cause was asked for, or nothing is broken and the report asks for different behaviour, stop here: report the cause and offer the change.
5. **Fix at the origin.** If the origin is out of reach (a dependency, another system) or its fix must be staged (charter rule 3), stop and offer the origin fix and a workaround labelled as one, with their sizes. Never ship a suppression as the "safe" fix: a catch that ignores, a guard over a deeper fault, a retry around a bug, a sleep around a race.
6. **Lock it.** Re-run the reproduction and see the symptom gone (with none, put the original symptom under Unverified), then meet the bug-fix floor (charter rule 17) and run the project's checks again.
7. **Clean up**, also when you stopped at step 4 or 5. Remove all temporary instrumentation and scratch files, including your reproduction unless it became the regression test, and end any bisect, checkout or worktree, so the branch is as you found it apart from the fix. If that changed any file after the fix was proven, re-run the proof.
8. **Report**, once your diff passes the charter's self-review checklist. State the cause on the Why line with the observation that established it and the closest other candidate it ruled out, by command or file:line, since a cause the operator can't check is taken on trust and one they can check shows them where to look next time. Under Noticed, list other places where the same fault pattern appears; don't fix them unasked. If the fault already wrote bad data or sent wrong output, say what it damaged under Risks and offer the repair. For a non-trivial fix, offer an independent review by the plumb-reviewer agent (the charter's Agents route when agents are off).

For a failing or flaky test, plumb-test's "When a test fails" decides whether the test or the code is wrong and how a flake is forced and proven fixed. Every step here still applies.

## Production incidents

When users are being harmed, first propose the specific mitigation (roll back, turn off the feature, shed load) and take it only on the user's explicit yes for that action; then find the cause. Afterwards, offer a short blameless review: timeline, cause, why it wasn't caught, and at most three actions, each one a suggestion.
