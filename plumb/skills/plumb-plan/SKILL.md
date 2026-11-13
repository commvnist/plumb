---
name: plumb-plan
description: Turns a feature request, spec or larger change into a short plan of small, independently mergeable diffs before any code is written. Use for "plan this", "design", "how should we build", "break this down", new features, cross-cutting changes, or any task too big for one reviewable diff.
---

# Plumb: plan

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

A plan makes every later diff small and lets the operator overturn decisions before code exists. It is a proposal in the reply and changes no code.

## Steps

1. **State the goal as outcomes,** and what is out of scope.
2. **Map the ground:** the code that will change, its dependents, what already exists.
3. **Find the thinnest end-to-end slice.** The first step works from input to output for one narrow case; whatever it needs (scaffolding, schema, auth) lands in its diff, never as a setup step before it. *A step that only prepares runs nothing, so it exposes no wrong assumption.*
4. **Decide only what is expensive to reverse:** for each, the options, the choice, its reason and what it gives up, and a decision record.
5. **Sequence the diffs,** each correct and mergeable on its own. Stage a change charter rule 3 names: add the new form, migrate, remove the old.
6. **Name the unknowns.**
7. **Principal pass:** suggestions, per the charter.

## Output

```
Goal:       <outcomes>   Out of scope: <…>
Decisions:  <decision — options — choice — reason — what it gives up — record>, one per line
Steps:
1. <diff title> — <what it delivers> — ~<n> lines
Questions:  <at most three, each with a recommended answer and its reason>
Suggestions: <ask which to include>
```

## Rules

No time estimates; size in changed lines. Wait for a go-ahead before building.
