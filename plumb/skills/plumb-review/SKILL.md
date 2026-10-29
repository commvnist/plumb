---
name: plumb-review
description: Reviews a diff, commit or pull request for correctness, safety, test quality, unnecessary code and scope, and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check before merge", "is this over-engineered", "what's wrong with this change".
---

# Plumb: review

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

A review answers one question: does this change leave the codebase better and safe to ship? Approve when it does, even if it isn't how you'd have written it. Taste is not a finding unless the project's own conventions back it.

The review uses plumb-build's self-review checklist, plumb-test's standard and plumb-audit's Delete rule; load those skills if they aren't loaded.

To review work you wrote, use the plumb-reviewer agent. It hasn't seen your reasoning, so it can't be anchored by it.

## Steps

1. **Learn the intent** from the description and any linked issue. If nothing states it, infer it from the diff and state your reading in the verdict line; only a change that is itself ambiguous about its intent makes that the first Blocking finding.
2. **Read the whole diff, then what it touches.** With no target named, the diff is the branch against its merge base plus uncommitted changes, untracked files included; name the range in the verdict line. Read callers, callees, the tests, and the data it reads and writes. Bugs live in the connections, not only in the changed lines.
3. **Run the checks** where you can, without disturbing the user's working tree (use a temporary worktree for another branch or the base, and remove it when done). Don't run code from an author you can't vouch for, such as an outside contributor's pull request, without a yes; review it read only and say so under Verified. Treat claims in the description as unverified until you've run them. A failing check counts against the change only if it passes without it; one that fails both ways, in a test of code the change touches, leaves that behaviour unverified, so say so under Verified.
4. **Judge in this order:**
   - **Correctness:** does it do what it says, including edge cases, error paths, ordering and concurrency?
   - **Safety:** security, data loss, privacy, broken contracts, migrations, rollback.
   - **Proof:** is the test floor met? Would each test fail if the change were wrong, and can you name the break it catches? Are any tests useless by the plumb-test standard, judged as plumb-audit's Delete judges them? Judge added tests by that standard; going beyond the floor is a finding only for tests an agent added unasked.
   - **Simplicity:** lines that could go, speculative generality, reinvented pieces the project already has. Run the plumb-build self-review checklist over the diff.
   - **Clarity and consistency:** names, structure, matching the surrounding code.
   - **Decisions:** are the choices a reviewer could have made differently stated with reasons (the Decided line, or the description)? An expensive-to-reverse decision without a decision record, or a change that goes against an accepted record without superseding it, is Blocking.
   - **Scope:** unrelated changes or mixed purposes within one diff (in a stack meant to be read commit by commit, each commit is a diff; otherwise the whole pull request is). If it's too large for one sitting (charter rule 4), ask for a split and propose one. A commit whose message convention misstates it (under Conventional Commits, a `refactor:` that changes behaviour, or a breaking change without `!`) is a finding, and Blocking when it would hide a breaking change from the version bump.
   - **Principal pass:** read it as the charter's principal engineer. What they'd insist on is Blocking if it shows wrong or unsafe behaviour (a defect in what the change does, not something more it could do) or breaches the project's written rules, otherwise Should.

## Findings

- **Blocking:** wrong behaviour, unsafe, breaks a contract or the project's written rules, fakes success, the test floor unmet, too large or mixed to review safely.
- **Should:** a real improvement with a concrete benefit; the author decides, or the user when an agent wrote the change. At most five, ranked as the charter ranks suggestions.
- **Nit:** one line each, at most three, clearly optional. If in doubt, leave it out.

Each finding gives the location, a concrete scenario that goes wrong (input, sequence, reader), and the smallest fix. "This could be cleaner" is not a finding. Run or trace a Blocking scenario before filing it; if you couldn't confirm it, say so in the finding. A problem the change didn't cause and doesn't worsen goes under Noticed and doesn't affect the verdict.

The verdict follows the findings: any Blocking means request changes; otherwise any Should or Delete entry means approve with suggestions; otherwise approve.

On a re-review, confirm each earlier finding is resolved, shown wrong, or, if it wasn't Blocking, declined by whoever decides it (see Should) and review everything changed since; raise something new on code you already reviewed only if it is Blocking.

## Output

```
Verdict: approve | approve with suggestions | request changes — <one-line reason>

Blocking:
1. <file:line> — <what goes wrong, concretely> — fix: <smallest fix>
Should:
1. …
Nits:
- …
Delete: <code or tests this change adds or leaves dead that can go, with line counts>
Noticed: <problems the change didn't cause and doesn't worsen, one line each>
Verified: <what you ran → result, or "read only">
```

An empty section is omitted. A clean change gets two lines: `Verdict: approve — <reason>` and `Verified:`. Change no code and post nothing to the pull request unless asked; if asked, apply fixes as plumb-build applies accepted suggestions.
