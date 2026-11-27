# 12. A wording can land on principle, owed a case

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md). Amended by [ADR 14](0014-the-gate-fits-the-change.md).

## Context

ADR 10 lets a clause land only with a case that fails without it. From November 2026, most one-turn cases pass on main for the models plumb is tested on, so a sound principle whose failure a short case can't show (a reviewer's false Blocking finding, an unpredicted result explained away) was dropped as "main passes" though nothing measured it. commvnist adopted a principle lane on 2026-11-23 (`plumb/evals/README.md`, `plumb/evals/owed.md`), admitting a wording only where a real output shows its failure, without a record of the change. Some failures (an instruction planted in text the work reads, an invented package name) are well measured in published work and rare in any one project's stored sessions.

## Decision

A wording that is an abstract principle can land on the operator's decision without a case that shows it red, when a real output or published measurement shows the failure it answers, it adds at most 25 words to the rule or step it changes, and no case or guard falls with it in. It is listed in `plumb/evals/owed.md` with the failure it answers and the case it is owed, until a case measures it. Behaviour a case can show still goes through ADR 10's gate.

## Consequences

- Text can land that no run has shown to change behaviour, so every such line costs words in every session on reasoning alone; `owed.md` keeps the debt visible.
- A guard run of the whole changed text against main is the only measured protection against a principle wording that harms another behaviour.
