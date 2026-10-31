---
name: plumb-build
description: Implements a feature or change as the smallest complete, reviewable diff, proves it works, self-reviews it against common agent failure modes, then offers a ranked menu of improvements. Use for "implement", "add", "build", "change", "make it do", or any request to write or modify code that isn't mainly a bug hunt, refactor or test task.
---

# Plumb: build

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

## Steps

1. **Size it.** If it won't fit one reviewable diff, or expensive-to-reverse decisions are open, go to plumb-plan first. If it continues earlier work, check recent pull requests, or commit bodies, touching this code for a Plan section; if it is a step of a plan, confirm the event the step waits for has happened (asking if you can't see it); if the plan is from an earlier session, also build from the latest Plan section rather than the request alone and read the decision records it names.
2. **Define done.** Name the observable check that proves the task works: a command, a test, a visible result. If you can't name one, either the task isn't clear yet (ask, per the charter) or it can't be checked here (name the closest check and put the gap under Unverified).
3. **Read before writing.** Read the code you'll change, its tests, and one nearby example of the same kind of thing. Find everything that calls it, and read each caller whose view the change could alter (what it passes, gets back, sees raised or relies on happening); a caller that sees nothing different can't break. Copy that example's conventions. In a large or unfamiliar codebase, send the plumb-scout agent and work from its map, reading each piece before you change or call it (charter rule 14); a map from earlier in this session still serves for code only this session's own diffs have changed since.
4. **Baseline.** Run the project's checks relevant to that code (charter rule 15). Note what already fails; it isn't yours.
5. **Climb the ladder** (charter rule 5) and stop at the first rung that works.
6. **Make the change.** Edit in place. Keep every contract others rely on unless changing it is the task; if it is, update every dependent in the same diff. A change charter rule 3 says to stage goes to plumb-plan. So does a change the code must first be restructured to take; the restructure is its own diff, landed first.
7. **Prove it.** Run the done-check: seen failing without the change (before it, or with it briefly reverted) and passing with it. Add tests to the floor (charter rule 17), plus any the user asked for, by plumb-test's bar. A throwaway check, such as a quick script or interactive session, is fine for proof and is not kept, within charter rule 2.
8. **Run the project's checks again.** Fix what you broke, deciding a test your change broke as plumb-test's "When a test fails" does. Leave failures that predate you alone and name them; one in a test of code you changed leaves that behaviour under Unverified.
9. **Review your own diff as its reviewer.** Read every hunk against the charter's self-review checklist. Delete every line the task doesn't need. If the review changed anything, re-prove only what that edit could have made untrue: run the done-check and those of step 8's checks it could affect, once, and review the hunks it changed.
10. **Report** with the charter's template and the suggestions from its principal pass. For a non-trivial change, offer an independent review by the plumb-reviewer agent, or the charter's Agents route when agents are off.

## Applying accepted suggestions

Apply them in the order chosen, dependencies first, each at its smallest: in this change's diff if it completes code this change adds, since it serves the same purpose (left for a new commit, never an amend, if that work is already committed), otherwise as its own diff, paced as charter rule 4 says. Take each one through steps 1–9 (plumb-refactor for a behaviour-preserving one) and give its own report in the charter's template. Show the remaining menu only if it changed or items are still open; don't invent new items to refill it.
