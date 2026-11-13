---
name: plumb-explain
description: Walks the operator through code, a diff or a decision until they could defend it in review, covering what it does, traced through one real case, why it is built this way, and where it could be wrong. Changes nothing. Use for "explain this", "walk me through", "how does this work", "why did you do it this way", "what does this diff do", "I don't follow".
---

# Plumb: explain

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

An explanation lets the operator vouch for the code and overturn what is wrong in it. It changes nothing.

## Steps

1. **Take the scope and depth from the question.**
2. **Read it before explaining it.** A reason you can't find is given as unknown or as your inference, never as fact.
3. **Lead with the point:** what it does, and the one idea that makes it work.
4. **Trace one real case** through the code by file:line, then where the path differs; say what you ran and what you read.
5. **Give the reasons:** the choice, the alternative, what the alternative would cost.
6. **Say where it could be wrong.**
7. **Hand them something to try:** one check they can run themselves.

## Output

```
In short:     <what it does and the idea that makes it work>
Walkthrough:  <one case traced by file:line, then where the path differs>
Why this way: <choice — alternative — cost>
Not sure:     <assumptions, inference — or "nothing">
Try it:       <one check they can run>
```
