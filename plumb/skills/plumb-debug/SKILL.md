---
name: plumb-debug
description: Finds the root cause of a bug from evidence, fixes it at its origin with the smallest diff, and locks it with one regression test. Use for bugs, errors, crashes, failing or flaky tests, "why does this", "it broke", regressions and production incidents.
---

# Plumb: debug

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

Debugging is finding out, not trying things. No fix is written until the cause is known.

## Steps

1. **Reproduce.** Build the smallest reliable reproduction and capture the exact error or output, and run the project's checks relevant to that code as a baseline (charter rule 15). Reproduce and probe where it affects nothing real; anything that writes to, sends from or loads a shared or production system needs the user's yes first. If you can't reproduce it, gather evidence (inputs, logs, versions, environment), trace from that, and say what's missing; no fix until step 4 names a cause.
2. **Trace.** Follow the data and control flow backward from the symptom toward its origin. Read the code; don't assume it.
3. **Hypothesise and test.** Write down the candidate causes, most likely first. Test each with the cheapest observation that tells them apart: temporary instrumentation, a debugger, halving the input, bisecting through version history (in a temporary worktree, never by stashing the user's changes). Change one thing at a time.
4. **Name the cause** in one sentence that explains every symptom. If it doesn't explain all of them, you haven't found it, or there is more than one bug: name each cause and fix each in its own diff, starting the next only once the user has committed the one before or asked you to; if they say to go on without committing, say once that the fixes will share one diff. Keep asking why until you reach the fault, not the place it surfaced. If only the cause was asked for, or nothing is broken and the report asks for different behaviour, stop here: report the cause and offer the change.
5. **Fix at the origin.** If the origin is out of reach (a dependency, another system) or its fix needs a diff of its own or staging across diffs (a breaking change to persisted data or outside consumers, per plumb-build step 6), stop and offer the origin fix and a workaround labelled as one, with their sizes. Never ship a suppression as the "safe" fix: a catch that ignores, a guard over a deeper fault, a retry around a bug, a sleep around a race.
6. **Lock it.** Re-run the reproduction and see the symptom gone (with none, put the original symptom under Unverified), then meet the bug-fix floor (charter rule 17) and run the project's checks again.
7. **Clean up**, also when you stopped at step 4 or 5. Remove every piece of temporary instrumentation and every scratch file you created, including your reproduction unless it became the regression test, and end any bisect, checkout or stash, and remove any worktree you made, so the branch is as you found it apart from the fix. If that changed any file after the fix was proven, re-run the regression test and the project's checks and report that run.
8. **Report**, once your diff passes plumb-build's self-review checklist (if that changed anything, re-run step 6's proof and checks); for a non-trivial fix, offer an independent review by the plumb-reviewer agent, as plumb-build does. Under Noticed, list other places where the same fault pattern appears; don't fix them unasked. If the fault already wrote bad data or sent wrong output, say what it damaged under Risks and offer the repair.

For a failing test, decide whether the test or the code is wrong as plumb-test's "When a test fails" describes; for a flaky test or any intermittent bug, force the nondeterminism to reproduce it and to prove the fix, as it describes. Every other step still applies.

## Production incidents

When users are being harmed, first propose the specific mitigation (roll back, turn off the feature, shed load) and take it only on the user's explicit yes for that action; then find the cause. Afterwards, offer a short blameless review: timeline, cause, why it wasn't caught, and at most three actions, each one a suggestion.
