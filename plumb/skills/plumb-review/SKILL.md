---
name: plumb-review
description: Reviews a diff, commit, branch or pull request and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check my work", "is this safe to merge". For a whole codebase, use plumb-audit.
---

# Plumb: review

Approve a change that leaves the codebase better and safe to ship; taste is not a finding. Change no code.

## Steps

1. **Learn the intent,** and state your reading of it; a change that delivers something else fails correctness.
2. **Read the whole diff, then what it touches.**
3. **Run the project's checks;** the description's claims are unverified until you do.
4. **Judge in order:** correctness, safety, proof (charter rules 12 and 16 to 18), simplicity, scope. Trace each finding's input to where it enters.

## Output

- **Verdict:** approve | approve with suggestions | request changes, on <the commit judged>, with the reason
- **Blocking:** <findings, or none>
- **Suggestions:** <findings>
- **Verified:** <command> → <result>
