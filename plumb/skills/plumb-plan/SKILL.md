---
name: plumb-plan
description: Turns a feature request or larger change into a short plan of small, independently mergeable diffs before any code is written. Use for "plan this", "design", "how should we build", "break this down", or work too big for one diff.
---

# Plumb: plan

A plan is a proposal in the reply. It changes no code and waits for a yes; a step that disproves what it assumed ends with the revised plan.

## Steps

1. **State the goal as outcomes,** and map the ground.
2. **Find the thinnest end-to-end slice:** the first step works from input to output for one narrow case, and what it needs (scaffolding, schema, auth) lands in its diff, never as a setup step before it.
3. **Decide only what is expensive to reverse,** each with a decision record landing in the diff that makes the choice.
4. **Sequence the diffs,** each mergeable on its own with main releasable (unfinished work unlinked, or behind a flag a later step removes), the riskiest unknown in the first slice. Stage a change charter rule 3 names: add the new form, migrate, stop using the old, then remove it once shown nothing reads it (outside readers warned by a deprecation first), each step correct while the one before it still runs on the same data.

## Output

- **Goal:** <the outcomes, and what would show each met>
- **Steps:** one numbered line per diff: <commit subject> — <what it delivers> — ~<n> lines — <its way back once shipped, or why it has none>
- **Decisions:** one line each: <decision>: <choice>, because <reason, the operator's where the request chose, or a question>; gives up <what the alternative offered>; record: <its decision record>
- **Unknowns:** <each no read settles now, and the step that settles it (a throwaway spike where the answer would change the plan)>
- **Waiting on:** <a yes, and any questions>

No time estimates.
