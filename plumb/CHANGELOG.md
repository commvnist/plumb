# Changelog

What changes for people using plumb. Versions follow semantic versioning; reinstall or run `/plugin marketplace update plumb-marketplace` to pick up a new one.

## 0.6.0

Decisions and checks are easier for the operator to see, and plumb loads less text and skips repeat work, with the same guarantees.

### Added
- Audit findings and Blocking review findings name the principle they serve, as suggestions already did.
- An audit's Scope line says how it split the repository into areas, or why it read it in one session.
- An eval case checks that a request for two diffs stops after the first one's report.

### Changed
- A request that names several phases (build it, then commit it) loads each phase's skill in the first turn, so the commit rules shape the build.
- The report's Done line uses the project's commit convention, else Conventional Commits. Plain imperative subjects in a project's history don't count as a convention.
- Decided names the record, or the question about starting `docs/adr/`, for a choice that is expensive to reverse.
- Unverified lists each behaviour the change adds or could have altered that no run exercised.
- A test, added or changed, counts as seen failing only when a run shows it failing on the break it exists to catch. A predicted failure isn't evidence, and the self-review checklist asks for the run.
- A change that misbehaves under conditions it will meet (its own calls repeated, concurrent or failing partway) is a defect to fix, not a menu item.
- A plan's first slice carries the narrowest form of whatever it needs to run, instead of following setup or foundation steps.
- Every plan step confirms the event it waits for before it is built.
- Building a later plan step no longer loads plumb-plan, and a scout map from earlier in the session is reused for code only this session has changed.
- The reviewer's briefing moved from its always-loaded description into the charter, cutting the text every session carries by about 17%.
- The Agents line says "the tool's default" when the model that ran isn't known, rather than guessing.
- With agents off, a missing independent review goes under Unverified only when one was asked for or accepted, so a standing go-ahead doesn't stop at every step.
- Fixing a confirmed reviewer finding is part of done in every phase, not only in build.
- Each question asks one thing.

## 0.5.0

Fits any budget and runs on Codex: plumb names no model, you choose one per agent or turn agents off, and the same files install on Codex (untested there).

### Added
- Choose each agent's model, and optionally its reasoning effort, with a `plumb agents:` line in the project's written rules, such as `- plumb agents: scout haiku low, reviewer opus high`. A role you don't name uses your tool's default. Every reply that started an agent says which model it ran on.
- `plumb agents: off` runs plumb without subagents. The session does each agent's work; a review of its own work says it isn't independent and offers one in a fresh session. A request in the conversation for an agent's work still starts one, and the reply says so.
- The build and ship offers of an independent review point to the agents-off route.
- Codex support, untested: a Codex plugin manifest, a Codex marketplace entry and Codex versions of the agents, all generated from the Claude Code files by `scripts/build_codex.py`, with install steps in the README.
- Eval cases for a chosen reviewer model, a build with agents off, and a whole-repository audit with agents off.

## 0.4.0

Faster and cheaper to run, with the same guarantees: tests seen failing before they pass, the Decided and Verified lines, skill routing, and waiting for a go-ahead on plans.

### Added
- A plan's go-ahead can cover every step, committing each as it passes. It still stops after a step that makes a decision needing a record, leaves something unverified, adds a risk, or changes the plan.
- Eval cases for building then committing in one session, a build with an independent review, and a whole-repository audit with parallel auditors.

### Changed
- Agents no longer set a model, so they follow your choice (the session's model, or `CLAUDE_CODE_SUBAGENT_MODEL` for all subagents). Setting that variable to a cheaper model is the main way to cut agent cost.
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
