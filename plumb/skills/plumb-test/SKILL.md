---
name: plumb-test
description: The standard for when a test should exist and what makes a good one. Use for "write tests", "add tests", "TDD", "is this a good test", "should I test this".
---

# Plumb: test

A test should exist when someone relies on the behaviour, you can name a plausible break, and nothing else would catch it. "Add tests" asks for those, not coverage: say in one line what you left untested and why.

A good test asserts outcomes through the surface a caller uses, has been seen to fail on its break, and is named for the behaviour and condition, so a failure reads as a sentence. Expected values come from what the behaviour should be (a spec, a doc), never from the code's output; where code and stated behaviour disagree, say so. Cases that differ only by data share one table.

Reject on sight: assertions on internals; expected values computed as the code computes them; tests of the language or trivial accessors; near-duplicates.

## Keep, merge, rewrite or delete

Merge near-duplicates; rewrite a test that guards the right behaviour badly; delete one that guards no behaviour anyone relies on; keep the rest.
