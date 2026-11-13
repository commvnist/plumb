---
name: plumb-refactor
description: Restructures code without changing behaviour, in small verified steps each kept green, with the goal of fewer concepts and less code. Use for "refactor", "clean up", "simplify", "restructure", "extract", "rename", "remove dead code", "reduce duplication" and paying down technical debt.
---

# Plumb: refactor

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

A refactor changes structure and never behaviour.

## Steps

1. **Name the goal:** fewer concepts, less indirection, less code.
2. **Know why it's there:** check its history and all of its users, indirect ones included.
3. **Pin the behaviour.** Find the tests that would fail if the code you'll move broke, and see them go red once with it briefly broken.
4. **Plan the moves** as named, mechanical steps.
5. **Move in small steps,** running the pinning checks after each.
6. **Report** with an added line, `Behaviour: unchanged — <checks> pass before and after`.

## Rules

- Refactor only what the user pointed at.
- If behaviour changed by accident, revert that step. A test that reached into internals you moved is re-pointed at the same behaviour through the public surface, not simply deleted.
