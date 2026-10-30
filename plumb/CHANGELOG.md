# Changelog

What changes for people using plumb. Versions follow semantic versioning; reinstall or run `/plugin marketplace update plumb-marketplace` to pick up a new one.

## 0.4.0

Faster and cheaper to run, with the same guarantees: tests seen failing before they pass, the Decided and Verified lines, skill routing, and waiting for a go-ahead on plans.

### Added
- A plan's go-ahead can cover every step, committing each as it passes. It still stops after a step that makes a decision needing a record, leaves something unverified, adds a risk, or changes the plan.
- Eval cases for building then committing in one session, a build with an independent review, and a whole-repository audit with parallel auditors.

### Changed
- The scout and auditors run on Sonnet. The reviewer still runs on your session's model.
- The charter and the phase skill load in the same turn, and another plumb skill loads only when a step applies a standard only that skill states.
- A check run earlier in the session still counts while version control shows the code is unchanged, so build, refactor and ship stop repeating runs. Committing or shipping still needs a full run on exactly what ships; an earlier one counts only if nothing has changed since.
- After a self-review edit, build and debug re-prove only what the edit could have made untrue. Refactors run the pinning checks after each move and the full checks once per diff.
- The reviewer is pointed at a commit range or the changed paths instead of being sent a pasted diff.
- Build reads only the callers whose view the change could alter.
- The self-review checklist now lives in the charter, and the keep, merge, rewrite or delete verdicts in plumb-test. The reviewer loads three skills instead of five, the scout loads none, and auditors don't load the charter.
- An audit runs the project's checks once and gives each auditor its area's results.
- A change confined to one area that changes no contract or data shape gets a shorter report and only high-risk suggestions. Its check for wrong or unsafe behaviour is unchanged.

### Fixed
- A request to build something and then commit it now loads plumb-ship before committing, so the commit gets ship's checks and a Conventional Commits subject. Before, the agent often committed straight from the build.

### Removed
- The example blocks in agent descriptions, which were in every session's system prompt.

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
- Rules are worded as a principle with its reason (see CONTRIBUTING.md). Pacing between diffs, staging of breaking changes, staying off shared systems and leaving the user's working tree alone are each stated once in the charter, and the other skills point to them.
- Committing work with a failing check "as it stands" needs the user to know what fails first; a plain "commit this" isn't that consent.
- A plan's first slice runs the path the request exists for, through its least certain part.
- A plan asks whether to start decision records when the project keeps none and a step will write one.
- Work that is part of done stays off the suggestions menu, so the menu holds only what the operator is choosing.
- A choice the user made that is expensive to reverse (such as renaming a public field) still gets a decision record stating their reason, or that none was given; plans list it under Decisions.

## 0.2.0

- First versioned release after the 2026-10-28 review rounds: one principal-engineer pass for suggestions, aligned test-change, staging and safety rules across all skills.
