---
name: plumb-refactor
description: Restructures code without changing behaviour, in small verified steps each kept green, with the goal of fewer concepts and less code. Use for "refactor", "clean up", "simplify", "restructure", "extract", "rename", "remove dead code", "reduce duplication" and paying down technical debt.
---

# Plumb: refactor

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

A refactor changes structure and never behaviour. If behaviour must change too, that is a separate diff, before or after.

## Steps

1. **Name the goal** in terms a reader feels: fewer concepts, less indirection, less code, a clearer name, one way of doing a thing instead of two. A refactor that adds layers needs a strong, stated reason.
2. **Know why it's there** before removing or reshaping anything. Check its history and all of its users, including indirect ones: dynamic lookup, configuration, serialised data, outside consumers.
3. **Pin the behaviour.** Find the tests that cover the code you'll move. If there aren't enough, write characterisation checks that record what the code does now, quirks included, and run them as throwaway proof across the steps. Don't commit them: a refactor's test floor is zero (charter rule 17). Offer any that meet the plumb-test standard as a suggestion.
4. **Plan the moves.** List, in the reply, the sequence of named, mechanical steps: rename, extract, inline, move, merge duplicates, delete dead code, replace a conditional with data. Prefer tool-driven renames and moves over hand edits.
5. **Move in small steps.** Run the checks after each step. Each diff holds one kind of move, so the reviewer can confirm it's mechanical.
6. **Report** with an added line, `Behaviour: unchanged — <checks> pass before and after`. Keep Risks for what checks can't see, such as indirect users, persisted names and performance.

## Rules

- If the moves need more than one diff, propose the sequence and wait for a go-ahead before the first, as plumb-plan does.
- Refactor only what the user pointed at. Opportunistic refactors elsewhere are suggestions.
- Interfaces with consumers outside the repository are never broken in one step: add the new one, migrate the users, remove the old one, each as its own diff.
- If behaviour changed by accident (a check differs, an output changed), revert that step; don't adjust the test to match. A test that fails only because it reached into internals you moved: if the behaviour behind it meets plumb-test's three conditions, re-point it at that behaviour through the public surface, see it go red once, and name it in the report; otherwise delete it in a diff of its own.
- Stop when the goal is met. Don't polish further.
