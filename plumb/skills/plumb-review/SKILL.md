---
name: plumb-review
description: Reviews a diff, commit or pull request for correctness, safety, test quality, unnecessary code and scope, and returns a verdict with ranked, concrete findings. Changes nothing. Use for "review this", "code review", "review my PR", "check before merge", "is this over-engineered", "what's wrong with this change".
---

# Plumb: review

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

A review answers one question: does this change leave the codebase better and safe to ship? Approve when it does, even if it isn't how you'd have written it. Taste is not a finding unless the project's own conventions back it.

To review work you wrote, use the plumb-reviewer agent, which hasn't seen your reasoning and so can't be anchored by it (with agents off, see the charter's Agents).

## Steps

1. **Learn the intent** from the description and any linked issue. If nothing states it, infer it from the diff and state your reading in the verdict line.
2. **Read the whole diff, then what it touches.** With no target named, the diff is the branch against its merge base plus uncommitted and untracked changes; name the range in the verdict line. Read callers, callees, the tests, and the data it reads and writes. Bugs live in the connections, not only in the changed lines.
3. **Run the checks** where you can, without disturbing the user's working tree (charter rule 2). Don't run code from an author you can't vouch for, such as an outside contributor's pull request, without a yes. Treat claims in the description as unverified until you've run them. A failing check counts against the change only if it passes without it.
4. **Judge in this order:**
   - **Correctness:** does it do what it says, including edge cases, error paths, ordering and concurrency?
   - **Safety:** security, data loss, privacy, broken contracts, migrations, rollback.
   - **Proof:** is the test floor met? Would each test fail if the change were wrong, and can you name the break it catches? Judge added and changed tests by plumb-test's standard and its "Keep, merge, rewrite or delete"; going beyond the floor is a finding only for tests an agent added unasked.
   - **Simplicity:** lines that could go, speculative generality, reinvented pieces the project already has. Run the charter's self-review checklist over the diff.
   - **Clarity and consistency:** names, structure, matching the surrounding code.
   - **Decisions:** are the choices a reviewer could have made differently stated with reasons? In a project that keeps decision records, an expensive decision without one, or a change that goes against an accepted record without superseding it, is Blocking; elsewhere, an expensive decision whose reason is stated nowhere is a Should.
   - **Scope:** unrelated changes or mixed purposes within one diff. If it's too large for one sitting (charter rule 4), ask for a split and propose one. A commit whose message convention misstates it (a `refactor:` that changes behaviour) is a finding, and Blocking when it would hide a breaking change from the version bump.
   - **Principal pass:** read it as the charter's principal engineer. What they'd insist on is Blocking if it shows wrong or unsafe behaviour (a defect in what the change does, not something more it could do) or breaches the project's written rules, otherwise Should.

## Findings

- **Blocking:** wrong behaviour, unsafe, breaks a contract or the project's written rules, fakes success, the test floor unmet, too large or mixed to review safely.
- **Should:** a real improvement with a concrete benefit; the author decides, or the user when an agent wrote the change. At most five, ranked as the charter ranks suggestions, each naming the principle it serves. What the charter already required of the author (a checklist hit or Delete entry in lines the change adds or leaves dead, a missing reason for a decision) is part of done, since a review can't make optional what the author owed before it.
- **Nit:** one line each, at most three, clearly optional. If in doubt, leave it out.

Each finding gives the location, a concrete scenario that goes wrong (input, sequence, reader), and the smallest fix; "this could be cleaner" is not a finding. The scenario must be one the system can produce: trace its input back to where it enters before filing, since a finding for a state the code is never given asks for the guard charter rule 8 forbids, and every false alarm teaches the reader to skim the real ones. Run or trace a Blocking scenario before filing it; if you couldn't confirm it, say so. A defect repeated in several places is one finding that lists them, since copies filed apart crowd out the next problem. A problem the change didn't cause and doesn't worsen goes under Noticed and doesn't affect the verdict. What the user asked for or decided knowing its risk, a waived rule included, isn't a finding; name its risk once in the verdict line, since a review judges the author's choices, not the user's.

The verdict follows the findings: any Blocking means request changes; otherwise any Should or Delete entry means approve with suggestions; otherwise approve.

On a re-review, confirm each earlier finding is resolved, shown wrong or declined, and review what changed since; raise something new on code you already reviewed only if it is Blocking.

## Output

```
Verdict: approve | approve with suggestions | request changes — <one-line reason>

Blocking:
1. <file:line> — <what goes wrong, concretely> (<principle>) — fix: <smallest fix>
Should:
1. …
Nits:
- …
Delete: <code or tests this change adds or leaves dead that can go, with line counts>
Noticed: <problems the change didn't cause and doesn't worsen, one line each>
Verified: <what you ran → result, or "read only">
```

An empty section is omitted. A clean change gets two lines: `Verdict: approve — <reason>` and `Verified:`. Change no code and post nothing to the pull request unless asked; if asked, apply fixes as plumb-build applies accepted suggestions.
