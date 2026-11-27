# Contributing to plumb

Plumb's skills are prompts, so a change in wording is a change in behaviour. These rules keep them general enough to improve as models do.

## How a rule is written

- **A principle, not a patch.** Each rule states the general judgement an agent should make, so it covers cases nobody listed. Its reason goes in the commit, changelog or ADR that adds it, and into the rule itself only when an eval shows the reason changes what agents do: every word is loaded in every session. "Judge the cost of reversing a choice by what will come to depend on it" is a principle. "Write an ADR when choosing SQLite" is a patch. *A patch fixes one case and teaches the model to look for lists. A principle fixes the class.*
- **Examples illustrate; they never define.** A parenthetical example ("such as a renamed column") helps the reader see the principle. Don't make it the trigger. If removing the example would change what the rule requires, the rule is too narrow.
- **No named technologies, products or one-off scenarios** in a rule, unless the rule is about that thing (for example, the Conventional Commits default).
- **Say it once.** A rule lives in one place, usually the charter. Other skills point to it by name or number rather than restating it, and `scripts/check_refs.py` keeps those pointers honest.
- **Fix the cause, not the symptom.** When an eval run shows an agent doing the wrong thing, name the judgement it got wrong and correct that, in the fewest words that change the outcome.

## How a change lands

- A change to skill text comes with evidence: an eval case that fails without the text and passes with it (`plumb/evals/`), each arm run at least three times and judged by the decision rule in `plumb/evals/README.md`. Text and its case live and die together: a clause whose case passes without it goes, and so does a case that passes as often without plumb as with it, since it tests the model rather than plumb. Each case names the text it guards (the cases that grade what a session built name theirs by hand in `plumb/evals/_built/guards.json`), and `scripts/check_refs.py` holds the two together.
- A new feature the operator asks for (a skill, an agent, a hook, a new kind of output) has no baseline to beat, so it lands when small cases written for it show it does what it promises and the nearest existing cases hold against main ([ADR 14](docs/adr/0014-a-new-feature-is-gated-by-evals-written-for-it.md)).
- A clause that guards against harm a diff can't revert (lost data, a leaked secret, a step on a live system) is removed only if its case passes without plumb in at least three runs on the floor model, the smallest model the tool offers.
- A rewording that adds no requirement and no words lands when the cases that touch it still pass.
- After changing an agent, `plumb/.claude-plugin/plugin.json` or the marketplace, run `python3 scripts/build_codex.py` to regenerate the Codex files; CI fails while they're out of date.
- Run `python3 scripts/check_refs.py`, and `python3 scripts/test_check_commit.py`, `python3 scripts/test_session_start.py`, `python3 scripts/test_charter_gate.py` and `python3 scripts/test_after_push.py` after changing a hook. A hook's output reaches the agent only in the shape each tool reads, so check both shapes. If you renumbered a rule or step, re-read every reference to it, then run it with `--update`, which also rewrites `scripts/unguarded.txt`, the list of rules and steps no eval case guards.
- Run the evals (see `plumb/evals/README.md`) and compare the score with the last run. Expect about ±0.1 between single runs. After editing `plumb/evals/_fixtures/write_cases.py`, regenerate the cases; CI runs it with `--check`. After changing a regex grader, add what it must and must not match to `scripts/test_graders.py` and run it.
- Commits follow Conventional Commits. Record what changes for users under `## Unreleased` at the top of `plumb/CHANGELOG.md`.

## How a release happens

Each merge to main releases itself (`.github/workflows/release.yml`, [ADR 5](docs/adr/0005-release-from-conventional-commits.md)). The pull request title, which becomes the squash commit's subject, sets the bump, read after any leading Jira key such as `[PROJ-123] `: `feat` is minor, `fix` and `perf` are patch, a `!` after the type or a `BREAKING CHANGE:` footer is major, and any other type is patch when it changes shipped text (skills, agents, hooks) and releases nothing otherwise. To override, add a `release:major`, `release:minor`, `release:patch` or `release:none` label to the pull request before merging. The workflow bumps the version files, turns `## Unreleased` into the version's section, commits that as `chore(release): X.Y.Z`, and publishes the release with the cleaned zip attached.
