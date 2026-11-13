---
name: plumb-review
description: Reviews a diff, commit or pull request for correctness, safety, test quality, unnecessary code and scope, and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check before merge", "is this over-engineered", "what's wrong with this change".
---

# Plumb: review

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

Does this change leave the codebase better and safe to ship? Approve when it does; taste is not a finding. Change no code. To review work you wrote, use the plumb-reviewer agent, which hasn't seen your reasoning.

## Steps

1. **Learn the intent** from the description or the diff.
2. **Read the whole diff, then what it touches:** callers, tests, data.
3. **Run the checks**, and treat claims in the description as unverified until you have.
4. **Judge in this order:** correctness, safety, proof (was a test weakened or deleted to go green), simplicity, scope.

## Findings

**Blocking:** wrong behaviour, unsafe, a broken contract, faked success, a missing floor test. **Should:** a real improvement, at most five. Each finding gives the location, a concrete scenario the system can actually produce (trace its input back to where it enters; a state the code is never given is not a finding), and the smallest fix. A defect repeated in several places is one finding.

## Output

```
Verdict: approve | approve with suggestions | request changes — <one-line reason>
Blocking:
1. <file:line> — <what goes wrong> — fix: <smallest fix>
Should:
1. …
Verified: <what you ran → result, or "read only">
```
