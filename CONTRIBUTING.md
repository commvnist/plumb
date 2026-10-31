# Contributing to plumb

Plumb's skills are prompts, so a change in wording is a change in behaviour. These rules keep them general enough to improve as models do.

## How a rule is written

- **A principle and its reason, not a patch.** Each rule states the general judgement an agent should make and why, so it covers cases nobody listed. "Judge the cost of reversing a choice by what will come to depend on it" is a principle. "Write an ADR when choosing SQLite" is a patch. *A patch fixes one case and teaches the model to look for lists. A principle fixes the class.*
- **Examples illustrate; they never define.** A parenthetical example ("such as a renamed column") helps the reader see the principle. Don't make it the trigger. If removing the example would change what the rule requires, the rule is too narrow.
- **No named technologies, products or one-off scenarios** in a rule, unless the rule is about that thing (for example, the Conventional Commits default).
- **Say it once.** A rule lives in one place, usually the charter. Other skills point to it by name or number rather than restating it, and `scripts/check_refs.py` keeps those pointers honest.
- **Fix the cause, not the symptom.** When an eval run shows an agent doing the wrong thing, name the judgement it got wrong and correct that, in the fewest words that change the outcome.

## How a change lands

- A change to skill text comes with evidence: an eval case that shows the failure it fixes (`plumb/evals/`), or an existing case that already covers it.
- After changing an agent, `plumb/.claude-plugin/plugin.json` or the marketplace, run `python3 scripts/build_codex.py` to regenerate the Codex files; CI fails while they're out of date.
- Run `python3 scripts/check_refs.py`, and `python3 scripts/test_check_commit.py` after changing the commit hook. If you renumbered a rule or step, re-read every reference to it, then run it with `--update`.
- Run the evals (see `plumb/evals/README.md`) and compare the score with the last run. Expect about ±0.1 between runs.
- Commits follow Conventional Commits. Record what changes for users under `## Unreleased` at the top of `plumb/CHANGELOG.md`.

## How a release happens

Each merge to main releases itself (`.github/workflows/release.yml`, [ADR 5](docs/adr/0005-release-from-conventional-commits.md)). The pull request title, which becomes the squash commit's subject, sets the bump: `feat` is minor, `fix` and `perf` are patch, a `!` after the type or a `BREAKING CHANGE:` footer is major, and other types release nothing. To override, add a `release:major`, `release:minor`, `release:patch` or `release:none` label to the pull request before merging. The workflow bumps the version files, turns `## Unreleased` into the version's section, commits that as `chore(release): X.Y.Z`, and publishes the release with the cleaned zip attached.
