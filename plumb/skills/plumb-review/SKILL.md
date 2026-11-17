---
name: plumb-review
description: Reviews a diff, commit, branch or pull request and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check my work", "is this safe to merge". For a whole codebase, use plumb-audit.
---

# Plumb: review

Approve a change that leaves the codebase better and safe to ship; taste is not a finding. Change no code.

## Steps

1. **Learn the intent.**
2. **Read the whole diff, then what it touches.**
3. **Run the project's checks**; claims in the description are unverified until you do.
4. **Judge in this order:** correctness, safety, proof (charter rules 12 and 16), simplicity, scope.

## Findings

In the charter's shape; trace each scenario's input to where it enters.

## Output

- **Verdict:** approve | approve with suggestions | request changes, with the reason
- **Blocking:** <findings, or none>
- **Suggestions:** <findings>
- **Verified:** <what you ran> → <result>
