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
2. It can break in a realistic way: logic, edge cases, integration, a past bug.
3. No existing test, type check or compiler check would already catch that break.

Highest value: regressions of real bugs, business rules and calculations, parsing and validation of untrusted input, state transitions, concurrency and repeat-delivery contracts, security boundaries, public interfaces others build on.

No test: wiring and configuration, plain data, pass-through and delegation, trivial accessors, constants, what the type system already proves, the behaviour of the language or a library, private helpers already exercised through public behaviour.

## What a good test is

- **Behavioural.** It goes through the surface a real caller uses and asserts on outcomes the caller can observe. It checks an interaction only when the interaction is the contract, such as "a message is sent".
- **Sensitive.** It fails when the behaviour breaks. Prove it: watch it fail before the fix exists, or briefly break the code and see it go red.
- **Resilient.** It passes under any change that preserves the behaviour: renames, restructuring, reordering of internals.
- **Focused.** It has one reason to fail, and its name states the behaviour ("rejects an expired coupon"), not the function it calls.
- **Readable alone.** Setup, action and assertion are visible in the test. Data is inline and minimal. A reader understands it without opening other files.
- **Deterministic and fast.** It controls time, randomness, ordering and concurrency, and touches no real network.
- **Honest about boundaries.** Fake only what the code doesn't own: networks, clocks, outside services. Use real collaborators inside the boundary.
- **Pitched at the right level.** Test at the lowest level that exercises the real behaviour with real collaborators. When the risk is in the wiring, one integration test beats five unit tests full of fakes.

Cases that differ only by data share one table-driven test. Coverage shows what nothing tests; it never shows what is tested well. Never chase a coverage number.

## Reject on sight

Assertions on source text, file layout, log wording or private internals. Expected values computed the way the code computes them. Fakes of the unit under test. Snapshots nobody reads. Tests of the language or a library. Tests that lock in incidental repository state, such as counts or lists of registered items. Tests with no assertion, or that catch an error in order to pass. Sleep-based waiting. Near-duplicates.

## Test-driven loop

Use it when the user asks for it, or when the behaviour is well specified up front.

1. **List** the behaviours the test floor requires (charter rule 17), briefly. Pick the simplest one that teaches something.
2. **Red.** Write one test and run it. Confirm it fails for the reason you expect, not because of a typo, a missing import or a setup error.
3. **Green.** Write the simplest honest code that passes. Never special-case the test's inputs.
4. **Refactor.** With everything green, simplify the code and the tests you just wrote without changing behaviour. Run again.
5. **Repeat** until the list is done. Then delete tests that later tests have made redundant.

The delivered diff holds tests that meet this standard, not a record of every step.

## When a test fails

- Decide whether the test or the code is wrong from the requirement, not from which is easier to change.
- Never weaken an assertion, widen a tolerance, skip or delete a test to go green (charter rule 12). Updating or removing a test whose behaviour the task deliberately changes is part of the change, not a weakening.
- A flaky test is a real bug. Find the nondeterminism (time, ordering, shared state, concurrency, outside dependence) and remove it. Never add retries or sleeps to hide it.

For pruning or finding gaps across a whole suite, use plumb-audit in tests mode.
