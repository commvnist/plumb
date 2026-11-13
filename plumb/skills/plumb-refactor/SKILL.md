---
name: plumb-refactor
description: Restructures code without changing behaviour, in small verified steps. Use for "refactor", "clean up", "simplify", "extract", "rename", "remove dead code", "reduce duplication".
---

# Plumb: refactor

A refactor changes structure, never behaviour.

## Steps

1. **Name the goal.**
2. **Know why it's there:** check its history and users.
3. **Pin the behaviour:** see the tests that cover it go red with the code briefly broken.
4. **Plan the moves.**
5. **Move in small steps,** checks green after each.
6. **Report** with `Behaviour: unchanged — <checks> pass before and after`.

## Rules

Refactor only what was pointed at. A test that reached into internals you moved is re-pointed at the same behaviour through the public surface, not deleted.
