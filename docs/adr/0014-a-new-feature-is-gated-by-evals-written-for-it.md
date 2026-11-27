# 14. A new feature is gated by evals written for it

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md) and [ADR 12](0012-a-wording-can-land-on-principle.md).

## Context

ADR 10 lands text only with a case that fails without it, and ADR 12 caps a wording landed without such a case at 25 words. Both measure a change to behaviour plumb already shapes. A feature that gives plumb new ground has no baseline to beat: without it, the agent still does something, just in no defined way, so a case built for the feature often passes on main by the model's own judgement while the feature's point (one format, every time) goes unmeasured. `plumb-jira` (PR #55) showed this: its format passed on main in single runs, yet main's 18 bug reports took 14 layouts. commvnist set the rule on 2026-11-27: a new feature the existing evals weren't built for can't be judged by beating main on them.

## Decision

A new feature the operator asks for (a skill, an agent, a hook, or a new kind of output) lands when evals written for it show it does what it promises, and the cases nearest the text it touches show no regression against main (`gate.py --guard`). It is exempt from ADR 12's 25-word cap. Its cases stay small and targeted: what the feature promises, on the floor model first, at ADR 10's staged run counts. Later changes to the feature's text go through ADR 10 and ADR 12 like any other wording.

## Consequences

- A feature's own cases, not main, are its baseline from the release it lands in.
- A promise no case shows kept (for `plumb-jira`, the markup and edit clauses) is still listed in `plumb/evals/owed.md` until one does.
- Words a feature adds load only where the feature is used, so the budget that bounds the charter doesn't bound a skill a request loads on its own.
