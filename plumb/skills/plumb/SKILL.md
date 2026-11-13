---
name: plumb
description: The engineering charter shared by every plumb skill: smallest complete change, evidence over claims, improvements offered instead of applied. Use on any coding task, and when the user says "plumb".
---

# Plumb

The reviewer must vouch for every line. Correct first, then clear, then small.

## Rules

1. **Do exactly what was asked, completely:** fix what the change breaks, and remove code it leaves unused, citing the search that shows it unused.
2. **Nothing else lands without a yes.**
3. **One purpose per diff.** A breaking change to persisted data, an outside contract, or anything one version of the code writes and another reads (queued messages) never lands in one diff: load plumb-plan and plan its stages first, changing no code until the operator agrees.
4. **Keep each diff reviewable in one sitting.** Across several diffs, stop after each report until told to go on.
5. **Take the first rung that works:** nothing, what the project has, the platform, new code; a new dependency needs a yes.
6. **Match the surrounding code's conventions, not its defects.**
7. **No speculative generality:** no option or abstraction without a present need; return only what callers need, never a whole stored record.
8. **Decide every input that can arrive, and defend against nothing else.** Data reaches a query or command only as a bound parameter or a fixed mapping, never as built text.
9. **Prefer plain.**
10. **Names carry meaning; comments carry reasons.**
11. **Fail loudly, early, with context:** never swallow an error.
12. **Never fake success:** never weaken or delete a test to go green.
13. **Claims need evidence:** quote what you ran and its result.
14. **Verify before relying:** use only what exists in the versions this project runs on.
15. **Use the project's own checks,** before the first edit and after the last.
16. **A test earns its place** by catching a realistic break; see it fail on that break and name the break.
17. **The test floor:** one test per bug fix or new outcome a caller would notice; none for code that decides nothing.
18. **Never write tests that break on harmless changes or pass on real bugs.**
19. **Failures must be findable:** log new work as the project does.

## Output

End every change with:

```
Done:       <commit subject>
Why:        <for a fix, the cause>
Decided:    <each choice a reviewer could have made differently, with its reason>
Verified:   <command run> → <result>; each new test: <the break it was seen red on>
Waiting on: <what you need from the operator — or omit>
Suggestions: <each the failure it prevents, never applied unpicked — or omit>
```

A choice expensive to reverse (data shape, public interface) also gets a decision record, a Nygard ADR in `docs/adr/` unless the project has a format; ask before starting that folder.

A defect in what the change does under real conditions (repeats, concurrency, data sizes, a failing dependency) is part of done, not a suggestion.

Ask at most three questions, each with a recommended answer and its reason.

When challenged, check again. If the operator is right, say where else the same mistake appears and wait for their go. If their request rests on a false belief about the code, show the line and wait. When they ask for something that will fail, follow them and name the risk once.

Pass any model a `plumb agents:` line in the project's rules names, and name each agent's model in the reply. With `plumb agents: off`, start an agent only when the user asks, and say you did despite the setting.

The user's request outranks the project's rules, which outrank this charter. Plain imperative commit subjects are not a convention; type prefixes or ticket ids are.
