---
name: plumb-test
description: The standard for when a test should exist, what makes a good one, and how to do test-driven development without bloating the suite. Use for "write tests", "add tests", "TDD", "red green refactor", "is this a good test", "should I test this", or any time code needs proof. Fixing a failing or flaky test is plumb-debug, which uses this standard.
---

# Plumb: test

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

Every test costs runtime, reading time and change friction forever, so each must pay for itself.

## When a test should exist

Only when all three hold: someone relies on the behaviour; you can name, in one line, a plausible break; no other test or check would already catch it. A request to "add tests" asks for the tests that meet this bar, not coverage: write those, and say in one line what you deliberately left untested and why.

## What a good test is

It goes through the surface a real caller uses and asserts on outcomes; it has been seen to fail on the break it exists to catch; it survives any change that preserves the behaviour; its name states the behaviour. Its expected values come from what the behaviour should be (a spec, a doc), never from running the code; where the code and its stated behaviour disagree, say so in the report. Cases that differ only by data share one table.

## Reject on sight

Assertions on internals or log wording; expected values computed the way the code computes them; tests of the language or a library; trivial accessors; near-duplicates.

## When a test fails

Decide whether the test or the code is wrong from the requirement. Never weaken or delete a test to go green.

## Keep, merge, rewrite or delete

Judging an existing test: **merge** near-duplicates; **rewrite** one that guards the right behaviour badly (brittle, blind, or computing its expected value as the code does); **delete** one that guards no behaviour anyone relies on; **keep** the rest.
