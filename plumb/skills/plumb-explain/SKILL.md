---
name: plumb-explain
description: Walks the operator through code, a diff or a decision: what it does, traced through one real case, and why. Changes nothing. Use for "explain this", "walk me through", "how does this work", "why did you do it this way".
---

# Plumb: explain

An explanation changes nothing.

## Steps

1. **Take scope and depth from the question.**
2. **Read before explaining,** history and your own earlier reports included: a reason none of them records is unknown or your inference, never fact.
3. **Trace one real case** by file:line, running it where you can, then where the path differs; say what you ran and read.
4. **Give the reasons:** choice, alternative, cost.
5. **Say where the code could misbehave.**
6. **Hand them one check they can run,** and what it should show, having run it where you can.
