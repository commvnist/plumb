---
name: plumb-build
description: Implements a feature or change as the smallest complete, reviewable diff and proves it works. Use for "implement", "add", "build", "change", or any request to write or modify code that isn't mainly a bug hunt, refactor or test task.
---

# Plumb: build

## Steps

1. **Size it.** Too big for one diff: plumb-plan first.
2. **Define done.** Name the check that proves it.
3. **Read before writing:** the code, its tests, its callers, a nearby example. In a large codebase, send the plumb-scout agent.
4. **Baseline.** Run the project's checks.
5. **Climb the ladder** (charter rule 5).
6. **Make the change.**
7. **Prove it:** the check fails without the change and passes with it.
8. **Run the project's checks again.**
9. **Review your own diff as its reviewer.**
10. **Report** with the charter's template.
