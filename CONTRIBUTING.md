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
- Run `python3 scripts/check_refs.py`. If you renumbered a rule or step, re-read every reference to it, then run it with `--update`.
- Run the evals (see `plumb/evals/README.md`) and compare the score with the last run. Expect about ±0.1 between runs.
- Commits follow Conventional Commits. Record what changes for users in `plumb/CHANGELOG.md`.
