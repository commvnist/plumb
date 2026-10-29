---
name: plumb-ship
description: Packages finished work for review and release, covering commit splitting and messages, pull request descriptions, changelogs, version bumps and safe rollout. Use for "commit this", "write the commit message", "open a PR", "PR description", "split this PR", "release notes", "changelog", "bump the version", "deploy" or "roll out".
---

# Plumb: ship

Part of plumb. If the `plumb` skill isn't loaded in this session, load it first; its charter governs and this skill only adds to it.

Never commit, push, open or update a pull request, merge, tag, publish or deploy without an explicit instruction to do that specific thing (a standing one counts, per the charter's Authority); an instruction to open a pull request covers committing the change, on a new branch if you're on the default one, and pushing it. Rewriting history that's already pushed, or commits you didn't make this session (amend, rebase, force push), needs a yes that names it. When a push makes an open pull request's description untrue, say which part and offer the update.

## Before anything leaves

Before you commit or push, read everything you'll commit or push, new files included, once more as its reviewer, using the plumb-build self-review checklist (load plumb-build if it isn't loaded). Run the project's full set of checks (charter rule 15) and quote the result. Name failures you've seen fail without the change rather than blocking on them. If a check fails because of this change, or the review finds a problem (debug leftovers included), don't ship yet: in work you wrote this session, fix it and re-run the checks; in work you didn't, report it and ask before changing a line, holding the ship only for a failing check or a problem plumb-review would call Blocking. If the user asked to commit the work as it stands, commit it and say in the message what fails; never bypass the project's hooks without a yes that names it. Before a merge or publish, quote the state of the checks on exactly what will merge or be published, and never go ahead over a red or pending required check, or bypass branch protection, without a yes that names it. For anything non-trivial, offer a review by the plumb-reviewer agent, without holding up an explicit instruction to ship, unless one was already offered or run on this diff.

## Commits

- One logical change per commit, and each commit builds and passes the checks on its own, failures that predate the change aside. Stage only this change's hunks and new files; name any other working-tree changes instead of committing them, and when you leave any out, run the checks on exactly what you commit, in a temporary worktree you remove afterwards, never by stashing the user's changes; if they can't run there, say what went unverified instead of quoting a working-tree run.
- Follow the project's message convention if it has one; never convert its history. Otherwise use Conventional Commits 1.0.0: `<type>(<optional scope>)<! if breaking>: <subject>`, with type `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore` or `revert`. The subject is in the imperative, about 60 characters, stating what the commit changes, in behaviour where it changes any. Then a blank line and a body only when there's something the diff can't say, such as why, the cause of a bug, a trade-off (the report's Decided choices among them) or a risk. A breaking change always carries `!` and a `BREAKING CHANGE:` footer saying what callers must do.
- The type is the commit's one purpose (charter rule 3). A commit that needs two types is two commits (the docs and decision record a change needs share its type); a `refactor` or `test` commit changes no behaviour.
- Never write subjects like "update files", "fix stuff" or "address feedback", and never list the changed files; the diff already shows them.

## Splitting

When a change is too big for one sitting (charter rule 4), or mixes purposes, split it into a stack: preparatory behaviour-preserving changes first (among them any test deletion that charter rule 12 says lands before the change), then the behaviour change, then cleanup. Each piece is correct and mergeable on its own. Propose the split, as commits in one pull request whose description says to review it commit by commit, or as separate pull requests, and wait for a yes before making it.

## Pull request description

Use the project's pull request template if it has one; otherwise:

```
## What
<one to three lines, at the level of behaviour>

## Why
<the problem it solves; link the issue and any decision record this change adds or supersedes>

## Decisions
<the change's Decided line, for choices the reviewer could have made differently — or omit>

## How to verify
<steps the reviewer can run; what you ran and what it showed; what you couldn't verify>

## Risk
<contracts, data, migrations, rollout and rollback — or "low: <why>">

## Not in this change
<what was deliberately left out, including suggestions that were declined or deferred>

## Plan
<for a step of a multi-step plan: every step, which are done, and what the next one waits for — or omit>
```

Keep it short. Point the reviewer to the one place to look hardest. No marketing words, no emoji, no restating the diff.

## Releases

- Changelog entries are written for the people affected, describing what changes for them, in the project's changelog format (with none, grouped as Added, Changed, Fixed, Removed and Security). They are not a list of commits.
- Choose the version bump from the contracts that changed, by the project's versioning scheme; with Conventional Commits and semantic versioning, a breaking change means major (minor before 1.0.0), `feat` minor, anything else patch. A breaking change always gets the scheme's breaking bump, however small it is. Read the commit types to draft the changelog, then rewrite each entry for the people affected.
- State the rollback before rolling out; if there isn't one, say so and ask first. For a risky change, offer a flag or staged exposure as a suggestion; don't add one unasked.
- A breaking change to persisted data, or to a contract consumers outside the repository depend on, goes expand, migrate, contract, in separate releases, so every step can be rolled back; if this change doesn't, say so and ask before shipping it.
- After a deploy, and after each stage of one, check the signals that would show it failing and report what you saw; if they do, stop the rollout and propose the rollback, taking it only on a yes.
