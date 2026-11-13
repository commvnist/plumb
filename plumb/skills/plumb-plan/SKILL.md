---
name: plumb-plan
description: Turns a feature request, spec or larger change into a short plan of small, independently mergeable diffs before any code is written. Use for "plan this", "design", "how should we build", "break this down", new features, cross-cutting changes, or any task too big for one reviewable diff.
---

# Plumb: plan

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

A plan exists to make every later diff small and obvious, and to let the operator see and overturn every decision before code exists. It is a proposal in the reply, not a document, and only as long as the decisions in it; its expensive decisions are kept as decision records (charter, Decisions).

## Steps

1. **State the goal as outcomes.** One to three lines on what a user or caller can do afterwards that they can't now. Add a line on what is explicitly out of scope.
2. **Map the ground.** Read the entry points, the code that will change, its dependents, its tests, and one existing example of the same kind of thing to copy. In a large codebase, send the plumb-scout agent and work from its map. List what already exists that does part of the job, and read the decision records that cover this area; a plan that goes against one says so and supersedes it.
3. **Find the thinnest end-to-end slice.** The first step should work from input to output, however narrow, rather than building one layer at a time, and should run the path the request exists for, through its least certain part (an outside system, a new kind of storage); later steps widen it. Nothing comes before it but a behaviour-preserving step that existing code needs (step 5). Whatever the slice needs in order to run (scaffolding, schema, configuration, a part of another feature) lands in its diff rather than in a step of its own, in the narrowest form that is still the real one, which later steps widen and never replace. Narrow the slice if the diff grows too large. *A slice that runs exposes wrong assumptions while they're still cheap; a step that only prepares for it runs nothing, so it exposes none, and a stand-in that a later step replaces was never the thing tested.*
4. **Decide only what is expensive to reverse,** judged as the charter's Decisions judges it. For each: the options worth considering (at most three), the choice, and in one line the reason, what the choice gives up to the strongest alternative and what would make that alternative win, since an operator can only weigh a choice differently if they can see its cost. A choice the request itself made is listed too, with the user's reason or a question asking for it. Each becomes a decision record in the step that acts on it, never in a separate documents step; if the project keeps no records yet, ask the charter's question about starting them. Leave cheap decisions to the build, which reports them under Decided.
5. **Sequence the diffs.** Each step is one diff that is correct, mergeable and reviewable on its own, its floor tests included; never a separate tests step. Put risky unknowns first. When the code resists the change, make a behaviour-preserving step first, as a separate diff. Stage a change charter rule 3 names: add the new form, migrate, remove the old, each its own step and release, the removal only once the migration has shipped and consumers have moved. A step that would leave users a half-working feature keeps it unreachable until the step that completes it.
6. **Name the unknowns.** Settle what a read or a throwaway check can settle now; if one still blocks the plan, propose a bounded spike whose output is an answer, not code.
7. **Principal pass.** Read the plan as the charter's principal engineer and list what they'd insist on as suggestions, each saying which step it would join or add. Suggestions aren't in Steps until picked; what the project's written rules demand, and any defect in the plan itself, goes straight into Steps.

## Output

```
Goal:          <outcomes>
Out of scope:  <what this deliberately won't do>
Reuse:         <existing pieces this builds on>
Decisions:     <decision — options — choice — reason — record: <new, supersedes NNNN, the project's, or none>>, one per line
Steps:
1. <diff title> — <what it delivers> — ~<n> lines — after: <step, or the event it waits for>
Unknowns:      <risks, and the step or throwaway spike that retires each>
Questions:     <only those that change the plan, at most three, each with a recommended answer and its reason>
Suggestions:   <from the principal pass, by the charter's menu rules; ask which to include, with a recommendation>
Noticed:       <problems this plan didn't cause and doesn't fix, one line each — or omit>
```

## Rules

- No speculative steps: nothing for scale, extensibility or features nobody asked for. Put those under suggestions if they're real.
- No time estimates; size in changed lines.
- A one-step plan with no expensive decisions is just a build: say so, and build it unless the user asked only for a plan.
- A plan of more than one step lives where the team will see it next week, not only in this conversation: each step's pull request description (or commit body) carries the Steps (plumb-ship's Plan section), marking which are done and what the next one waits for.
- For more than one step, or any expensive decision, wait for a go-ahead before building, then build one step at a time with plumb-build (plumb-refactor for a behaviour-preserving step), paced as charter rule 4 says. When asking, offer both forms: step by step, or every step committed as it passes. Re-plan, and get a new go-ahead, when a step teaches you something that changes later steps.
