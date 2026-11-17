---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing. When something you were told to send can't leave, give the exact text you would have used.

Run the project's full checks on what ships. If one fails, don't ship: report it and ask before changing code you didn't write.

## Commits and branches

One logical change per commit, always in Conventional Commits: `<type>(<scope>)<! if breaking>: <subject>`, type one of `feat`, `fix`, `perf`, `refactor`, `style`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. What the history's own format carries, such as a ticket id, goes in the scope or a footer.

Every commit gets a body, wrapped at 72 columns and as long as the change needs, telling a later reader what the diff can't: why, the choices made, how it was verified. Footers hold only facts a tool reads, such as `BREAKING CHANGE: <what callers must do>` or the issue closed.

Name a branch `<type>/<short-slug>` unless the repo has its own convention.

## Pull requests

Title it as a commit subject, with `!` if any commit is breaking. Fill the project's template if it has one; otherwise write for a principal engineer deciding whether to merge, under short headings and as long as the change needs, what the diff can't show them, such as why, what changes for dependents, the choices and their costs, the risk and the way back, what was verified, where to look first, what was left out.

## Changelogs and releases

What changes for users and what they must do, never the commit list, in the project's file and versioning scheme.
