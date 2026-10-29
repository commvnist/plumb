# plumb

One engineering philosophy across the whole development lifecycle.

Plumb is not for vibe coding. It is a way of working between an agent and its operator: the operator stays on top of every line, decision and reason, can overturn any choice the agent made, and becomes a better engineer from the suggestions it offers.

**The reviewer is the customer.** Every change is the smallest complete diff that does the job, proven by evidence rather than claims, with one purpose per diff. Everything else (cleanups, extra tests, refactors, hardening) is offered as a ranked, numbered menu. An accepted item lands as its own diff unless it completes code the change itself adds.

## Skills

| Skill | Phase | Does |
|---|---|---|
| `plumb` | all | The charter: the rules every other skill inherits |
| `plumb-plan` | design | Breaks large work into small, independently mergeable diffs |
| `plumb-build` | implement | Smallest complete change, proof, self-review, suggestions menu |
| `plumb-test` | test | When a test should exist, what a good one is, the TDD loop |
| `plumb-debug` | fix | Evidence to root cause to origin fix to one regression test |
| `plumb-refactor` | maintain | Behaviour-preserving restructuring in small green steps |
| `plumb-review` | review | Verdict plus concrete, ranked findings; changes nothing |
| `plumb-ship` | release | Commits, PR descriptions, splitting, changelogs, safe rollout |
| `plumb-audit` | maintain | Read-only repository or test-suite audit, ranked |

## Agents

| Agent | Used by | Why a separate agent |
|---|---|---|
| `plumb-scout` | plan, build | Maps what a change touches without flooding the main context |
| `plumb-reviewer` | build, debug, refactor, review, ship | Fresh eyes: never sees the author's reasoning |
| `plumb-auditor` | audit | One per area, run in parallel |

## Flow

```
plan → build → (test · debug · refactor as needed) → review → ship
                      audit any time
```

Every phase that changes code ends with the same report: what changed, what was decided and why, what was verified, what wasn't, risks, and the suggestions menu. Plan, review and audit return their own formats.

Every change's report has a `Decided` line for the choices a reviewer could have made differently, with the reason for each. Decisions that are expensive to reverse are kept as decision records (Nygard ADRs in `docs/adr/` unless the project has its own format), and commits follow Conventional Commits unless the project has its own convention.

## What surprises people

Each of these is on purpose:

- **It writes fewer tests than you asked for.** A general "add tests" gets the tests that would catch a realistic break, plus a line naming what it left untested and why. Name a test and you get it.
- **It stops after each diff.** A multi-step plan waits for you to commit each step (or tell it to go on), so you review one purpose at a time.
- **It offers instead of fixing.** Cleanups, refactors and hardening come as a numbered menu with the failure each one prevents. Nothing on it lands until you pick it.
- **It won't commit, push or deploy unasked,** and won't add a dependency without a yes.
- **It asks before starting `docs/adr/`** in a project that keeps no decision records.

## Tuning it

The project's written rules (CLAUDE.md, contributing guides, tool configuration) outrank the charter, and an explicit request outranks both. To change a default for a project, say so in its CLAUDE.md, for example:

```
- plumb: commit each plan step without stopping; I review the PR as a whole.
- plumb: diffs up to 600 changed lines are fine here.
- plumb: decision records live in design/decisions/, in MADR format.
```

## Status

Plumb's behaviour is checked by seeded tasks in [evals/](evals/README.md), and CI checks that every numbered rule and step reference still points at the right target (`python3 scripts/check_refs.py`). See [CHANGELOG.md](CHANGELOG.md) for what changes between versions; a change in wording is a change in behaviour.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

To change plumb itself, see [CONTRIBUTING.md](../CONTRIBUTING.md): rules are general principles with their reasons, never case-specific patches.
