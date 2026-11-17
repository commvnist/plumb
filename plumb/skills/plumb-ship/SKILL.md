---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing. When something you were told to send can't leave, give the exact message or description you would have used, so nothing is lost but the last step.

## Before anything leaves

Run the project's full checks on what ships and quote the result. If one fails, don't ship: report it and ask before changing code you didn't write.

## Commits

One logical change per commit, always in Conventional Commits: `<type>(<scope>)<! if breaking>: <subject>`, with `feat`, `fix`, `perf`, `refactor`, `style`, `test`, `docs`, `build`, `ci`, `chore` or `revert`. Whatever the history's own format carries, such as a ticket id, goes in the scope or a footer.

Every commit gets a body, wrapped at 72 columns and as long as the change needs, telling a later reader what the diff can't, such as why it was needed, the choices made and how it was verified. Footers hold only facts a tool reads, such as `BREAKING CHANGE: <what callers must do>` or the issue it closes.

## Pull requests

Title it as a commit subject, with `!` if any commit is breaking. Fill the project's template if it has one. Otherwise write the body for a principal engineer deciding whether to merge: under short headings, as long as the change needs, what they can't learn from the diff, such as why, what changes for whoever depends on it, the choices and their costs, the risk and the way back, what was verified, where to look first and what was left out.

## Changelogs and releases

Say what changes for users and what they must do, never the commit list, in the project's file and versioning scheme.
