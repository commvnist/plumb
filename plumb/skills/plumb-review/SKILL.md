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
4. **Judge in this order:** correctness, safety, proof (was a test weakened or deleted), simplicity, scope.

## Findings

Each gives a location, a scenario the system can actually produce (trace its input to where it enters), and the smallest fix. A defect repeated in several places is one finding.

## Output

- **Verdict:** approve | approve with suggestions | request changes, with the reason
- **Blocking:** <numbered findings — or none>
- **Suggestions:** <numbered findings — or omit>
- **Verified:** <what you ran> → <result>
