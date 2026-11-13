---
name: plumb-build
description: Implements a feature or change as the smallest complete, reviewable diff, proves it works, self-reviews it against common agent failure modes, then offers a ranked menu of improvements. Use for "implement", "add", "build", "change", "make it do", or any request to write or modify code that isn't mainly a bug hunt, refactor or test task.
---

# Plumb: build

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

## Steps

1. **Size it.** If it won't fit one reviewable diff, go to plumb-plan first.
2. **Define done.** Name the observable check that proves the task works.
3. **Read before writing.** Read the code you'll change, its tests, its callers, and one nearby example to copy. In a large or unfamiliar codebase, send the plumb-scout agent and work from its map.
4. **Baseline.** Run the project's checks relevant to that code.
5. **Climb the ladder** (charter rule 5).
6. **Make the change.** Edit in place, keeping every contract others rely on.
7. **Prove it.** See the done-check fail without the change and pass with it; add tests to the floor (charter rule 17).
8. **Run the project's checks again.**
9. **Review your own diff as its reviewer,** and delete every line the task doesn't need.
10. **Report** with the charter's template.

## Applying accepted suggestions

Apply each at its smallest, through steps 1–9, with its own report.
