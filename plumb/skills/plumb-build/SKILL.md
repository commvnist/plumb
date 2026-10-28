---
name: plumb-build
description: Implements a feature or change as the smallest complete, reviewable diff, proves it works, self-reviews it against common agent failure modes, then offers a ranked menu of improvements. Use for "implement", "add", "build", "change", "make it do", or any request to write or modify code that isn't mainly a bug hunt, refactor or test task.
---

# Plumb: build

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

## Steps

1. **Size it.** If it won't fit one reviewable diff, or expensive-to-reverse decisions are open, go to plumb-plan first.
2. **Define done.** Name the observable check that proves the task works: a command, a test, a visible result. If you can't name one, either the task isn't clear yet (ask, per the charter) or it can't be checked here (name the closest check and put the gap under Unverified).
3. **Read before writing.** Read the code you'll change, everything that calls it, its tests, and one nearby example of the same kind of thing. Copy that example's conventions. In a large or unfamiliar codebase, send the plumb-scout agent and work from its map.
4. **Baseline.** Run the project's checks relevant to that code (charter rule 15). Note what already fails; it isn't yours.
5. **Climb the ladder** (charter rule 5) and stop at the first rung that works.
6. **Make the change.** Edit in place. Keep every contract others rely on unless changing it is the task; if it is, update every dependent in the same diff. A change to persisted data or to consumers outside the repository has to be staged across diffs: go to plumb-plan.
7. **Prove it.** Run the done-check: it fails or is absent before, and passes after. Add tests only to the floor (charter rule 17). A throwaway check, such as a quick script or interactive session, is fine for proof and is not kept.
8. **Run the project's checks again.** Fix what you broke. Leave failures that predate you alone and name them.
9. **Review your own diff as its reviewer.** Read every hunk against the checklist below. Delete every line the task doesn't need. If the review changed anything, repeat steps 7–8.
10. **Report** with the charter's template and the suggestions from its principal pass. For a non-trivial change, offer an independent review by the plumb-reviewer agent.

## Self-review checklist

Each item is a known failure of generated code. Any "yes" gets fixed before the report.

- A line, file or branch the task doesn't require?
- A new helper that duplicates something the project has?
- An abstraction, parameter or option with only one use?
- A catch that swallows, broadens or hides an error? A made-up fallback value?
- A check for a state that can't occur?
- A comment that says what the code does?
- Untouched code renamed, reformatted, reordered or "tidied"?
- A rewrite where an edit would do? A new file where an existing one fits?
- A new dependency without a yes?
- A call to something you haven't confirmed exists?
- A test beyond the floor, or one that would still pass with the bug present?
- Leftover debug output, scratch files or commented-out code?
- Anything sensitive logged, exposed or trusted without validation at the boundary?

## Applying accepted suggestions

Apply them in the order chosen, dependencies first, each at its smallest: in this change's diff if it completes code this change adds, otherwise as its own diff, started only once the work before it is committed; if the user says to go on without committing, say once that they will share one diff. Take each one through steps 7–9 and give its own report in the charter's template. Show the remaining menu only if it changed or items are still open; don't invent new items to refill it.
