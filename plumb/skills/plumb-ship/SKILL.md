---
name: plumb-ship
description: Packages finished work for review and release, covering commit splitting and messages, pull request descriptions, changelogs, version bumps and safe rollout. Use for "commit this", "write the commit message", "open a PR", "PR description", "split this PR", "release notes", "changelog", "bump the version", "deploy" or "roll out".
---

# Plumb: ship

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

Never push, merge, tag, publish or deploy without an explicit instruction to do that specific thing.

## Before anything leaves

Read the full diff once more as its reviewer, using the plumb-build checklist. Remove debug leftovers. Run the project's checks and quote the result. For anything non-trivial, offer a review by the plumb-reviewer agent first.

## Commits

- One logical change per commit, and each commit builds and passes the checks on its own.
- Follow the project's message convention if it has one. Otherwise: a subject line in the imperative, about 60 characters, stating what changes in behaviour; a blank line; then a body only when there's something the diff can't say, such as why, the cause of a bug, a trade-off or a risk.
- Never write subjects like "update files", "fix stuff" or "address feedback", and never list the changed files; the diff already shows them.

## Splitting

When a change is too big for one sitting, or mixes purposes, split it into a stack: preparatory behaviour-preserving changes first, then the behaviour change, then cleanup. Each piece is correct and mergeable on its own. Propose the split and wait for a yes before rewriting history.

## Pull request description

```
## What
<one to three lines, at the level of behaviour>

## Why
<the problem it solves; link the issue>

## How to verify
<steps the reviewer can run; what you ran and what it showed>

## Risk
<contracts, data, migrations, rollout and rollback — or "low: <why>">

## Not in this change
<what was deliberately left out, including suggestions that were declined or deferred>
```

Keep it short. Point the reviewer to the one place to look hardest. No marketing words, no emoji, no restating the diff.

## Releases

- Changelog entries are written for the people affected, describing what changes for them, grouped as Added, Changed, Fixed, Removed and Security. They are not a list of commits.
- Choose the version bump from the contracts that changed, by the project's versioning scheme. A breaking change is never hidden in a minor release, however small it is.
- Prefer rollouts that can be reversed: flags or staged exposure for risky changes. Know the rollback before rolling out.
- Persisted data changes go expand, migrate, contract, in separate releases, so every step can be rolled back.
- After a deploy, check the signals that would show it failing, and report what you saw.
