---
name: plumb-plan
description: Turns a feature request or larger change into a short plan of small, independently mergeable diffs before any code is written. Use for "plan this", "design", "how should we build", "break this down", or work too big for one diff.
---

# Plumb: plan

A plan is a proposal in the reply. It changes no code and waits for a go-ahead.

## Steps

1. **State the goal as outcomes,** and map the ground.
2. **Find the thinnest end-to-end slice:** the first step works from input to output for one narrow case, and what it needs (scaffolding, schema, auth) lands in its diff, never as a setup step before it.
3. **Decide only what is expensive to reverse,** each with a decision record landing in the diff that makes the choice.
4. **Sequence the diffs,** each mergeable on its own. Stage a change charter rule 3 names: add the new form, migrate, remove the old.
5. **Name the unknowns.**

## Output

- **Goal:** <the outcomes>
- **Steps:** one numbered line per diff: <commit subject> — <what it delivers> — ~<n> lines
- **Decisions:** one line each: <decision>: <choice>, because <reason>; gives up <what the alternative offered>; record: <its decision record>
- **Waiting on:** <the go-ahead, and any questions>

No time estimates.
