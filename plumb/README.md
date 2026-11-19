# plumb

One engineering philosophy across the whole development lifecycle.

Plumb is not for vibe coding. It is a way of working between an agent and its operator: the operator stays on top of every line, decision and reason, can overturn any choice the agent made, and becomes a better engineer from the suggestions it offers.

**The reviewer is the customer.** Every change is the smallest complete diff that does the job, proven by evidence rather than claims, with one purpose per diff. Everything else (cleanups, extra tests, refactors, hardening) is offered as suggestions.

## Skills

| Skill | Phase | Does |
|---|---|---|
| `plumb` | all | The charter: the rules every other skill inherits |
| `plumb-plan` | design | Breaks large work into small, independently mergeable diffs |
| `plumb-build` | implement | Smallest complete change, proof, self-review, suggestions |
| `plumb-test` | test | When a test should exist and what a good one is |
| `plumb-debug` | fix | Evidence to root cause to origin fix to one regression test |
| `plumb-refactor` | maintain | Behaviour-preserving restructuring in small green steps |
| `plumb-review` | review | Verdict plus concrete, ranked findings; changes nothing |
| `plumb-ship` | release | Commits and pull requests, only when asked |
| `plumb-audit` | maintain | Read-only repository or test-suite audit, ranked |
| `plumb-explain` | any | Walks you through code, a diff or a decision, traced through one real case; changes nothing |
| `plumb-auto` | all | Runs a whole task without stopping, checks pinned first and an independent review last, then one report of every commit, choice and assumption |

## Agents

| Agent | Used by | Why a separate agent |
|---|---|---|
| `plumb-scout` | build, auto | Maps what a change touches without flooding the main context |
| `plumb-reviewer` | auto, or on request | Fresh eyes: never sees the author's reasoning |
| `plumb-auditor` | audit | One per area, run in parallel |

All three are told to change nothing, and Claude Code gives them no edit tools, but each can run shell commands (to run checks and read history), so "read-only" is an instruction for the shell.

## Flow

```
plan → build → (test · debug · refactor as needed) → review → ship
                 audit · explain any time · auto runs the whole line
```

Every phase that changes code ends with the same short report: what was done and why, what was decided, what was verified, what it is waiting on from you, and any suggestions. Plan, review and audit return their own formats. All of them are written to be skimmed: formatted text rather than code blocks, one item per line, numbered where you might answer by number.

A report for a small change reads like this:

- **Done:** fix(pricing): accept thousands separators in typed prices (uncommitted)
- **Why:** `Decimal("1,200.50")` raises; `parse_price` passed the text to `Decimal` with the comma still in it (shop/pricing.py:6).
- **Decided:** strip every comma rather than check group positions, over a stricter parse that rejects "1,2,3": the smaller change covers the reported input.
- **Verified:** `python3 -m unittest` → 5 tests OK; the new test failed on the old code with the same error.
- **Waiting on:** a yes to commit.
- **Suggestions:** 1. "1,50" (a European decimal comma) now parses as 150; if those customers exist, reject a comma not followed by three digits.

Read Decided and Suggestions first: they are where you agree, overrule, or pick what comes next, by number.

Every change's report has a `Decided` line for the choices a reviewer could have made differently, with the reason for each. Decisions that are expensive to reverse are kept as decision records (Nygard ADRs in `docs/adr/` unless the project has its own format). Commits follow Conventional Commits, and commits and pull requests carry what the diff can't show, for a reviewer deciding whether to merge (see plumb-ship).

## What surprises people

Each of these is on purpose:

- **It writes fewer tests than you asked for.** A general "add tests" gets the tests that would catch a realistic break, plus a line naming what it left untested and why. Name a test and you get it.
- **It stops after each diff.** A multi-step plan waits for you after each step: commit it yourself or tell it to, then say to go on, so you review one purpose at a time. Ask for `plumb-auto` and it runs to the end instead, one commit per diff on a new branch, and reports every assumption it made in place of asking.
- **It offers instead of fixing.** Cleanups, refactors and hardening come as suggestions, each with the failure it prevents. None lands until you pick it.
- **Nothing it writes says an AI wrote it.** Code, comments, commits and pull requests are written in a neutral technical voice, never "I" or "we", never mention AI help, carry no co-author or generated-by lines, and are committed under your own git identity.
- **It won't commit, push or deploy unasked,** and won't add a dependency without a yes.
- **It asks before starting `docs/adr/`** in a project that keeps no decision records.
- **It doesn't fold when you push back.** Question a choice and it checks again: if you're right it says what was wrong and where else the same mistake appears. If what you ask rests on a fact about the code that isn't true, it shows you the line and waits. Ask for something it can see failing and it follows you, naming the risk once.

## Tuning it

The project's written rules (CLAUDE.md, contributing guides, tool configuration) outrank the charter, and an explicit request outranks both. To change a default for a project, say so in its CLAUDE.md, for example:

```
- plumb: decision records live in design/decisions/, in MADR format.
```

### Choosing models

Plumb names no model for its agents. Unless you choose, each one runs on your tool's default for subagents (in Claude Code, `CLAUDE_CODE_SUBAGENT_MODEL` if you set it, otherwise your session's model; in Codex, see [installing on Codex](../README.md#codex); in Copilot CLI, your `/subagents` setting if you set one). To choose per role, add a `plumb agents:` line with a model, and optionally a reasoning effort, for any role; use whatever model names your tool accepts:

```
- plumb agents: scout haiku low, auditor haiku, reviewer opus high
```

What each role needs, to help you spend where it counts:

- **Scout and auditor** read, search and map. A small, fast model usually does this well, and an audit starts one auditor per area, so their cost multiplies.
- **Reviewer** is the last independent check before you merge, and runs only when you ask for it (asking for `plumb-auto` counts). This is where a stronger model pays off, if your budget has one.

Every reply that started an agent says which model each ran on, or that it ran on your tool's default when the tool doesn't report which, so you can see what a run cost and spot a setting that didn't take.

A model choice that is yours rather than the project's (your budget, your subscription) can go in your own instruction file instead of the shared one: in Claude Code, `CLAUDE.local.md` in the project or `~/.claude/CLAUDE.md`. Plumb reads the line wherever your tool loads it.

To run without subagents, because your budget or tool has none, write `- plumb agents: off`. Plumb then does each agent's work in the session, except when you ask for an agent yourself: it then starts one and says that it did despite the setting.

## Status

Plumb's behaviour is checked by seeded tasks in [evals/](evals/README.md), and CI checks that every numbered rule and step reference still points at the right target (`python3 scripts/check_refs.py`). See [CHANGELOG.md](CHANGELOG.md) for what changes between versions; a change in wording is a change in behaviour.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

To change plumb itself, see [CONTRIBUTING.md](../CONTRIBUTING.md): rules are general principles with their reasons, never case-specific patches.
