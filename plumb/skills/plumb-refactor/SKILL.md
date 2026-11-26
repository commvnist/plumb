---
name: plumb-refactor
description: Restructures code without changing behaviour, in small verified steps. Use for "refactor", "clean up", "simplify", "extract", "rename", "remove dead code", "reduce duplication". A change to stored data or an outside contract is plumb-plan's.
---

# Plumb: refactor

A refactor changes structure, never behaviour, and only what was pointed at.

## Steps

1. **Name the goal,** and check the code's history and users.
2. **Pin the behaviour:** see the tests that cover it go red with the code briefly broken; where none do, first add tests expecting what it does now, bugs included (here today's behaviour is the spec).
3. **Move in small steps,** checks green after each.
4. **Report,** Verified showing the same checks pass before and after.

A test that reached into internals you moved is re-pointed at the same behaviour through the public surface, not deleted.
