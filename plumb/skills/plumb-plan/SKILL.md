---
name: plumb-plan
description: Turns a feature request, spec or larger change into a short plan of small, independently mergeable diffs before any code is written. Use for "plan this", "design", "how should we build", "break this down", new features, cross-cutting changes, or any task too big for one reviewable diff.
---

# Plumb: plan

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

A plan exists to make every later diff small and obvious. It is a proposal in the reply, not a document, and it is only as long as the decisions in it.

## Steps

1. **State the goal as outcomes.** One to three lines on what a user or caller can do afterwards that they can't now. Add a line on what is explicitly out of scope.
2. **Map the ground.** Read the entry points, the code that will change, its dependents, its tests, and one existing example of the same kind of thing to copy. In a large codebase, send the plumb-scout agent and work from its map. List what already exists that does part of the job.
3. **Find the thinnest end-to-end slice.** The first step that changes behaviour should work from input to output, however narrow, rather than building one layer at a time. *A slice that runs exposes wrong assumptions while they're still cheap.*
4. **Decide only what is expensive to reverse:** data shape, persisted formats, public interfaces, new dependencies, anything other teams will build on. For each: the options worth considering (at most three), the choice, and the reason in one line. Leave cheap decisions to the build.
5. **Sequence the diffs.** Each step is one diff that is correct, mergeable and reviewable on its own, its floor tests included; never a separate tests step. Put risky unknowns first. When the code resists the change, make a behaviour-preserving step first ("make the change easy, then make the easy change") and keep it a separate diff. Stage a change to persisted data or to consumers outside the repository as plumb-build does: add the new form, migrate, remove the old, each its own step, the removal only once the migration has shipped and consumers have moved. A step that would leave users a half-working feature keeps it unreachable until the step that completes it.
6. **Name the unknowns.** Settle what a read or a throwaway check can settle now; if one still blocks the plan, propose a bounded spike whose output is an answer, not code. Spike code is thrown away.
7. **Principal pass.** Read the plan as the charter's principal engineer and list what they'd insist on as suggestions, each saying which step it would join (only if it completes code that step adds) or add as its own step. Suggestions aren't in Steps until picked; what project rules demand, and any defect in the plan itself (something it would get wrong or make unsafe), goes straight into Steps.

## Output

```
Goal:          <outcomes>
Out of scope:  <what this deliberately won't do>
Reuse:         <existing pieces this builds on>
Decisions:     <decision — options — choice — reason>, one per line
Steps:
1. <diff title> — <what it delivers or proves> — ~<n> lines — after: <step, or the event it waits for>
Unknowns:      <risks, and the step or throwaway spike that retires each>
Questions:     <only those that change the plan, at most three, each with a recommended answer>
Suggestions:   <from the principal pass, by the charter's menu rules; ask which to include, with a recommendation>
Noticed:       <problems this plan didn't cause and doesn't fix, one line each — or omit>
```

## Rules

- No speculative steps: nothing for scale, extensibility or features nobody asked for. Put those under suggestions if they're real.
- No time estimates; size in changed lines.
- A one-step plan with no expensive decisions is just a build: say so, and proceed with plumb-build unless the user asked only for a plan.
- For more than one step, or any expensive decision, wait for a go-ahead before building, then build one step at a time with plumb-build (plumb-refactor for a behaviour-preserving step), stopping after each step's report until the user commits it or asks you to; if the user says to go on without committing, say once that the steps will share one diff. Re-plan, and get a new go-ahead, when a step teaches you something that changes later steps; don't push on with a plan you know is wrong.
