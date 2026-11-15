---
name: plumb-auto
description: Carries a task to a finished, verified result without stopping for the operator, and leaves a record they can check every choice against. Use for "do it all", "work autonomously", "don't stop to ask", "one-shot this", "I'll be away", "end to end".
---

# Plumb: auto

Asking for this is the go-ahead for the whole task: charter rule 4's stops become one final report, and each diff is its own commit on a new local branch. Nothing is pushed or deployed unasked; every other rule holds.

## Steps

1. **Pin done first:** checks that can fail, each tied to the request's words, seen failing before any code. A check written first can't be bent to fit the code.
2. **Read until nothing surprises you:** the code, tests, callers, versions in use; plumb-scout in a large codebase.
3. **Plan the diffs** as plumb-plan does, one purpose each and the riskiest unknown first, so a wrong assumption shows before work rests on it.
4. **Decide instead of asking:** take the reading the code and request best support, and record it. Stop only for what can't be undone or needs a yes even when asked (a breaking change to persisted data or a contract, charter rule 3; a new dependency, rule 5), after finishing what doesn't depend on it.
5. **Build each diff** by the matching plumb skill, seeing each new check fail before the code that passes it, and running the checks after every step.
6. **Get an independent review:** send the whole change, committed or not, to the plumb-reviewer agent, since an author can't see past their own assumptions. Asking for this skill is the ask for that agent. Fix or dispute each Blocking finding, and send it back until it finds none. With `plumb agents: off`, re-read the request, then the diff, as a stranger's.
7. **Try to break it:** name the likeliest way it is wrong (a misread request, an untried input, an unrun caller) and check it.

## Output

The charter's report, with every commit under Done and every diff's choices under Decided, plus:

```
Assumed:  <each reading taken without asking, and what changes if it is wrong>
Reviewed: <verdict, reviewer model, what was fixed or disputed>
```
