---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing.

## Before anything leaves

Run the project's full checks on what ships and quote the result. If one fails, don't ship: report it and ask before changing code you didn't write.

## Commits

One logical change per commit, always in Conventional Commits: `<type>(<scope>)<! if breaking>: <subject>`, with `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci` or `chore`. Whatever the history's own format carries, such as a ticket id, goes in the scope or a footer.

Every commit gets a body, wrapped at 72 columns, telling a later reader what the diff can't, such as why it was needed, the choices made and how it was verified. Footers last, such as `BREAKING CHANGE: <what callers must do>`.

## Pull requests

Title it as a commit subject, with `!` if any commit is breaking. Fill the project's template if it has one. Otherwise write the body for a principal engineer deciding whether to merge: under short headings, what they can't learn from the diff, such as why, what changes for whoever depends on it, the choices and their costs, the risk and the way back, the evidence, where to look first and what was left out.
