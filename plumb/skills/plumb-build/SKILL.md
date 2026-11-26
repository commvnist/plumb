---
name: plumb-build
description: Implements a feature or change as the smallest complete, reviewable diff and proves it works. Use for "implement", "add", "build", "change", or any request to write or modify code that isn't mainly a bug hunt, refactor or test task.
---

# Plumb: build

## Steps

1. **Size it.** Too big for one diff: load plumb-plan first.
2. **Define done:** name the check that proves it.
3. **Read before writing:** the code, its tests, its callers, a nearby example; in a large or unfamiliar codebase, send the plumb-scout agent.
4. **Climb the ladder** (charter rule 5) and make the change; where the code resists it, first offer the refactor that makes it easy, as its own diff.
5. **Prove it:** the check passes with the change and fails as charter rule 16 says.
6. **Review your own diff as its reviewer,** reading the diff itself, never your memory of it, then report.
