# 8. One principal engineer's lens for suggestions, not checklists or panels

## Status

Accepted

## Context

Plumb must raise the quality bar beyond the diff so the operator grows, without turning into a checklist the agent works through. Proposals in October 2026 tried a fixed "bar" checklist and a panel of personas (maintainer, operator, adversary). commvnist rejected both (2026-10-28) as too specific: they age as models improve and teach the agent to look for lists.

## Decision

Suggestions come from a single lens: what a principal engineer sharing the charter would still insist on before relying on the change, each with the failure it prevents, ranked and unapplied. Rules are worded as principles; examples illustrate and never define (CONTRIBUTING.md).

## Consequences

- No skill carries a checklist of quality attributes; a review that proposes one is re-raising this.
- What the lens surfaces depends on the model's judgement, so evals grade that a material point appears (`bf-medium-suggestions`), not which one.
