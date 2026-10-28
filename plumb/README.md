# plumb

One engineering philosophy across the whole development lifecycle.

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
| `plumb-reviewer` | build, review, ship | Fresh eyes: never sees the author's reasoning |
| `plumb-auditor` | audit | One per area, run in parallel |

## Flow

```
plan → build → (test · debug · refactor as needed) → review → ship
                      audit any time
```

Every phase that changes code ends with the same report: what changed, what was verified, what wasn't, risks, and the suggestions menu. Plan, review and audit return their own formats.
