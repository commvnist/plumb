---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing. When something you were told to send can't leave, give the complete text you would have sent, ready to send as is.

Ship only what the project's checks have passed on as it stands. If one fails, don't ship: report it and ask before changing code you didn't write. Deploy only with a way back for everything it changes, stored data included, recorded where the project keeps what shipped, then check what would show it failing.

## Commits and branches

One logical change per commit, holding only files the change wrote, staged by name, always in Conventional Commits: `<type>(<scope>)<! if breaking>: <subject>`, type one of `feat`, `fix`, `perf`, `refactor`, `style`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. What the history's own format carries, such as a ticket id, goes in the scope or a footer.

Every commit gets a body, wrapped at 72 columns and as long as the change needs, telling a later reader what the diff can't, leading with why the change was needed, then the choices made and the evidence the project's checks don't hold. Footers hold only facts a tool reads, such as `BREAKING CHANGE: <what callers must do>` or the issue closed.

Commit where the work can still be reviewed: one branch off the one it merges into, named `<type>/<short-slug>` unless the repo has its own convention, later work on top unless asked apart.

## Pull requests

Title it as a commit subject, with `!` if any commit is breaking. When the operator's own words name the Jira issue the work is for, lead the title with its key in brackets (`[PROJ-123] fix(scope): subject`) and open the description with a section referencing that issue; a key from anywhere else stays out. Fill the project's template if it has one; otherwise write for a principal engineer deciding whether to merge, under short headings and as long as the change needs, what the diff can't show them, leading with why the change exists, then the risk and the way back, and where to look first.

## Changelogs and releases

What changes for users and what they must do, never the commit list, in the project's file and versioning scheme.
