---
name: plumb-refactor
description: Restructures code without changing behaviour, in small verified steps each kept green, with the goal of fewer concepts and less code. Use for "refactor", "clean up", "simplify", "restructure", "extract", "rename", "remove dead code", "reduce duplication" and paying down technical debt.
---

# Plumb: refactor

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

A refactor changes structure and never behaviour. If behaviour must change too, that is a separate diff, before or after, and needs a yes unless the user asked for it.

## Steps

1. **Name the goal** in terms a reader feels: fewer concepts, less indirection, less code, a clearer name, one way of doing a thing instead of two. A refactor that adds layers needs a strong, stated reason.
2. **Know why it's there** before removing or reshaping anything. Check its history and all of its users, including indirect ones: dynamic lookup, configuration, serialised data, outside consumers.
3. **Pin the behaviour.** Find the tests that would fail if the code you'll move broke, run them as a baseline (charter rule 15; one already red pins nothing), and see them go red once with that code briefly broken. If there aren't enough, write characterisation checks that record what the code does now, quirks included, seen red the same way, and run them as throwaway proof across the steps. Keep them out of every diff, name them in each report so they aren't committed, and delete them before the last diff's report: a refactor's test floor is zero (charter rule 17). Offer any that meet the plumb-test standard as a suggestion; a quirk that looks like a bug goes under Noticed, not into a test. For dead code you delete, the proof is step 2's search for users, cited in the Behaviour line, and its own tests go with it (charter rule 12); code outside consumers can reach is never proven dead by a search, so removing it is an interface change, staged as the Rules say.
4. **Plan the moves.** List, in the reply, the sequence of named, mechanical steps: rename, extract, inline, move, merge duplicates, delete dead code, replace a conditional with data. Prefer tool-driven renames and moves over hand edits.
5. **Move in small steps.** Run the pinning checks from step 3, and any fast check that sees a broken reference (a compiler or type check), after each step, since they are what sees a move go wrong, and the project's full checks once each diff is complete. Each diff holds only moves a reviewer can confirm are mechanical; a tool-driven rename or move goes in its own (charter rule 4).
6. **Report** with an added line, `Behaviour: unchanged — <checks that would fail if the moved code broke> pass before and after`; whatever no such check pins goes under Unverified. Keep Risks for what checks can't see, such as indirect users, persisted names and performance. For a non-trivial refactor, offer an independent review by the plumb-reviewer agent, as plumb-build does.

## Rules

- If the moves need more than one diff, propose the sequence and wait for a go-ahead before the first; then pace them as charter rule 4 says.
- Refactor only what the user pointed at. Opportunistic refactors elsewhere are suggestions.
- A change charter rule 3 says to stage is never made in one step: stage it as plumb-plan step 5 does.
- If behaviour changed by accident (a check differs, an output changed), revert that step; don't adjust the test to match. A test that fails only because it reached into internals you moved is re-pointed if its behaviour meets plumb-test's three conditions (judged as its "When a test fails" judges a broken test), otherwise deleted, each as charter rule 12's list says, a deletion landing before that step; name it in the report.
- Stop when the goal is met. Don't polish further.
