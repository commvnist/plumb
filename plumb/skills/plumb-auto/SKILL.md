---
name: plumb-auto
description: Carries a task to a finished, verified result without stopping for the operator, and leaves a record they can check every choice against. Use when the operator says to go on without them or won't be there to answer: "do it all", "work autonomously", "don't stop to ask", "one-shot this", "take it from here", "I'll be away". Load it with the skill for the work itself.
---

# Plumb: auto

Asking for this is the go-ahead for the whole task and the instruction to commit each diff, by plumb-ship, on a new local branch: charter rule 4's stops become one final report. Nothing is pushed or deployed unasked; every other rule holds.

## Steps

1. **Read until nothing surprises you:** the code, tests, callers, versions in use; the plumb-scout agent in a large or unfamiliar codebase.
2. **Pin done:** before writing any code, write checks tied to the request's words and see each fail (for behaviour the request keeps, fail with it briefly broken). A check written first can't be bent to fit the code.
3. **Plan the diffs** as plumb-plan does.
4. **Decide instead of asking:** take the reading the code and request best support, and record it. Stop only for what can't be undone or needs a yes even when asked (a breaking change to persisted data or a contract, charter rule 3; a new dependency, rule 5), after finishing what doesn't depend on it.
5. **Build each diff** by the matching plumb skill, loaded, and running the checks after every step.
6. **Get an independent review:** send the change, committed or not, to the plumb-reviewer agent as its description says, since an author can't see past their own assumptions; asking for this skill is the ask for that agent. Fix or dispute each Blocking finding, then send the change back; stop when no Blocking finding stands unfixed and undisputed, and put the disputes under Reviewed. With `plumb agents: off`, which this ask doesn't override, re-read the request, then the diff, as a stranger's.
7. **Try to break it:** name the likeliest way it is wrong (a misread request, an untried input, an unrun caller) and check it.

## Output

The charter's report, with every commit under Done and every diff's choices under Decided, plus after Decided:

- **Assumed:** <each reading taken without asking, and what changes if it is wrong>
- **Reviewed:** <verdict, reviewer model, what was fixed or disputed>
