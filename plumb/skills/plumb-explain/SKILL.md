---
name: plumb-explain
description: Walks the operator through code, a diff or a decision: what it does, traced through one real case, and why. Changes nothing. Use for "explain this", "walk me through", "how does this work", "why did you do it this way".
---

# Plumb: explain

An explanation changes nothing.

## Steps

1. **Take the scope and depth from the question.**
2. **Read it before explaining it.** A reason you can't find is unknown or your inference, never fact.
3. **Lead with the point.**
4. **Trace one real case** by file:line, then where the path differs; say what you ran and what you read.
5. **Give the reasons:** choice, alternative, cost.
6. **Say where it could be wrong.**
7. **Hand them something to try:** one check they can run.
