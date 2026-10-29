# Changelog

What changes for people using plumb. Versions follow semantic versioning; reinstall or run `/plugin marketplace update plumb-marketplace` to pick up a new one.

## 0.3.0

### Added
- Every report has a `Decided` line: each choice a reviewer could reasonably have made differently, with its reason.
- Decisions that are expensive to reverse get a decision record in the diff that acts on them: the project's format, or a Nygard ADR in `docs/adr/`. Plan, review, audit and the scout read and check them.
- Commits follow Conventional Commits 1.0.0 unless the project has its own convention; review flags a commit type that hides a breaking change.
- A multi-step plan is carried in each step's pull request description, so a new session can pick it up and check what the next step waits for.
- Debug and refactor offer the independent reviewer for non-trivial work.
- README sections on behaviour that surprises people and on tuning plumb per project.
- Licensed under GPL-3.0-or-later.
- A reference checker (`scripts/check_refs.py`, run in CI) fails when a numbered rule, step or section reference stops pointing at its target.
- A session-start hook tells the agent to load the charter and the fitting phase skill for any coding request. In evals, phase skills went from firing in about half the cases to all of them.
- An eval suite (`evals/`): 14 seeded tasks across greenfield and brownfield work on small, medium and large codebases, run with `claude plugin eval`.

### Changed
- The suggestions menu shows only medium and high-risk items; low-risk ones are counted under "N more on request". Each suggestion names the principle it serves.
- Standing instructions in the environment the user set up (such as "commit and push when done") count as the user's request.
- The charter itself stages breaking changes to persisted data through plumb-plan, and the charter routes to the fitting phase skill.
- Suggestions are strictly opt-in: never "I'll include it unless you object".
- Charter rule 12 states its three allowed test edits once, as a list; plumb-test and plumb-refactor point to it.
- The report's Verified line names the exact command or manual check that was run.
- The cost of reversing a decision is judged by what will come to depend on it, not by how little code it is today, so foundational choices in new projects get decision records too.
- A commit convention means one the project states or its history visibly follows; otherwise commits use Conventional Commits.

## 0.2.0

- First versioned release after the 2026-10-28 review rounds: one principal-engineer pass for suggestions, aligned test-change, staging and safety rules across all skills.
