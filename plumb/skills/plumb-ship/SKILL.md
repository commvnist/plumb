---
name: plumb-ship
description: Packages finished work for review and release, covering commit splitting and messages, pull request descriptions, changelogs, version bumps and safe rollout. Use for "commit this", "write the commit message", "open a PR", "PR description", "split this PR", "release notes", "changelog", "bump the version", "deploy" or "roll out".
---

# Plumb: ship

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

Never commit, push, open or update a pull request, merge, tag, publish or deploy without an explicit instruction to do that specific thing; an instruction to open a pull request covers committing the change, on a new branch if you're on the default one, and pushing it. These need a yes that names them: rewriting history that's already pushed, or commits you didn't make this session (amend, rebase, force push); bypassing the project's hooks or branch protection; merging or publishing over a red or pending required check. When a push makes an open pull request's description untrue, say which part and offer the update.

## Before anything leaves

Before you commit or push, read everything going out, new files included, once more as its reviewer against plumb-build's self-review checklist (load plumb-build if it isn't loaded), and run the project's checks, quoting the result.

- If a check fails because of this change, or the review finds a problem (debug leftovers included), don't ship yet. In work you wrote this session, fix it and re-run the checks. In work you didn't, report it and ask before changing a line, holding the ship only for a failing check or a problem plumb-review would call Blocking.
- If the user asked to commit the work as it stands, commit it and say in the message what fails.
- Before a merge or publish, quote the state of the checks on exactly what will merge or be published. Name failures you've seen fail without the change rather than blocking on them.
- For anything non-trivial, offer a review by the plumb-reviewer agent, unless one was already offered or run on this diff; the offer never holds up an explicit instruction to ship.

## Commits

- One logical change per commit, and each commit builds and passes the checks on its own. Stage only this change's hunks and new files, and name any other working-tree changes instead of committing them. When you leave any out, run the checks on exactly what you commit in a temporary worktree (charter rule 20); if they can't run there, say what went unverified instead of quoting a working-tree run.
- Follow the project's message convention if it has one. Otherwise: a subject line in the imperative, about 60 characters, stating what the commit changes, in behaviour where it changes any; a blank line; then a body only when there's something the diff can't say, such as why, the cause of a bug, a trade-off or a risk. Never subjects like "update files", "fix stuff" or "address feedback", and never a list of the changed files; the diff shows them.

## Splitting

When a change is too big for one sitting, or mixes purposes, split it into a stack: preparatory behaviour-preserving changes first, then the behaviour change, then cleanup. Each piece is correct and mergeable on its own. Propose the split, as commits in one pull request or as separate pull requests, and wait for a yes before making it.

## Pull request description

Use the project's pull request template if it has one; otherwise:

```
## What
<one to three lines, at the level of behaviour>

## Why
<the problem it solves; link the issue>

## How to verify
<steps the reviewer can run; what you ran and what it showed; what you couldn't verify>

## Risk
<contracts, data, migrations, rollout and rollback — or "low: <why>">

## Not in this change
<what was deliberately left out, including suggestions that were declined or deferred>
```

Keep it short. Point the reviewer to the one place to look hardest. No marketing words, no emoji, no restating the diff.

## Releases

- Changelog entries are written for the people affected, describing what changes for them, in the project's changelog format (with none, grouped as Added, Changed, Fixed, Removed and Security). They are not a list of commits.
- Choose the version bump from the contracts that changed, by the project's versioning scheme. A breaking change always gets the scheme's breaking bump, however small it is.
- State the rollback before rolling out; if there isn't one, say so and ask first. For a risky change, offer a flag or staged exposure as a suggestion; don't add one unasked.
- Persisted data changes go expand, migrate, contract, in separate releases, so every step can be rolled back; if this change doesn't, say so and ask before shipping it.
- After a deploy, and after each stage of one, check the signals that would show it failing and report what you saw; if they do, stop the rollout and propose the rollback, taking it only on a yes.
