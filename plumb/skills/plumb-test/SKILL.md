---
name: plumb-test
description: The standard for when a test should exist and what makes a good one. Use for "write tests", "add tests", "TDD", "is this a good test", "should I test this".
---

# Plumb: test

A test should exist when someone relies on the behaviour, you can name a realistic break, and nothing else would catch it. "Add tests" asks for those, not coverage: say in one line what you left untested and why.

A good test asserts outcomes through the public surface, with real collaborators wherever they run fast and the same every time, and is named for the behaviour and condition, so a failure reads as a sentence. Expected values come from what the behaviour should be (a spec, a doc, a case worked by hand), never from the code's output or its logic restated; where code and stated behaviour disagree, say so. Each test shows the data its outcome depends on; cases that differ only by data share one table.

## Keep, merge, rewrite or delete

Merge near-duplicates; rewrite a test that guards the right behaviour badly; delete one that guards no behaviour anyone relies on; keep the rest.
