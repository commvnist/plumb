---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing. When something you were told to send can't leave, give the complete text you would have sent, ready to send as is.

Ship only what the project's checks have passed on as it stands. If one fails, don't ship: report it and ask before changing code you didn't write. Deploy only with a way back for everything it changes, stored data included, tried on a copy where it can be, or a yes to the step that has none, either recorded where the project keeps what shipped. Name first what would show it failing, release first to the smallest share the project's deploy can reach, then check that against how it ran before; at a sign of failure, take the way back before looking for the cause, under the same instruction.

## Commits and branches

One logical change per commit, holding only files the change wrote, staged by name, always in Conventional Commits: `<type>(<scope>)<! if breaking>: <subject>`, the subject an imperative that reads whole in a one-line log (never "fix bug"), type one of `feat`, `fix`, `perf`, `refactor`, `style`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. What the history's own format carries, such as a ticket id, goes in the scope or a footer.

Every commit gets a body, wrapped at 72 columns and as long as the change needs, telling a later reader what the diff can't, whole without any link it cites: what is wrong or missing without the change, then the choices made and what each beat, then the evidence the project's checks don't hold. Footers hold only facts a tool reads, such as `BREAKING CHANGE: <what callers must do>` or the issue closed.

Commit where the work can still be reviewed: one branch off the one it merges into, named `<type>/<short-slug>` unless the repo has its own convention, later work on top unless asked apart; a fix to an unpushed commit of this work goes into it, so each commit passes on its own.

## Pull requests

Title it as a commit subject, with `!` if any commit is breaking. When the operator's own words name the Jira issue the work is for, lead the title with its key in brackets (`[PROJ-123] fix(scope): subject`) and open the description with a section referencing that issue; a key from anywhere else stays out. Write for a principal engineer deciding whether to merge, in the project's template where it has one and under short headings for what it lacks, as long as the change needs, what a commit body holds, then the risk and the way back, what was run and what nothing exercised, and where to look first; when later commits make it untrue, offer the corrected text.

## Changelogs and releases

What changes for users and what they must do (every breaking change and deprecation), never the commit list, in the project's file and versioning scheme, the bump set by what changed for users, not by the commits' types; a change users notice adds its entry to the project's unreleased section, where it keeps one, in its own diff.
