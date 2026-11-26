---
name: plumb-review
description: Reviews a diff, commit, branch or pull request and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check my work", "is this safe to merge". For a whole codebase, use plumb-audit.
---

# Plumb: review

Approve a change that leaves the codebase better and safe to ship; taste is not a finding.

## Steps

1. **Learn the intent,** and state your reading of it; a change that delivers something else fails correctness.
2. **Read the whole diff, then what it touches.**
3. **Run the project's checks;** the description's claims are unverified until you do. Make each finding happen and try its fix in a scratch copy, with whatever the change allows (a render, a dry run, a script); a defect you can neither make happen nor trace from its input is a question, never Blocking.
4. **Judge in order:** correctness, safety (charter rules 8 and 11), proof (charter rules 12 and 16 to 18), simplicity (5 to 10), scope (1 to 3). Trace each finding's input to where it enters.

## Output

A review posted to the host carries this verdict as its state; each comment says whether it blocks, and the body only what the lines can't.

- **Verdict:** approve | approve with suggestions | request changes, on <the commit judged>, with the reason
- **Blocking:** <findings, or none>
- **Suggestions:** <findings>
- **Verified:** <command> → <result>; unchecked: <what the change touches that nothing run exercised>
