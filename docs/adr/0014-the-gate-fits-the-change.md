# 14. The gate fits the change

## Status

Accepted. Amends [ADR 10](0010-skill-text-and-its-eval-live-and-die-together.md) and [ADR 12](0012-a-wording-can-land-on-principle.md).

## Context

ADR 10 lands text only with a case that fails without it, and ADR 12 caps a wording landed without such a case at 25 words. Both measure a change to behaviour plumb already shapes. A new feature has no baseline to beat: without it the agent still does something, in no defined way, so a case built for the feature can pass on main run by run while the feature's point goes unmeasured. `plumb-jira` (PR #55) showed this: its format passed on main in single runs, yet main's 18 bug reports took 14 layouts. commvnist set the rule on 2026-11-27: a gate built for rewordings must not cost plumb good new additions, so the process fits the ask.

## Decision

Each change is gated by the question it raises:

- **A rewording, addition or trim in text existing cases guard** is decided against main, as ADR 10 and the evals README's decision rule say.
- **A new feature the operator asks for,** text main doesn't have and guarded by a case written for it, is gated on its own arm: each of its checks passes in at least two thirds of runs on each model (4 of 6 at the first stage), and the nearest existing cases (the same skill, the rules it leans on) hold against main as guards. Its cases aren't removed for passing on main; they are its baseline from the release it lands in. Its text that loads only when the feature is invoked (a skill's or agent's body) is exempt from ADR 12's word cap; text that loads in every session (a description, a hook's output) is not.
- **New text no case guards** is reported as owed a case, under ADR 12.

## Consequences

- A promise of a feature that no check grades (for `plumb-jira`, the need format, the evidence part and cross-run consistency) stays listed in `plumb/evals/owed.md` until one does.
- A later change to a feature's text is a rewording of guarded text and goes against main.
- A feature passing on its own arm shows it keeps its promise, not that it beats doing without it; the operator's ask is the reason it exists.
