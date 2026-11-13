---
name: plumb-ship
description: Packages finished work for review and release, covering commit splitting and messages, pull request descriptions, changelogs, version bumps and safe rollout. Use for "commit this", "write the commit message", "open a PR", "PR description", "split this PR", "release notes", "changelog", "bump the version", "deploy" or "roll out".
---

# Plumb: ship

Part of plumb. If the `plumb` skill isn't loaded in this session, load it now; its charter governs and this skill only adds to it.

Never commit, push, open or update a pull request, merge, tag, publish or deploy without an explicit instruction to do that specific thing (a standing one counts, per the charter's Authority); an instruction to open a pull request covers committing the change, on a new branch if you're on the default one, and pushing it. Rewriting history that's already pushed, or commits you didn't make this session, needs a yes that names it.

## Before anything leaves

Read everything you'll commit or push, new files included, as its reviewer, using the charter's self-review checklist, unless a self-review from this session already covered exactly those lines. Run the project's full set of checks, or use a full run that charter rule 15 says still counts, and quote the result. Name failures that predate the change rather than blocking on them. If a check fails because of this change, or the review finds a problem, don't ship: fix it and re-run in work you wrote this session; in work you didn't, report it and ask before changing a line, holding the ship only for a failing check or a problem plumb-review would call Blocking. If the user, knowing what fails, asked to commit the work as it stands, commit it and say in the message what fails; a request made before they could know is not consent to that, so tell them first and ask. Never bypass the project's hooks, a red or pending required check, or branch protection without a yes that names it. For anything non-trivial, offer a review by the plumb-reviewer agent (the charter's Agents route when agents are off), without holding up an explicit instruction to ship.

## Commits

- One logical change per commit, and each commit builds and passes the checks on its own. Stage only this change's hunks and new files, and name other working-tree changes instead of committing them.
- Follow the project's message convention if it has one: a format its subjects share that a reader or tool could check, such as type prefixes or ticket ids (the charter's Authority). A history of plain sentences has none, however alike they read, since every good subject is a plain imperative sentence, Conventional Commits' included; matching their wording keeps no format, and a typed subject continues such a history rather than converting it. Never rewrite past commits to match. Where there is no such format, use Conventional Commits 1.0.0: `<type>(<optional scope>)<! if breaking>: <subject>`, with type `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `style` (formatting only) or `revert`. The subject is in the imperative, about 60 characters, stating what the commit changes, in behaviour where it changes any; never "update files" or "address feedback", and never a list of changed files, which the diff already shows. Add a body only when there's something the diff can't say, such as why, the cause of a bug, a trade-off (the report's Decided choices among them) or a risk. A breaking change always carries `!` and a `BREAKING CHANGE:` footer saying what callers must do. The first commit in a format the history hasn't used goes under Decided, so the operator can keep it or state their own convention in the written rules.
- The type is the commit's one purpose (charter rule 3). A commit that needs two types is two commits; a `refactor` or `test` commit changes no behaviour.

## Splitting

When a change is too big for one sitting (charter rule 4), or mixes purposes, split it into a stack: preparatory behaviour-preserving changes first, then the behaviour change, then cleanup. Each piece is correct and mergeable on its own. Propose the split, as commits in one pull request reviewed commit by commit or as separate pull requests, and wait for a yes.

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

Title the pull request as its commit subject would be written (Commits above), with the breaking marker if any commit in it carries one, since a squash merge makes the title the commit on the target branch. Keep the description short. Carry the report's Look hardest line into How to verify. No marketing words, no emoji, no restating the diff.

## Releases

- Changelog entries are written for the people affected, describing what changes for them, in the project's changelog format (with none, grouped as Added, Changed, Fixed, Removed and Security).
- Choose the version bump from the contracts that changed, by the project's versioning scheme; with Conventional Commits and semantic versioning, a breaking change means major (minor before 1.0.0), `feat` minor, `fix` or `perf` patch. A breaking change always gets the scheme's breaking bump, however small it is.
- State the rollback before rolling out; if there isn't one, say so and ask first. For a risky change, offer a flag or staged exposure as a suggestion; don't add one unasked.
- A change charter rule 3 says to stage ships one stage per release (plumb-plan step 5), so every step can be rolled back; if this change doesn't, say so and ask before shipping it.
- After a deploy, and after each stage of one, check the signals that would show it failing and report what you saw; if they do, stop the rollout and propose the rollback, taking it only on a yes.
