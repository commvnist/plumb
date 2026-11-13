---
name: plumb-ship
description: Packages finished work for review and release, covering commit splitting and messages, pull request descriptions, changelogs, version bumps and safe rollout. Use for "commit this", "write the commit message", "open a PR", "PR description", "split this PR", "release notes", "changelog", "bump the version", "deploy" or "roll out".
---

# Plumb: ship

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

Never commit, push, open a pull request, merge or deploy without an explicit instruction to do that specific thing.

## Before anything leaves

Read what you'll commit as its reviewer, run the project's full checks on exactly what ships, and quote the result. If a check fails because of this change, don't ship: report it and ask before changing code you didn't write.

## Commits

One logical change per commit. Follow the project's message convention if its subjects share a checkable format, such as type prefixes or ticket ids. A history of plain sentences has none, since every good subject is a plain imperative sentence; there, use Conventional Commits (`<type>(<scope>)<! if breaking>: <subject>`, type `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci` or `chore`) and say so under Decided. The subject states what changes in behaviour, in the imperative.

## Pull request description

What, Why, Decisions, How to verify, Risk. Title the pull request as its commit subject would be written, with the breaking marker if any commit carries one, since a squash merge makes the title the commit.

## Releases

Changelog entries are written for the people affected. A breaking change is a major bump, `feat` minor, `fix` patch. State the rollback before rolling out.
