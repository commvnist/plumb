---
name: plumb-test
description: The standard for when a test should exist and what makes a good one. Use for "write tests", "add tests", "TDD", "is this a good test", "should I test this".
---

# Plumb: test

## When a test should exist

When someone relies on the behaviour, you can name a plausible break, and nothing else would catch it. "Add tests" asks for those, not coverage: say in one line what you left untested and why.

## What a good test is

It asserts outcomes through the surface a caller uses and has been seen to fail on its break. Expected values come from what the behaviour should be (a spec, a doc), never from the code's output; where code and stated behaviour disagree, say so. Cases that differ only by data share one table.

## Reject on sight

Assertions on internals; expected values computed as the code computes them; tests of the language or of trivial accessors; near-duplicates.

## Keep, merge, rewrite or delete

Merge near-duplicates; rewrite a test that guards the right behaviour badly; delete one that guards no behaviour anyone relies on; keep the rest.
