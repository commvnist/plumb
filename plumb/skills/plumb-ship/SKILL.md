---
name: plumb-ship
description: Packages finished work for review and release: commits, pull requests, changelogs, version bumps. Use for "commit this", "commit message", "open a PR", "PR description", "release notes", "bump the version", "deploy".
---

# Plumb: ship

Never commit, push, open a pull request, merge or deploy without an instruction to do that specific thing.

## Before anything leaves

Run the project's full checks on what ships and quote the result. If one fails, don't ship: report it and ask before changing code you didn't write.

## Commits

One logical change per commit. Keep the project's convention if its subjects share a checkable format (type prefixes, ticket ids). Plain sentences are no format: there, use Conventional Commits (`<type>(<scope>)<! if breaking>: <subject>`; `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`) and say so under Decided.

## Pull request description

Title it as a commit subject, with `!` if any commit is breaking.
