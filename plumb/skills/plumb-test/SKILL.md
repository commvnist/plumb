---
name: plumb-test
description: The standard for when a test should exist, what makes a good one, and how to do test-driven development without bloating the suite. Use for "write tests", "add tests", "TDD", "red green refactor", "is this a good test", "should I test this", fixing a failing or flaky test, or any time code needs proof.
---

# Plumb: test

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

A test suite is code that holds the rest of the code still. Every test costs runtime, reading time and change friction forever, so each one must pay for itself by catching breaks people would otherwise ship.

## When a test should exist

Write one only when all three hold:
1. Someone relies on the behaviour: a user, a caller, another system.
2. You can name the break: a plausible edit by a future maintainer, or a real input, that would get this behaviour wrong. If you can't say it in one line, the test isn't worth its cost.
3. No existing test, type check or compiler check would already catch that break.

If catching that break needs heavy setup, many fakes or a slow resource, test it at the level where it is cheap and real; if no such level exists, write no test unless the floor (charter rule 17) requires one, and say so in the report.

A general request to "add tests" asks for the tests that meet this bar, not for coverage. Write those, and list in one line what you deliberately left untested and why, so the user can override. A test the user names specifically gets written; if it fails the bar, say so once.

Highest value: regressions of real bugs, business rules and calculations, parsing and validation of untrusted input, state transitions, concurrency and repeat-delivery contracts, security boundaries, public interfaces others build on.

No test of its own: wiring and configuration, plain data, pass-through and delegation, trivial accessors, constants, what the type system already proves, the behaviour of the language or a library, private helpers whose breaks tests of public behaviour already catch.

## What a good test is

- **Behavioural.** It goes through the surface a real caller uses and asserts on outcomes the caller can observe. It checks an interaction only when the interaction is the contract, such as "a message is sent".
- **Sensitive.** It fails when the behaviour breaks. Prove it: watch it fail before the fix exists, or briefly break the code and see it go red.
- **Resilient.** It passes under any change that preserves the behaviour: renames, restructuring, reordering of internals. It asserts only what the behaviour promises; comparing whole objects or exact order locks in what callers don't rely on.
- **Focused.** It has one reason to fail, and its name states the behaviour ("rejects an expired coupon"), not the function it calls.
- **Readable alone.** Setup, action and assertion are visible in the test, and the data that decides the outcome is inline and minimal; build the rest with the project's own fixtures.
- **Deterministic and fast.** It controls time, randomness, ordering and concurrency, and depends on no service it can't run locally.
- **Honest about boundaries.** Fake only what the code doesn't own: clocks, third-party and remote services. Use real collaborators inside the boundary.
- **Pitched at the right level.** Test at the lowest level that exercises the real behaviour with real collaborators. When the risk is in the wiring, one integration test beats five unit tests full of fakes.

Cases that differ only by data share one table-driven test, with one row per distinct break. Coverage shows what nothing tests; it never shows what is tested well. Never chase a coverage number.

## Reject on sight

Assertions on source text, file layout, log wording or private internals. Expected values computed the way the code computes them. Fakes of the unit under test. Snapshots nobody reads. Tests of the language or a library. Tests that lock in incidental repository state, such as counts or lists of registered items. Tests with no assertion, or that catch an error in order to pass. Sleep-based waiting. Near-duplicates.

## Test-driven loop

Use it when the user asks for it, or when the behaviour is well specified up front.

1. **List** the behaviours the test floor requires (charter rule 17), briefly. Pick the simplest one that teaches something.
2. **Red.** Write one test and run it. Confirm it fails for the reason you expect, not because of a typo, a missing import or a setup error.
3. **Green.** Write the simplest honest code that passes. Never special-case the test's inputs.
4. **Refactor.** With everything green, simplify the code and the tests you just wrote without changing behaviour. Run again.
5. **Repeat** until the list is done. Then delete the tests from this loop that later ones have made redundant.

The delivered diff holds tests that meet this standard, not a record of every step.

## When a test fails

- Decide whether the test or the code is wrong from the requirement, not from which is easier to change. When a new test exposes an existing bug, never assert the wrong output. If the task's behaviour depends on it, stop and propose fixing it first, in its own diff with plumb-debug; otherwise report it and offer the fix as a suggestion, with that test landing alongside it as its regression test.
- Never weaken an assertion, widen a tolerance, skip or delete a test to go green, except as charter rule 12 allows.
- A flaky test is a real bug. When fixing it is the task, or your change made it flaky, find the nondeterminism (time, ordering, shared state, concurrency, outside dependence), force it so the test fails every time, then remove the nondeterminism and see the test pass under that same forcing; a streak of passes is not proof. Otherwise name it under Noticed. Never add retries or sleeps to hide it.

For pruning or finding gaps across a whole suite, use plumb-audit in tests mode.
