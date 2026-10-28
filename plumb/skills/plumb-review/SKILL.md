---
name: plumb-review
description: Reviews a diff, commit or pull request for correctness, safety, test quality, unnecessary code and scope, and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check before merge", "is this over-engineered", "what's wrong with this change".
---

# Plumb: review

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

A review answers one question: does this change leave the codebase better and safe to ship? Approve when it does, even if it isn't how you'd have written it. Taste is not a finding unless the project's own conventions back it.

The review uses plumb-build's self-review checklist and plumb-test's standard; load those skills if they aren't loaded.

For an independent review of your own work, use the plumb-reviewer agent. It hasn't seen your reasoning, so it can't be anchored by it.

## Steps

1. **Learn the intent** from the description and any linked issue. If the intent is unclear, that is the first finding.
2. **Read the whole diff, then what it touches:** callers, callees, the tests, and the data it reads and writes. Bugs live in the connections, not only in the changed lines.
3. **Run the checks** where you can. Treat claims in the description as unverified until you've run them.
4. **Judge in this order** and stop to report anything blocking:
   - **Correctness:** does it do what it says, including edge cases, error paths, ordering and concurrency?
   - **Safety:** security, data loss, privacy, broken contracts, migrations, rollback.
   - **Proof:** is the test floor met, and is nothing above it unrequested? Would each test fail if the change were wrong, and can you name the break it catches? Are any tests useless by the plumb-test standard?
   - **Simplicity:** lines that could go, speculative generality, reinvented pieces the project already has. Run the plumb-build self-review checklist over the diff.
   - **Clarity and consistency:** names, structure, matching the surrounding code.
   - **Scope:** unrelated changes or mixed purposes. If it's too large for one sitting, ask for a split and propose one.
   - **Principal pass:** read it as the charter's principal engineer. What they'd insist on is Blocking if it shows wrong or unsafe behaviour or breaches the project's rules, otherwise Should.

## Findings

- **Blocking:** wrong behaviour, unsafe, breaks a contract, fakes success, risky logic with no proof.
- **Should:** a real improvement with a concrete benefit; the author decides.
- **Nit:** one line each, at most three, clearly optional. If in doubt, leave it out.

Each finding gives the location, a concrete scenario that goes wrong (input, sequence, reader), and the smallest fix. "This could be cleaner" is not a finding.

The verdict follows the findings: any Blocking means request changes; otherwise any Should means approve with suggestions; otherwise approve.

## Output

```
Verdict: approve | approve with suggestions | request changes — <one-line reason>

Blocking:
1. <file:line> — <what goes wrong, concretely> — fix: <smallest fix>
Should:
1. …
Nits:
- …
Delete: <code or tests that can go, with line counts>
Verified: <what you ran → result, or "read only">
```

An empty section is omitted. A clean change gets one line: `Verdict: approve — <reason>`. Change no code unless asked; if asked, each fix is its own diff.
